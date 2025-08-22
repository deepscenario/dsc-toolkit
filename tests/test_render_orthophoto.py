import shlex
from pathlib import Path

from dsc_toolkit.render_orthophoto import main


def test_render_orthophoto(data_dir: str, mesh_path: str, tmp_path: Path) -> None:
    test_args = shlex.split(f'''
    --data_dir {data_dir}
    --mesh {mesh_path}
    --save_dir {str(tmp_path)}
    --pixel_size 0.3
    ''')
    main(test_args)

    orthophoto_path = tmp_path / 'orthophoto.tif'
    assert orthophoto_path.exists()
