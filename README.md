# DeepScenario Toolkit

A Python toolkit for visualizing and working with DeepScenario datasets, which can be downloaded at [app.deepscenario.com](https://app.deepscenario.com).

## Overview

DeepScenario provides a platform to virtualize real-world recordings into:
- a **3D reconstruction** of the static environment
- **3D trajectories** of the dynamic objects

This toolkit provides easy-to-use tools for visualizing and working with DeepScenario datasets, including:
- visualization of the object annotations in 3D or in OpenStreetMap
- creation of an orthophoto from the 3D reconstruction

## Installation

### From PyPI (Recommended)

```bash
pip install dsc-toolkit
```

### From Source (Development)

This project uses [uv](https://github.com/astral-sh/uv) for dependency management. Make sure you have `uv` installed first.

```bash
# Clone the repository
git clone https://github.com/deepscenario/dsc-toolkit.git
cd dsc-toolkit

# Install the package and dependencies
uv sync
```

## Quick Start

The toolkit provides a command-line tool with several commands. Each command has detailed help available using the `--help` option, for example:

```bash
dsc-toolkit plot_annotations_3d --help
```

### `plot_annotations_3d`

Interactive 3D visualization of the object annotations:

```bash
dsc-toolkit plot_annotations_3d \
	--data_dir tests/assets/data \
	--recording 2000-12-31T23-59-59 \
	--mesh tests/assets/data/textured_mesh/textured_mesh.obj
```

### `plot_annotations_georeferenced`

Interactive visualization of the object annotations in OpenStreetMap:

```bash
dsc-toolkit plot_annotations_georeferenced \
	--data_dir tests/assets/data \
	--recording 2000-12-31T23-59-59 \
	--save_dir /tmp/output
```

### `render_orthophoto`

Render a georeferenced orthophoto from the textured mesh:

```bash
dsc-toolkit render_orthophoto \
	--data_dir tests/assets/data \
	--mesh tests/assets/data/textured_mesh/textured_mesh.obj \
	--save_dir /tmp/output
```

## OpenDRIVE Map Visualization

To visualize an OpenDRIVE map in `plot_annotations_3d`, you need to first convert it to [OBJ format](https://en.wikipedia.org/wiki/Wavefront_.obj_file). Choose one of the following methods:

### Method 1: Online Conversion

1. Navigate to [odrviewer.io](https://odrviewer.io/)
2. In **"Parse Options"**, disable **"Center Map"**
3. Click **"Open .xodr"** and select your OpenDRIVE file
4. Click **"Export .obj"** to download the converted file

### Method 2: Offline Conversion

This method relies on [esmini](https://github.com/esmini/esmini) and [OpenSceneGraph](https://openscenegraph.github.io/openscenegraph.io/):

#### Prerequisites
```bash
# Install OpenSceneGraph
sudo apt install openscenegraph

# Download and set up esmini
wget https://github.com/esmini/esmini/releases/latest/download/esmini-demo_ubuntu-latest.zip
unzip esmini-demo_ubuntu-latest.zip
export PATH=$PATH:$(pwd)/esmini/bin
```

#### Conversion Steps

1. **Generate OpenSceneGraph model** from your OpenDRIVE file:
   ```bash
   odrviewer --odr map.xodr --save_generated_model --headless --duration 0 --disable_log --disable_stdout
   ```

2. **Convert to OBJ format**:
   ```bash
   osgconv generated_road.osgb map.obj --use-world-frame
   ```

The resulting `map.obj` file can now be used with `plot_annotations_3d`.

## License

This project is licensed under the Apache License 2.0. See [LICENSE.txt](LICENSE.txt) for details.

## Support

For questions, issues, or contributions, please:
- open an [issue in this repository](https://github.com/deepscenario/dsc-toolkit/issues)
- contact DeepScenario at info@deepscenario.com
