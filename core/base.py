"""Base class for all pole types with common component handling."""

import random
import bpy
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Tuple

#from ..utils.scene_utils import toggle_visibility, reset_scene
from utils.scene_utils import toggle_visibility, toggle_collection_visibility
from utils.wire_generator import create_power_wire
from generators.anomalies import rotate_object_global

class PoleBase(ABC):
    """Base class for pole generation with configuration handling."""

    def __init__(self, config: Optional[Dict[str, Any]] = None, pole_type: str = None):
        """
        Initialize pole with configuration.
        
        Args:
            config: Configuration dictionary containing pole generation settings
        """
        if not config:
            raise ValueError("Configuration is required")

        # Initialize basic attributes
        self.config = config
        
        # Select number of phases based on config probabilities
        self.phases = self._select_phases(config.get('phases', {}))
        
        # Select pole material and type
        self.pole_collection = bpy.data.collections.get("Poles")
        self.pole_material = self._select_material(config.get('pole_materials', {}))
        self.pole_type = self._get_pole_object(f"{self.pole_material}Pole")
        # Get pole type name from class name
        pole_type_name = pole_type
        # Get configuration for specific pole type
        self.pole_config = config.get('pole_framing_types', {}).get(pole_type_name, {})
        self.configurations = self.pole_config.get('configurations', {})
        
        # Get possible setups and components
        self.possible_setups = self.configurations.get('possible_setups', [])
        self.optional_components = self.configurations.get('optional_components', [])
        self.insulator_types = self.configurations.get('insulator_types', [])
        # Get valid setup based on requirements and probabilities
        self.selected_setup = self._select_valid_setup(
            self.possible_setups,
            self.config.get('component_requirements', {}),
            self.config.get('equipment_chances', {})
        )
        
        # Initialize component states based on selected setup
        self.has_aetx = 'aetx' in self.selected_setup
        self.has_fuse = 'fuse' in self.selected_setup
        self.has_ats = 'ats' in self.selected_setup

        self.has_ats = False # NOTE: TEMPORARY
        
        self.has_doubleals = 'als' in self.selected_setup and self.phases == 3
        self.has_als = 'als' in self.selected_setup and not self.has_doubleals
        self.has_als = 'als' in self.selected_setup
        self.als_count = self.selected_setup.count('als')
        self.has_afs = 'afs' in self.selected_setup
        self.has_three_phase_aetx = 'three_phase_aetx' in self.selected_setup
        self.has_crossarm_pulloff = 'crossarm' in self.selected_setup
        # Initialize optional components based on config probabilities
        equipment_chances = self.config.get('equipment_chances', {})


        self.has_surge_arresters = ('surge_arresters' in self.optional_components and 
                                   random.random() < equipment_chances.get('surge_arresters', 0)/100)
        print('has_surge_arresters ', self.has_surge_arresters)
        self.has_fcis = ('fcis' in self.optional_components and 
                         random.random() < equipment_chances.get('fcis', 0)/100 and self.phases == 3)
        self.has_insulator_support_bracket = ('insulator_support_bracket' in self.optional_components and 
                                   random.random() < equipment_chances.get('support_bracket', 0)/100)
        # Initialize anomaly settings
        anomaly_config = self.config.get('anomalies', {})
        self.enable_anomalies = random.random() < anomaly_config.get('enable_chance', 0)
        self.anomaly_types = anomaly_config.get('types', {}) if self.enable_anomalies else {}

    def _select_phases(self, phase_config: Dict[str, int]) -> int:
        """Select number of phases based on configuration probabilities."""
        phase_mapping = {'single_phase': 1, 'two_phase': 2, 'three_phase': 3}

        phase_type = random.choices(list(phase_config.keys()), weights=phase_config.values())[0]
        return phase_mapping[phase_type]

    def _select_material(self, material_config: Dict[str, int]) -> str:
        """Select pole material based on configuration probabilities."""
        materials = list(material_config.keys())
        weights = list(material_config.values())
        return random.choices(materials, weights=weights, k=1)[0]

    def _get_pole_object(self, pole_type_name: str) -> Optional[bpy.types.Object]:
        """Get pole object from collection based on type name."""
        if self.pole_collection:
            # If it's a wood pole, randomly choose between WoodPole and WoodPole2
            if pole_type_name == "WoodPole":
                wood_poles = ["WoodPole", "WoodPole2"]
                selected_pole = random.choice(wood_poles)
            
                return self.pole_collection.objects.get(selected_pole)
            # For other materials, use the original pole type name
            return self.pole_collection.objects.get(pole_type_name)
        return None

    def _check_component_requirements(self, component: str) -> bool:
        """Check if pole meets requirements for a given component."""
        requirements = self.config.get('component_requirements', {}).get(component, {})
        min_phases = requirements.get('min_phases', 1)
        return self.phases >= min_phases

    def _get_valid_setups(self, pole_type: str) -> List[List[str]]:
        """Get valid setups for current pole configuration."""
        pole_config = self.config.get('pole_framing_types', {}).get(pole_type, {})
        possible_setups = pole_config.get('configurations', {}).get('possible_setups', [])
        
        valid_setups = []
        for setup in possible_setups:
            if all(self._check_component_requirements(component) for component in setup):
                valid_setups.append(setup)
        
        return valid_setups

    @abstractmethod
    def setup_pole(self):
        """Set up the basic pole structure. Must be implemented by subclasses."""
        pass

    def generate(self):
        """Generate the pole with selected configuration."""
        if not self.pole_type:
            raise ValueError("No valid pole type selected")
        
        self.setup_pole()

    def _select_pole_type(self, material_config: Dict[str, int]) -> str:
        """Select pole type based on material probabilities."""
        materials = list(material_config.keys())
        weights = list(material_config.values())
        selected = random.choices(materials, weights=weights, k=1)[0]
        return f"{selected}Pole"

    def _select_valid_setup(self, possible_setups: List[List[str]], 
                           requirements: Dict[str, Dict[str, int]], 
                           chances: Dict[str, float]) -> List[str]:
        """
        Select a valid setup based on requirements and dynamic probability calculations.
        
        Args:
            possible_setups: List of possible component combinations
            requirements: Dictionary of component requirements
            chances: Dictionary of probability modifiers for components and their combinations
        """
        valid_setups = []
        
        # Filter valid setups based on requirements
        for setup in possible_setups:
            if all(self.phases >= requirements.get(component, {}).get('min_phases', 1) 
                   for component in setup):
                valid_setups.append(setup)
        
        if not valid_setups:
            return []
        
        # Calculate weights dynamically
        setup_weights = []
        for setup in valid_setups:
            weight = 1.0
            
            # Process each component's base probability (convert from percent to decimal)
            for component in setup:
                weight += chances.get(component, 1) / 100  # Default 50% if not specified
            setup_weights.append(weight)

        # Print valid setups and their weights
        print("\nValid setups and weights:")
        for setup, weight in zip(valid_setups, setup_weights):
            print(f"Setup: {setup}, Weight: {weight:.2f}")
        
        # Select setup based on calculated weights
        final_setup = random.choices(valid_setups, weights=setup_weights, k=1)[0]
        print(f"\nSelected setup: {final_setup}\n")
        return final_setup
    def _add_surge_arresters(self):
        if self.has_aetx or self.has_fcis or self.has_doubleals or self.has_three_phase_aetx:
            return
        """Add surge arresters based on configuration."""
        surge_arrester_collection = bpy.data.collections.get("SurgeArresters")
        
        Surge_Arrester_Wires = surge_arrester_collection.children.get("SA_Wires")
        
        # Randomly choose between SurgeArresters1 and SurgeArresters2 collections
        variant = random.choice(['1', '2'])
        
        for i in range(1, self.phases + 1):
            if variant == '1':
                sub_collection = surge_arrester_collection.children.get('SurgeArresters1')
                arrester = sub_collection.objects.get(f"SurgeArrester{i}") if sub_collection else None
            else:
                sub_collection = surge_arrester_collection.children.get('SurgeArresters2')
                arrester = sub_collection.objects.get(f"SurgeArrester{i}{i}") if sub_collection else None
                cylinder = sub_collection.objects.get(f"Cylinder{i}{i}") if sub_collection else None
                if cylinder:
                    toggle_visibility(cylinder, True)
                
            if arrester:
                toggle_visibility(arrester, True)

                wire_collection = Surge_Arrester_Wires.children.get(f"{i}_SA_Wires")
                toggle_collection_visibility(wire_collection, True)
                if wire_collection and len(wire_collection.objects) >= 2:
                    create_power_wire(wire_collection.objects[0], wire_collection.objects[1])
    
    def _add_fcis(self):
        """Add FCI components based on configuration."""
        fci_collection = bpy.data.collections.get("FCIs")
        if not fci_collection:
            return
        toggle_collection_visibility(fci_collection, True)
    
    def _add_aetx(self):
        """Add AETX with either barrel fuse or ATS based on setup."""
        if not self.has_aetx or not self._check_component_requirements('aetx'):
            return
        
        aetx_collection = bpy.data.collections.get("1PhTransformer")
        if not aetx_collection:
            return

        toggle_collection_visibility(aetx_collection, True)

        #Choose a random fuse type #NOTE: CHANGE THIS LATER TO SETTINGS CONFIG
        # Choose between porcelain or polymer fuse
        fuse_type = random.choice(['porcelain', 'polymer'])
        if fuse_type == 'polymer':
            toggle_visibility(aetx_collection.objects.get('PorcelainFuse1'), False)
            toggle_visibility(aetx_collection.objects.get('PorcelainFuse2'), False)
        else:
            toggle_visibility(aetx_collection.objects.get('Fuse.001'), False)
            toggle_visibility(aetx_collection.objects.get('Barrel'), False)
            toggle_visibility(aetx_collection.objects.get('FuseCap'), False)
            
            porcelain_fuse1 = aetx_collection.objects.get('PorcelainFuse1')
            # Modify noise texture for porcelain fuse rust
            rust_mat = bpy.data.materials.get('PorcelainFuse1')
            if rust_mat and rust_mat.node_tree:
                nodes = rust_mat.node_tree.nodes
                rust_noise = nodes.get('Noise Texture.001')
                if rust_noise:
                    if random.random() < self.anomaly_types.get('porcelain_fuse_flashed', 0.3):
                        rust_noise.inputs['W'].default_value = random.uniform(0, 500)
                        porcelain_fuse1['label'] = porcelain_fuse1.get('label', '') + '_Flashed'
                        print(f"Porcelain fuse label: {porcelain_fuse1.get('label', '')}")
                        print('FLASHED')
                    else:
                        rust_noise.inputs['W'].default_value = 0
                        print(f"Porcelain fuse label: {porcelain_fuse1.get('label', '')}")
                        if '_Flashed' in porcelain_fuse1.get('label', ''):
                            porcelain_fuse1['label'] = porcelain_fuse1['label'].replace('_Flashed', '')
                        
            
        
        # Modify noise texture for porcelain fuse rust
        rust_mat = bpy.data.materials.get('PorcelainFuse1')
        if rust_mat and rust_mat.node_tree:
            nodes = rust_mat.node_tree.nodes
            rust_noise = nodes.get('Noise Texture.001')
            if rust_noise:
                rust_noise.inputs['W'].default_value = random.uniform(0, 500)
        
        # Choose a random AETX from choices
        chosen_aetx = random.choice(['AETX', 'AETX_2'])
        toggle_visibility(aetx_collection.objects.get('AETX' if chosen_aetx == 'AETX_2' else 'AETX_2'), False)

        ## NOTE: CHANGE THIS LATER TO SETTINGS CONFIG
        fuse_cap_chance = random.randint(0,3)
      
        if fuse_cap_chance < 3 or self.has_ats:
            toggle_visibility(aetx_collection.objects.get("FuseCap"),False)
        
        if self.has_ats:
            toggle_visibility(aetx_collection.objects.get('Fuse.001'), False)
            toggle_visibility(aetx_collection.objects.get('Barrel'), False)
            toggle_visibility(aetx_collection.objects.get('PorcelainFuse1'), False)
            toggle_visibility(aetx_collection.objects.get('PorcelainFuse2'), False)
            
            Wires = aetx_collection.children.get("ATS_Wires")
            # Add ATS anomaly if enabled
            if self.enable_anomalies and random.random() < self.anomaly_types.get('ats_open', 0.15):
                ats_part = aetx_collection.children.get('ATSConfig').objects.get('ATSpart')
                if ats_part:
                    rotate_object_global(ats_part, 40)
        else:
            toggle_collection_visibility(aetx_collection.children.get('ATSConfig'), False)
            Wires = aetx_collection.children.get("FuseWires")
            # Add fuse anomaly if enabled
            if self.enable_anomalies and random.random() < self.anomaly_types.get('fuse_open', 0.25):
                barrel = aetx_collection.objects.get('Barrel')
                if barrel:
                    rotate_object_global(barrel, random.randint(140, 180))

        if Wires:
            for wire_collection in Wires.children:
                empties = [obj for obj in wire_collection.objects if obj.type == 'EMPTY']
                if len(empties) == 2:
                    create_power_wire(empties[0], empties[1])
    
    def _add_neut_framing(self):
        conductors =  bpy.data.collections.get("Conductors")
        neut_framings = bpy.data.collections.get("Modified_Vertical_Framing")
        if self.has_aetx:
            toggle_visibility(conductors.objects.get('XNeut'), True)
            toggle_visibility(neut_framings.objects.get('ExtendedFork'), True)
        else:
            toggle_visibility(conductors.objects.get('Neut'), True)
            toggle_visibility(neut_framings.objects.get('SmFork'), True)
    