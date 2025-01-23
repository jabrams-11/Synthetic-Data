"""
Main generation script for FPL synthetic data.
Generates pole configurations based on config file.
"""

import argparse
import logging
import random
import yaml
from pathlib import Path
from typing import Dict, Any, List

import bpy

from ..src.poles import (
    ModifiedVertical,
    VerticalPole,
    CrossarmPole,
    DeadendPole,
    DoubleDeadendPole
)
from fpl_synthetic_data.utils.scene import reset_scene
from fpl_synthetic_data.rendering import render_scene

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(config_path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config from {config_path}: {e}")
        raise

def get_enabled_configurations(pole_type_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get list of enabled configurations for a pole type."""
    configs = []
    for config in pole_type_config.get('configurations', []):
        for name, details in config.items():
            if details.get('enabled', True):
                configs.append({
                    'name': name,
                    'details': details
                })
    return configs

def select_random_pole_type(config: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
    """Select a random enabled pole type and its configuration."""
    enabled_types = {
        name: details for name, details in config['pole_framing_types'].items()
        if details.get('enabled', True)
    }
    
    if not enabled_types:
        raise ValueError("No enabled pole types found in configuration")
    
    pole_type = random.choice(list(enabled_types.keys()))
    enabled_configs = get_enabled_configurations(enabled_types[pole_type])
    
    if not enabled_configs:
        raise ValueError(f"No enabled configurations found for {pole_type}")
    
    chosen_config = random.choice(enabled_configs)
    return pole_type, chosen_config

def get_material(config: Dict[str, Any]) -> str:
    """Get random material based on configured percentages."""
    roll = random.uniform(0, 100)
    current_sum = 0
    
    for material in ['wood', 'concrete']:
        percentage = config['pole_materials'][material]['percentage']
        current_sum += percentage
        if roll <= current_sum:
            return material
    
    return 'wood'  # Default fallback

def get_phases(config: Dict[str, Any]) -> int:
    """Get random number of phases based on configured percentages."""
    roll = random.uniform(0, 100)
    current_sum = 0
    
    phases_map = {
        'single_phase': 1,
        'two_phase': 2,
        'three_phase': 3
    }
    
    for phase_type, num_phases in phases_map.items():
        percentage = config['phases'][phase_type]
        current_sum += percentage
        if roll <= current_sum:
            return num_phases
    
    return 3  # Default fallback

def generate_pole(config: Dict[str, Any]) -> bool:
    """Generate a single pole based on configuration."""
    try:
        # Reset scene
        reset_scene()
        
        # Select pole type and configuration
        pole_type, pole_config = select_random_pole_type(config)
        
        # Get material and phases
        material = get_material(config)
        phases = get_phases(config)
        
        # Initialize base components
        components = {}
        
        # Process configuration components
        if 'components' in pole_config['details']:
            for component in pole_config['details']['components']:
                # Handle dictionary components
                if isinstance(component, dict):
                    components.update(component)
                # Handle simple component flags
                else:
                    components[component] = True
        
        # Apply component chances from global settings
        component_settings = config.get('components', {})
        for comp_name, settings in component_settings.items():
            # Skip if component is already set
            if comp_name in components:
                continue
                
            # Check phase requirements
            if 'min_phases' in settings and phases < settings['min_phases']:
                continue
                
            # Check material exclusions
            if 'excluded_materials' in settings and material in settings['excluded_materials']:
                continue
                
            # Apply random chance
            if random.random() < settings.get('enable_chance', 0):
                components[comp_name] = True
                
                # Handle special cases like double_als
                if comp_name == 'als' and random.random() < settings.get('double_als_chance', 0):
                    components['double_als'] = True
        
        # Handle variations if present
        if 'variations' in pole_config['details']:
            variation = random.choice(pole_config['details']['variations'])
            if variation.get('enabled', True):
                for component in variation.get('components', []):
                    components[component] = True
        
        # Create pole instance
        PoleClass = {
            'modified_vertical': ModifiedVertical,
            'vertical': VerticalPole,
            'crossarm': CrossarmPole,
            'deadend': DeadendPole,
            'double_deadend': DoubleDeadendPole
        }[pole_type]
        
        # Create and generate pole with all components
        pole = PoleClass(
            phases=phases,
            pole_type=material,
            **components
        )
        
        success = pole.generate_pole()
        
        if success:
            logger.info(
                f"Generated {pole_type} pole with {phases} phases ({material})"
                f"\nComponents: {', '.join(components.keys())}"
            )
        
        return success
    
    except Exception as e:
        logger.error(f"Error generating pole: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Generate synthetic pole dataset')
    parser.add_argument('--config', type=Path, 
                      default='configs/pole_generation_config.yaml',
                      help='Path to configuration file')
    parser.add_argument('--output', type=Path, 
                      default='output/renders',
                      help='Output directory')
    parser.add_argument('--count', type=int, default=100,
                      help='Number of images to generate')
    parser.add_argument('--seed', type=int, 
                      help='Random seed for reproducibility')
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)
    
    # Set random seed if provided
    if args.seed is not None:
        random.seed(args.seed)

    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)

    # Generate poles
    successful = 0
    for i in range(args.count):
        logger.info(f"Generating pole {i+1}/{args.count}")
        
        if generate_pole(config):
            # Render
            render_scene(
                output_path=args.output / f"pole_{i:04d}",
                config=config['rendering']
            )
            successful += 1
    
    logger.info(f"Generation complete. {successful}/{args.count} poles generated successfully")

if __name__ == "__main__":
    main()