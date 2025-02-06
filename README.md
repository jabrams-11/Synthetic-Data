# Utility Pole Synthetic Data Generator

A comprehensive system for generating synthetic training data of utility poles and their components using Blender. This project enables the creation of large-scale, annotated datasets for computer vision and machine learning applications in power infrastructure inspection.

![Example Synthetic Utility Pole](exampleimage.png)
*Example of a generated synthetic utility pole with segmentation mask and annotations*

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
- Required Python packages (installed via requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Install required Python packages into Blender's Python environment:

First, locate your Blender Python executable and site-packages directory. For Blender 4.3 on Windows, these are typically:
```bash
BLENDER_PYTHON="C:\Program Files\Blender Foundation\Blender 4.3\4.3\python\bin\python.exe"
BLENDER_SITE_PACKAGES="C:\Program Files\Blender Foundation\Blender 4.3\4.3\python\Lib\site-packages"
```

Then install all required packages using the requirements.txt file:
```bash
& "$BLENDER_PYTHON" -m pip install -r requirements.txt --target "$BLENDER_SITE_PACKAGES"
```

Or install packages individually if needed:
```bash
& "$BLENDER_PYTHON" -m pip install [package-name] --target "$BLENDER_SITE_PACKAGES"
```

The requirements.txt file includes:
```
opencv-python
numpy
Pillow
PyYAML
scipy
matplotlib
tqdm
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

## Code Overview

### Core Components

#### 1. Generation Pipeline
The main generation pipeline is handled by `scripts/generate.py`, which orchestrates the entire process:

- Scene initialization and cleanup
- Pole type selection and generation
- Camera and background setup
- Rendering and output processing

Key components:
```python
# Main entry point
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-images", type=int, default=1)
    args = parser.parse_args()
    
    reset_scene()
    setup_render_settings()
    render_config = batch_render(args.num_images)
```

#### 2. Pole Generation
The system uses a hierarchical class structure for pole generation:

- `PoleBase`: Base class with common functionality
- Specialized classes (ModifiedVertical, Vertical, Deadend, etc.)

Example from ModifiedVertical class (see `poles/ModifiedVertical.py`):
```python:poles/ModifiedVertical.py
startLine: 11
endLine: 41
```

#### 3. Component Management
Components are managed through Blender collections and configured via YAML:

```yaml:configs/pole_generation_config.yaml
startLine: 34
endLine: 48
```

#### 4. Rendering Pipeline

The rendering pipeline (`scripts/process_output.py`) handles:
- Image rendering
- Mask generation
- COCO format annotation export
- Progress tracking

Key components:
```python:scripts/process_output.py
startLine: 19
endLine: 64
```

### Configuration System

The project uses two main configuration files:

1. **rendering.yaml**: Controls rendering settings
   - Resolution and quality
   - Camera parameters
   - Output formats
   - Performance settings

2. **pole_generation_config.yaml**: Defines pole generation parameters
   - Pole type probabilities
   - Component configurations
   - Material settings
   - Anomaly chances

### Integration Flow

1. **Initialization**
   - Script is launched via Blender's Python interface
   - Configuration files are loaded
   - Scene is reset and prepared

2. **Generation**
   - Random pole type is selected based on weights
   - Components are added according to configuration
   - Anomalies are generated if specified

3. **Rendering**
   - Camera is positioned
   - Background is randomized
   - Scene is rendered
   - Masks and annotations are generated

4. **Output Processing**
   - Images are saved
   - COCO annotations are generated
   - Progress is tracked and reported

### Example Workflow

1. **Setup**: Configure generation parameters in YAML files
2. **Execute**: Run the main script through Blender

3. **Monitor**: Watch progress through the GUI monitor
4. **Collect**: Gather generated images and annotations from output directory