import numpy as np
import pandas as pd
import pytest
import vedo

from dsc_toolkit.utils.generic import (
    check_recording_in_dataset,
    filter_by_frame_range,
    filter_by_track_ids,
    get_frame_range,
    get_look_at_transform,
)
from dsc_toolkit.utils.visuals import get_coordinate_frame


def visualize_scene(center: np.ndarray, eye: np.ndarray, transform: np.ndarray, text: str) -> None:
    plotter = vedo.Plotter()
    plotter.add(get_coordinate_frame().apply_transform(transform))
    plotter.add(vedo.Text2D(text))

    plotter.add(vedo.Sphere(pos=center, c='orange', r=0.1))
    plotter.add(vedo.Sphere(pos=eye, c='pink', r=0.1))
    plotter.add(vedo.Line(p0=eye, p1=center))

    plotter.show(axes=1, viewup='z').close()


def test_top_down_look_at_transform(show: bool) -> None:
    kwargs = {'center': np.array([2, 2, 0]), 'eye': np.array([2, 2, 3]), 'up': np.array([0, 1, 0])}
    top_down_transform = get_look_at_transform(**kwargs)

    if show:
        visualize_scene(kwargs['center'], kwargs['eye'], top_down_transform, 'top down look at')

    assert np.allclose(top_down_transform[:3, 3], kwargs['eye'])

    assert np.allclose(top_down_transform[:3, 0], [1, 0, 0])
    assert np.allclose(top_down_transform[:3, 1], [0, -1, 0])
    assert np.allclose(top_down_transform[:3, 2], [0, 0, -1])


def test_front_face_look_at_transform(show: bool) -> None:
    kwargs = {'center': np.array([0, 3, 0]), 'eye': np.array([0, 0, 0]), 'up': np.array([0, 0, 1])}
    front_face_transform = get_look_at_transform(**kwargs)

    if show:
        visualize_scene(kwargs['center'], kwargs['eye'], front_face_transform, 'front face look at')

    assert np.allclose(front_face_transform[:3, 3], kwargs['eye'])

    assert np.allclose(front_face_transform[:3, 0], [1, 0, 0])
    assert np.allclose(front_face_transform[:3, 1], [0, 0, -1])
    assert np.allclose(front_face_transform[:3, 2], [0, 1, 0])


def test_filter_frame_range(anns_df: pd.DataFrame) -> None:
    assert get_frame_range(anns_df) == (0, 148)

    frame_range = (10, 20)
    anns_df = filter_by_frame_range(anns_df, frame_range)
    assert get_frame_range(anns_df) == frame_range


def test_filter_track_ids(anns_df: pd.DataFrame) -> None:
    assert tuple(anns_df['track_id'].unique()) == (2, 3, 4)
    anns_df = filter_by_track_ids(anns_df, track_ids=[2, 4])
    assert tuple(anns_df['track_id'].unique()) == (2, 4)


def test_check_recording_in_dataset(data_meta: dict, recording_id: str) -> None:
    check_recording_in_dataset(data_meta, recording_id)

    with pytest.raises(AssertionError, match='not found'):
        check_recording_in_dataset(data_meta, 'invalid_recording_id')
