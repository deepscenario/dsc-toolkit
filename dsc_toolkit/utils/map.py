import os
import shlex
import shutil
import subprocess
import tempfile

import vedo


def load_map_as_obj(map_path: str, odrviewer_path: str = 'odrviewer', osgconv_path: str = 'osgconv') -> list[vedo.Mesh]:
    assert map_path.endswith('.xodr') and os.path.isfile(map_path), \
        f'The map path is not an xodr file: {map_path}'
    map_path = os.path.abspath(map_path)

    assert (odrviewer_path_resolved := shutil.which(odrviewer_path)) is not None, \
        'odrviewer is required for plotting the map, see https://esmini.github.io/#_odrviewer'

    assert (osgconv_path_resolved := shutil.which(osgconv_path)) is not None, \
        'osgconv is required for plotting the map. Install it with: sudo apt install openscenegraph'

    with tempfile.TemporaryDirectory() as tmp_dir:
        os.chdir(tmp_dir)

        odrviewer_cmd = shlex.split(f'''
        {odrviewer_path_resolved}
        --odr {map_path}
        --save_generated_model
        --headless
        --duration 0
        --disable_log
        --disable_stdout
        ''')
        print(f'Running: {shlex.join(odrviewer_cmd)}')
        subprocess.run(odrviewer_cmd, shell=False, check=True, capture_output=True)

        assert os.path.isfile('generated_road.osgb'), 'Failed to convert OpenDRIVE map to OpenSceneGraph'

        osgconv_cmd = shlex.split(f'''
        {osgconv_path_resolved}
        generated_road.osgb
        generated_road.obj
        ''')
        print(f'Running: {shlex.join(osgconv_cmd)}')
        subprocess.run(osgconv_cmd, shell=False, check=True, capture_output=True)

        assert os.path.isfile('generated_road.obj'), 'Failed to convert OpenSceneGraph to OBJ'

        return vedo.load_obj('generated_road.obj')
