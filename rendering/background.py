import random
from pathlib import Path
import bpy

def setup_random_background(config):
    """Set up random HDRI background from configured directory."""
    env_tex_dir = Path(config['backgrounds']['hdri_path'])
    env_tex_files = list(env_tex_dir.glob('*.exr'))
    
    if not env_tex_files:
        print("Warning: No .exr files found in backgrounds directory")
        return
        
    random_env_tex = random.choice(env_tex_files)
    world = bpy.context.scene.world
    world.use_nodes = True
    node_tree = world.node_tree
    node_tree.nodes.clear()
    
    # Setup nodes
    env_tex_node = node_tree.nodes.new(type='ShaderNodeTexEnvironment')
    background_node = node_tree.nodes.new(type='ShaderNodeBackground')
    output_node = node_tree.nodes.new(type='ShaderNodeOutputWorld')
    
    # Link nodes
    node_tree.links.new(env_tex_node.outputs['Color'], background_node.inputs['Color'])
    node_tree.links.new(background_node.outputs['Background'], output_node.inputs['Surface'])
    
    # Load image
    env_tex_node.image = bpy.data.images.load(str(random_env_tex))
