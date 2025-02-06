from typing import Optional, Dict, Any
import random
import bpy
from mathutils import Vector

from core.base import PoleBase
from utils.scene_utils import toggle_visibility, toggle_collection_visibility
from utils.wire_generator import create_power_wire


class Vertical(PoleBase):   
    """
        Modified vertical pole configuration with support for various components
        and customizable insulator positions.
        """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        print('gonna init modified vertical')
        # Initialize base class with config
        super().__init__(config, 'Vertical')
        
        # Initialize collections
        self.framing_collection = bpy.data.collections.get("Vertical_Framing")
        self.conductors_collection = bpy.data.collections.get("Conductors")
        self.supportbracket_collection = self.framing_collection.children.get('SupportBrackets')

        
        # Define standard positions
        self.insulator_positions_medium = [(-0.740069,-3.94067,39.1149), (-0.740069,-3.94067,30.115), (-0.028575,-3.94067,21.115)]
        self.insulator_positions_short = [(-0.028575,-2.39464,38.1557), (-0.028575,-2.39464,30.115), (-0.028575,-2.39464,21.115)]
        self.insulator_wbracket_positions_medium = [(-0.812422,-5.36507,38.2129), (-0.822692,-5.31377,30.115), (-0.772269,-5.37186,21.115)]
        self.insulator_wbracket_positions_short = [(-0.028575,-3.79048,38.1557), (-0.028575,-3.79048,30.115), (-0.028575,-3.79048,21.115)]
        self.conductor_positions_medium = [(34.1186, -8.54345, 39.5244), (34.6691, -8.53448, 30.5727), (34.8086, -8.53338, 21.5455)]
        self.conductor_positions_medium_wbracket = [(34.1186, -9.99235, 38.727), (34.6691, -9.94244, 30.5727), (34.6691, -9.99287, 21.5455)]
        self.conductor_positions_short = [(34.1186, -7.89351, 38.7011), (34.6691, -7.83458, 30.5727), (34.6691, -7.8928, 21.5455)]
        self.conductor_positions_short_wbracket = [(34.1186, -9.28959, 38.727), (34.6691, -9.67384, 30.5727), (34.6691, -9.25654, 21.5455)]

    def setup_pole(self):
        if self.pole_type:
            """Set up the basic pole structure and components."""
            toggle_visibility(self.pole_type, True)
                 
            # Set up base components (insulators)
            self._setup_insulators_and_conductors()
            
            # Add components based on selected setup
            if self.has_aetx:
                self._add_aetx()
            
            if self.has_als or self.has_doubleals:
                self._add_als()
            
            # Add optional components
            if self.has_surge_arresters:
                self._add_surge_arresters()
            
            if self.has_fcis:
                self._add_fcis()
    
    def _setup_insulators_and_conductors(self):
        """Set up insulators based on configuration."""
        if not (self.framing_collection and self.conductors_collection):
            return

        # Select insulator type from configuration
        selected_type = random.choice(self.insulator_types)
        selected_collection = self.framing_collection.children.get(f"Insulators_{selected_type}1")
        
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
            if self.has_insulator_support_bracket and selected_type == "Medium":
                insulator.location = Vector(self.insulator_wbracket_positions_medium[i])
            elif self.has_insulator_support_bracket and selected_type == "Short":
                insulator.location = Vector(self.insulator_wbracket_positions_short[i])
            elif selected_type == "Medium":
                insulator.location = Vector(self.insulator_positions_medium[i])
            elif selected_type == "Short":
                insulator.location = Vector(self.insulator_positions_short[i])
            
            toggle_visibility(insulator, is_visible)

            if self.has_insulator_support_bracket:
                supportbracket = self.supportbracket_collection.objects.get(f"{i+1}.001")
                toggle_visibility(supportbracket, is_visible)
            
            if not is_visible:
                continue
            
            conductor = self.conductors_collection.objects.get(str(i + 1))
            if conductor:
                toggle_visibility(conductor, is_visible)
                # Adjust conductor position based on insulator type
                if selected_type == "Medium":
                    if self.has_insulator_support_bracket:  
                        conductor.location = Vector(self.conductor_positions_medium_wbracket[i])
                    else:
                        conductor.location = Vector(self.conductor_positions_medium[i])
                elif selected_type == "Short":
                    if self.has_insulator_support_bracket:
                        conductor.location = Vector(self.conductor_positions_short_wbracket[i])
                    else:
                        conductor.location = Vector(self.conductor_positions_short[i])
