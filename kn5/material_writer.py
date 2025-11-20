# Copyright (C) 2014  Thomas Hagnhofer
# edited by leBluem

import numbers
import os
import re
from exporter_utils import (
    get_active_material_texture_slot,
    get_texture_nodes,
)
from kn5_writer import KN5Writer

MATERIALS  = "materials"
PROPERTIES = "properties"
TEXTURES   = "textures"

MATERIAL_BLEND_MODE = {
    "Opaque" : 0,
    "AlphaBlend" : 1,
    "AlphaToCoverage" : 2,
}

MATERIAL_DEPTH_MODE = {
    "DepthNormal" : 0,
    "DepthNoWrite" : 1,
    "DepthOff" : 2,
}

class MaterialWriter(KN5Writer):
    def __init__(self, file, context, settings, warnings):
        super().__init__(file)

        self.selected_obj = context.selected_objects.copy()
        self.available_materials = {}
        self.material_positions = {}
        self.material_settings = []
        self.context = context
        self.settings = settings
        self.warnings = warnings
        self._fill_available_materials()

    def write(self):
        self.write_int(len(self.available_materials))
        for material_name, _position in sorted(self.material_positions.items(), key=lambda k: k[1]):
            material = self.available_materials[material_name]
            self._write_material(material)

    def _write_material(self, material):
        self.write_string(material.name)
        self.write_string(material.shaderName)
        self.write_byte(material.alphaBlendMode)
        self.write_bool(material.alphaTested)
        self.write_int(material.depthMode)
        self.write_uint(len(material.shaderProperties))
        for property_name in material.shaderProperties:
            self._write_material_property(material.shaderProperties[property_name])
        self.write_uint(len(material.texture_mapping))
        texture_slot = 0
        for mapping_name in material.texture_mapping:
            self.write_string(mapping_name)
            self.write_uint(texture_slot)
            self.write_string(material.texture_mapping[mapping_name])
            texture_slot += 1

    def _write_material_property(self, prop):
        self.write_string(prop.name)
        self.write_float(prop.valueA)
        self.write_vector2(prop.valueB)
        self.write_vector3(prop.valueC)
        self.write_vector4(prop.valueD)

    def _fill_available_materials(self):
        self.available_materials = {}
        self.material_positions = {}
        self.material_settings = []
        print('getting materials from objects')
        if MATERIALS in self.settings:
            for material_key in self.settings[MATERIALS]:
                self.material_settings.append(MaterialSettings(self.settings, self.warnings, material_key))
        position = 0
        print('mats from json: ' + str(len(self.material_settings)))

        mats = []
        matsNames = []
        for obj in self.selected_obj:
            if len(obj.material_slots)>1:
                print('  ! using more than 1 mat : ' + obj.name)
            for s in obj.material_slots:
                if s.material and s.material.use_nodes and not s.material.name in matsNames:
                    mats.append(s.material)
                    matsNames.append(s.material.name)

        print('materials from selected objs: ' + str(len(matsNames)))

        # for material in self.context.blend_data.materials:
        for material in mats:
            if material.users == 0:
                self.warnings.append(f"Ignoring unused material '{material.name}'")
            else:   ### if not material.name.startswith("__"):
                if not get_active_material_texture_slot(material):
                    warning_message = f"'{material.name}' : no active texture for material found. Using default UV scaling for objects without UV maps."
                    self.warnings.append(warning_message)
                # else:
                #     print(material.name)

                material_properties = MaterialProperties(material)
                for setting in self.material_settings:
                    setting.apply_settings_to_material(material_properties)
                self.available_materials[material.name] = material_properties
                self.material_positions[material.name] = position
                position += 1


class ShaderProperty:
    def __init__(self, name):
        self.name = name
        self.valueA = 0.0
        self.valueB = (0.0, 0.0)
        self.valueC = (0.0, 0.0, 0.0)
        self.valueD = (0.0, 0.0, 0.0, 0.0)

    def fill(self, prop):
        self.valueA = prop.valueA
        self.valueB = prop.valueB
        self.valueC = prop.valueC
        self.valueD = prop.valueD


class MaterialProperties:
    def __init__(self, material):
        self.name = material.name
        # ac_mat = material.assettoCorsa
        self.shaderName = 'ksPerPixel' ### ac_mat.shaderName
        self.alphaBlendMode = 0 ### int(ac_mat.alphaBlendMode)
        self.alphaTested = False ### ac_mat.alphaTested
        self.depthMode = 0 ###int(ac_mat.depthMode)
        self.shaderProperties = self.copy_shader_properties(material)
        self.texture_mapping = self._generate_texture_mapping(material)

    def copy_shader_properties(self, material):
        # ac_mat = material.assettoCorsa
        properties = {}
        ### for shader_property in ac_mat.shaderProperties:
        for shader_property in ["ksAmbient","ksDiffuse","ksSpecular","ksSpecularEXP","ksEmissive","ksAlphaRef"]:
            ### new_property = ShaderProperty(shader_property.name) ### now all default at 0.0
            new_property = ShaderProperty(shader_property) ### now all default at 0.0
            properties[shader_property] = new_property
        return properties

    def _generate_texture_mapping(self, material):
        mapping = {}
        texture_nodes = get_texture_nodes(material)
        for texture_node in texture_nodes:
            ### shader_input = texture_node.assettoCorsa.shaderInputName
            shader_input = 'txDiffuse'
            mapping[shader_input] = texture_node.image.name
        return mapping


