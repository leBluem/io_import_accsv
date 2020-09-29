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


import bpy, bmesh, os, struct, csv, math
from mathutils import Vector
from bpy_extras.object_utils import object_data_add


def CenterOrigin(scaling):
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.ops.transform.resize(value=(scaling, scaling, scaling))


def distance(point1, point2) -> float:
    """Calculate distance between two points in 3D."""
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2 + (point2[2] - point1[2]) ** 2)


def load(context, filepath, scaling, doDoubleCheck):
    meshname=os.path.basename(filepath)
    csvfile = open(filepath)
    inFile = csv.reader(csvfile, delimiter=',', quotechar='"')

    # insert stuff at origin
    # taken from, https://blenderartists.org/t/setting-origin-to-world-centre-using-blender-python/1174798
    bpy.ops.transform.translate(value=(0, 0, 1), orient_type='GLOBAL')
    bpy.context.scene.cursor.location = Vector((0.0, 0.0, 0.0))
    bpy.context.scene.cursor.rotation_euler = Vector((0.0, 0.0, 0.0))

    skipped = 0
    mesh=0
    for row in inFile:
        #  column order (1: x, 2: z, 3: y)
        coords = (float(row[0]),float(row[2]),float(row[1]))
        if mesh==0:
            mesh = bpy.data.meshes.new( name=meshname )
            mesh.from_pydata( [Vector(coords)], [], [] )
            mesh = object_data_add(bpy.context, mesh)
            meshname = mesh.name
            bpy.context.view_layer.objects.active = bpy.data.objects[meshname]
            bpy.ops.object.mode_set(mode='EDIT')
        else:
            mesh = bmesh.from_edit_mesh(bpy.data.objects[meshname].data)
            skip = False
            if doDoubleCheck:
                for ms in mesh.verts:
                    #if (ms.co[0]-0.01 >= coords[0] and ms.co[0]+0.01 <= coords[0]) and  (ms.co[1]-0.01 >= coords[2] and ms.co[1]+0.01 <= coords[2]) and  (ms.co[2]-0.01 >= coords[1] and ms.co[2]+0.01 <= coords[1]):
                    if distance(ms.co, coords)<0.1:
                        skipped += 1
                        skip = True
                        break
            if skip==False:
                mesh.verts.new( coords )
                mesh.verts.ensure_lookup_table()
                mesh.edges.new([mesh.verts[len(mesh.verts)-2],mesh.verts[len(mesh.verts)-1]])
                bmesh.update_edit_mesh(bpy.data.objects[meshname].data, True)
    # set last edge
    if mesh.verts[0] and mesh.verts[len(mesh.verts)-1]:
        mesh.edges.new( [ mesh.verts[0], mesh.verts[len(mesh.verts)-1] ] )
    print('Imported ' + str(len(mesh.verts)) + ' points, points skipped: ' + str(skipped) )
    bpy.ops.object.mode_set(mode='OBJECT')
    CenterOrigin(scaling)
    return {'FINISHED'}

# obj.data.vertices[0].select = True

