# Copyright (C) 2014  Thomas Hagnhofer
# edited by leBluem

import json
import os
import configparser
import bpy, math
from mathutils import Matrix, Quaternion, Vector


def convert_matrix(in_matrix):
    co, rotation, scale = in_matrix.decompose()
    co = convert_vector3(co)
    rotation = convert_quaternion(rotation)
    mat_loc = Matrix.Translation(co)
    #mat_loc_new = [ mat_loc[0], mat_loc[2], -mat_loc[1] ]

    mat_scale_1 = Matrix.Scale(scale[0] , 4, (1, 0, 0))
    mat_scale_2 = Matrix.Scale(scale[2] , 4, (0, 1, 0))
    mat_scale_3 = Matrix.Scale(scale[1] , 4, (0, 0, 1))
    mat_scale = mat_scale_1 @ mat_scale_2 @ mat_scale_3

    #halfrotmat = mathutils.Matrix.Rotation(math.pi,4,'X')
    #rotation = rotation @ halfrotmat

    #transform_matrix = Matrix()
    #if obj.parent:
    #    transform_matrix = convert_matrix(obj.parent.matrix_world.inverted())
    #else:
    #    #transform_matrix = convert_matrix(obj.matrix_world)
    #    transform_matrix = convert_matrix(obj.location)

    #p = list(obj.location)
    #position = [p[0], p[2], -p[1]]
    #node_data["transform"] = transform_matrix

    #return mat_loc_new @ mat_rot @ mat_scale

    mat_rot = rotation.to_matrix().to_4x4()
    return mat_loc @ mat_rot @ mat_scale


def convert_vector3(in_vec):
    # return Vector((in_vec[0]*100, in_vec[2]*100, -in_vec[1]*100))
    return Vector((in_vec[0], in_vec[2], -in_vec[1]))

def convert_vector3_normal(in_vec):
    ### return Vector((in_vec[0]*100, in_vec[2]*100, -in_vec[1]*100))
    return Vector((in_vec[0], in_vec[1], in_vec[2]))


def convert_quaternion(in_quat):
    axis, angle = in_quat.to_axis_angle()
    axis = convert_vector3(axis)
    return Quaternion(axis, angle)


def get_texture_nodes(material):
    texture_nodes = []
    if material.node_tree:
        for node in material.node_tree.nodes:
            if node.type == 'TEX_IMAGE':
                texture_nodes.append(node)
            #if isinstance(node, bpy.types.ShaderNodeTexImage):
            #    if os.path.isfile(node.image.filepath):
            #       texture_nodes.append(node)
    return texture_nodes


def get_all_texture_nodes(objects):
    scene_texture_nodes = []
    for obj in objects:
        if obj.type != "MESH":
            continue
        for slot in obj.material_slots:
            if slot.material:
                scene_texture_nodes.extend(get_texture_nodes(slot.material))
    return scene_texture_nodes


def get_active_material_texture_slot(material):
    texture_nodes = get_texture_nodes(material)
    for texture_node in texture_nodes:
        #if texture_node.show_texture:
        return texture_node
    return None


def check_settings_for_obj(filen, obj, objdata, fbxini):
    sectname = 'model_FBX: ' + filen + '_' + obj
    if not fbxini.has_section(sectname):
        print('adding: ' + obj + ' | ' + sectname)
        fbxini.add_section(sectname)
        fbxini.set(sectname   , 'ACTIVE', str(1) )
        fbxini.set(sectname   , 'PRIORITY', str(0) )

    sectname1 = 'model_FBX: ' + filen + '_' + obj + '_' + obj      ### objdata
    if not fbxini.has_section(sectname1):
        print('adding: ' + obj + ' | ' + sectname1)
        fbxini.add_section(sectname1)
        # set some default values
        fbxini.set(sectname1  , 'ACTIVE', str(1) )
        fbxini.set(sectname1  , 'PRIORITY', str(0) )
        fbxini.set(sectname1  , 'VISIBLE', str(1) )
        fbxini.set(sectname1  , 'TRANSPARENT', str(0) )
        fbxini.set(sectname1  , 'CAST_SHADOWS', str(1) )
        fbxini.set(sectname1  , 'LOD_IN', str(0) )
        fbxini.set(sectname1  , 'LOD_OUT', str(1222) )
        fbxini.set(sectname1  , 'RENDERABLE', str(1) )


def read_settings(context, file, basename):
    full_path = os.path.abspath(file)
    dir_name = os.path.dirname(full_path)

    # read from "settings.json"
    settings_path = os.path.join(dir_name, "settings.json")
    if os.path.exists(settings_path):
        print('reading JSON ' + settings_path)
        return json.loads(open(settings_path, "r").read())
    else:
        settings_path = os.path.join(dir_name, basename + ".json")
        if os.path.exists(settings_path):
            print('reading JSON ' + settings_path)
            return json.loads(open(settings_path, "r").read())
        else:
            # read from ".fbx.ini"
            # convert to "....json" in the process
            settings_path = os.path.join(dir_name, basename + '.fbx.ini')
            jsonFile = settings_path.lower().replace('.ini', '.json')
            if os.path.exists(settings_path):
                print('reading INI ' + settings_path)
                config = configparser.ConfigParser(empty_lines_in_values=False, strict=False, allow_no_value=True, inline_comment_prefixes=(";","#","/","_"), comment_prefixes=(";","#","/","_"))
                config.optionxform=str # keep upper/lower case
                config.read(settings_path)

                # check for missing nodes in INI
                selected_obj = context.selected_objects.copy()
                for obj in selected_obj:
                    check_settings_for_obj(basename + '.fbx', obj.name, obj.data.name, config)

                with open(settings_path.lower().replace('.ini', '_converted.ini'), 'w') as configfile:
                    config.write(configfile, space_around_delimiters=False)

                print('converting to JSON ')
                sJSON = convert_ini_to_json(config)

                # if not os.path.exists(jsonFile) or os.path.getmtime(jsonFile) < os.path.getmtime(settings_path):
                # not overwriting existing, this might bite me in the ass later
                # edit: 2 month later... it did! but only shortly
                print('writing to JSON ' + jsonFile)
                with open(jsonFile, 'w') as f:
                    #f.write( str(convert_ini_to_json(fbxini)) )
                    for s in sJSON:
                        f.write(s)
                print('JSON written : ' + jsonFile)

                return json.loads( sJSON )
            else:
                print('"settings.json" not found, neither ' + settings_path)
                return {}


