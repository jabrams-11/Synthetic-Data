import bpy
import random
from mathutils import Vector, Matrix
from createwires import create_power_wire
from typing import Dict, Tuple
from object_variations import ObjectVariationManager

# Utility functions for managing collections and object visibility
def reset_scene():
    # Reset any rotated objects
    RotationTracker.get_instance().reset_rotations()
    
    # Delete wires collection if it exists
    if 'Wires' in bpy.data.collections:
        wires_collection = bpy.data.collections['Wires']
        # First remove all objects in the collection
        for obj in wires_collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
    
    # Only operate on objects that are in the view layer
    for obj in bpy.context.view_layer.objects:
        obj.pass_index = 0
        obj.hide_viewport = True
        obj.hide_render = True
        obj.hide_set(True)

def toggle_visibility(obj, visible):
    if obj:
        print(f"Toggling {obj.name} to {'visible' if visible else 'invisible'}")
        obj.hide_viewport = not visible
        obj.hide_render = not visible
        obj.hide_set(not visible)

def toggle_collection_visibility(collection, visible):
    if collection:
        for obj in collection.objects:
            toggle_visibility(obj, visible)
        for child in collection.children:
            toggle_collection_visibility(child, visible)

def toggle_surge_arrester(phases, has_aetx = False, has_als=False):
    # Get collections with error handling
    Surge_Arrester_Collection = bpy.data.collections.get("SurgeArresters")
    if not Surge_Arrester_Collection:
        print("Warning: SurgeArresters collection not found")
        return
        
    Surge_Arrester_Wires = Surge_Arrester_Collection.children.get("SA_Wires")
    if not Surge_Arrester_Wires:
        print("Warning: SA_Wires collection not found")
        return
    # Handle surge arresters for each phase
    for i in range(1, phases + 1):
        if has_aetx and i == 2:
            continue
        if has_als and i == 3:
            break
        arrester = Surge_Arrester_Collection.objects.get(f"SurgeArrester{i}")
        if arrester:
            toggle_visibility(arrester, True)
            
            # Get and connect wires
            wire_collection = Surge_Arrester_Wires.children.get(f"{i}_SA_Wires")
            toggle_collection_visibility(wire_collection, True)
            if wire_collection and len(wire_collection.objects) >= 2:
                create_power_wire(wire_collection.objects[0], wire_collection.objects[1])
            else:
                print(f"Warning: Wire collection {i}_SA_Wires not found or incomplete")

def create_aetx(pole_config, ats=False, anomaly = False):
    if pole_config == "ModifiedVertical" or pole_config == "Vertical":
        aetx_collection = bpy.data.collections.get("1PhTransformer")
        if aetx_collection:
            toggle_collection_visibility(aetx_collection, True)
            print(f"ats: {ats}")
            if ats:
                toggle_visibility(aetx_collection.objects.get('Fuse.001'), False)
                toggle_visibility(aetx_collection.objects.get('Barrel'), False)
                print(f"ats tiogglin: {ats}")
                Wires = aetx_collection.children.get("ATS_Wires")
                if anomaly:
                    rotate_object_global(aetx_collection.children.get('ATSConfig').objects.get('ATSpart'), 40)
            else:
                toggle_collection_visibility(aetx_collection.children.get('ATSConfig'), False)
                Wires = aetx_collection.children.get("FuseWires")
                if anomaly:
                    rotate_object_global(aetx_collection.objects.get('Barrel'), random.randint(140, 180))
            if Wires:
                for wire_collection in Wires.children:
                    empties = [obj for obj in wire_collection.objects if obj.type == 'EMPTY']
                    if len(empties) == 2:
                        create_power_wire(empties[0], empties[1])

