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
    # taken from
    # https://blenderartists.org/t/setting-origin-to-world-centre-using-blender-python/1174798
    bpy.ops.transform.translate(value=(0, 0, 1), orient_type='GLOBAL')
    #put cursor at origin
    bpy.context.scene.cursor.location = Vector((0.0, 0.0, 0.0))
    bpy.context.scene.cursor.rotation_euler = Vector((0.0, 0.0, 0.0))
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.ops.transform.resize(value=(scaling, scaling, scaling))

def load(context, filepath, scaling):
    with open(filepath, "rb") as buffer:
        meshname = os.path.basename(filepath)
        meshwallL = meshname + '_wall_left'
        meshwallR = meshname + '_wall_right'

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

        # create vertices from ai line data
        mesh = 0
        for i in range(detailCount):
            x, z, y, dist, id = data_ideal[i]
            coords = ( float(x), -float(y), float(z) )
            if mesh==0: # create new mesh
                mesh = bpy.data.meshes.new( name=meshname )
                mesh.from_pydata( [Vector(coords)] , [], [] )
                mesh = object_data_add(bpy.context, mesh)
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

        # create vertices from wallLeft
        meshname = meshwallL
        mesh=0
        xl, z, yl, dist, id = data_ideal[detailCount-1]
        for i in range(detailCount):
            x, z, y, dist, id = data_ideal[i]
            direction = -math.degrees( math.atan2(yl - y, x - xl))
            _wallRight = data_detail[i][6]
            rx = x + math.cos((-direction + 90) * math.pi / 180) * _wallRight
            ry = y - math.sin((-direction + 90) * math.pi / 180) * _wallRight
            yl = y
            xl = x
            coords = ( float(rx), -float(ry), float(z)  )
            if mesh==0: # create new mesh
                mesh = bpy.data.meshes.new( name=meshname )
                mesh.from_pydata( [Vector(coords)] , [], [] )
                mesh = object_data_add(bpy.context, mesh)
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

        # create vertices from wallRight
        meshname = meshwallR
        mesh=0
        xl, z, yl, dist, id = data_ideal[detailCount-1]
        for i in range(detailCount):
            x, z, y, dist, id = data_ideal[i]
            _wallLeft         = data_detail[i][7]
            direction = -math.degrees( math.atan2(yl - y, x - xl))
            lx = x + math.cos((-direction - 90) * math.pi / 180) * _wallLeft
            ly = y - math.sin((-direction - 90) * math.pi / 180) * _wallLeft
            yl = y
            xl = x
            coords = ( float(lx), -float(ly), float(z)  )
            if mesh==0: # create new mesh
                mesh = bpy.data.meshes.new( name=meshname )
                mesh.from_pydata( [Vector(coords)] , [], [] )
                mesh = object_data_add(bpy.context, mesh)
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

    return {'FINISHED'}
