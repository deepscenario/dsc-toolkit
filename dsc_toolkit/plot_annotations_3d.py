import argparse
import os
from typing import Callable

import numpy as np
import pandas as pd
import vedo
from tqdm import tqdm

from dsc_toolkit.utils.generic import (
    check_recording_in_dataset,
    filter_by_frame_range,
    filter_by_track_ids,
    get_frame_range,
    get_look_at_transform,
)
from dsc_toolkit.utils.io import load_data_meta
from dsc_toolkit.utils.map import DiscretizedMap
from dsc_toolkit.utils.visuals import get_ann_visuals, set_camera_transform


def make_animate_fn(plotter: vedo.Plotter, anns_df: pd.DataFrame, frames_df: pd.DataFrame,
                    save_dir: str | None) -> Callable:
    frame_idx = 0
    visuals_curr = []
    pbar = tqdm(total=len(frames_df), desc='Visualizing frames', unit='frame')
    anns_df_grouped = anns_df.groupby('frame_id')

    def animate_fn(event: vedo.plotter.Event) -> None:
        nonlocal frame_idx
        if frame_idx >= len(frames_df):
            plotter.close()
            return

        frame_dict = frames_df.iloc[frame_idx]
        frame_id = frame_dict['frame_id']

        plotter.remove(visuals_curr)
        visuals_curr.clear()
        visuals_curr.append(vedo.Text2D(f'Frame id: {frame_id}'))

        if frame_id in anns_df_grouped.groups:
            anns_frame_df = anns_df_grouped.get_group(frame_id)
            anns_visuals = [
                get_ann_visuals(track_id, translation, rotation, dimension)
                for track_id, translation, rotation, dimension in zip(
                    anns_frame_df['track_id'],
                    anns_frame_df[['translation_x', 'translation_y', 'translation_z']].to_numpy(),
                    anns_frame_df[['rotation_x', 'rotation_y', 'rotation_z']].to_numpy(),
                    anns_frame_df[['dimension_x', 'dimension_y', 'dimension_z']].to_numpy(),
                )
            ]
            visuals_curr.extend(anns_visuals)

        plotter.add(visuals_curr)

        if plotter._interactive:
            plotter.render()

        if save_dir is not None:
            img_fname = f'{frame_id}.png'
            vedo.screenshot(os.path.join(save_dir, img_fname))

        frame_idx += 1
        pbar.update(1)

    return animate_fn


def set_initial_camera_pose(plotter: vedo.Plotter, anns_df: pd.DataFrame, relative_altitude: float) -> None:
    anns_center = anns_df[['translation_x', 'translation_y', 'translation_z']].mean().to_numpy()
    eye = anns_center + np.array([0, 0, relative_altitude])
    camera_transform = get_look_at_transform(center=anns_center, eye=eye, up=np.array([0, 1, 0]))
    set_camera_transform(plotter, camera_transform)


def plot_annotations_3d(
    data_dir: str,
    recording_id: str,
    save_dir: str | None = None,
    mesh_path: str | None = None,
    map_path: str | None = None,
    relative_altitude: float = 100,
    headless: bool = False,
    track_ids: list[int] | None = None,
    frame_range: tuple[int, int] | None = None,
) -> None:
    data_meta = load_data_meta(data_dir)
    check_recording_in_dataset(data_meta, recording_id)

    time_step = data_meta['frame_distance'] / data_meta['frame_rate']
    background_color = np.array([251, 245, 255], np.uint8) / 255

    anns_path = os.path.join(data_dir, 'annotations', recording_id, 'annotations.parquet')
    anns_df = pd.read_parquet(anns_path)

    frames_path = os.path.join(data_dir, 'annotations', recording_id, 'frames.parquet')
    frames_df = pd.read_parquet(frames_path)

    if track_ids is not None:
        anns_df = filter_by_track_ids(anns_df, track_ids)

    if frame_range is not None:
        anns_df = filter_by_frame_range(anns_df, frame_range)

    assert len(anns_df) > 0, 'No annotations to visualize'

    frame_range = get_frame_range(anns_df)
    frames_df = filter_by_frame_range(frames_df, frame_range)

    plotter = vedo.Plotter(interactive=not headless, offscreen=headless)
    plotter.background(background_color)

    if mesh_path is not None:
        textured_mesh_visuals = vedo.load_obj(mesh_path, texture_path=os.path.dirname(mesh_path))
        for mesh_visual in textured_mesh_visuals:
            mesh_visual.lighting(style='ambient')
        plotter.add(textured_mesh_visuals)

    if map_path is not None:
        road_map = DiscretizedMap.load_from_file(map_path)
        lane_visuals = road_map.get_lane_visuals()
        plotter.add(lane_visuals)

    if save_dir is not None:
        print(f'Screenshots will be saved in {save_dir}')
        os.makedirs(save_dir, exist_ok=True)

    set_initial_camera_pose(plotter, anns_df, relative_altitude)
    animate_fn = make_animate_fn(plotter, anns_df, frames_df, save_dir)

    if headless:
        for frame in frames_df.iterrows():
            animate_fn(None)
    else:
        plotter.add_callback('timer', animate_fn, enable_picking=False)
        plotter.timer_callback('start', dt=int(time_step * 1000))
        plotter.show()

    # prevent OpenGL context pollution
    plotter.clear()
    if hasattr(plotter, 'window') and plotter.window:
        plotter.window.Finalize()
    plotter.close()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Script to visualize the provided annotations in 3D')
    parser.add_argument('--data_dir', help='Directory that contains the released data', type=str, required=True)
    parser.add_argument('--recording', help='Recording to plot', type=str, dest='recording_id', required=True)
    parser.add_argument('--save_dir', help='Directory where the rendered images are saved', type=str)
    parser.add_argument('--map', help='Path to the OpenDRIVE map', dest='map_path', type=str)
    parser.add_argument('--mesh', help='Path to the textured mesh', dest='mesh_path', type=str)
    parser.add_argument('--relative_altitude', help='Relative altitude of camera [m]', type=float, default=100)
    parser.add_argument('--headless', help='Do not show the visualizer', action='store_true')
    parser.add_argument('--track_ids', help='Filter annotations by track ids', type=int, nargs='+', default=None)
    parser.add_argument('--frame_range', help='Filter annotations with frame id range', type=int, nargs=2, default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    plot_annotations_3d(**vars(args))


if __name__ == '__main__':
    main()
