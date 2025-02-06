# Utility Pole Synthetic Data Generator

A comprehensive system for generating synthetic training data of utility poles and their components using Blender. This project enables the creation of large-scale, annotated datasets for computer vision and machine learning applications in power infrastructure inspection.

## Features

- **Diverse Pole Types**: Support for multiple pole configurations and equipment:
  - Modified Vertical
  - Vertical
  - Deadend
  - Crossarm
  - ALS, Fuses, ATS, AETXs, LAs, etc

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

## Prerequisites

- Blender 3.0+
- Python 3.7+
- Required Python packages:
  - OpenCV (cv2)
  - NumPy
  - PyYAML

## Installation

1. Clone the repository:

```bash
git clone [repository-url]
cd [repository-name]
```

2. Set up the Blender Python environment with required packages
3. Configure the paths in the configuration files

## Configuration

The system uses YAML configuration files for various settings:

### Rendering Configuration
Located in `configs/rendering.yaml`:
- Resolution and quality settings
- Output format and paths
- Camera parameters
- Background settings

### Pole Generation Configuration
Located in `configs/pole_generation_config.yaml`:
- Pole type probabilities
- Equipment chances
- Component requirements
- Anomaly settings

## Usage

### Basic Generation

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
