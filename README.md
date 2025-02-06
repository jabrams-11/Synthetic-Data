# Utility Pole Synthetic Data Generator

A comprehensive system for generating synthetic training data of utility poles and their components using Blender. This project enables the creation of large-scale, annotated datasets for computer vision and machine learning applications in power infrastructure inspection.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Output Structure](#output-structure)
- [Progress Monitoring](#progress-monitoring)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Features

- **Diverse Pole Types**: Support for multiple pole configurations:
  - Modified Vertical
  - Vertical
  - Deadend
  - Crossarm
  - ALS (Air Line Switch) configurations
  - Combination setups (ALS with Fuse, etc.)

- **Component Variations**:
  - Multiple phase configurations (single, two, and three-phase)
  - Various equipment types (AETX, ATS, Fuses, Surge Arresters)
  - Support for anomaly generation (open switches, damaged components)
  - Different pole materials (wood, concrete)

- **Advanced Rendering**:
  - GPU-accelerated rendering with CYCLES
  - Support for OPTIX/CUDA acceleration
  - Configurable resolution and quality settings
  - HDR background integration
  - Segmentation mask generation

- **Annotation Export**:
  - COCO format annotation export
  - Instance segmentation support
  - Automated label generation
  - Progress tracking and visualization

## Prerequisites

- Blender 4.0+
- Python 3.7+
- Required Python packages (see Installation section for setup):
  - OpenCV (cv2)
  - NumPy
  - PyYAML
  - Pillow
  - scipy
  - matplotlib
  - tqdm

## Installation

1. Clone the repository:

```bash
git clone [repository-url]
cd [repository-name]
```

2. Install required Python packages into Blender's Python environment:

```bash
# Base command structure for Windows:
& "[Blender Path]/[version]/python/bin/python.exe" -m pip install [package] --target "[Blender Path]/[version]/python/Lib/site-packages"

# Example for Blender 4.3:
& "C:\Program Files\Blender Foundation\Blender 4.3\4.3\python\bin\python.exe" -m pip install opencv-python --target "C:\Program Files\Blender Foundation\Blender 4.3\4.3\python\Lib\site-packages"
```

Required packages to install:
```bash
# Install each of these packages using the command structure above
opencv-python
numpy
Pillow
PyYAML
scipy
matplotlib
tqdm
```

For convenience, here are the full commands for Blender 4.3 on Windows:
```bash
& "C:\Program Files\Blender Foundation\Blender 4.3\4.3\python\bin\python.exe" -m pip install opencv-python --target "C:\Program Files\Blender Foundation\Blender 4.3\4.3\python\Lib\site-packages"
& "C:\Program Files\Blender Foundation\Blender 4.3\4.3\python\bin\python.exe" -m pip install numpy --target "C:\Program Files\Blender Foundation\Blender 4.3\4.3\python\Lib\site-packages"
& "C:\Program Files\Blender Foundation\Blender 4.3\4.3\python\bin\python.exe" -m pip install Pillow --target "C:\Program Files\Blender Foundation\Blender 4.3\4.3\python\Lib\site-packages"
& "C:\Program Files\Blender Foundation\Blender 4.3\4.3\python\bin\python.exe" -m pip install PyYAML --target "C:\Program Files\Blender Foundation\Blender 4.3\4.3\python\Lib\site-packages"
& "C:\Program Files\Blender Foundation\Blender 4.3\4.3\python\bin\python.exe" -m pip install scipy --target "C:\Program Files\Blender Foundation\Blender 4.3\4.3\python\Lib\site-packages"
& "C:\Program Files\Blender Foundation\Blender 4.3\4.3\python\bin\python.exe" -m pip install matplotlib --target "C:\Program Files\Blender Foundation\Blender 4.3\4.3\python\Lib\site-packages"
& "C:\Program Files\Blender Foundation\Blender 4.3\4.3\python\bin\python.exe" -m pip install tqdm --target "C:\Program Files\Blender Foundation\Blender 4.3\4.3\python\Lib\site-packages"
```

Note: For other operating systems or Blender versions, adjust the paths accordingly.

3. Configure the paths in the configuration files

## Project Structure

```
project_root/
├── scripts/
│   ├── generate.py          # Main generation script
│   ├── process_output.py    # Post-processing utilities
│   └── save_coco.py        # COCO format conversion
├── core/
│   ├── __init__.py
│   └── trackers.py         # Progress tracking
├── poles/
│   ├── ModifiedVertical.py # Pole type implementations
│   ├── Vertical.py
│   ├── Deadend.py
│   └── Crossarm.py
├── rendering/
│   ├── renderer.py         # Rendering configuration
│   ├── camera.py          # Camera setup
│   └── background.py      # Background handling
├── utils/
│   ├── progress_window.py # GUI progress monitor
│   └── wire_generator.py  # Wire generation utilities
└── configs/
    ├── rendering.yaml     # Render settings
    └── pole_generation_config.yaml  # Pole configuration
```

## Usage

### Command Line Execution

The system is designed to be run from the command line using Blender's Python interface. Use the following command structure:

```bash
"[path-to-blender]/blender.exe" -b "[path-to-blend-file]" -P "[path-to-script]/generate.py" -- --num-images <count>
```

Example:
```bash
"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe" -b "C:\path\to\your\scene.blend" -P Synthetic-Data/scripts/generate.py -- --num-images 5
```

Parameters:
- `-b`: Run Blender in background mode
- `--num-images`: Number of synthetic images to generate
- Additional parameters can be configured in the YAML config files

### Python API Usage

For programmatic control, you can also use the Python API:

```python
from scripts.generate import batch_render

# Generate 100 synthetic images
batch_render(num_images=100)
```

### Custom Configuration

```python
from core.config import load_config
from scripts.generate import batch_render

config = load_config("configs/custom_config.yaml")
batch_render(num_images=50, config=config)
```

## Output Structure

```
output_dir/
├── Image_0001.png           # Rendered images
├── Mask_0001.png           # Segmentation masks
├── coco_annotations.json    # COCO format annotations
└── generation_status.json   # Progress tracking
```

## Progress Monitoring

The system includes a GUI progress monitor that displays:
- Generation progress
- Time estimates
- Pole type distribution
- Current status

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your License Here]

## Acknowledgments

- [Any acknowledgments or credits]