def convert_ini_to_json(config):
    matsDone=False
    prefix = ''
    result = []
    iMat = 0
    iTex = 0
    iObj = 0

    result.append('{')
    result.append('    "materials": {')

    for section in config.sections():
        if 'MATERIAL_' in section and section != 'MATERIAL_LIST':
            iMat += 1
            # open material
            result.append('        "' + config[section]['NAME'] + '": {')

            #"Opaque", "AlphaBlend" or "AlphaToCoverage"
            if config.get(section,  'ALPHABLEND') == '1':
                result.append('            "alphaBlendMode": "AlphaBlend",')
                result.append('            "alphaTested": false,')
            elif config.get(section,'ALPHATEST')  == '1':
                result.append('            "alphaBlendMode": "AlphaToCoverage",')
                result.append('            "alphaTested": true,')
            else:
                result.append('            "alphaBlendMode": "Opaque",')
                result.append('            "alphaTested": false,')

            #"DepthNormal", "DepthNoWrite", "DepthOff"
            if config.get(  section,'DEPTHMODE') == '0':
                result.append('            "depthMode": "DepthNormal",')
            elif config.get(section,'DEPTHMODE') == '1':
                result.append('            "depthMode": "DepthNoWrite",')
            elif config.get(section,'DEPTHMODE') == '2':
                result.append('            "depthMode": "DepthOff",')

            # open vars
            result.append('            "properties": {')
            varc = int(config.get(section,'VARCOUNT'))
            for v in range(varc):
                sv = 'VAR_' + str(v) + '_'
                result.append('                "' + config.get(section, sv+'NAME')+ '": { ')
                result.append('                    "valueA": '  + config.get(section, sv+'FLOAT1') + ',')
                result.append('                    "valueB": [' + config.get(section, sv+'FLOAT2') + '],')
                result.append('                    "valueC": [' + config.get(section, sv+'FLOAT3') + '],')
                result.append('                    "valueD": [' + config.get(section, sv+'FLOAT4') + ']' )
                result.append('                },')
            # close vars
            result[len(result)-1] = '                }'
            result.append('            },')
            result.append('            "shaderName": "' + config[section]['SHADER'] + '",')

            # open res/textures
            varc = int(config.get(section,'RESCOUNT'))
            if varc > 0:
                iTex += varc
                result.append('            "textures": {')
                for v in range(varc):
                    sv = 'RES_' + str(v) + '_'
                    result.append('                "' + config.get(section, sv+'NAME') + '": { ')   # "txDiffuse": {
                    result.append('                    "slot": ' + config.get(section, sv+'SLOT') + ', ')
                    result.append('                    "textureName": "' + config.get(section, sv+'TEXTURE') + '" ')
                    result.append('                },')
                result[len(result)-1] = '                }'
                # close res
                result.append('            }')
            # close material
            result.append('        },\n')

        elif 'model_FBX' in section:
            if not matsDone:
                result[len(result)-1] = '        }'
                result.append('    },\n')
                result.append('    "nodes": {')
                prefix = section
            matsDone=True

            if len(config.items(section))>3:
                nodename = section.replace(prefix+'_','')  # nodename
                nodename = nodename[:int(len(nodename)/2)]
                result.append( '        "' + nodename +'": {')
                v = str(config.getboolean(section, 'CAST_SHADOWS')).lower()
                result.append('            "castShadows": ' + v + ',')
                v = str(config.getboolean(section, 'RENDERABLE')).lower()
                result.append('            "isRenderable": ' + v + ',')
                v = str(config.getboolean(section, 'TRANSPARENT')).lower()
                result.append('            "isTransparent": ' + v + ',')
                v = str(config.getboolean(section, 'VISIBLE')).lower()
                result.append('            "isVisible": ' + v + ',')
                v = str(int(config.getfloat(section, 'PRIORITY')))
                result.append('            "layer": ' + v + ',')
                v = str(config.getfloat(section, 'LOD_IN'))
                result.append('            "lodIn": ' + v + ',')
                v = str(config.getfloat(section, 'LOD_OUT'))
                result.append('            "lodOut": ' + v + '')
                # close node
                result.append('        },\n')
                iObj += 1
            else:
                nodename = section.replace(prefix+'_','')  # nodename
                #nodename = nodename[:int(len(nodename)/2)]
                #  result.append( '        "' + nodename +'": {')
                #  v = str(config.getboolean(section, 'ACTIVE')).lower()
                #  result.append('            "active": ' + v + ',')
                #  v = str(int(config.getfloat(section, 'PRIORITY')))
                #  result.append('            "priority": ' + v + '')
                #  # close node
                #  result.append('        },\n')
                iObj += 1


    result[len(result)-1] = '        }\n'
    result.append('    }\n')
    result.append('}\n')
    print('materials: ' + str(iMat) + ' - textures: ' + str(iTex) + ' - objects: ' + str(iObj) )
    return '\n'.join(s for s in result)