def rotate_object_global(obj, angle_degrees, axis='Y'):
    """Rotate an object around any global axis by the specified angle in degrees
    
    Args:
        obj: The object to rotate
        angle_degrees: Rotation angle in degrees
        axis: 'X', 'Y', or 'Z' axis to rotate around
    """
    import math
    from mathutils import Matrix
    
    # Store original matrix before rotation
    tracker = RotationTracker.get_instance()
    if obj.name not in tracker.rotated_objects:
        tracker.track_rotation(obj, obj.matrix_world.copy())
    
    # Convert degrees to radians
    angle_rad = math.radians(angle_degrees)
    
    # Create rotation matrix for specified global axis
    rot_mat = Matrix.Rotation(angle_rad, 4, axis)
    
    # Get current world matrix
    orig_loc = obj.matrix_world.to_translation()
    
    # Apply rotation while preserving location
    obj.matrix_world = rot_mat @ obj.matrix_world
    obj.matrix_world.translation = orig_loc

# Add after imports, before other functions
class RotationTracker:
    _instance = None
    
    def __init__(self):
        self.rotated_objects: Dict[str, Tuple[object, Matrix, str]] = {}
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = RotationTracker()
        return cls._instance
    
    def track_rotation(self, obj, original_matrix):
        # Store original label if it exists
        original_label = obj.get('label', '')
        print(f"original_label: {original_label}")
        self.rotated_objects[obj.name] = (obj, original_matrix, original_label)
        
        # Update label with _Anomaly suffix
        if original_label:
            obj['label'] = f"{original_label}_Anomaly"
    
    def reset_rotations(self):
        for obj_name, (obj, original_matrix, original_label) in self.rotated_objects.items():
            if obj:
                obj.matrix_world = original_matrix
                if original_label:
                    obj['label'] = original_label
        self.rotated_objects.clear()

# Base class for pole setup
class PoleBase:
    def __init__(self, phases=None, pole_type=None):
        self.phases = phases if phases is not None else random.choice([1, 2, 3])
        self.pole_collection = bpy.data.collections.get("Poles")
        self.pole_type = (self.pole_collection.objects.get(pole_type)
                          if pole_type else random.choice(self.pole_collection.objects)) if self.pole_collection else None

    def reset_scene(self):
        reset_scene()

    def setup_pole(self):
        pass  # To be implemented in subclasses

    def generate_pole(self):
        self.reset_scene()
        self.setup_pole()
        #self.apply_variations()
        
        # Add camera randomization after pole is set up
        if self.pole_type:
            randomize_camera(self.pole_type)

    def apply_variations(self):
        variation_manager = ObjectVariationManager()
        
        # Apply variations to pole
        if self.pole_type:
            variation_manager.apply_material_variations(
                self.pole_type, 
                'metal' if 'Steel' in self.pole_type.name else 'wood'
            )
            
            # Add wear and tear with random intensity
            if random.random() < 0.7:  # 70% chance of wear
                variation_manager.apply_wear_and_tear(
                    self.pole_type, 
                    intensity=random.uniform(0.2, 0.6)
                )
            
            # Add surface damage
            if random.random() < 0.4:  # 40% chance of damage
                damage_type = random.choice(['scratches', 'dents'])
                variation_manager.add_surface_damage(self.pole_type, damage_type)

