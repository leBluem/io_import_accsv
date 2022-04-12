"""
This script imports a AssettoCorsa cameras.INI file to Blender.

Usage:
Run this script from "File->Import" menu and then load the desired INI file.
"""


import bpy, bmesh, configparser, codecs, os
from mathutils import Vector
from bpy_extras.object_utils import object_data_add


def CenterOrigin(scaling):
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.ops.transform.resize(value=(scaling, scaling, scaling))


def load(context, filepath, scaling, asMesh):
    s=''
    c=0
    mesh = 0
    print('import ' + filepath)
    with codecs.open(filepath, 'r', errors='ignore') as file:
        s = file.read()
        s = s.replace('POSITION = ', 'POSITION=')

    if 'POSITION=' in s and '[' in s:
        ini = configparser.ConfigParser(empty_lines_in_values=False, strict=False, allow_no_value=True, inline_comment_prefixes=(";","#","/","_"), comment_prefixes=(";","#","/","_"))
        ini.optionxform=str # keep upper/lower case
        ini.read(filepath)
        vertC = 0
        meshname = os.path.basename(filepath)
        for sects in ini.sections():
            if asMesh:
                coords = ['-999999.0','0.0','0.0']
                if ini.has_option(sects, 'POSITION'):
                    coords = ini.get(sects, 'POSITION').split(',')
                elif ini.has_option(sects, 'WORLD_POSITION'):
                    coords = ini.get(sects, 'WORLD_POSITION').split(',')

                if coords!=['-999999.0','0.0','0.0']:
                    if mesh==0:
                        mesh = bpy.data.meshes.new( name=meshname )
                        mesh.from_pydata( [Vector((float(coords[0])*scaling, -float(coords[2])*scaling, float(coords[1])*scaling ))], [], [] )
                        mesh = object_data_add(bpy.context, mesh)
                        meshname = mesh.name # update name, may have .001 or something
                        bpy.context.view_layer.objects.active = bpy.data.objects[meshname]
                        bpy.ops.object.mode_set(mode='EDIT')
                        vertC = 1
                    else:
                        mesh = bmesh.from_edit_mesh(bpy.data.objects[meshname].data)
                        mesh.verts.new( (float(coords[0])*scaling, -float(coords[2])*scaling, float(coords[1])*scaling ) )
                        mesh.verts.ensure_lookup_table()
                        mesh.edges.new([mesh.verts[len(mesh.verts)-2],mesh.verts[len(mesh.verts)-1]])
                        bmesh.update_edit_mesh(bpy.data.objects[meshname].data)
            else:
                coords = ['-999999.0','0.0','0.0']
                if ini.has_option(sects, 'POSITION'):
                    coords = ini.get(sects, 'POSITION').split(',')
                elif ini.has_option(sects, 'WORLD_POSITION'):
                    coords = ini.get(sects, 'WORLD_POSITION').split(',')
                if coords!=['-999999.0','0.0','0.0']:
                    bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(float(coords[0])*scaling, -float(coords[2])*scaling, float(coords[1])*scaling ), scale=(scaling*5, scaling*5, scaling*5))
                    bpy.context.object.name = sects
                c+=1

    if asMesh:
        if mesh!=0:
            print('Imported ' + str(len(mesh.verts)) + ' points' )
            bpy.ops.object.mode_set(mode='OBJECT')
        else:
            print('nothing found in ' +filepath)

    else:
        print('Imported ' + str(c) + ' empties' )

    # CenterOrigin(scaling)

    return {'FINISHED'}
