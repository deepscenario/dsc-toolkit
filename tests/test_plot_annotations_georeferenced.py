import shlex
from pathlib import Path

from dsc_toolkit.plot_annotations_georeferenced import main


def test_plot_georeferenced_anns(data_dir: str, recording_id: str, tmp_path: Path) -> None:
    test_args = shlex.split(f'''
    --data_dir {data_dir}
    --recording {recording_id}
    --save_dir {str(tmp_path)}
    ''')
    main(test_args)

    map_path = tmp_path / 'annotations_map.html'
    assert map_path.exists()
