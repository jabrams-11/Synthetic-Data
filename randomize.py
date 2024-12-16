import sys
import os
import bpy

# Add the script directory to sys.path
script_dir = r"C:\Users\FPL Laptop\Desktop\BlenderSyntheticDataCode"
sys.path.append(script_dir)

# Assign unique pass indices to objects
for idx, obj in enumerate(bpy.data.objects):
    if obj.type == 'MESH':
        obj.pass_index = idx + 1  # Start indices from 1

# Enable nodes in the scene
bpy.context.scene.use_nodes = True
tree = bpy.context.scene.node_tree
tree.nodes.clear()

# Add necessary nodes
render_layers = tree.nodes.new(type='CompositorNodeRLayers')
math_divide = tree.nodes.new(type='CompositorNodeMath')
math_divide.operation = 'DIVIDE'
math_divide.inputs[1].default_value = 255.0  # Divide by 255 to normalize

file_output = tree.nodes.new(type='CompositorNodeOutputFile')
file_output.base_path = r'C:\Users\FPL Laptop\Desktop\basictest'

# Set up two file output slots: one for the RGBA image and one for the BW mask
file_output.file_slots.new(name="Image_RGBA")
file_output.file_slots.new(name="Mask_BW")

# Configure the output formats for each slot
file_output.file_slots[0].path = "image_rgba_#####"
file_output.file_slots[1].path = "mask_bw_#####"

file_output.format.file_format = 'PNG'

# Configure slot 0 (Image_RGBA) for RGBA format
file_output.file_slots[0].use_node_format = False
file_output.file_slots[0].color_mode = 'RGBA'
file_output.file_slots[0].color_depth = '8'

# Configure slot 1 (Mask_BW) for BW 8-bit format
file_output.file_slots[1].use_node_format = False
file_output.file_slots[1].color_mode = 'BW'
file_output.file_slots[1].color_depth = '8'

composite = tree.nodes.new(type='CompositorNodeComposite')

# Connect nodes
tree.links.new(render_layers.outputs['Image'], file_output.inputs[0])  # RGBA image
tree.links.new(render_layers.outputs['IndexOB'], math_divide.inputs[0])
tree.links.new(math_divide.outputs[0], file_output.inputs[1])  # BW mask
tree.links.new(render_layers.outputs['Image'], composite.inputs[0])
