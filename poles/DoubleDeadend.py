from typing import Optional, Dict, Any
import random
import bpy
from mathutils import Vector

from core.base import PoleBase
from utils.scene_utils import toggle_visibility, toggle_collection_visibility
from utils.wire_generator import create_power_wire
#from generators.anomalies import rotate_object_global

class DoubleDeadend(PoleBase):
    """
    Double Deadend pole configuration with OH disconnect switch
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config, 'DoubleDeadend')
        self.double_deadend_collection = bpy.data.collections.get("DoubleDeadendPole")

    def setup_pole(self):
        toggle_visibility(self.pole_type, True)
        toggle_collection_visibility(self.double_deadend_collection, True)
        wire_collection = self.double_deadend_collection.children.get("SwitchSurgeArresters")
        if wire_collection:
            for child_collection in wire_collection.children:
                empties = [obj for obj in child_collection.objects if obj.type == 'EMPTY']
                if len(empties) == 2:
                    create_power_wire(empties[0], empties[1])
        self._add_neut_framing()