# Subclasses for specific pole types
class ALSPole(PoleBase):
    def __init__(self, phases=None, pole_type=None, surge_arresters=None, anomaly=None, has_als=False):
        self.framing_collection = bpy.data.collections.get("Modified_Vertical_Framing")
        self.insulator_collections = ["Insulators_Medium", "Insulators_Short"]
        self.supportbracket_collection = bpy.data.collections.get('SupportBrackets')
        self.conductors_collection = bpy.data.collections.get("Conductors")
        #self.insulator_positions_medium = [(,,), (,,), (,,)]
        #self.insulator_positions_short = [(,,), (,,), (,,)]
        #self.insulator_wbracket_positions_medium = [(,,), (,,), (,,)]
        #self.insulator_wbracket_positions_short = [(,,), (,,), (,,)]
        self.conductor_positions_medium = [(34.6691, -2.23303, 44.7747), (34.6691, -8.53448, 33.2859), (34.6691, -8.53528, 24.1912)]
        self.conductor_positions_short = [(34.6691, -2.17132, 44.0459), (34.6691, -7.84183, 33.2859), (34.6691, -7.84471, 24.1912)]
        self.surge_arresters = surge_arresters if surge_arresters is not None else random.choice([True, False])
        self.anomaly = anomaly if anomaly is not None else random.choice([True, False])
        self.has_als = has_als
        print(f"has_als: {has_als}")
        super().__init__(phases if phases is not None else random.choice([2, 3]), pole_type)

    def setup_pole(self):
        if self.pole_collection and self.pole_type:
            toggle_visibility(self.pole_type, True)
  

            top_clamp = self.framing_collection.objects.get("TopClamp") if self.framing_collection else None
            toggle_visibility(top_clamp, self.pole_type.name != "ConcretePole")

        als_collection = bpy.data.collections.get("ALS")
        wire_attachments = bpy.data.collections.get("WireAttatchments")
        if als_collection and wire_attachments:
            toggle_collection_visibility(als_collection, True)
            if self.anomaly:
                rotate_object_global(als_collection.objects.get('ALS'), -55)
        if self.phases > 1:
            self.chickensupportbracket = random.choice([True, False])
        if self.framing_collection and self.conductors_collection:
            selected_collection_name = random.choice(self.insulator_collections)
            selected_collection = self.framing_collection.children.get(selected_collection_name)
            if selected_collection:
                insulators = sorted([obj for obj in selected_collection.objects if obj.name.lower().startswith("insulator")],
                                    key=lambda x: x.name)
                for i, insulator in enumerate(insulators):
                    is_visible = i < self.phases
                    '''
                    if selected_collection_name == "Insulators_Medium":
                        if self.chickensupportbracket:
                            insulator.location = Vector(self.insulator_wbracket_positions_medium[i])
                        else:   
                            insulator.location = Vector(self.insulator_positions_medium[i])
                    elif selected_collection_name == "Insulators_Short":
                        if self.chickensupportbracket:
                            insulator.location = Vector(self.insulator_wbracket_positions_short[i])
                        else:   
                            insulator.location = Vector(self.insulator_positions_short[i])
                    
                    if self.chickensupportbracket and i > 0:
                        supportbracket = self.supportbracket_collection.objects.get(str(i+1))
                        toggle_visibility(supportbracket, is_visible)
                    '''
                    toggle_visibility(insulator, is_visible)
                    conductor = self.conductors_collection.objects.get(str(i + 1))
                    if conductor:
                        toggle_visibility(conductor, is_visible)
                        # Adjust conductor position based on insulator types
                        print('condiuctor moved')
                        if selected_collection_name == "Insulators_Medium":
                            conductor.location = Vector(self.conductor_positions_medium[i])
                        elif selected_collection_name == "Insulators_Short":
                            conductor.location = Vector(self.conductor_positions_short[i])
        if wire_attachments:
            for collection in wire_attachments.children:
                # Get the empty objects from each collection
                empties = [obj for obj in collection.objects if obj.type == 'EMPTY']
                if len(empties) == 2:
                    print('wire created')
                    create_power_wire(empties[0], empties[1])
            if self.surge_arresters:
                toggle_surge_arrester(self.phases, self.has_als)

