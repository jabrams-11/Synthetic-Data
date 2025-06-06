from typing import Optional, Dict, Any
import random
import bpy
from mathutils import Vector

from core.base import PoleBase
from utils.scene_utils import toggle_visibility, toggle_collection_visibility
from utils.wire_generator import create_power_wire
from generators.anomalies import rotate_object_global


class DoubleCrossarm(PoleBase):
    """
    Duble crossarm pole with ALS
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config, 'DoubleCrossarm')

        self.framing_collection = bpy.data.collections.get("DoubleCrossArmPole")
        self.crossarm_parent_collection = bpy.data.collections.get("CrossarmFraming")
        self.crossarm_collection = self.crossarm_parent_collection.children.get("Framings")
        self.als_collection = self.framing_collection.children.get("ALSComponents")
        self.fuse_wires = self.framing_collection.children.get("JumperAttachment")
        self.conductors_collection = self.crossarm_parent_collection.children.get("Conductor")
        self.insulator_collections = ["Insulators"]

    def setup_pole(self):
        self.pole_collection = bpy.data.collections.get("Poles")
        self.pole_type = self.pole_collection.objects.get("WoodPole")
        if self.phases == 1:
            self.phases = random.randint(2, 3)
        if self.pole_type: # note: Should be wood pole for now until we add steel/fg xarms
            toggle_visibility(self.pole_type, True)
        
        toggle_collection_visibility(self.framing_collection, True)
        toggle_visibility(self.crossarm_parent_collection.objects.get('WoodSupport1'), True)
        toggle_visibility(self.crossarm_parent_collection.objects.get('WoodSupport2'), True)

        if self.phases == 2:
            toggle_visibility(self.framing_collection.objects.get("Insulator3.004"), False)

        self.pole_material = "Wood"
        self.crossarm_type = self.crossarm_collection.objects.get("Wood")
        toggle_visibility(self.crossarm_type, True)

        if self.framing_collection and self.conductors_collection:
            selected_collection_name = random.choice(self.insulator_collections)
            selected_collection = self.crossarm_parent_collection.children.get(selected_collection_name)
            if selected_collection:
                insulators = sorted([obj for obj in selected_collection.objects if obj.name.lower().startswith("insulator")],
                                    key=lambda x: x.name)
                for i, insulator in enumerate(insulators):
                    is_visible = i < self.phases
                    toggle_visibility(insulator, is_visible)
                    
                    conductor = self.conductors_collection.objects.get(f"{i+1}.003")
                    if conductor:
                        toggle_visibility(conductor, is_visible)
                        # Adjust conductor position based on insulator type
                    toggle_visibility(self.framing_collection.objects.get('WoodSupport1'), True)
                    toggle_visibility(self.framing_collection.objects.get('WoodSupport2'), True)
      

        if self.has_als:
            self.setup_als()
        else:
            toggle_collection_visibility(self.als_collection, False)



    def setup_als(self):
        wire_collections = ['ALS_Fuse_Crossarm_Wire1.001', 'ALS_Fuse_Crossarm_Wire2.001', 'ALS_Fuse_Crossarm_Wire3.001']
        toggle_collection_visibility(self.als_collection, True)
        toggle_collection_visibility(self.fuse_wires, True)
        if self.phases == 2:
            toggle_visibility(self.als_collection.objects.get("ALS3.000"), False)
            toggle_visibility(self.als_collection.objects.get("Lateral3.008"), False)
            toggle_visibility(self.als_collection.objects.get("Sharp fusion 1.013"), False)
            toggle_visibility(self.als_collection.objects.get("DEInsulator3.002"), False)

            wire_collection = ["JumperStart22", "JumperStart2"]
            for wire_name in wire_collections:
                wire_collection = self.fuse_wires.children.get(wire_name)
                if wire_collection:
                    toggle_collection_visibility(wire_collection, True)
                    empties = [obj for obj in wire_collection.objects if obj.type == 'EMPTY']
                    if len(empties) == 2:
                        create_power_wire(empties[0], empties[1])
        else:
            if self.fuse_wires:
                for collection in self.fuse_wires.children:
                    empties = [obj for obj in collection.objects if obj.type == 'EMPTY']
                    if len(empties) == 2:
                        create_power_wire(empties[0], empties[1])




