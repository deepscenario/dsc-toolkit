import argparse
import os

import numpy as np
import open3d as o3d
import rasterio

from dsc_toolkit.utils.geospatial import get_utm_crs
from dsc_toolkit.utils.io import load_data_meta


def get_orthographic_intrinsics(
    bound_min: np.ndarray,
    bound_max: np.ndarray,
    pixel_size: float,
    near_offset: float,
) -> dict:
    assert near_offset > 0 and pixel_size > 0

    width = int((bound_max[0] - bound_min[0]) / pixel_size)
    height = int((bound_max[1] - bound_min[1]) / pixel_size)

    return {
        'width': width,
        'height': height,
        'left': bound_min[0],
        'right': bound_max[0],
        'bottom': bound_min[1],
        'top': bound_max[1],
        'near': near_offset,
        'far': bound_max[2] - bound_min[2] + near_offset
    }


def get_orthographic_look_at(bound_max: np.ndarray, near_offset: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    assert near_offset > 0

    camera_position = np.array([0., 0., bound_max[2] + near_offset])
    target = np.array([0., 0., bound_max[2]])
    up = np.array([0., 1., 0.])
    return target, camera_position, up


def render_orthographic_image(
    mesh: o3d.visualization.rendering.TriangleMeshModel,
    bound_min: np.ndarray,
    bound_max: np.ndarray,
    pixel_size: float,
    near_offset: float = 1,
) -> np.ndarray:
    # create renderer with orthophoto camera intrinsics and extrinsics
    intrinsics = get_orthographic_intrinsics(bound_min, bound_max, pixel_size, near_offset)
    center, eye, up = get_orthographic_look_at(bound_max, near_offset)

    renderer = o3d.visualization.rendering.OffscreenRenderer(width=intrinsics['width'], height=intrinsics['height'])
    renderer.scene.camera.set_projection(
        o3d.visualization.rendering.Camera.Projection.Ortho,
        intrinsics['left'],
        intrinsics['right'],
        intrinsics['bottom'],
        intrinsics['top'],
        intrinsics['near'],
        intrinsics['far'],
    )
    renderer.scene.camera.look_at(center, eye, up)

    # add the mesh to the scene for rendering
    material = o3d.visualization.rendering.MaterialRecord()
    material.shader = 'defaultUnlit'
    renderer.scene.add_model('mesh', mesh)
    renderer.scene.modify_geometry_material('Mesh', material)
    renderer.scene.set_lighting(renderer.scene.LightingProfile.NO_SHADOWS, (0, 0, 0))
    # fixes strong colors shifts https://github.com/isl-org/Open3D/issues/6020#issuecomment-1907148063
    cg_settings = o3d.visualization.rendering.ColorGrading(o3d.visualization.rendering.ColorGrading.Quality.ULTRA,
                                                           o3d.visualization.rendering.ColorGrading.ToneMapping.LINEAR)
    renderer.scene.view.set_color_grading(cg_settings)

    img = np.asarray(renderer.render_to_image())
    assert img.shape[2] == 3 and img.dtype == np.uint8, f'Rendered image ({img.shape},dtype={img.dtype}) is not RGB'

    # add alpha channel for transparent areas
    img_depth_normalized = np.asarray(renderer.render_to_depth_image(z_in_view_space=False))
    alpha_channel = (img_depth_normalized < 1.0).astype(np.uint8) * 255
    img_rgba = np.dstack((img, alpha_channel))

    return img_rgba


def get_bounds(triangle_model: o3d.visualization.rendering.TriangleMeshModel) -> tuple[np.ndarray, np.ndarray]:
    bound_min = np.full(3, np.inf)
    bound_max = np.full(3, -np.inf)

    for mesh in triangle_model.meshes:
        bound_max = np.maximum(bound_max, np.asarray(mesh.mesh.vertices).max(axis=0))
        bound_min = np.minimum(bound_min, np.asarray(mesh.mesh.vertices).min(axis=0))

    assert np.all(np.isfinite(bound_min)) and all(np.isfinite(bound_max))

    return bound_min, bound_max


def save_orthophoto(
    img: np.ndarray,
    raster_path: str,
    reference_utm: dict,
    bound_min: np.ndarray,
    bound_max: np.ndarray,
    pixel_size: float,
) -> None:
    utm_crs = get_utm_crs(*reference_utm['zone'])

    transform = rasterio.transform.from_origin(
        bound_min[0] + reference_utm['offset'][0],
        bound_max[1] + reference_utm['offset'][1],
        pixel_size,
        pixel_size,
    )

    data = img.transpose((2, 0, 1))
    n_bands, height, width = data.shape

    metadata = {
        'driver': 'GTiff',
        'height': height,
        'width': width,
        'count': n_bands,
        'dtype': data.dtype,
        'crs': utm_crs,
        'transform': transform,
        'nodata': 0,
        'compress': 'jpeg',
        'jpeg_quality': 100,
    }

    os.makedirs(os.path.dirname(raster_path), exist_ok=True)
    with rasterio.open(raster_path, 'w+', **metadata) as dst:
        dst.write(data)


def render_orthophoto(data_dir: str, mesh_path: str, save_dir: str, pixel_size: float = 0.5) -> None:
    data_meta = load_data_meta(data_dir)
    reference_utm = data_meta['reference_utm']

    triangle_model = o3d.io.read_triangle_model(mesh_path)
    assert len(triangle_model.meshes) > 0, 'No mesh in triangle model'

    bound_min, bound_max = get_bounds(triangle_model)
    img = render_orthographic_image(triangle_model, bound_min, bound_max, pixel_size=pixel_size)

    save_orthophoto_path = os.path.join(save_dir, 'orthophoto.tif')
    save_orthophoto(img, save_orthophoto_path, reference_utm, bound_min, bound_max, pixel_size)
    print(f'Orthophoto saved to {save_orthophoto_path}')


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Script to render an orthophoto from a textured mesh')
    parser.add_argument('--data_dir', help='Directory that contains the released data', type=str, required=True)
    parser.add_argument('--mesh', help='Path to the textured mesh', dest='mesh_path', type=str)
    parser.add_argument('--save_dir', help='Directory where the orthophoto is saved', type=str, required=True)
    parser.add_argument('--pixel_size', help='Size of a pixel in meters', type=float, default=0.5)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    render_orthophoto(**vars(args))


if __name__ == '__main__':
    main()
