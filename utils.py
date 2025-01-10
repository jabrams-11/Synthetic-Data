import bpy
import random

def create_insulator_anomaly(obj):
	"""
	Create an insulator anomaly by cutting a hole in a duplicate of the insulator and adding a material to the cut.
	obj: The insulator object to create the anomaly on.
	"""
	# Create a duplicate of the object
	obj_duplicate = obj.copy()
	obj_duplicate.data = obj.data.copy()
	
	# Get or create the Cleanup collection
	cleanup_collection = bpy.data.collections.get("Cleanup")
	# Link the duplicate to the Cleanup collection
	cleanup_collection.objects.link(obj_duplicate)
	# Access the vertex group
	vertex_group = obj_duplicate.vertex_groups.get("OuterRings")
	if not vertex_group:
		print("Vertex group 'OuterRings' not found.")
		return
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
