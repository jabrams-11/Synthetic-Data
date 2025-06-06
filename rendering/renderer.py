import os
import bpy
import json
from pathlib import Path

def setup_render_settings(config):
    """Configure render settings based on config file."""
    scene = bpy.context.scene
    render = scene.render
    
    
    # Set resolution
    render.resolution_x = config['resolution']['x']
    render.resolution_y = config['resolution']['y']
    
    # Set render engine and samples
    scene.render.engine = config['render_engine']
    if scene.render.engine == 'CYCLES':
        scene.cycles.samples = config['samples']
        scene.cycles.use_denoising = config['denoising']['enabled']
        if hasattr(scene.cycles, 'denoising_strength'):
            scene.cycles.denoising_strength = config['denoising']['strength']
    
    # Set output format
    render.image_settings.file_format = config['file_format']
    render.image_settings.color_mode = config['color_mode']
    render.image_settings.color_depth = str(config['color_depth'])
    if config['file_format'] == 'PNG':
        render.image_settings.compression = config['compression']
    
    # Performance settings
    if scene.render.engine == 'CYCLES':
        scene.render.tile_x = config['tile_size']
        scene.render.tile_y = config['tile_size']
        if config['gpu_enabled']:
            scene.cycles.device = 'GPU'
        scene.render.threads = config['threads']

def render_scene(image_num, config):
    """
    Render scene with configured settings and save outputs.
    
    Args:
        output_dir: Directory to save renders
        image_num: Current image number
        config: Rendering configuration dictionary
    """
    # Create output directory if it doesn't exist
    output_dir = Path(config["output"]["base_path"])
    output_dir.mkdir(parents=True, exist_ok=True)
    bpy.context.scene.render.filepath = str(output_dir / "image.png")
    
    node_tree = bpy.context.scene.node_tree
    file_output_node = node_tree.nodes.get("File Output")

    if file_output_node:
        file_output_node.base_path = config["output"]["base_path"]
        file_output_node.file_slots[0].path = "Image_####"
        file_output_node.file_slots[1].path = "Mask_####"

    # Set frame number
    bpy.context.scene.frame_set(image_num)
    scene = bpy.context.scene
    scene.cycles.samples = config['samples']
    
    # Handle object indexing for segmentation
    if config['output']['mask_enabled']:
        object_to_index = {}
        index = 1
        group_indices = {}
        
        # Process objects for segmentation
        for obj in bpy.data.objects:
            if not(obj.hide_render) and obj.get("annotate") == "True":
                print(obj.name)
                group_id = obj.get("group_id")
                if group_id:
                    if group_id not in group_indices:
                        group_indices[group_id] = index
                        index += 1
                    obj.pass_index = group_indices[group_id]
                else:
                    obj.pass_index = index
                    index += 1
                
                label = obj.get("label")
                if label:
                    object_to_index[obj.pass_index] = label
        
        # Save mapping to JSON
        if object_to_index:
            mapping_file = output_dir / "all_frame_mappings.json"
            frame_mapping = {f"{config['output']['file_prefix']}{image_num:0{config['output']['file_padding']}d}": object_to_index}
            
            # Append to existing file or create new one
            try:
                with open(mapping_file, 'r+') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {}
                    data.update(frame_mapping)
                    f.seek(0)
                    json.dump(data, f, indent=2)
            except FileNotFoundError:
                with open(mapping_file, 'w') as f:
                    json.dump(frame_mapping, f, indent=2)
    
    # Perform render
    bpy.ops.render.render(write_still=True)
    
    print(f"Rendering complete for image {image_num}")
    return True