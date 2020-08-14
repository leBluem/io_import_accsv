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
This script exports a AssettoCorsa CSV file.

Usage:
Run this script from "File->Export" menu and then save the desired CSV file.
"""

import bpy, bmesh, os, struct, csv
from mathutils import Vector
from bpy_extras.object_utils import object_data_add


def save(context, filepath):
    bm = bmesh.new()
    ob = context.active_object
    if not bpy.context.active_object.mode=='EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(ob.data)
    i=1
    with open(filepath, 'w') as file:
        for v in bm.verts:
            file.write("{:.4f},{:.4f},{:.4f},{:.6f}\n".format(round(v.co[0],6), round(v.co[2],6), round(v.co[1],6), round(float(i)/float(len(bm.verts)+1),6) ) )
            i+=1
    bpy.ops.object.mode_set(mode='OBJECT')
    return {'FINISHED'}
