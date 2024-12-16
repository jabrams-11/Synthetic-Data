import os
import bpy
import json

def render_images(output_dir, image_num, pole_generator):
    os.makedirs(output_dir, exist_ok=True)

    node_tree = bpy.context.scene.node_tree
    file_output_node = node_tree.nodes.get("File Output")

    if file_output_node:
        file_output_node.base_path = output_dir
        file_output_node.file_slots[0].path = "Image_####"
        file_output_node.file_slots[1].path = "Mask_####"

    index_mapping_path = os.path.join(output_dir, "all_frame_mappings.json")

    
    # Set the frame number and reset object-to-index mapping
    bpy.context.scene.frame_set(image_num)
    object_to_index = {}
    index = 1
    processed_objects = set()
    group_indices = {}  # Store group_id -> pass_index mappings

    # Only assign pass indices to visible objects with 'annotate' property set to "True"
    for obj in bpy.data.objects:
        if obj.visible_get() and obj.get("annotate") == "True":
            group_id = obj.get("group_id")  # Check for a group_id property
            if group_id:
                if group_id not in group_indices:
                    group_indices[group_id] = index  # Assign a new pass index for the group
                    index += 10
                obj.pass_index = group_indices[group_id]  # Use the group's pass index
            else:
                obj.pass_index = index  # Assign a unique index if no group_id
                index += 10
            
            label = obj.get("label")
            if label:
                object_to_index[obj.pass_index] = label
                processed_objects.add(obj)

    frame_mapping = {f"Image_{image_num:04d}": object_to_index}

    with open(index_mapping_path, 'a') as f:
        json.dump(frame_mapping, f)
        f.write("\n")

    bpy.ops.render.render(write_still=True)

    print("Rendering complete. Images and mask outputs saved.")
