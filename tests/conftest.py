import os
from pathlib import Path

import pandas as pd
import pytest

from dsc_toolkit.utils.io import load_json


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption('--show', action='store_true', help='Open visualizer')


@pytest.fixture
def show(request: pytest.FixtureRequest) -> None:
    return request.config.getoption('--show', False)


@pytest.fixture
def data_dir() -> str:
    assets_dir = Path(__file__).parent / 'assets'
    return str(assets_dir / 'data')


@pytest.fixture
def data_meta(data_dir: str) -> dict:
    data_meta_dict = load_json(os.path.join(data_dir, 'data_meta.json'))
    return data_meta_dict


@pytest.fixture
def recording_id(data_meta: dict) -> dict:
    return data_meta['locations'][0]['recordings'][0]


@pytest.fixture
def mesh_path(data_dir: str) -> str:
    return os.path.join(data_dir, 'textured_mesh', 'textured_mesh.obj')


@pytest.fixture
def map_path(data_dir: str) -> str:
    return os.path.join(data_dir, 'map', 'map.xodr')


@pytest.fixture
def anns_df(data_dir: str, recording_id: str) -> dict:
    anns_path = os.path.join(data_dir, 'annotations', recording_id, 'annotations.parquet')
    return pd.read_parquet(anns_path)


@pytest.fixture
def frames_df(data_dir: str, recording_id: str) -> dict:
    frames_path = os.path.join(data_dir, 'annotations', recording_id, 'frames.parquet')
    return pd.read_parquet(frames_path)
