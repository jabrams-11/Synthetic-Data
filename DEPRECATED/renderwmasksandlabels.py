import sys
import os
import bpy
import json

# Add the script directory to sys.path
script_dir = r"C:\Users\FPL Laptop\Desktop\BlenderSyntheticDataCode"
sys.path.append(script_dir)

# Set output directory
output_dir = r"C:\Users\FPL Laptop\Desktop\BlenderSyntheticDataCode\RenderedImages"
os.makedirs(output_dir, exist_ok=True)

# Configure the base path and subpaths for the file output node
node_tree = bpy.context.scene.node_tree
file_output_node = node_tree.nodes.get("File Output")

if file_output_node:
    file_output_node.base_path = output_dir  # Set base path for all outputs
    file_output_node.file_slots[0].path = "Image_####"  # Subpath for image (#### will be replaced by frame number)
    file_output_node.file_slots[1].path = "Mask_####"   # Subpath for mask

# Path to the JSON file to store object-to-index mappings
index_mapping_path = os.path.join(output_dir, "all_frame_mappings.json")

# Render loop for multiple images
for i in range(1, 3):
    # Set the frame number for output consistency
    bpy.context.scene.frame_set(i)

    # Dynamic object-to-index mapping generation for the current frame
    object_to_index = {}
    index = 1

    # Assign unique pass indices only to objects with 'annotate' set to "True"
    for obj in bpy.data.objects:
        if obj.type in {'MESH', 'CURVE'} and obj.get("annotate") == "True":
            obj.pass_index = index  # Assign unique pass index
            label = obj.get("label", obj.name)  # Use the custom label for annotation or default to object name
            object_to_index[obj.pass_index] = label  # Store label and pass index in dictionary
            index += 1

    # Prepare a frame-specific dictionary with the frame key
    frame_mapping = {f"Image_{i:04d}": object_to_index}

    # Append the current frame's mapping to the JSON file
    with open(index_mapping_path, 'a') as f:
        json.dump(frame_mapping, f)
        f.write("\n")  # Newline to separate each frame's mapping

    # Render the scene; outputs should automatically save due to compositor setup
    bpy.ops.render.render(write_still=True)

print("Rendering complete. Image and mask outputs saved with differentiated object-to-index mappings for each frame in a single JSON file.")
