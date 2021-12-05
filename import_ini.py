"""
This script imports a AssettoCorsa cameras.INI file to Blender.

Usage:
Run this script from "File->Import" menu and then load the desired INI file.
"""


import bpy, bmesh, configparser, codecs

def load(context, filepath, scaling):
    s=''
    with codecs.open(filepath, 'r', errors='ignore') as file:
        s = file.read()
    if 'POSITION=' in s and '[' in s and 'NAME=' in s:
        ini = configparser.ConfigParser(inline_comment_prefixes=';')
        ini.optionxform=str # keep upper/lower case
        ini.read(filepath)
        for sects in ini.sections():
            if ini.has_option(sects,'NAME') and ini.has_option(sects, 'POSITION'):
                pos = ini.get(sects, 'POSITION').split(',')
                bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(float(pos[0])*scaling, -float(pos[2])*scaling, float(pos[1])*scaling ), scale=(scaling*5, scaling*5, scaling*5))
                bpy.context.object.name = sects

    # CenterOrigin(scaling)

    return {'FINISHED'}