class ModifiedVertical(PoleBase):
    def __init__(self, phases=None, pole_type=None, surge_arresters=None, aetx=None, ats=None, anomaly=None):
        self.framing_collection = bpy.data.collections.get("Modified_Vertical_Framing")
        self.insulator_collections = ["Insulators_Medium", "Insulators_Short"]
        self.conductors_collection = bpy.data.collections.get("Conductors")
        self.conductor_positions_medium = [(34.6691, -2.23303, 44.7747), (34.6691, -8.53448, 33.2859), (34.6691, -8.53528, 24.1912)]
        self.conductor_positions_short = [(34.6691, -2.17132, 44.0459), (34.6691, -7.84183, 33.2859), (34.6691, -7.84471, 24.1912)]
        self.surge_arresters = surge_arresters if surge_arresters is not None else random.choice([True, False])
        super().__init__(phases, pole_type)
        self.aetx = aetx if aetx is not None else (random.choice([True, False]) if self.phases >= 2 else False)
        self.ats = ats if ats is not None else random.choice([True, False]) if self.aetx else False
        self.anomaly = anomaly if anomaly is not None else random.choice([True, False]) if self.aetx else False

    def setup_pole(self):
        if self.pole_collection and self.pole_type:
            toggle_visibility(self.pole_type, True)
            top_clamp = self.framing_collection.objects.get("TopClamp") if self.framing_collection else None
            toggle_visibility(top_clamp, self.pole_type.name != "ConcretePole")

        if self.framing_collection and self.conductors_collection:
            selected_collection_name = random.choice(self.insulator_collections)
            selected_collection = self.framing_collection.children.get(selected_collection_name)
            if selected_collection:
                insulators = sorted([obj for obj in selected_collection.objects if obj.name.lower().startswith("insulator")],
                                    key=lambda x: x.name)
                for i, insulator in enumerate(insulators):
                    is_visible = i < self.phases
                    '''
                    if selected_collection_name == "Insulators_Medium":
                        if self.chickensupportbracket:
                            insulator.location = Vector(self.insulator_wbracket_positions_medium[i])
                        else:   
                            insulator.location = Vector(self.insulator_positions_medium[i])
                    elif selected_collection_name == "Insulators_Short":
                        if self.chickensupportbracket:
                            insulator.location = Vector(self.insulator_wbracket_positions_short[i])
                        else:   
                            insulator.location = Vector(self.insulator_positions_short[i])
                    '''
                    toggle_visibility(insulator, is_visible)
                    conductor = self.conductors_collection.objects.get(str(i + 1))
                    if conductor:
                        toggle_visibility(conductor, is_visible)
                        # Adjust conductor position based on insulator type
                        if selected_collection_name == "Insulators_Medium":
                            conductor.location = Vector(self.conductor_positions_medium[i])
                        elif selected_collection_name == "Insulators_Short":
                            conductor.location = Vector(self.conductor_positions_short[i])
            
            if self.surge_arresters:
                toggle_surge_arrester(self.phases, self.aetx)
            if self.aetx:
                create_aetx("ModifiedVertical", self.ats, self.anomaly)


class ALSPole2(ALSPole):
    def __init__(self, phases=3, pole_type=None, anomaly=None):
        self.als2x_collection = bpy.data.collections.get("ALS2x")
        self.anomaly_als = anomaly if anomaly is not None else random.choice([True, False])
        if self.anomaly_als:
            # If anomaly is True, randomly decide which ALS parts have anomalies
            anomaly_type = random.choice(['both', 'als1', 'als2'])
            super().__init__(phases, pole_type, anomaly=(anomaly_type in ['both', 'als1']), has_als=True)
            self.anomaly2 = anomaly_type in ['both', 'als2']
        else:
            # If anomaly is False or None, use parent class logic
            super().__init__(phases, pole_type, anomaly=False, has_als=True)
            self.anomaly2 = False

    def setup_pole(self):
        # Run the parent ALSPole setup first (this will handle the first ALS anomaly)
        super().setup_pole()
        
        wire_attachments = self.als2x_collection.children.get("WireAttatchment")
        if self.als2x_collection:
            toggle_collection_visibility(self.als2x_collection, True)
            
            # Add anomaly rotation for ALS2 if needed
            if self.anomaly2:
                rotate_object_global(self.als2x_collection.objects.get('ALS2'), random.randint(50, 60))
            
            if wire_attachments:
                for collection in wire_attachments.children:
                    empties = [obj for obj in collection.objects if obj.type == 'EMPTY']
                    if len(empties) == 2:
                        create_power_wire(empties[0], empties[1])

