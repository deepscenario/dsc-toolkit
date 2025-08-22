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

## License

This project is licensed under the Apache License 2.0. See [LICENSE.txt](LICENSE.txt) for details.

## Support

For questions, issues, or contributions, please:
- open an [issue in this repository](https://github.com/deepscenario/dsc-toolkit/issues)
- contact DeepScenario at info@deepscenario.com
