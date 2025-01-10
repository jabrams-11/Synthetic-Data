import bpy
import random

# Function to add a new material with a specific color
def create_material(name, color):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)  # RGBA
    return mat

# Get the active object (insulator)
obj = bpy.context.active_object

# Ensure the object is a mesh
if obj and obj.type == 'MESH':
    # Access the vertex group
    vertex_group = obj.vertex_groups.get("OuterRings")
    if not vertex_group:
        print("Vertex group 'OuterRings' not found.")

    # Go into Object Mode (ensure we can access data)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Collect all vertices in the group
    mesh = obj.data
    candidate_vertices = [
        v for v in mesh.vertices
        for g in v.groups
        if g.group == vertex_group.index and g.weight > 0.5  # Only consider vertices with weight > 0.5
    ]

    # Ensure there are vertices in the group
    if candidate_vertices:
        # Pick one random vertex from the group
        selected_vertex = random.choice(candidate_vertices)

        # Create a "chip tool" object at the vertex location
        bpy.ops.mesh.primitive_ico_sphere_add(
            radius=50,  # Adjust size of the chip
            location=obj.matrix_world @ selected_vertex.co  # Convert to world coordinates
        )
        chip_tool = bpy.context.object
        chip_tool.name = "ChipTool"

        # Add the material to ensure it's available
        material_name = "ImprovedBurnedMetal"
        if material_name not in bpy.data.materials:
            fill_color = (1.0, 0.0, 0.0)  # Example color
            create_material(material_name, fill_color)
        fill_material = bpy.data.materials.get(material_name)

        # Make sure the material is on the object
        if material_name not in obj.data.materials:
            obj.data.materials.append(fill_material)

        # 1) Record the current polygon indices before Boolean
        old_polygon_indices = set(p.index for p in obj.data.polygons)

        # 2) Create a Boolean Modifier
        boolean = obj.modifiers.new(name="ChipBoolean", type='BOOLEAN')
        boolean.operation = 'DIFFERENCE'
        boolean.object = chip_tool

        # 3) Apply the Boolean Modifier
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=boolean.name)

        # 4) Identify the new polygons created by the cut
        new_polygons = [p for p in obj.data.polygons if p.index not in old_polygon_indices]

        # 5) Assign the material only to these new polygons
        material_index = obj.data.materials.find(material_name)
        for poly in new_polygons:
            poly.material_index = material_index

        # 6) Delete the chip tool object
        bpy.data.objects.remove(chip_tool, do_unlink=True)

        print("One chip created at vertex:", selected_vertex.index)

    else:
        print("No suitable vertices found in the vertex group.")
else:
    print("Please select a valid mesh object.")
