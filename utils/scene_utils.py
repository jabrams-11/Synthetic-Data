import bpy

def toggle_visibility(obj, visible):
    """
    Toggle the visibility state of a Blender object.

    Args:
        obj (bpy.types.Object): The Blender object to toggle visibility for
        visible (bool): Whether to make the object visible (True) or invisible (False)
    """
    if obj:
        obj.hide_viewport = not visible
        obj.hide_render = not visible
        obj.hide_set(not visible)

def toggle_collection_visibility(collection, visible):
    """
    Recursively toggle visibility of all objects in a collection and its child collections.

    Args:
        collection (bpy.types.Collection): The Blender collection to toggle visibility for
        visible (bool): Whether to make the collection visible (True) or invisible (False)
    """
    if collection:
        for obj in collection.objects:
            toggle_visibility(obj, visible)
        for child in collection.children:
            toggle_collection_visibility(child, visible)

def reset_scene():
    # Import trackers here to avoid circular dependency
    from core.trackers import RotationTracker
    from core.trackers import MaterialTracker
    
    # Reset any rotated objects
    RotationTracker.get_instance().reset_rotations()
    
    # Reset any modified materials
    MaterialTracker.get_instance().reset_materials()
    
    # Delete wires collection if it exists
    if 'Wires' in bpy.data.collections:
        wires_collection = bpy.data.collections['Wires']
        # First remove all objects in the collection
        for obj in wires_collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
    
    # Only operate on objects that are in the view layer
    for obj in bpy.context.view_layer.objects:
        if obj.type not in {'CAMERA', 'LIGHT'}:
            obj.pass_index = 0
            obj.hide_viewport = True
            obj.hide_render = True
            obj.hide_set(True)
