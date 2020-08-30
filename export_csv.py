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
import math, mathutils


def distance(point1, point2) -> float:
    """Calculate distance between two points in 3D."""
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2 + (point2[2] - point1[2]) ** 2)


def save(context, filepath, scaling, shiftCount):
    selected_obj = bpy.context.selected_objects.copy()
    if len(selected_obj)==1:
        bm = bmesh.new()
        ob = context.active_object
        bm = bpy.context.object.data
        if len(bm.vertices) > 1:
            with open(filepath, 'w') as file:
                lastOne = bm.vertices[len(bm.vertices)-1].co
                lastco = lastOne
                # we need this to not have 1.0 as pointOfTrack in last CSV line
                distTotal = distance(bm.vertices[0].co, lastOne)
                # run to get complete length
                for v in bm.vertices:
                    distTotal += distance(v.co, lastco)
                    lastco = v.co

                lastco = lastOne
                dist = 0.0
                # print( str(distTotal) + ' - ' + str(len(bm.vertices)) + 'verts\n' )
                for v in bm.vertices:
                    dist += distance(v.co, lastco)
                    lastco = v.co
                    file.write("{:.4f},{:.4f},{:.4f},{:.6f}\n".format(
                                v.co[0]*scaling, v.co[2]*scaling, v.co[1]*scaling,
                                dist/distTotal )
                        )
    else:
        return {'Select only one Object!'}

    return {'FINISHED'}
