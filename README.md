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

## OpenDRIVE Map Support

To plot an OpenDRIVE map in `plot_annotations_3d`, convert it to OBJ file format first:

### Online OpenDRIVE Map Conversion

- Navigate to [odrviewer](https://odrviewer.io/)
- Disable **Center Map** in Parse Options
- Click on **Open .xodr** and select your OpenDRIVE map
- Click on **Export .obj**

### Offline OpenDRIVE Map Conversion

- Install OpenSceneGraph: `sudo apt install openscenegraph`
- Download the latest [esmini release](https://github.com/esmini/esmini/releases)
- Add `esmini/bin` to your `$PATH`
- Convert the map to [OpenSceneGraph](https://openscenegraph.github.io/openscenegraph.io/) using esmini's `odrviewer`:

```bash
odrviewer --odr map.xodr --save_generated_model --headless --duration 0 --disable_log --disable_stdout
```

- Convert the generated OpenSceneGraph road to .obj:

```bash
osgconv generated_road.osgb map.obj --use-world-frame
```

## License

This project is licensed under the Apache License 2.0. See [LICENSE.txt](LICENSE.txt) for details.

## Support

For questions, issues, or contributions, please:
- open an [issue in this repository](https://github.com/deepscenario/dsc-toolkit/issues)
- contact DeepScenario at info@deepscenario.com
