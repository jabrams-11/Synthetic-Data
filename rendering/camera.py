import bpy
import math
import random
from mathutils import Vector

def setup_camera(config):
    """
    Randomize camera position and orientation based on configuration.
    
    Args:
        config: Configuration dictionary containing camera settings
    """
    scene = bpy.context.scene
    camera = bpy.data.objects.get('Camera')
    view_target = random.choice([
        bpy.data.objects.get('PorcelainFuse1'),
        bpy.data.objects.get('ViewPart'),
    ])
    
    if not camera or not view_target:
        print("Warning: Camera or ViewPart empty not found in scene")
        return None
    
    # Get camera settings from config
    cam_config = config['camera']
    
    # Make camera the active camera
    scene.camera = camera
    
    # Get view target position
    target_pos = view_target.location
    
    # Random distance within configured range
    distance = random.uniform(cam_config['distance']['min'], 
                            cam_config['distance']['max'])
    
    # Multiply distance by 3 if view target is ViewPart
    if view_target == bpy.data.objects.get('ViewPart'):
        distance *= 3
    
    # Convert azimuth range from degrees to radians
    azimuth = math.radians(random.uniform(cam_config['azimuth']['min'], 
                                        cam_config['azimuth']['max']))
    
    # Choose camera angle style based on weights
    weights = cam_config['style_weights']
    angle_style = random.choices(
        ['low', 'eye_level', 'high'],
        weights=[weights['low'], weights['eye_level'], weights['high']]
    )[0]
    
    # Set elevation based on chosen style
    if angle_style == 'low':
        elevation = math.radians(random.uniform(cam_config['angles']['low']['min'],
                                              cam_config['angles']['low']['max']))
    elif angle_style == 'eye_level':
        elevation = math.radians(random.uniform(cam_config['angles']['eye_level']['min'],
                                              cam_config['angles']['eye_level']['max']))
    else:  # high
        elevation = math.radians(random.uniform(cam_config['angles']['high']['min'],
                                              cam_config['angles']['high']['max']))
    
    # Convert spherical to Cartesian coordinates
    x = target_pos.x + (distance * math.cos(azimuth) * math.cos(elevation))
    y = target_pos.y + (distance * math.sin(azimuth) * math.cos(elevation))
    z = target_pos.z + (distance * math.sin(elevation))
    
    # Ensure minimum height from ground
    min_height = cam_config['min_height']
    if z < min_height:
        z = min_height
    
    # Position camera
    camera.location = (x, y, z)
    
    # Point camera at view target
    direction = target_pos - camera.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()
    
    # Add subtle random rotation variation
    camera.rotation_euler.z += random.uniform(
        cam_config['rotation']['random_z']['min'],
        cam_config['rotation']['random_z']['max']
    )
    
    return camera