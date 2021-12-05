"""
This script exports a AssettoCorsa INI file.

Usage:
Run this script from "File->Export" menu and then save the desired INI file.
"""

import bpy, bmesh, codecs, configparser

def save(context, filepath, scaling, reverse):
    selected_obj = bpy.context.selected_objects.copy()

    print(filepath)
    s=''
    with codecs.open(filepath, 'r', errors='ignore') as file:
        s = file.read()

    if 'POSITION=' in s and '[' in s and 'NAME=' in s:
        ini = configparser.ConfigParser(inline_comment_prefixes=';')
        ini.optionxform=str # keep upper/lower case
        ini.read(filepath)
        count=0
        for sects in ini.sections():
            if 'CAMERA_' in sects:
                count += 1

        # must match existing INI, cant write new ones atm
        if count != len(selected_obj):
            return {'camera num mismatch!'}

        for o in selected_obj:
            if o.type == 'PLAIN_AXES':
                ss=str(o.matrix_world.to_translation()).replace('<Vector (','')
                ss=ss.replace(')>','')
                ss=ss.replace(' ','')
                sss = ss.split(',')
                ini.set(o.name, 'POSITION', \
                    +str(round(float(sss[0])*  scaling , 4) ) + ', ' \
                    +str(round(float(sss[2])* -scaling , 4) ) + ', ' \
                    +str(round(float(sss[1])*( scaling), 4) )             )

        with codecs.open(filepath, 'w') as configfile:
            ini.write(configfile, space_around_delimiters=False)

        return {'FINISHED'}
    else:
        print('... not a camera.ini!')

