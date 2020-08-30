# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>


"""
This script imports a AssettoCorsa CSV file to Blender.

Usage:
Run this script from "File->Import" menu and then load the desired CSV file.
"""

import bpy, bmesh, os, struct, csv
from mathutils import Vector
from bpy_extras.object_utils import object_data_add

def CenterOrigin(scaling):
    # taken from
    # https://blenderartists.org/t/setting-origin-to-world-centre-using-blender-python/1174798
    bpy.ops.transform.translate(value=(0, 0, 1), orient_type='GLOBAL')
    #put cursor at origin
    bpy.context.scene.cursor.location = Vector((0.0, 0.0, 0.0))
    bpy.context.scene.cursor.rotation_euler = Vector((0.0, 0.0, 0.0))
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.ops.transform.resize(value=(scaling, scaling, scaling))

def load(context, filepath, scaling):
    meshname=os.path.basename(filepath)
    csvfile = open(filepath)
    inFile = csv.reader(csvfile, delimiter=',', quotechar='"')
    mesh=0
    for row in inFile:
        #  column order (1: x, 2: z, 3: y)
        coords = (float(row[0]),float(row[2]),float(row[1]))
        if mesh==0:
            mesh = bpy.data.meshes.new( name=meshname )
            mesh.from_pydata( [Vector(coords)], [], [] )
            mesh = object_data_add(bpy.context, mesh)
            bpy.context.view_layer.objects.active = bpy.data.objects[meshname]
            bpy.ops.object.mode_set(mode='EDIT')
        else:
            mesh = bmesh.from_edit_mesh(bpy.data.objects[meshname].data)
            mesh.verts.new( coords )
            mesh.verts.ensure_lookup_table()
            mesh.edges.new([mesh.verts[len(mesh.verts)-2],mesh.verts[len(mesh.verts)-1]])
            bmesh.update_edit_mesh(bpy.data.objects[meshname].data, True)
    # set last edge
    if mesh.verts[0] and mesh.verts[len(mesh.verts)-1]:
        mesh.edges.new( [ mesh.verts[0], mesh.verts[len(mesh.verts)-1] ] )
    bpy.ops.object.mode_set(mode='OBJECT')
    CenterOrigin(scaling)
    return {'FINISHED'}
