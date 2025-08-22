import shlex
from pathlib import Path

import pandas as pd

from dsc_toolkit.plot_annotations_3d import main
from dsc_toolkit.utils.generic import filter_by_frame_range


def test_main_function(data_dir: str, recording_id: str, mesh_path: str, map_path: str, tmp_path: Path,
                       frames_df: pd.DataFrame, show: bool) -> None:
    frame_range = (10, 20)
    headless = '--headless' if not show else ''
    test_args = shlex.split(f'''
    --data_dir {data_dir}
    --recording {recording_id}
    --mesh {mesh_path}
    --map {map_path}
    --save_dir {str(tmp_path)}
    --frame_range {frame_range[0]} {frame_range[1]}
    {headless}
    ''')
    main(test_args)

    n_imgs_expected = len(filter_by_frame_range(frames_df, frame_range))
    n_imgs_actual = len(list(tmp_path.glob('*.png')))
    assert n_imgs_actual == n_imgs_expected, f'Unexpected number of images: {n_imgs_expected} != {n_imgs_actual}'
