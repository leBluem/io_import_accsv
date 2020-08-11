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
This script imports a fast_lane.ai/ideal_line.ai into Blender.

Usage:
Run this script from "File->Import" menu and then load the desired *.ai file.
"""

import bpy, bmesh, os, struct
from mathutils import Vector
from bpy_extras.object_utils import object_data_add

def load(context, filepath):
    with open(filepath, "rb") as buffer:
        meshname = os.path.basename(filepath)

        # temporary arrays
        data_ideal = []
        data_detail = []
        mesh = 0

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

        # now dissect data from temporary arrays
        for i in range(detailCount):
            x, y, z, dist, id = data_ideal[i]
            coords = ( float(x), -1.0 * float(z), float(y) )
            # coords = ( float(x)/100.0, -1.0 * float(z)/100.0, float(y)/100.0 )
            if mesh==0:
                mesh = bpy.data.meshes.new( name=meshname )
                mesh.from_pydata( [Vector(coords)] , [], [] )
                mesh = object_data_add(bpy.context, mesh)

                # Blender<2.8
                # bpy.context.scene.objects.active = bpy.data.objects[meshname]

                # Blender>=2.8
                bpy.context.view_layer.objects.active = bpy.data.objects[meshname]

                bpy.ops.object.mode_set(mode='EDIT')
            else:
                mesh = bmesh.from_edit_mesh(bpy.data.objects[meshname].data)
                mesh.verts.new(coords)
                mesh.verts.ensure_lookup_table()
                mesh.edges.new([mesh.verts[len(mesh.verts)-2],mesh.verts[len(mesh.verts)-1]])
                bmesh.update_edit_mesh(bpy.data.objects[meshname].data, True)
    bpy.ops.object.mode_set(mode='OBJECT')
    # bpy.ops.transform.resize(value=(0.01, 0.01, 0.01), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, True, True), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)

    return {'FINISHED'}
