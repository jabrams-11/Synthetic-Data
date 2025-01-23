"""Base class for all pole types with common component handling."""

import random
import bpy
from abc import ABC, abstractmethod
from mathutils import Vector
from typing import Optional, Dict, Any, List

from ..utils.scene_utils import toggle_visibility, reset_scene
from ..generators.anomalies import rotate_object_global

class PoleBase(ABC):
    """
    Base class for all pole types with common component handling.
    
    Attributes:
        phases (int): Number of electrical phases
        pole_type (str): Type of pole (wood, concrete, etc.)
        aetx (bool): Whether AETX is enabled
        ats (bool): Whether ATS is enabled
        surge_arresters (bool): Whether surge arresters are enabled
        fci (bool): Whether FCIs are enabled
    """

    def __init__(self, 
                 phases: Optional[int] = None,
                 pole_type: Optional[str] = None,
                 surge_arresters: Optional[bool] = None,
                 aetx: Optional[bool] = None,
                 ats: Optional[bool] = None,
                 fci: Optional[bool] = None,
                 anomaly: Optional[bool] = None):
        """
        Initialize pole with common components.

        Args:
            phases: Number of phases (1-3)
            pole_type: Specific pole type to use
            surge_arresters: Enable surge arresters
            aetx: Enable AETX
            ats: Enable ATS (requires AETX)
            fci: Enable Fault Circuit Indicators
            anomaly: Enable anomaly generation
        """
        # Basic pole setup
        self.phases = phases if phases is not None else random.choice([1, 2, 3])
        self.pole_collection = bpy.data.collections.get("Poles")
        self.pole_type = (self.pole_collection.objects.get(pole_type)
                         if pole_type else random.choice(self.pole_collection.objects)) if self.pole_collection else None

        # Get collections
        self.framing_collection = bpy.data.collections.get("Framing")
        self.aetx_collection = bpy.data.collections.get("AETX")
        self.fci_collection = bpy.data.collections.get("FCI")
        self.surge_collection = bpy.data.collections.get("SurgeArresters")
        self.conductors_collection = bpy.data.collections.get("Conductors")

        # Initialize component flags
        self.surge_arresters = (surge_arresters if surge_arresters is not None 
                              else random.choice([True, False]))
        
        self.aetx = (aetx if aetx is not None 
                    else (random.choice([True, False]) if self.phases >= 2 else False))
        
        self.ats = (ats if ats is not None 
                   else random.choice([True, False]) if self.aetx else False)
        
        self.fci = (fci if fci is not None 
                   else random.choice([True, False]) if self.phases >= 3 else False)
        
        self.anomaly = (anomaly if anomaly is not None 
                       else random.choice([True, False]))

        # Track objects for rendering
        self.objects_to_render = set()

    @abstractmethod
    def setup_pole(self):
        """Set up the basic pole structure. Must be implemented by subclasses."""
        pass

    def generate_pole(self):
        """Generate the complete pole with all components."""
        try:
            # Reset scene
            reset_scene()
            
            # Basic pole setup
            self.setup_pole()
            
            # Common components
            self.setup_surge_arresters()
            self.setup_aetx()
            self.setup_fci()
            
            # Optional anomalies
            if self.anomaly:
                self.apply_anomalies()
            
            return True
        except Exception as e:
            print(f"Error generating pole: {str(e)}")
            return False

    def setup_surge_arresters(self):
        """Set up surge arresters if enabled."""
        if not (self.surge_arresters and self.surge_collection):
            return
            
        for i in range(self.phases):
            arrester = self.surge_collection.objects.get(f"SurgeArrester{i+1}")
            if arrester:
                toggle_visibility(arrester, True)
                self.objects_to_render.add(arrester)

    def setup_aetx(self):
        """Set up AETX and ATS if enabled."""
        if not (self.aetx and self.aetx_collection):
            return
            
        # Setup AETX
        aetx_obj = self.aetx_collection.objects.get("AETX")
        if aetx_obj:
            toggle_visibility(aetx_obj, True)
            self.objects_to_render.add(aetx_obj)
            
        # Setup ATS if enabled
        if self.ats:
            ats_obj = self.aetx_collection.objects.get("ATS")
            if ats_obj:
                toggle_visibility(ats_obj, True)
                self.objects_to_render.add(ats_obj)

    def setup_fci(self):
        """Set up Fault Circuit Indicators if enabled."""
        if not (self.fci and self.fci_collection):
            return
            
        for i in range(self.phases):
            fci = self.fci_collection.objects.get(f"FCI{i+1}")
            if fci:
                toggle_visibility(fci, True)
                self.objects_to_render.add(fci)

    def apply_anomalies(self):
        """Apply random anomalies to components."""
        if not self.anomaly:
            return
            
        # List of possible anomalies
        anomaly_types = []
        
        # Add AETX anomalies if AETX is present
        if self.aetx:
            anomaly_types.extend(['aetx_rotation', 'aetx_damage'])
            
        # Add FCI anomalies if FCI is present
        if self.fci:
            anomaly_types.extend(['fci_missing', 'fci_damage'])
            
        # Add surge arrester anomalies if present
        if self.surge_arresters:
            anomaly_types.append('surge_damage')
            
        # Apply random anomaly if available
        if anomaly_types:
            anomaly_type = random.choice(anomaly_types)
            self._apply_specific_anomaly(anomaly_type)

    def _apply_specific_anomaly(self, anomaly_type: str):
        """Apply a specific type of anomaly."""
        if anomaly_type == 'aetx_rotation':
            aetx_obj = self.aetx_collection.objects.get("AETX")
            if aetx_obj:
                rotate_object_global(aetx_obj, random.uniform(-0.2, 0.2))
        # Add more anomaly implementations as needed

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about the generated pole."""
        return {
            "pole_type": self.pole_type.name if self.pole_type else None,
            "phases": self.phases,
            "components": {
                "aetx": self.aetx,
                "ats": self.ats,
                "surge_arresters": self.surge_arresters,
                "fci": self.fci
            },
            "anomaly": self.anomaly
        }
