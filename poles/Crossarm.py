from typing import Optional, Dict, Any
import random
import bpy
from mathutils import Vector

from core.base import PoleBase
from utils.scene_utils import toggle_visibility, toggle_collection_visibility
from utils.wire_generator import create_power_wire
from generators.anomalies import rotate_object_global

class Crossarm(PoleBase):
    """
    Deadend pole configuration with guy wires
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        # Initialize base class with config
        super().__init__(config, 'Crossarm')
        
        self.framing_collection = bpy.data.collections.get("CrossarmFraming")
        self.insulator_collections = ["Insulators"]
        self.crossarm_collection = self.framing_collection.children.get('Framings')
        self.conductors_collection = self.framing_collection.children.get("Conductor")

    def setup_pole(self):
        if self.pole_type:
            toggle_visibility(self.pole_type, True)

        if self.pole_material == "Concrete":
            self.crossarm_type = self.crossarm_collection.objects.get("Steel")
        elif self.pole_material == "Wood":
            self.crossarm_type = self.crossarm_collection.objects.get("Wood")
        toggle_visibility(self.crossarm_type, True)
        if self.framing_collection and self.conductors_collection:
            selected_collection_name = random.choice(self.insulator_collections)
            selected_collection = self.framing_collection.children.get(selected_collection_name)
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

                    if self.pole_material == "Wood":
                        toggle_visibility(self.framing_collection.objects.get('WoodSupport1'), True)
                        toggle_visibility(self.framing_collection.objects.get('WoodSupport2'), True)
                    if self.has_afs:
                        afs_collection = self.framing_collection.children.get("Scadamate")
                        toggle_collection_visibility(afs_collection, True)
        
        if self.has_fuse or self.has_als:
            self.setup_3xfuse_or_als()
    

    def setup_3xfuse_or_als(self):
        self.ALS_Fuse_Crossarm_Collection = bpy.data.collections.get("ALS_Fuse_Crossarm")
        self.fuse_collection = self.ALS_Fuse_Crossarm_Collection.children.get("Framings.001")
        self.Fuse_Wires = self.ALS_Fuse_Crossarm_Collection.children.get("WireAttatchesForCrossArm")
        self.BarrelFuses = self.ALS_Fuse_Crossarm_Collection.children.get("CrossarmFuses")
        if random.random() < self.anomaly_types.get('als_open' if self.has_als else 'fuse_open', 0.2):
                        # Randomly choose which ALS parts have anomalies
            # Options: any single one, any pair, or all three
            possible_combinations = [
                [1], [2], [3],  # single anomaly
                [1, 2], [1, 3], [2, 3],  # pair of anomalies
                [1, 2, 3]  # all three
            ]
            self.anomaly_parts = random.choice(possible_combinations)
        else:
            self.anomaly_parts = []
        

        if self.pole_material == "Wood":
            toggle_visibility(self.fuse_collection.objects.get('WoodSupports1'), True)
            toggle_visibility(self.fuse_collection.objects.get('WoodSupports2'), True)
            toggle_visibility(self.fuse_collection.objects.get('WoodxArm'), True)
        else:
            toggle_visibility(self.fuse_collection.objects.get('SteelXArm'), True)

        if self.phases == 3:
            wire_collections = ['ALS_Fuse_Crossarm_Wire1.001', 'ALS_Fuse_Crossarm_Wire2.001', 'ALS_Fuse_Crossarm_Wire3.001']
            
            if self.has_als:
                toggle_collection_visibility(self.fuse_collection.children.get('1PH_ALS_Fuse_Crossarm'), True)
                toggle_collection_visibility(self.fuse_collection.children.get('2PH_ALS_Fuse_Crossarm'), True)
                toggle_collection_visibility(self.fuse_collection.children.get('3PH_ALS_Fuse_Crossarm'), True)
                
                # Apply anomalies to ALS parts
                for i in range(1, 4):
                    if i in self.anomaly_parts:
                        als_obj = self.fuse_collection.children.get(f'{i}PH_ALS_Fuse_Crossarm').objects.get(f'ALS{i}.009')
                        if als_obj:
                            rotate_object_global(als_obj, random.randint(-60, -50), 'X')
            else:  # Barrel fuses
                toggle_collection_visibility(self.BarrelFuses.children.get('CrossarmFuses 1'), True)
                toggle_collection_visibility(self.BarrelFuses.children.get('CrossarmFuses 2'), True)
                toggle_collection_visibility(self.BarrelFuses.children.get('CrossarmFuses 3'), True)
                for i in range(1, 4):
                    if i in self.anomaly_parts:
                        fuse_obj = self.BarrelFuses.children.get(f'CrossarmFuses {i}').objects.get(f'BarrelFuse{i}')
                        if fuse_obj:
                            rotate_object_global(fuse_obj, random.randint(-170, -140), 'X')
        
        elif self.phases == 2:
            wire_collections = ['ALS_Fuse_Crossarm_Wire1.001', 'ALS_Fuse_Crossarm_Wire2.001']
            
            if self.has_als:
                toggle_collection_visibility(self.fuse_collection.children.get('1PH_ALS_Fuse_Crossarm'), True)
                toggle_collection_visibility(self.fuse_collection.children.get('2PH_ALS_Fuse_Crossarm'), True)
                
                # Apply anomalies to ALS parts (only first two)
                for i in range(1, 3):
                    if i in self.anomaly_parts:
                        als_obj = self.fuse_collection.children.get(f'{i}PH_ALS_Fuse_Crossarm').objects.get(f'ALS{i}.009')
                        if als_obj:
                            rotate_object_global(als_obj, random.randint(-60, -50), 'X')
            else:  # Barrel fuses
                toggle_collection_visibility(self.BarrelFuses.children.get('CrossarmFuses 1'), True)
                toggle_collection_visibility(self.BarrelFuses.children.get('CrossarmFuses 2'), True)
                for i in range(1, 3):
                    if i in self.anomaly_parts:
                        fuse_obj = self.BarrelFuses.children.get(f'CrossarmFuses {i}').objects.get(f'BarrelFuse{i}')
                        if fuse_obj:
                            rotate_object_global(fuse_obj, random.randint(-170, -140), 'X')

        if self.Fuse_Wires:
            for wire_name in wire_collections:
                collection = self.Fuse_Wires.children.get(wire_name)
                if collection:
                    toggle_collection_visibility(collection, True)
                    empties = [obj for obj in collection.objects if obj.type == 'EMPTY']
                    if len(empties) == 2:
                        create_power_wire(empties[0], empties[1])

        
