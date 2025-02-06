from core.trackers import RotationTracker

def rotate_object_global(obj, angle_degrees, axis='Y'):
    """Rotate an object around any global axis by the specified angle in degrees
    
    Args:
        obj: The object to rotate
        angle_degrees: Rotation angle in degrees
        axis: 'X', 'Y', or 'Z' axis to rotate around
    """
    import math
    from mathutils import Matrix
    
    # Store original matrix before rotation
    tracker = RotationTracker.get_instance()
    if obj.name not in tracker.rotated_objects:
        tracker.track_rotation(obj, obj.matrix_world.copy())
    
    # Convert degrees to radians
    angle_rad = math.radians(angle_degrees)
    
    # Create rotation matrix for specified global axis
    rot_mat = Matrix.Rotation(angle_rad, 4, axis)
    
    # Get current world matrix
    orig_loc = obj.matrix_world.to_translation()
    
    # Apply rotation while preserving location
    obj.matrix_world = rot_mat @ obj.matrix_world
    obj.matrix_world.translation = orig_loc