class VerticalPole(PoleBase):
    def __init__(self, phases=None, pole_type=None, aetx=None, ats=None, anomaly=None):
        self.framing_collection = bpy.data.collections.get("Vertical_Framing")
        self.insulator_collections = ["Insulators_Medium1", "Insulators_Short1"]
        self.supportbracket_collection = self.framing_collection.children.get('SupportBrackets')
        self.conductors_collection = bpy.data.collections.get("Conductors")
        self.insulator_positions_medium = [(-0.740069,-3.94067,39.1149), (-0.740069,-3.94067,30.115), (-0.028575,-3.94067,21.115)]
        self.insulator_positions_short = [(-0.028575,-2.39464,38.1557), (-0.028575,-2.39464,30.115), (-0.028575,-2.39464,21.115)]
        self.insulator_wbracket_positions_medium = [(-0.812422,-5.36507,38.2129), (-0.822692,-5.31377,30.115), (-0.772269,-5.37186,21.115)]
        self.insulator_wbracket_positions_short = [(-0.028575,-3.79048,38.1557), (-0.028575,-3.79048,30.115), (-0.028575,-3.79048,21.115)]
        self.conductor_positions_medium = [(34.1186, -8.54345, 39.5244), (34.6691, -8.53448, 30.5727), (34.8086, -8.53338, 21.5455)]
        self.conductor_positions_medium_wbracket = [(34.1186, -9.99235, 38.727), (34.6691, -9.94244, 30.5727), (34.6691, -9.99287, 21.5455)]
        self.conductor_positions_short = [(34.1186, -7.89351, 38.7011), (34.6691, -7.83458, 30.5727), (34.6691, -7.8928, 21.5455)]
        self.conductor_positions_short_wbracket = [(34.1186, -9.28959, 38.727), (34.6691, -9.67384, 30.5727), (34.6691, -9.25654, 21.5455)]
        super().__init__(phases, pole_type)
        self.aetx = aetx if aetx is not None else (random.choice([True, False]) if self.phases >= 2 else False)
        self.ats = ats if ats is not None else random.choice([True, False]) if self.aetx else False
        self.anomaly = anomaly if anomaly is not None else random.choice([True, False]) if self.aetx else False
    
    def setup_pole(self):
        if self.pole_collection and self.pole_type:
            toggle_visibility(self.pole_type, True)
        if self.pole_type.name != "ConcretePole":
            self.chickensupportbracket = random.choice([True, False])
        else:
            self.chickensupportbracket = False

        if self.framing_collection and self.conductors_collection:
            selected_collection_name = random.choice(self.insulator_collections)
            selected_collection = self.framing_collection.children.get(selected_collection_name)
            if selected_collection:
                insulators = sorted([obj for obj in selected_collection.objects if obj.name.lower().startswith("insulator")],
                                    key=lambda x: x.name)
                for i, insulator in enumerate(insulators):
                    is_visible = i < self.phases
                    if selected_collection_name == "Insulators_Medium1":
                        if self.chickensupportbracket == True:
                            print('insulator w chicken wing')
                            insulator.location = Vector(self.insulator_wbracket_positions_medium[i])
                        else:   
                            insulator.location = Vector(self.insulator_positions_medium[i])
                    elif selected_collection_name == "Insulators_Short1":
                        if self.chickensupportbracket == True:
                            print('insulator w chicken wing')
                            insulator.location = Vector(self.insulator_wbracket_positions_short[i])
                        else:   
                            insulator.location = Vector(self.insulator_positions_short[i])

                    
                    toggle_visibility(insulator, is_visible)

                    if self.chickensupportbracket:
                        supportbracket = self.supportbracket_collection.objects.get(f"{i+1}.001")
                        print('got chicken')
                        toggle_visibility(supportbracket, is_visible)
                    
                    conductor = self.conductors_collection.objects.get(str(i + 1))
                    if conductor:
                        toggle_visibility(conductor, is_visible)
                        # Adjust conductor position based on insulator type
                        if selected_collection_name == "Insulators_Medium1":
                            if self.chickensupportbracket:
                                conductor.location = Vector(self.conductor_positions_medium_wbracket[i])
                            else:
                                conductor.location = Vector(self.conductor_positions_medium[i])
                        elif selected_collection_name == "Insulators_Short1":
                            if self.chickensupportbracket:
                                conductor.location = Vector(self.conductor_positions_short_wbracket[i])
                            else:
                                conductor.location = Vector(self.conductor_positions_short[i])
                    
                if self.aetx:
                    create_aetx("Vertical", self.ats, self.anomaly) 
    

