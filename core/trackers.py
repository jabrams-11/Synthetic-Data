from typing import Dict, Tuple, Any, Optional
from mathutils import Matrix

class RotationTracker:
    """Tracks and manages object rotations and their associated labels.
    
    This singleton class keeps track of rotated objects and their original states,
    allowing for restoration of original rotations and labels.
    """
    _instance: Optional['RotationTracker'] = None
    
    def __init__(self):
        self.rotated_objects: Dict[str, Tuple[Any, Matrix, str]] = {}
    
    @classmethod
    def get_instance(cls) -> 'RotationTracker':
        if cls._instance is None:
            cls._instance = RotationTracker()
        return cls._instance
    
    def track_rotation(self, obj: Any, original_matrix: Matrix) -> None:
        """Track an object's rotation and update its label.
        
        Args:
            obj: The Blender object being rotated
            original_matrix: The original world matrix of the object
        """
        if not obj or not hasattr(obj, 'name'):
            raise ValueError("Invalid object provided for rotation tracking")
            
        # Store original label if it exists
        original_label = obj.get('label', '')
        self.rotated_objects[obj.name] = (obj, original_matrix, original_label)
        
        # Update label with _Anomaly suffix
        if original_label:
            obj['label'] = f"{original_label}_Anomaly"
    
    def reset_rotations(self) -> None:
        """Reset all tracked objects to their original rotation and label."""
        for obj_name, (obj, original_matrix, original_label) in self.rotated_objects.items():
            if obj:
                obj.matrix_world = original_matrix
                if original_label:
                    obj['label'] = original_label
        self.rotated_objects.clear()

class MaterialTracker:
    """Tracks and manages object materials and their associated labels.
    
    This singleton class keeps track of material changes and allows restoration
    of original materials and labels.
    """
    _instance: Optional['MaterialTracker'] = None
    
    def __init__(self):
        self.original_materials: Dict[str, Tuple[Any, Any]] = {}
    
    @classmethod
    def get_instance(cls) -> 'MaterialTracker':
        if cls._instance is None:
            cls._instance = MaterialTracker()
        return cls._instance
    
    def track_material(self, obj: Any, original_material: Any) -> None:
        """Track an object's original material before modification.
        
        Args:
            obj: The Blender object being modified
            original_material: The original material of the object
        """
        if not obj or not hasattr(obj, 'name'):
            raise ValueError("Invalid object provided for material tracking")
            
        self.original_materials[obj.name] = (obj, original_material)
    
    def reset_materials(self) -> None:
        """Reset all tracked objects back to their original materials and labels."""
        for obj_name, (obj, original_material) in self.original_materials.items():
            if obj:
                obj.active_material = original_material
                # Reset label if it was changed to ALS_Flashed
                if obj.get('label') == 'ALS_Flashed':
                    obj['label'] = 'ALS'
        self.original_materials.clear()
