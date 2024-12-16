import bpy
import math
import random
from mathutils import Vector

def create_power_wire(cube1, cube2, wire_thickness=0.1, sag_factor=0.15, randomize=True):
    """
    Creates a realistic overhead power wire between two points using a simple bezier curve
    wire_thickness: diameter of the conductor in meters
    sag_factor: controls how much the wire sags (0.15 = 15% of span length)
    randomize: adds natural variation to the wire
    """
    # Create or get the Wires collection
    if 'Wires' not in bpy.data.collections:
        wires_collection = bpy.data.collections.new('Wires')
        bpy.context.scene.collection.children.link(wires_collection)
    else:
        wires_collection = bpy.data.collections['Wires']
    
    # Get cube positions
    # Get global positions of the cubes
    depsgraph = bpy.context.evaluated_depsgraph_get()
    start_point = cube1.evaluated_get(depsgraph).matrix_world.translation.copy()
    end_point = cube2.evaluated_get(depsgraph).matrix_world.translation.copy()
    
    # Create curve
    curve_data = bpy.data.curves.new(name='PowerLine', type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 96
    
    # Create curve object
    wire_obj = bpy.data.objects.new('PowerLine', curve_data)
    wires_collection.objects.link(wire_obj)
    
    # Create spline
    spline = curve_data.splines.new('BEZIER')
    
    # Calculate parameters with randomization
    direction = (end_point - start_point).normalized()
    span_length = (end_point - start_point).length
    
    if randomize:
        # Random variations
        sag_variation = random.uniform(0.85, 1.15)  # ±15% sag variation
        sway_variation = random.uniform(-0.05, 0.05)  # ±5% lateral sway
        thickness_variation = random.uniform(0.9, 1.1)  # ±10% thickness variation
        wire_thickness *= thickness_variation
        sag_depth = span_length * sag_factor * sag_variation
    else:
        sag_depth = span_length * sag_factor
        sway_variation = 0
    
    # Calculate middle point with randomization
    mid_point = (start_point + end_point) / 2
    mid_point.z -= sag_depth
    
    # Add slight random lateral sway if randomization is enabled
    if randomize:
        # Calculate perpendicular vector for sway
        if abs(direction.y) < abs(direction.x):
            sway_direction = Vector((-direction.y, direction.x, 0)).normalized()
        else:
            sway_direction = Vector((direction.y, -direction.x, 0)).normalized()
        
        sway_amount = span_length * sway_variation
        mid_point += sway_direction * sway_amount
    
    # Add points for bezier curve
    spline.bezier_points.add(2)
    points = spline.bezier_points
    
    # Start point
    points[0].co = start_point
    points[0].handle_left = start_point
    handle_right = start_point + direction * (span_length/4)
    handle_right.z -= sag_depth/2
    if randomize:
        handle_right += sway_direction * (sway_amount * 0.5)
    points[0].handle_right = handle_right
    
    # Middle point
    points[1].co = mid_point
    points[1].handle_left = mid_point + direction * (-span_length/4)
    points[1].handle_right = mid_point + direction * (span_length/4)
    
    # End point
    points[2].co = end_point
    handle_left = end_point + direction * (-span_length/4)
    handle_left.z -= sag_depth/2
    if randomize:
        handle_left += sway_direction * (sway_amount * 0.5)
    points[2].handle_left = handle_left
    points[2].handle_right = end_point
    
    # Set handle types for smooth curve
    for point in points:
        point.handle_left_type = 'ALIGNED'
        point.handle_right_type = 'ALIGNED'
    
    # Add thickness and make it slightly rounded
    curve_data.bevel_depth = wire_thickness
    curve_data.bevel_resolution = 6
    
    # Set material to Material.008
    wire_obj.data.materials.append(bpy.data.materials['Material.008'])
    
    # Add custom properties
    wire_obj["annotate"] = "True"
    wire_obj["label"] = "Wire"
    
    return wire_obj
