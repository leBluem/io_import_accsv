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
This script exports a AssettoCorsa fast_lane.ai/ideal_line.ai from Blender (not for walls, use AC-csv reading with shift!).

Usage:
Run this script from "File->Export" menu to save desired *.ai file.
"""

import bpy, bmesh, os, struct, math
from mathutils import Vector

def save(context, filepath, shiftCount):
    # temporary arrays
    data_ideal = []
    data_detail = []
    data_rest = []
    filesize = os.stat(filepath).st_size
    header = 0
    detailCount = 0
    u1 = 0
    u2 = 0

    with open(filepath, "rb") as buffer:
        # should be at start, but do it anyway
        buffer.seek(0)
        # read header, detailCount is number of data points available
        header, detailCount, u1, u2 = struct.unpack("4i", buffer.read(4 * 4))
        filesize -= 4*4
        # read ideal-line data
        for i in range(detailCount):       # 4 floats, one integer
            data_ideal.append(struct.unpack("4f i", buffer.read(4 * 5)))
            filesize -= 4*5
        # read more details data
        for i in range(detailCount):        # 18 floats
            data_detail.append(struct.unpack("18f", buffer.read(4 * 18)))
            filesize -= 4*18

        # now comes more data, no info available for that
        data_rest = buffer.read(filesize)

    print('Export AC ai-line points: ' + str(detailCount) + ' ' + filepath )

    # check if ai line data count matches our vertices
    bm = bmesh.new()
    ob = context.active_object
    bm = bpy.context.object.data
    if len(bm.vertices) != detailCount:
        print('Export AC ai-line: vertex count does not match!')
        return {'ai line and vertex count dont match!'}


    ## now dissect data from temporary arrays and write changed data
    with open(filepath, "wb") as buffer:
        buffer.write(struct.pack("4i", header, detailCount, u1, u2))

        runIndex = detailCount+shiftCount+1
        if runIndex>=detailCount:
            runIndex=0
        # print('runIndex ' + str(runIndex))
        for i in range(detailCount):
            # x, z, y, dist, id = data_ideal[i]
            x =  bm.vertices[runIndex].co[0]
            z = -bm.vertices[runIndex].co[1]
            y =  bm.vertices[runIndex].co[2]
            # 4 floats, one integer
            buffer.write( struct.pack("4f i", x, y, z, data_ideal[runIndex][3], data_ideal[runIndex][4] ) )
            runIndex += 1
            if runIndex>=detailCount:
                runIndex=0

        runIndex = detailCount+shiftCount+1
        if runIndex>=detailCount:
            runIndex=0
        for i in range(detailCount):
            # write other data unchanged
            # 18 floats
            data = struct.pack("18f", data_detail[runIndex][0], data_detail[runIndex][1], data_detail[runIndex][2], data_detail[runIndex][3], data_detail[runIndex][4], data_detail[runIndex][5], data_detail[runIndex][6], data_detail[runIndex][7], data_detail[runIndex][8], data_detail[runIndex][9], data_detail[runIndex][10], data_detail[runIndex][11], data_detail[runIndex][12], data_detail[runIndex][13], data_detail[runIndex][14], data_detail[runIndex][15], data_detail[runIndex][16], data_detail[runIndex][17])
            buffer.write(data)
            runIndex += 1
            if runIndex>=detailCount:
                runIndex=0

        # write rest of data unchanged
        buffer.write(data_rest)

    return {'FINISHED'}
