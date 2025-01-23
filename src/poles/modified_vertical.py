from typing import Optional, Dict, Any, List, Tuple
import random
import bpy
from mathutils import Vector

from .base import PoleBase
from ..utils.scene_utils import toggle_visibility
from ..utils.wire_generator import create_power_wire

class ModifiedVertical(PoleBase):
    """
    Modified vertical pole configuration with support for various components
    and customizable insulator positions.
    
    Attributes:
        chickensupportbracket (bool): Whether to include support bracket
        insulator_collections (List[str]): Available insulator collections
        insulator_positions (Dict): Mapping of insulator positions
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        
        # Initialize specific attributes
        self.chickensupportbracket = False
        self.framing_collection = bpy.data.collections.get("Framing")
        self.conductors_collection = bpy.data.collections.get("Conductors")
        
        # Define insulator collections and positions
        self.insulator_collections = ["Insulators_Medium1", "Insulators_Short1"]
        
        # Define standard insulator positions
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
        if self.pole_collection and self.pole_type:
            toggle_visibility(self.pole_type, True)
        
        # Determine if chicken support bracket should be used
        if self.pole_type.name != "ConcretePole":
            self.chickensupportbracket = random.choice([True, False])
        else:
            self.chickensupportbracket = False
        
        # Set up insulators
        self._setup_insulators()
        
        # Add additional components
        self._add_required_components()

    def _setup_insulators(self):
        """Set up insulators based on configuration."""
        if not (self.framing_collection and self.conductors_collection):
            return

        # Select insulator collection
        selected_collection_name = random.choice(self.insulator_collections)
        selected_collection = self.framing_collection.children.get(selected_collection_name)
        
        if not selected_collection:
            return

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

            # Set insulator position based on type and bracket configuration
            if selected_collection_name == "Insulators_Medium1":
                positions = (self.insulator_wbracket_positions_medium 
                           if self.chickensupportbracket 
                           else self.insulator_positions_medium)
            else:  # Insulators_Short1
                positions = (self.insulator_wbracket_positions_short 
                           if self.chickensupportbracket 
                           else self.insulator_positions_short)
            
            insulator.location = Vector(positions[i])
            
            # Add to render tracking
            self.objects_to_render.add(insulator)

    def _add_required_components(self):
        """Add components specific to modified vertical configuration."""
        # Add support bracket if enabled
        if self.chickensupportbracket:
            self._add_support_bracket()
        
        # Add other standard components
        self._add_hardware()
        self._add_conductors()

    def _add_support_bracket(self):
        """Add chicken wing support bracket."""
        if not self.framing_collection:
            return
            
        bracket = self.framing_collection.objects.get("ChickenWingBracket")
        if bracket:
            toggle_visibility(bracket, True)
            self.objects_to_render.add(bracket)

    def _add_hardware(self):
        """Add necessary hardware components."""
        # Implementation for adding bolts, clamps, etc.
        pass

    def _add_conductors(self):
        """Add power conductors between insulators."""
        if not self.conductors_collection:
            return
            
        # Implementation for adding power lines
        pass

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata specific to modified vertical configuration.
        
        Returns:
            Dictionary containing pole metadata including specific attributes.
        """
        base_metadata = super().get_metadata()
        
        # Add modified vertical specific metadata
        additional_metadata = {
            "has_support_bracket": self.chickensupportbracket,
            "insulator_type": self.insulator_collections[0],  # Currently selected type
            "num_phases": self.phases
        }
        
        return {**base_metadata, **additional_metadata}