class DeadendPole(PoleBase):
    def __init__(self, phases=None, pole_type=None):
        self.framing_collection = bpy.data.collections.get("DeadendFraming")
        self.insulator_collections = ["Framing"]
        self.conductors_collection = self.framing_collection.children.get("Conductors.001")
        self.guy_collection = self.framing_collection.children.get("Guys")
        super().__init__(phases, pole_type)

    def setup_pole(self):
        if self.pole_collection and self.pole_type:
            toggle_visibility(self.pole_type, True)

        if self.framing_collection and self.conductors_collection:
            selected_collection_name = random.choice(self.insulator_collections)
            selected_collection = self.framing_collection.children.get(selected_collection_name)
            print('search9ng')
            if selected_collection:
                print('found)')
                toggle_visibility(self.guy_collection.objects.get('Guy1'), True)
                toggle_visibility(self.guy_collection.objects.get('Guy2'), True)
                insulators = sorted([obj for obj in selected_collection.objects if obj.name.lower().startswith("deinsulator")],
                                    key=lambda x: x.name)
                for i, insulator in enumerate(insulators):
                    is_visible = i < self.phases
                    '''
                    if selected_collection_name == "Insulators_Medium":
                        if self.chickensupportbracket:
                            insulator.location = Vector(self.insulator_wbracket_positions_medium[i])
                        else:   
                            insulator.location = Vector(self.insulator_positions_medium[i])
                    elif selected_collection_name == "Insulators_Short":
                        if self.chickensupportbracket:
                            insulator.location = Vector(self.insulator_wbracket_positions_short[i])
                        else:   
                            insulator.location = Vector(self.insulator_positions_short[i])
                    '''
                    toggle_visibility(insulator, is_visible)
                    
                    conductor = self.conductors_collection.objects.get(f"{i+1}.002")
                    if conductor:
                        toggle_visibility(conductor, is_visible)



class CrossarmPole(PoleBase):
    def __init__(self, phases=None, pole_type=None, crossarm_type=None):
        # Call parent constructor first
        super().__init__(phases, pole_type)
        
        self.framing_collection = bpy.data.collections.get("CrossarmFraming")
        self.insulator_collections = ["Insulators"]
        self.crossarm_collection = self.framing_collection.children.get('Framings')
        self.conductors_collection = self.framing_collection.children.get("Conductor")
        
        # Move crossarm logic after super() call to use the properly initialized pole_type
        if crossarm_type:
            self.crossarm_type = self.crossarm_collection.objects.get(crossarm_type)
        else:
            if self.pole_type and self.pole_type.name == "ConcretePole":
                self.crossarm_type = self.crossarm_collection.objects.get("Steel")
            elif self.pole_type and self.pole_type.name == "WoodPole":
                self.crossarm_type = self.crossarm_collection.objects.get("Wood")
            else:
                self.crossarm_type = None

    def setup_pole(self):
        if self.pole_collection and self.pole_type:
            toggle_visibility(self.pole_type, True)
            toggle_visibility(self.crossarm_type, True)

        if self.framing_collection and self.conductors_collection:
            selected_collection_name = random.choice(self.insulator_collections)
            selected_collection = self.framing_collection.children.get(selected_collection_name)
            if selected_collection:
                insulators = sorted([obj for obj in selected_collection.objects if obj.name.lower().startswith("insulator")],
                                    key=lambda x: x.name)
                for i, insulator in enumerate(insulators):
                    is_visible = i < self.phases
                    '''
                    if selected_collection_name == "Insulators_Medium":
                        if self.chickensupportbracket:
                            insulator.location = Vector(self.insulator_wbracket_positions_medium[i])
                        else:   
                            insulator.location = Vector(self.insulator_positions_medium[i])
                    elif selected_collection_name == "Insulators_Short":
                        if self.chickensupportbracket:
                            insulator.location = Vector(self.insulator_wbracket_positions_short[i])
                        else:   
                            insulator.location = Vector(self.insulator_positions_short[i])
                    '''
                    toggle_visibility(insulator, is_visible)
                    
                    conductor = self.conductors_collection.objects.get(f"{i+1}.003")
                    if conductor:
                        toggle_visibility(conductor, is_visible)
                        # Adjust conductor position based on insulator type

                    if self.crossarm_type.name == "Wood":
                        toggle_visibility(self.framing_collection.objects.get('WoodSupport1'), True)
                        toggle_visibility(self.framing_collection.objects.get('WoodSupport2'), True)


