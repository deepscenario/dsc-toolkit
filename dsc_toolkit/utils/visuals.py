import numpy as np
import vedo

from dsc_toolkit.utils.generic import get_transform


def get_coordinate_frame() -> vedo.Arrows:
    arrows = vedo.Arrows(start_pts=[(0, 0, 0), (0, 0, 0), (0, 0, 0)], end_pts=[(1, 0, 0), (0, 1, 0), (0, 0, 1)],
                         c=['r', 'g', 'b'], res=100)
    return arrows


def get_ann_visuals(track_id: int, translation: np.ndarray, rotation: np.ndarray, dimension: np.ndarray) -> list:
    transform = vedo.LinearTransform(get_transform(translation, rotation))
    center = np.array([0, 0, 0.5]) * dimension

    color = np.array([172, 133, 241], np.uint8) / 255
    front_top_line_color = np.array([251, 39, 62], np.uint8) / 255
    label_color = np.array([0, 0, 1], np.uint8) / 255

    box = vedo.Box(
        pos=center,
        size=dimension,
        c=color,
    ).apply_transform(transform).alpha(0.35)
    box.lighting(ambient=0.5, diffuse=0.2, specular=0.2, specular_power=3, specular_color=(1, 1, 1))

    front_top_line = vedo.Line(box.vertices[5], box.vertices[7], c=front_top_line_color, lw=2)

    caption_kwargs = {
        'size': (0.025, 0.025),
        'lw': 1,
        'vspacing': 0,
        'padding': 0,
        'c': label_color,
        'justify': 'center',
        'font': 'VictorMono'
    }
    label = box.caption(txt=str(track_id), **caption_kwargs)

    perimeter_kwargs = {'c': color, 'lw': 2}
    perimeter_start = np.array([
        [0.5, 0.5, 1],
        [0.5, 0.5, 0],
        [0.5, -0.5, 0],
        [-0.5, -0.5, 1],
        [-0.5, 0.5, 1],
        [-0.5, 0.5, 0],
        [-0.5, -0.5, 0],
        [0.5, 0.5, 1],
        [-0.5, 0.5, 0],
        [0.5, -0.5, 1],
        [-0.5, -0.5, 0],
    ]) * dimension
    perimeter_end = np.array([
        [0.5, 0.5, 0],
        [0.5, -0.5, 0],
        [0.5, -0.5, 1],
        [-0.5, 0.5, 1],
        [-0.5, 0.5, 0],
        [-0.5, -0.5, 0],
        [-0.5, -0.5, 1],
        [-0.5, 0.5, 1],
        [0.5, 0.5, 0],
        [-0.5, -0.5, 1],
        [0.5, -0.5, 0],
    ]) * dimension
    perimeter = vedo.Lines(
        start_pts=perimeter_start,
        end_pts=perimeter_end,
        **perimeter_kwargs,
    ).apply_transform(transform)

    return [front_top_line, box, label, perimeter]


def set_camera_transform(plotter: vedo.Plotter, camera_transform: np.ndarray) -> None:
    assert camera_transform.shape == (4, 4), f'Malformed camera transform {camera_transform}'
    assert np.allclose(camera_transform[3, :], [0, 0, 0, 1])

    plotter.camera.SetPosition(0, 0, 0)
    plotter.camera.SetFocalPoint(0, 0, 1)
    plotter.camera.SetViewUp(0, -1, 0)
    plotter.camera.ApplyTransform(vedo.LinearTransform(camera_transform).T)