class MaterialSettings:
    def __init__(self, settings, warnings, material_settings_key):
        self.settings = settings
        self.warnings = warnings
        self.material_settings_key = material_settings_key
        self.material_name_matches = self._convert_to_matches_list(material_settings_key)

    def apply_settings_to_material(self, material):
        if not self._does_material_name_match(material.name):
            return
        shader_name = self._get_material_shader()
        if shader_name:
            material.shaderName = shader_name

        alpha_blend_mode = self._get_material_blend_mode()
        if alpha_blend_mode:
            material.alphaBlendMode = alpha_blend_mode
        alpha_tested = self._get_material_alpha_tested()
        if alpha_tested:
            material.alphaTested = alpha_tested
        depth_mode = self._get_material_depth_mode()
        if depth_mode:
            material.depthMode = depth_mode

        property_names = self._get_material_property_names()
        if property_names:
            material.shaderProperties.clear()
        for property_name in property_names:
            shader_property = None
            if property_name in material.shaderProperties:
                shader_property = material.shaderProperties[property_name]
            else:
                shader_property = ShaderProperty(property_name)
                material.shaderProperties[property_name] = shader_property
            value_a = self._get_material_property_value_a(property_name)
            if value_a:
                shader_property.valueA = value_a
            value_b = self._get_material_property_value_b(property_name)
            if value_b:
                shader_property.valueB = value_b
            value_c = self._get_material_property_value_c(property_name)
            if value_c:
                shader_property.valueC = value_c
            value_d = self._get_material_property_value_d(property_name)
            if value_d:
                shader_property.valueD = value_d

        texture_mapping_names = self._get_material_texture_mapping_names()
        if texture_mapping_names:
            material.texture_mapping.clear()

        for texture_mapping_name in texture_mapping_names:
            texture_name = self._get_material_texture_mapping_name(texture_mapping_name)
            if not texture_name:
                msg = f"Ignoring texture mapping '{texture_name}' for material '{material.name}' without texture name"
                self.warnings.append(msg)
            else:
                material.texture_mapping[texture_mapping_name] = texture_name

    def _does_material_name_match(self, material_name):
        for regex in self.material_name_matches:
            if regex.match(material_name):
                return True
        return False

    def _convert_to_matches_list(self, key):
        matches = []
        for subkey in key.split("|"):
            matches.append(re.compile(f"^{self._escape_match_key(subkey)}$", re.IGNORECASE))
        return matches

    def _escape_match_key(self, key):
        wildcard_replacement = "__WILDCARD__"
        key = key.replace("*", wildcard_replacement)
        key = re.escape(key)
        key = key.replace(wildcard_replacement, ".*")
        return key

    def _get_material_shader(self):
        if "shaderName" in self.settings[MATERIALS][self.material_settings_key]:
            return self.settings[MATERIALS][self.material_settings_key]["shaderName"]
        return None

    def _get_material_blend_mode(self):
        if "alphaBlendMode" in self.settings[MATERIALS][self.material_settings_key]:
            return MATERIAL_BLEND_MODE[self.settings[MATERIALS][self.material_settings_key]["alphaBlendMode"]]
        return None

    def _get_material_depth_mode(self):
        if "depthMode" in self.settings[MATERIALS][self.material_settings_key]:
            return MATERIAL_DEPTH_MODE[self.settings[MATERIALS][self.material_settings_key]["depthMode"]]
        return None

    def _get_material_alpha_tested(self):
        if "alphaTested" in self.settings[MATERIALS][self.material_settings_key]:
            return self.settings[MATERIALS][self.material_settings_key]["alphaTested"]
        return None

    def _get_material_property_names(self):
        if PROPERTIES in self.settings[MATERIALS][self.material_settings_key]:
            return self.settings[MATERIALS][self.material_settings_key][PROPERTIES]
        return []

    def _get_material_property_value(self, property_name, value_name):
        if value_name in self.settings[MATERIALS][self.material_settings_key][PROPERTIES][property_name]:
            return self.settings[MATERIALS][self.material_settings_key][PROPERTIES][property_name][value_name]
        return None

    def _get_material_texture_mapping_names(self):
        if TEXTURES in self.settings[MATERIALS][self.material_settings_key]:
            return self.settings[MATERIALS][self.material_settings_key][TEXTURES]
        return []

    def _get_material_texture_mapping_name(self, mapping_name):
        if TEXTURES in self.settings[MATERIALS][self.material_settings_key]:
            return self.settings[MATERIALS][self.material_settings_key][TEXTURES][mapping_name]["textureName"]
        return None

    def _get_material_property_value_a(self, property_name):
        value_a = self._get_material_property_value(property_name, "valueA")
        if value_a is None:
            return None
        if not isinstance(value_a, numbers.Number):
            raise Exception("valueA must be a float")
        return value_a

    def _get_material_property_value_b(self, property_name):
        value_b = self._get_material_property_value(property_name, "valueB")
        if value_b is None:
            return None
        if not self._is_list_of_numbers_valid(value_b, 2):
            raise Exception("valueB must be a list of two floats")
        return value_b

    def _get_material_property_value_c(self, property_name):
        value_c = self._get_material_property_value(property_name, "valueC")
        if value_c is None:
            return None
        if not self._is_list_of_numbers_valid(value_c, 3):
            raise Exception("valueC must be a list of three floats")
        return value_c

    def _get_material_property_value_d(self, property_name):
        value_d = self._get_material_property_value(property_name, "valueD")
        if value_d is None:
            return None
        if not self._is_list_of_numbers_valid(value_d, 4):
            raise Exception("valueD must be a list of four floats")
        return value_d

    @staticmethod
    def _is_list_of_numbers_valid(number_list, count):
        if not (not hasattr(number_list, "strip")
                and (hasattr(number_list, "__getitem__") or hasattr(number_list, "__iter__"))):
            return False
        elif len(number_list) != count:
            return False
        return all([isinstance(x, numbers.Number) for x in number_list])
