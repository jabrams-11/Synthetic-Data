import bpy
import random
from mathutils import Vector, Color
import numpy as np

class ObjectVariationManager:
    def __init__(self):
        self.material_presets = {
            'metal': {
                'roughness_range': (0.3, 0.8),
                'metallic_range': (0.7, 1.0),
                'color_variation': 0.1
            },
            'wood': {
                'roughness_range': (0.6, 0.9),
                'metallic_range': (0.0, 0.1),
                'color_variation': 0.2
            },
            'plastic': {
                'roughness_range': (0.4, 0.7),
                'metallic_range': (0.0, 0.2),
                'color_variation': 0.15
            }
        }

    def apply_material_variations(self, obj, material_type='metal'):
        if obj.type != 'MESH':
            return

        preset = self.material_presets.get(material_type)
        if not preset:
            return

        for material_slot in obj.material_slots:
            material = material_slot.material
            if material and material.use_nodes:
                principled = material.node_tree.nodes.get('Principled BSDF')
                if principled:
                    # Vary material properties
                    principled.inputs['Roughness'].default_value = random.uniform(*preset['roughness_range'])
                    principled.inputs['Metallic'].default_value = random.uniform(*preset['metallic_range'])
                    
                    # Vary base color slightly
                    base_color = principled.inputs['Base Color'].default_value
                    variation = preset['color_variation']
                    new_color = [
                        max(0, min(1, c + random.uniform(-variation, variation)))
                        for c in base_color[:3]
                    ]
                    principled.inputs['Base Color'].default_value = (*new_color, base_color[3])

    def apply_wear_and_tear(self, obj, intensity=0.5):
        """Add wear and tear effects to object"""
        material = obj.active_material
        if not material or not material.use_nodes:
            return

        nodes = material.node_tree.nodes
        links = material.node_tree.links

        # Add noise texture for wear pattern
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = random.uniform(5, 15)
        noise.inputs['Detail'].default_value = random.uniform(0.3, 0.7)

        # Add color ramp for wear control
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = 0.4
        ramp.color_ramp.elements[1].position = 0.6
        
        # Link nodes
        links.new(noise.outputs['Fac'], ramp.inputs[0])
        
        # Mix with original material
        mix = nodes.new('ShaderNodeMixRGB')
        mix.inputs[0].default_value = intensity
        links.new(ramp.outputs[0], mix.inputs[0])

    def add_surface_damage(self, obj, damage_type='scratches'):
        """Add surface damage like scratches or dents"""
        if damage_type == 'scratches':
            self._add_scratches(obj)
        elif damage_type == 'dents':
            self._add_dents(obj)

    def _add_scratches(self, obj):
        if obj.type != 'MESH':
            return

        # Create scratch texture
        scratch_mat = bpy.data.materials.new(name="Scratch_Layer")
        scratch_mat.use_nodes = True
        nodes = scratch_mat.node_tree.nodes
        
        # Add scratch pattern
        wave = nodes.new('ShaderNodeTexWave')
        wave.wave_type = 'BANDS'
        wave.inputs['Scale'].default_value = random.uniform(50, 100)
        wave.inputs['Distortion'].default_value = random.uniform(0.5, 2.0)

        # Mix with base material
        mix = nodes.new('ShaderNodeMixShader')
        mix.inputs[0].default_value = 0.3

    def _add_dents(self, obj):
        if obj.type != 'MESH':
            return
            
        # Create displacement for dents
        mod = obj.modifiers.new(name="Dents", type='DISPLACE')
        texture = bpy.data.textures.new('DentPattern', type='VORONOI')
        texture.noise_scale = random.uniform(0.5, 2.0)
        texture.intensity = random.uniform(0.1, 0.3)
        mod.texture = texture

    def randomize_object_transform(self, obj, rotation_range=5, scale_range=0.1):
        """Apply random variations to object transform"""
        # Random rotation
        obj.rotation_euler.x += random.uniform(-rotation_range, rotation_range)
        obj.rotation_euler.y += random.uniform(-rotation_range, rotation_range)
        obj.rotation_euler.z += random.uniform(-rotation_range, rotation_range)

        # Random scale variation
        scale_factor = 1 + random.uniform(-scale_range, scale_range)
        obj.scale *= scale_factor 