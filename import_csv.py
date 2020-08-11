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
This script imports a CSV file to Blender.

Usage:
Run this script from "File->Import" menu and then load the desired CSV file.
"""

import bpy, bmesh, os, struct, csv
from mathutils import Vector
from bpy_extras.object_utils import object_data_add


def load(context, filepath):
    meshname=os.path.basename(filepath)
    csvfile = open(filepath)
    inFile = csv.reader(csvfile, delimiter=',', quotechar='"')
    # skip header
    inFile.__next__()
    mesh=0
    for row in inFile:
        #  column order (1: x, 2: z, 3: y)
        coords = (float(row[0]),float(row[2]),float(row[1]))
        # coords = (float(row[0])/100.0,float(row[2])/100.0,float(row[1])/100.0)
        if mesh==0:
            mesh = bpy.data.meshes.new( name=meshname )
            mesh.from_pydata( [Vector(coords)], [], [] )
            mesh = object_data_add(bpy.context, mesh)

            # Blender<2.8
            # bpy.context.scene.objects.active = bpy.data.objects[meshname]

            # Blender>=2.8
            bpy.context.view_layer.objects.active = bpy.data.objects[meshname]

            bpy.ops.object.mode_set(mode='EDIT')
        else:
            mesh = bmesh.from_edit_mesh(bpy.data.objects[meshname].data)
            mesh.verts.new( coords )
            mesh.verts.ensure_lookup_table()
            # mesh.edges.new([mesh.verts[len(mesh.verts)-1],mesh.verts[len(mesh.verts)]])
            mesh.edges.new([mesh.verts[len(mesh.verts)-2],mesh.verts[len(mesh.verts)-1]])
            bmesh.update_edit_mesh(bpy.data.objects[meshname].data, True)
    bpy.ops.object.mode_set(mode='OBJECT')
    # bpy.ops.transform.resize(value=(0.01, 0.01, 0.01), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, True, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
    return {'FINISHED'}