class ALS_Fuse_Crossarm(ModifiedVertical):
    def __init__(self, phases=None, pole_type=None, fuse_type=None, anomaly=None):
        phases = random.choice([2, 3]) if phases is None else phases
        # Call parent constructor with aetx=False to prevent transformer spawning
        super().__init__(phases, pole_type, 
                        surge_arresters=False,
                        aetx=False,  # Force transformer off
                        ats=False,   # Force ATS off
                        anomaly=False)  # No transformer anomalies
        
        self.ALS_Fuse_Crossarm_Collection = bpy.data.collections.get("ALS_Fuse_Crossarm")
        self.fuse_collection = self.ALS_Fuse_Crossarm_Collection.children.get("Framings.001")
        self.Fuse_Wires = self.ALS_Fuse_Crossarm_Collection.children.get("WireAttatches")
        self.BarrelFuses = self.ALS_Fuse_Crossarm_Collection.children.get("CrossarmFuses")
        self.fuse_type = fuse_type if fuse_type is not None else random.choice(['ALS', 'Barrel'])
        self.anomaly = anomaly if anomaly is not None else random.choice([True, False])
        # Handle anomalies for the three ALS parts
        if anomaly:
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

    def setup_pole(self):
        # Run the parent setup first
        super().setup_pole()
        
        if self.pole_type.name == "WoodPole":
            toggle_visibility(self.fuse_collection.objects.get('WoodSupports1'), True)
            toggle_visibility(self.fuse_collection.objects.get('WoodSupports2'), True)
            toggle_visibility(self.fuse_collection.objects.get('WoodxArm'), True)
        else:
            toggle_visibility(self.fuse_collection.objects.get('SteelXArm'), True)
        
        # Show appropriate phase collections based on number of phases
        if self.phases == 3:
            wire_collections = ['ALS_Fuse_Crossarm_Wire1', 'ALS_Fuse_Crossarm_Wire2', 'ALS_Fuse_Crossarm_Wire3']
            
            if self.fuse_type == 'ALS':
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
            
            if self.fuse_type == 'ALS':
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

class ALS_Fuse_Crossarm_2(CrossarmPole):
    def __init__(self, phases=None, pole_type=None, fuse_type=None, anomaly=None):
        phases = random.choice([2, 3]) if phases is None else phases
        # Call parent constructor with aetx=False to prevent transformer spawning
        super().__init__(phases, pole_type)  # No transformer anomalies
        
        self.ALS_Fuse_Crossarm_Collection = bpy.data.collections.get("ALS_Fuse_Crossarm")
        self.fuse_collection = self.ALS_Fuse_Crossarm_Collection.children.get("Framings.001")
        self.Fuse_Wires = self.ALS_Fuse_Crossarm_Collection.children.get("WireAttatchesForCrossArm")
        self.BarrelFuses = self.ALS_Fuse_Crossarm_Collection.children.get("CrossarmFuses")
        self.fuse_type = fuse_type if fuse_type is not None else random.choice(['ALS', 'Barrel'])
        self.anomaly = anomaly if anomaly is not None else random.choice([True, False])
        # Handle anomalies for the three ALS parts
        if anomaly:
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

    def setup_pole(self):
        # Run the parent setup first
        super().setup_pole()
        
        if self.pole_type.name == "WoodPole":
            toggle_visibility(self.fuse_collection.objects.get('WoodSupports1'), True)
            toggle_visibility(self.fuse_collection.objects.get('WoodSupports2'), True)
            toggle_visibility(self.fuse_collection.objects.get('WoodxArm'), True)
        else:
            toggle_visibility(self.fuse_collection.objects.get('SteelXArm'), True)
        
        # Show appropriate phase collections based on number of phases
        if self.phases == 3:
            wire_collections = ['ALS_Fuse_Crossarm_Wire1.001', 'ALS_Fuse_Crossarm_Wire2.001', 'ALS_Fuse_Crossarm_Wire3.001']
            
            if self.fuse_type == 'ALS':
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
            
            if self.fuse_type == 'ALS':
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
        
        # Create power wires
        if self.Fuse_Wires:
            for wire_name in wire_collections:
                collection = self.Fuse_Wires.children.get(wire_name)
                if collection:
                    toggle_collection_visibility(collection, True)
                    empties = [obj for obj in collection.objects if obj.type == 'EMPTY']
                    if len(empties) == 2:
                        create_power_wire(empties[0], empties[1])

