from typing import Optional, Dict, Any
import random
import bpy
from mathutils import Vector

from core.base import PoleBase
from utils.scene_utils import toggle_visibility, toggle_collection_visibility
from utils.wire_generator import create_power_wire
#from generators.anomalies import rotate_object_global

class Deadend(PoleBase):
    """
    Deadend pole configuration with guy wires
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # Initialize base class with config
        super().__init__(config, 'Deadend')
        
        self.framing_collection = bpy.data.collections.get("DeadendFraming")
        self.insulator_collections = ["Framing"]
        self.conductors_collection = self.framing_collection.children.get("Conductors.001")
        self.guy_collection = self.framing_collection.children.get("Guys")

    def setup_pole(self):
        if self.pole_collection and self.pole_type:
            toggle_visibility(self.pole_type, True)
        if self.framing_collection and self.conductors_collection:
            selected_collection_name = random.choice(self.insulator_collections)
            selected_collection = self.framing_collection.children.get(selected_collection_name)
            if selected_collection:
                toggle_visibility(self.guy_collection.objects.get('Guy1'), True)
                toggle_visibility(self.guy_collection.objects.get('Guy2'), True)
                insulators = sorted([obj for obj in selected_collection.objects if obj.name.lower().startswith("deinsulator")],
                                    key=lambda x: x.name)
                for i, insulator in enumerate(insulators):
                    is_visible = i < self.phases
                    toggle_visibility(insulator, is_visible)
                    
                    conductor = self.conductors_collection.objects.get(f"{i+1}.002")
                    if conductor:
                        toggle_visibility(conductor, is_visible)

