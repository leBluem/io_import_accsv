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
This script imports AssettoCorsa fast_lane.ai/ideal_line.ai into Blender.

Usage:
Run this script from "File->Import" menu and then load the desired *.ai file.
"""

import bpy, bmesh, os, struct, math
from mathutils import Vector
from bpy_extras.object_utils import object_data_add


def CenterOrigin(scaling):
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.ops.transform.resize(value=(scaling, scaling, scaling))


def CreateMeshFromDataPoints(meshname, idx, data_ideal, data_detail, scaling):
        # create vertices from ai line data
        mesh = 0
        if idx!=-1:
            meshname = meshname + str(idx)
        xl, z, yl, dist, id = data_ideal[len(data_ideal)-1]
        for i in range(len(data_ideal)):
            x, z, y, dist, id = data_ideal[i]
            if idx!=-1:
                if idx==6 or idx==7:
                    direction = -math.degrees( math.atan2(yl - y, x - xl))
                    yl = y
                    xl = x
                    if idx==6:
                        _wallLeft = data_detail[i][6]
                        x = x + math.cos((-direction + 90) * math.pi / 180) * _wallLeft
                        y = y - math.sin((-direction + 90) * math.pi / 180) * _wallLeft
                    else:
                        _wallRight= data_detail[i][7]
                        x = x + math.cos((-direction - 90) * math.pi / 180) * _wallRight
                        y = y - math.sin((-direction - 90) * math.pi / 180) * _wallRight
                elif idx==5:
                    z = data_detail[i][idx] / 100.0
                elif idx==1:
                    z = data_detail[i][idx]
                else:
                    z = data_detail[i][idx] * 100
            coords = ( float(x), -float(y), float(z)  )

            if i==0:
                print('Import AC ai-line start-pos: ' + str(coords))
            if mesh==0: # create new mesh
                mesh = bpy.data.meshes.new( name=meshname )
                mesh.from_pydata( [Vector(coords)] , [], [] )
                mesh = object_data_add(bpy.context, mesh)
                meshname = mesh.name
                bpy.context.view_layer.objects.active = bpy.data.objects[meshname]
                bpy.ops.object.mode_set(mode='EDIT')
            else: # add to existing mesh
                mesh = bmesh.from_edit_mesh(bpy.data.objects[meshname].data)
                mesh.verts.new(coords)
                mesh.verts.ensure_lookup_table()
                mesh.edges.new([mesh.verts[len(mesh.verts)-2],mesh.verts[len(mesh.verts)-1]])
                bmesh.update_edit_mesh(bpy.data.objects[meshname].data, True)
        # set last edge
        if mesh.verts[0] and mesh.verts[len(mesh.verts)-1]:
            mesh.edges.new( [ mesh.verts[0], mesh.verts[len(mesh.verts)-1] ] )
        bpy.ops.object.mode_set(mode='OBJECT')
        CenterOrigin(scaling)

def load(context, filepath, scaling, importExtraData):
    with open(filepath, "rb") as buffer:
        meshname       = os.path.basename(filepath)
        meshnameBL     = meshname + '_border_left'
        meshnameBR     = meshname + '_border_right'
        meshnameDetail = meshname + '_detail'

        # insert stuff at origin
        # taken from, https://blenderartists.org/t/setting-origin-to-world-centre-using-blender-python/1174798
        bpy.ops.transform.translate(value=(0, 0, 1), orient_type='GLOBAL')
        bpy.context.scene.cursor.location = Vector((0.0, 0.0, 0.0))
        bpy.context.scene.cursor.rotation_euler = Vector((0.0, 0.0, 0.0))


        # temporary arrays
        data_ideal = []
        data_detail = []
        mesh = 0
        # bpy.ops.view3d.snap_cursor_to_center()

        # should be at start, but do it anyway
        buffer.seek(0)
        # read header, detailCount is number of data points available
        header, detailCount, u1, u2 = struct.unpack("4i", buffer.read(4 * 4))
        # read ideal-line data
        for i in range(detailCount):       # 4 floats, one integer
            data_ideal.append(struct.unpack("4f i", buffer.read(4 * 5)))
        # read more details data
        for i in range(detailCount):        # 18 floats
            data_detail.append(struct.unpack("18f", buffer.read(4 * 18)))

        # now comes more data, no info available for that

        CreateMeshFromDataPoints(meshnameBL , 6, data_ideal, data_detail, scaling)
        CreateMeshFromDataPoints(meshnameBR , 7, data_ideal, data_detail, scaling)
        print(str(importExtraData))
        if importExtraData:
            CreateMeshFromDataPoints(meshnameDetail , 0, data_ideal, data_detail, scaling)
            CreateMeshFromDataPoints(meshnameDetail , 1, data_ideal, data_detail, scaling)
            CreateMeshFromDataPoints(meshnameDetail , 2, data_ideal, data_detail, scaling)
            CreateMeshFromDataPoints(meshnameDetail , 3, data_ideal, data_detail, scaling)
            CreateMeshFromDataPoints(meshnameDetail , 4, data_ideal, data_detail, scaling)
            CreateMeshFromDataPoints(meshnameDetail , 5, data_ideal, data_detail, scaling)
            CreateMeshFromDataPoints(meshnameDetail , 8, data_ideal, data_detail, scaling)
            CreateMeshFromDataPoints(meshnameDetail , 9, data_ideal, data_detail, scaling)
            CreateMeshFromDataPoints(meshnameDetail ,10, data_ideal, data_detail, scaling)
            CreateMeshFromDataPoints(meshnameDetail ,11, data_ideal, data_detail, scaling)
            CreateMeshFromDataPoints(meshnameDetail ,12, data_ideal, data_detail, scaling)
            CreateMeshFromDataPoints(meshnameDetail ,13, data_ideal, data_detail, scaling)
            CreateMeshFromDataPoints(meshnameDetail ,14, data_ideal, data_detail, scaling)
            CreateMeshFromDataPoints(meshnameDetail ,15, data_ideal, data_detail, scaling)
            CreateMeshFromDataPoints(meshnameDetail ,16, data_ideal, data_detail, scaling)
            CreateMeshFromDataPoints(meshnameDetail ,17, data_ideal, data_detail, scaling)
        CreateMeshFromDataPoints(meshname       ,-1, data_ideal, data_detail, scaling)

    return {'FINISHED'}