class ThreePH_AETX_Pole(ModifiedVertical):
    def __init__(self, phases=None, pole_type=None, anomaly=None):
        super().__init__(phases=3, pole_type='ConcretePole', aetx=False, ats=False, anomaly=False)
        self.transformers_collection = bpy.data.collections.get("3PhTransformer")
        self.anomaly = anomaly if anomaly is not None else random.choice([True, False])
        if anomaly:
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


    def setup_pole(self):
        toggle_collection_visibility(self.transformers_collection, True)
        super().setup_pole()
        wire_collection = self.transformers_collection.children.get("WireAttatchesTx")
        if wire_collection:
            for child_collection in wire_collection.children:
                empties = [obj for obj in child_collection.objects if obj.type == 'EMPTY']
                if len(empties) == 2:
                    create_power_wire(empties[0], empties[1])
  
        for i in range(1, self.phases + 1):
            if i in self.anomaly_parts:
                print(self.transformers_collection)
                for child in self.transformers_collection.children:
                    print(f"Child collection: {child.name}")
                fuse_switch = self.transformers_collection.children.get(f'3PhTransformer{i}').objects.get(f'BarrelAetx{i}')
                if fuse_switch:
                    print(f'BarrelAetx{i} found')
                    if i == 1:
                        rotate_object_global(fuse_switch, random.randint(140, 170), 'Y')
                    elif i == 2:
                        rotate_object_global(fuse_switch, random.randint(-170, -140), 'Y')
                    elif i == 3:
                        rotate_object_global(fuse_switch, random.randint(140, 170), 'X')


def randomize_camera(pole_obj, min_distance=50, max_distance=400):
    """
    Randomize camera position and orientation to look at the ViewPart empty,
    with varied perspectives including ground-level and upward angles.
    
    Args:
        pole_obj: The pole object (used for reference)
        min_distance: Minimum distance from view target (default: 20)
        max_distance: Maximum distance from view target (default: 35)
    """
    import math
    import random
    
    # Get the scene and camera
    scene = bpy.context.scene
    camera = bpy.data.objects.get('Camera')
    view_target = bpy.data.objects.get('ViewPart')
    
    if not camera or not view_target:
        print("Warning: Camera or ViewPart empty not found in scene")
        return None
    
    # Make camera the active camera
    scene.camera = camera
    
    # Get view target position
    target_pos = view_target.location
    
    # Random spherical coordinates with better constraints
    distance = random.uniform(min_distance, max_distance)
    
    # Restrict azimuth to front 180 degrees (facing pole)
    azimuth = random.uniform(-math.pi/2, math.pi/2)
    
    # Choose camera angle style randomly
    angle_style = random.choice(['low', 'eye_level', 'high'])
    
    if angle_style == 'low':
        # Looking up at pole (10 to 30 degrees below horizontal)
        elevation = random.uniform(-math.pi/18, -math.pi/6)
    elif angle_style == 'eye_level':
        # Near horizontal view (±15 degrees from horizontal)
        elevation = random.uniform(-math.pi/12, math.pi/12)
    else:  # high
        # Looking down at pole (15 to 45 degrees above horizontal)
        elevation = random.uniform(math.pi/12, math.pi/4)
    
    # Convert spherical to Cartesian coordinates
    x = target_pos.x + (distance * math.cos(azimuth) * math.cos(elevation))
    y = target_pos.y + (distance * math.sin(azimuth) * math.cos(elevation))
    z = target_pos.z + (distance * math.sin(elevation))
    
    # Ensure minimum height from ground (adjust as needed)
    min_height = 2.0  # minimum 2 units from ground
    if z < min_height:
        z = min_height
    
    # Position camera
    camera.location = (x, y, z)
    
    # Point camera at view target
    direction = target_pos - camera.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    camera.rotation_euler = rot_quat.to_euler()
    
    # Add subtle random rotation variation
    camera.rotation_euler.z += random.uniform(-0.05, 0.05)
    
    
    return camera