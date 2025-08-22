import json
import os

from dsc_toolkit import __version__


def load_json(json_file: str) -> dict:
    with open(json_file) as file:
        return json.load(file)


def load_data_meta(data_dir: str) -> dict:
    data_meta = load_json(os.path.join(data_dir, 'data_meta.json'))
    dsc_toolkit_version = __version__
    data_meta_interface_version = data_meta['interface_version']
    if dsc_toolkit_version[0].split('.')[0] != data_meta_interface_version.split('.')[0]:
        raise RuntimeError(f'Incompatible version number between '
                           f'the dataset (v{data_meta_interface_version}) '
                           f'and this dsc-toolkit (v{dsc_toolkit_version})')
    return data_meta
