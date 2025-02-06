"""
Synthetic Utility Pole Generation Script
This script handles the generation of synthetic utility poles in Blender.
"""

import bpy
import yaml
from pathlib import Path
import sys
import random
import time
from datetime import datetime, timedelta
import json

# Add the project root to Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from utils.scene_utils import reset_scene
from rendering.camera import setup_camera
from rendering.background import setup_random_background
from rendering.renderer import render_scene
from core.trackers import RotationTracker

def format_time(seconds):
    """Convert seconds to a human readable format."""
    return str(timedelta(seconds=int(seconds)))

class GenerationStats:
    """Track statistics for the generation process."""
    def __init__(self, total_images):
        self.start_time = time.time()
        self.total_images = total_images
        self.completed_images = 0
        self.pole_type_counts = {}
        self._write_status()
        
    def update(self, pole_type):
        """Update statistics after generating an image."""
        self.completed_images += 1
        self.pole_type_counts[pole_type] = self.pole_type_counts.get(pole_type, 0) + 1
        self._write_status()
    
    def print_status(self):
        """Print current generation status to console."""
        elapsed_time = time.time() - self.start_time
        avg_time = elapsed_time / max(1, self.completed_images)
        remaining = self.total_images - self.completed_images
        eta = remaining * avg_time

        print(f"\nProgress: {self.completed_images}/{self.total_images} images")
        print(f"Elapsed Time: {format_time(elapsed_time)}")
        print(f"Average Time per Image: {avg_time:.1f} seconds")
        print(f"Estimated Time Remaining: {format_time(eta)}")
        print("\nPole Type Distribution:")
        for pole_type, count in self.pole_type_counts.items():
            print(f"  {pole_type}: {count}")
    
    def _write_status(self):
        """Write current status to file for UI to read."""
        status = {
            'total_images': self.total_images,
            'completed_images': self.completed_images,
            'pole_type_counts': self.pole_type_counts,
            'start_time': self.start_time,
            'last_update': time.time()
        }
        
        output_dir = Path("Renders")
        output_dir.mkdir(exist_ok=True)
        
        with open(output_dir / "generation_status.json", 'w') as f:
            json.dump(status, f)

def load_config(config_path: str = "configs/pole_generation_config.yaml") -> dict:
    """Load pole generation configuration from YAML file."""
    config_path = Path(config_path)
    if not config_path.is_absolute():
        config_path = project_root / config_path
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Convert path strings to proper Path objects
    if 'output' in config and 'base_path' in config['output']:
        config['output']['base_path'] = str(Path(config['output']['base_path']).resolve())
    
    if 'backgrounds' in config and 'hdri_path' in config['backgrounds']:
        config['backgrounds']['hdri_path'] = str(Path(config['backgrounds']['hdri_path']).resolve())
    
    return config

def select_pole_type(config: dict) -> str:
    """Select a random enabled pole type and return the corresponding pole class."""
    # Filter enabled pole types
    pole_types = config['pole_framing_types']
    enabled_types = []
    
    for name, details in pole_types.items():
        if isinstance(details, dict) and details.get('enabled', True):
            enabled_types.append(name)
    
    if not enabled_types:
        raise ValueError("No enabled pole types found in configuration")
    
    # Select pole type based on weights from config
    weights = [pole_types[t].get('weight', 1) for t in enabled_types]
    selected_type = random.choices(enabled_types, weights=weights, k=1)[0]
    print(f"Selected pole type: {selected_type}")
    
    # Dynamically import the pole class

    module = __import__(f'poles.{selected_type}', fromlist=[selected_type])
    return getattr(module, selected_type)

def generate_scene():
    """Generate a complete scene with a random pole type."""
    # Load configuration
    config = load_config()
    
    # Select and create pole
    pole_class = select_pole_type(config)
    
    # Initialize and generate pole
    pole = pole_class(config)
    objects = pole.generate()
    
    return objects, pole_class.__name__

