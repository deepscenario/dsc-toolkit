import numpy as np
import pandas as pd
from scipy.spatial.transform import Rotation


def check_recording_in_dataset(data_meta: dict, recording_id: str) -> None:
    assert any(recording_id in location['recordings'] for location in data_meta['locations']), \
        f'Recording {recording_id} not found in data meta'


def filter_by_track_ids(anns_df: pd.DataFrame, track_ids: list[int]) -> pd.DataFrame:
    return anns_df[anns_df['track_id'].isin(track_ids)]


def filter_by_frame_range(df: pd.DataFrame, frame_range: tuple[int, int]) -> pd.DataFrame:
    assert len(frame_range) == 2 and 0 <= frame_range[0] <= frame_range[1], f'Invalid frame range: {frame_range}'
    return df[df['frame_id'].between(frame_range[0], frame_range[1])]


def get_frame_range(df: pd.DataFrame) -> tuple[int, int]:
    assert 'frame_id' in df.columns, 'No frame_id column in DataFrame'
    assert len(df) > 0, 'DataFrame is empty'

    return (int(df['frame_id'].iloc[0]), int(df['frame_id'].iloc[-1]))


def get_transform(translation: np.ndarray, rotation: np.ndarray) -> np.ndarray:
    transform = np.eye(4)
    transform[:3, :3] = Rotation.from_rotvec(rotation).as_matrix()
    transform[:3, 3] = translation
    return transform


def normalize(vector: np.ndarray) -> np.ndarray:
    return vector / np.linalg.norm(vector)


def get_look_at_transform(center: np.ndarray, eye: np.ndarray, up: np.ndarray) -> np.ndarray:
    ez = normalize(center - eye)
    ey = normalize(-up)

    ex = normalize(np.cross(ey, ez))
    ey = normalize(np.cross(ez, ex))

    eye_rotation_matrix = np.column_stack([ex, ey, ez])

    transform = np.eye(4)
    transform[:3, :3] = eye_rotation_matrix
    transform[:3, 3] = eye

    return transform
