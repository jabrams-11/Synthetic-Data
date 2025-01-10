import random
from pathlib import Path
import bpy

def setup_random_background():
    env_tex_dir = Path(r"C:\Users\jackp\Desktop\JackTransfer\Backgrounds") 
    env_tex_files = list(env_tex_dir.glob('*.exr'))
    if env_tex_files:
        random_env_tex = random.choice(env_tex_files)
        world = bpy.context.scene.world
        world.use_nodes = True
        node_tree = world.node_tree
        node_tree.nodes.clear()
        env_tex_node = node_tree.nodes.new(type='ShaderNodeTexEnvironment')
        background_node = node_tree.nodes.new(type='ShaderNodeBackground')
        output_node = node_tree.nodes.new(type='ShaderNodeOutputWorld')
        node_tree.links.new(env_tex_node.outputs['Color'], background_node.inputs['Color'])
        node_tree.links.new(background_node.outputs['Background'], output_node.inputs['Surface'])
        env_tex_node.image = bpy.data.images.load(str(random_env_tex))