def batch_render(num_images: int = 1):
    """Generate and render multiple scenes."""
    render_config = load_config("configs/rendering.yaml")
    stats = GenerationStats(num_images)
    
    print(f"\nStarting batch render of {num_images} images at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Output directory: {render_config['output']['base_path']}")
    
    for image_num in range(num_images):
        # Reset scene and generate new pole
        reset_scene()
        objects, pole_type = generate_scene()
        stats.update(pole_type)
        
        # Setup camera and background
        setup_camera(render_config)
        setup_random_background(render_config)
        
        # Render and save
        render_scene(image_num, render_config)
        
        # Print progress every image, or every 5 images for larger batches
        if num_images < 10 or image_num % 5 == 0 or image_num == num_images - 1:
            stats.print_status()
        
        RotationTracker.get_instance().reset_rotations()
    
    # Print final statistics
    print("\nGeneration Complete!")
    print(f"Total time: {format_time(time.time() - stats.start_time)}")
    print(f"Average time per image: {(time.time() - stats.start_time) / num_images:.2f} seconds")
    print(f"Output saved to: {render_config['output']['base_path']}")
    
    return render_config

def print_device_info():
    """Print current render device information."""
    print("\nRender Device Information:")
    prefs = bpy.context.preferences.addons['cycles'].preferences
    print(f"Compute Device Type: {prefs.compute_device_type}")
    print(f"Render Device: {bpy.context.scene.cycles.device}")
    print("\nAvailable Devices:")
    for device in prefs.devices:
        print(f"- {device.name} ({'ENABLED' if device.use else 'DISABLED'})")
    print("\n")

def setup_render_settings():
    """Configure optimal render settings for GPU."""
    scene = bpy.context.scene
    
    # Force GPU compute
    cycles_prefs = bpy.context.preferences.addons['cycles'].preferences
    
    # Try OptiX first (faster for RTX cards), fall back to CUDA
    if hasattr(cycles_prefs, 'compute_device_type'):
        # Check if OPTIX is available by trying to set it
        try:
            cycles_prefs.compute_device_type = 'OPTIX'
        except:
            # If OPTIX fails, fall back to CUDA
            cycles_prefs.compute_device_type = 'CUDA'
    
    cycles_prefs.refresh_devices()
    
    # Enable only GPU devices, disable CPU
    for device in cycles_prefs.devices:
        if 'NVIDIA' in device.name:  # Only enable NVIDIA GPU
            device.use = True
        else:
            device.use = False  # Disable CPU and other devices
    
    # Optimize render settings
    scene.cycles.device = 'GPU'
    scene.cycles.samples = 128
    scene.cycles.use_denoising = False
    
    # Additional optimizations for RTX cards
    if cycles_prefs.compute_device_type == 'OPTIX':
        scene.cycles.use_denoising_prefilter = True
    
    # Print confirmation
    print("\nRender settings configured for GPU acceleration:")
    print(f"Active Device: {scene.cycles.device}")
    print(f"Compute Type: {cycles_prefs.compute_device_type}")
    print(f"Samples: {scene.cycles.samples}")
    print(f"Adaptive Sampling: {scene.cycles.use_adaptive_sampling}")

def main():
    """Main entry point."""
    import argparse
    try:
        separator_index = sys.argv.index("--")
        script_args = sys.argv[separator_index + 1:]
    except ValueError:
        script_args = []  # No additional arguments provided

    # Parse only the script arguments
    parser = argparse.ArgumentParser(description="Generate synthetic utility pole images")
    parser.add_argument("--num-images", type=int, default=1, help="Number of images to generate")
    args = parser.parse_args(script_args)
    
    reset_scene() # Clean up scene before starting render batch

    # Add this before batch_render
    setup_render_settings()
    print_device_info()
    
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
    bpy.context.scene.cycles.device = 'GPU'

    render_config = batch_render(args.num_images)

    # Process outputs if needed
    if render_config['output'].get('save_coco') or render_config['output'].get('visualize_annotations'):
        from scripts.process_output import process_outputs
        process_outputs(
            output_dir=render_config['output']['base_path'],
            save_coco=render_config['output'].get('save_coco', False),
            visualize=render_config['output'].get('visualize_annotations', False)
        )

if __name__ == "__main__":
    main()
