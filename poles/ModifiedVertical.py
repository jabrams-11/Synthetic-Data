from typing import Optional, Dict, Any
import random
import bpy
from mathutils import Vector

from core.base import PoleBase
from utils.scene_utils import toggle_visibility, toggle_collection_visibility
from utils.wire_generator import create_power_wire
from generators.anomalies import rotate_object_global

class ModifiedVertical(PoleBase):
    """
    Modified vertical pole configuration with support for various components
    and customizable insulator positions.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        print('gonna init modified vertical')
        # Initialize base class with config
        super().__init__(config, 'ModifiedVertical')
        
        # Initialize collections
        self.pole_collection = bpy.data.collections.get("Poles")
        self.framing_collection = bpy.data.collections.get("Modified_Vertical_Framing")
        self.conductors_collection = bpy.data.collections.get("Conductors")
        
        # Get pole object
        self.pole_type = self._get_pole_object(f"{self.pole_material}Pole")
        
        # Define standard positions
        self.conductor_positions_medium = [
            (34.6691, -2.23303, 44.7747),
            (34.6691, -8.53448, 33.2859), 
            (34.6691, -8.53528, 24.1912)
        ]
        
        self.conductor_positions_short = [
            (34.6691, -2.17132, 44.0459),
            (34.6691, -7.84183, 33.2859),
            (34.6691, -7.84471, 24.1912)
        ]

    def setup_pole(self):
        """Set up the basic pole structure and components."""
        # Set up base pole
        if self.pole_type:
            toggle_visibility(self.pole_type, True)
        
        # Set up base components (insulators)
        self._setup_insulators_and_conductors()
        
        # Add components based on selected setup
        if self.has_aetx and not self.has_three_phase_aetx:
            self._add_aetx()
        
        if (self.has_als or self.has_doubleals) and not self.has_crossarm_pulloff:
            self._add_als()
        
        # Add optional components
        if self.has_surge_arresters:
            self._add_surge_arresters()
        
        if self.has_fcis:
            self._add_fcis()
            print('added fcis')

        if self.has_three_phase_aetx:
            self._add_three_phase_aetx()
        
        if self.has_crossarm_pulloff:
            self._add_crossarm_pulloff()


    def _setup_insulators_and_conductors(self):
        """Set up insulators based on configuration."""

        if not (self.framing_collection and self.conductors_collection):
            return

        # Select insulator type from configuration
        selected_type = random.choice(self.insulator_types)
        selected_collection = self.framing_collection.children.get(f"Insulators_{selected_type}")
        
        if not selected_collection:
            return
        
        if self.pole_material == "Wood":
            toggle_visibility(self.framing_collection.objects.get("TopClamp"), True)

        # Get and sort insulators
        insulators = sorted(
            [obj for obj in selected_collection.objects 
             if obj.name.lower().startswith("insulator")],
            key=lambda x: x.name
        )

        # Position insulators based on configuration
        for i, insulator in enumerate(insulators):
            # Only show insulators up to the number of phases
            is_visible = i < self.phases
            toggle_visibility(insulator, is_visible)
            
            if not is_visible:
                continue
            
            conductor = self.conductors_collection.objects.get(str(i + 1))
            if conductor:
                toggle_visibility(conductor, is_visible)
                # Adjust conductor position based on insulator type
                if selected_type == "Medium":
                    conductor.location = Vector(self.conductor_positions_medium[i])
                elif selected_type == "Short":
                    conductor.location = Vector(self.conductor_positions_short[i])

        self._add_neut_framing()
    
    def _add_als(self):
        """Add ALS components based on setup."""
        als_collection = bpy.data.collections.get("ALS")
        als2_collection = bpy.data.collections.get("ALS2x")
        wire_attachments = bpy.data.collections.get("WireAttatchments")
        wire_attachments2 = als2_collection.children.get("WireAttatchment")
        if not als_collection:
            return
        
        toggle_collection_visibility(als_collection, True)

        if wire_attachments:
            for collection in wire_attachments.children:
                empties = [obj for obj in collection.objects if obj.type == 'EMPTY']
                if len(empties) == 2:
                    create_power_wire(empties[0], empties[1])

        if self.has_doubleals:  # Double lateral pull off with ALS pole
            toggle_collection_visibility(als2_collection, True)
            for collection in wire_attachments2.children:
                empties = [obj for obj in collection.objects if obj.type == 'EMPTY']
                if len(empties) == 2:
                    create_power_wire(empties[0], empties[1])
        
        # Handle ALS anomalies
        if self.enable_anomalies:
            if random.random() < self.anomaly_types.get('als_open', 0.2):
                if self.has_doubleals:
                    # Randomly choose which ALS(s) to affect
                    choice = random.choice(['als1', 'als2', 'both'])
                    
                    if choice in ['als1', 'both']:
                        als_obj = als_collection.objects.get('ALS')
                        if als_obj:
                            rotate_object_global(als_obj, random.randint(-60, -50))
                    
                    if choice in ['als2', 'both']:
                        als2_obj = als2_collection.objects.get('ALS2')
                        if als2_obj:
                            rotate_object_global(als2_obj, random.randint(50, 60))
                else:
                    # If only one ALS, just rotate it
                    als_obj = als_collection.objects.get('ALS')
                    if als_obj:
                        rotate_object_global(als_obj, random.randint(-60, -50))
            
            elif random.random() < self.anomaly_types.get('als_flashed', 0.2):
                for obj in als_collection.objects:
                    if obj.get('label') == 'ALS':
                        flashed_mat = bpy.data.materials.get('FlashedALSMaterial')
                        if flashed_mat:
                            obj.active_material = flashed_mat
                            obj['label'] = 'ALS_Flashed'

    def _add_three_phase_aetx(self):
        self.transformers_collection = bpy.data.collections.get("3PhTransformer")
        if random.random() < self.anomaly_types.get('fuse_open', 0.2):
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
        
        toggle_collection_visibility(self.transformers_collection, True)
        wire_collection = self.transformers_collection.children.get("WireAttatchesTx")
        if wire_collection:
            for child_collection in wire_collection.children:
                empties = [obj for obj in child_collection.objects if obj.type == 'EMPTY']
                if len(empties) == 2:
                    create_power_wire(empties[0], empties[1])
        for i in range(1, self.phases + 1):
            if i in self.anomaly_parts:
                fuse_switch = self.transformers_collection.children.get(f'3PhTransformer{i}').objects.get(f'BarrelAetx{i}')
                if fuse_switch:
                    print(f'BarrelAetx{i} found')
                    if i == 1:
                        rotate_object_global(fuse_switch, random.randint(140, 170), 'Y')
                    elif i == 2:
                        rotate_object_global(fuse_switch, random.randint(-170, -140), 'Y')
                    elif i == 3:
                        rotate_object_global(fuse_switch, random.randint(140, 170), 'X')

    def _add_crossarm_pulloff(self):
        """
        Add a crossarm pulloff configuration to the pole.
        
        This method sets up a crossarm with either ALS or fuse components based on the pole configuration.
        It handles both wood and concrete pole materials, and supports 2 or 3 phase setups.
        The method also manages anomaly states for ALS/fuse components and creates the necessary wire connections.
        """
        self.ALS_Fuse_Crossarm_Collection = bpy.data.collections.get("ALS_Fuse_Crossarm")
        self.fuse_collection = self.ALS_Fuse_Crossarm_Collection.children.get("Framings.001")
        self.Fuse_Wires = self.ALS_Fuse_Crossarm_Collection.children.get("WireAttatches")
        self.BarrelFuses = self.ALS_Fuse_Crossarm_Collection.children.get("CrossarmFuses")
        if random.random() < self.anomaly_types.get('als_open' if self.has_als else 'fuse_open', 0.2):
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
            wire_collections = ['ALS_Fuse_Crossarm_Wire1', 'ALS_Fuse_Crossarm_Wire2', 'ALS_Fuse_Crossarm_Wire3']
            
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
                            rotate_object_global(fuse_obj, random.randint(-180, -140), 'X')
                        
        elif self.phases == 2:
            wire_collections = ['ALS_Fuse_Crossarm_Wire1', 'ALS_Fuse_Crossarm_Wire2']
            
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
                            rotate_object_global(fuse_obj, random.randint(-180, -140), 'X')
        
        # Create power wires
        if self.Fuse_Wires:
            for wire_name in wire_collections:
                collection = self.Fuse_Wires.children.get(wire_name)
                if collection:
                    toggle_collection_visibility(collection, True)
                    empties = [obj for obj in collection.objects if obj.type == 'EMPTY']
                    if len(empties) == 2:
                        create_power_wire(empties[0], empties[1])