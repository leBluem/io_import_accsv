# ##### BEGIN GPL LICENSE BLOCK #####
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
# ##### END GPL LICENSE BLOCK #####
# <pep8 compliant>

"""
This script exports a AssettoCorsa fast_lane.ai/ideal_line.ai from Blender (not for walls, use AC-csv reading with shift!).

Usage:
Run this script from "File->Export" menu to save desired *.ai file.
"""


import bpy, bmesh, os, struct, math
from mathutils import Vector


def distance(point1, point2) -> float:
    """Calculate distance between two points in 3D."""
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2 + (point2[2] - point1[2]) ** 2)


def save(context, filepath, shiftCount, lineIDX):
    selected_obj = bpy.context.selected_objects.copy()
    if len(selected_obj)!=1:
        return {'Select only one object!'}

    bm = bmesh.new()
    ob = context.active_object
    bm = bpy.context.object.data
    if len(bm.vertices) < 2:
        return {'Not enough vertices!'}

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


    # check if ai line data count matches our vertices
    if len(bm.vertices) != detailCount:
        print('Export AC ai-line: vertex count does not match!')
        return {'AI-line point count and vertex-count of selected mesh dont match!'}

    print('Export AC ai-line, points: ' + str(detailCount) + ' ' + filepath )

    ## now dissect data from temporary arrays and write changed data
    with open(filepath, "wb") as buffer:
        buffer.write(struct.pack("4i", header, detailCount, u1, u2))

        runIndex = detailCount+shiftCount+1
        if runIndex>=detailCount:
            runIndex=0

        lastOne = bm.vertices[len(bm.vertices)-1].co
        lastco = lastOne
        # we need this to not have 1.0 as pointOfTrack in last dataset
        distTotal = distance(bm.vertices[0].co, lastOne)
        # run to get complete length
        for v in bm.vertices:
            distTotal += distance(v.co, lastco)
            lastco = v.co

        # print('runIndex ' + str(runIndex))
        for i in range(detailCount):
            if int(lineIDX)!=-1:
                # if lineIDX just read current values from orig ai-line
                x, y, z, dist, id = data_ideal[i]
            else:
                x =  bm.vertices[runIndex].co[0]
                # y =  bm.vertices[runIndex].co[2]
                y =  bm.vertices[runIndex].co[2]
                z = -bm.vertices[runIndex].co[1]
                dist = distance(v.co, lastco)
                lastco = v.co

            # 4 floats, one integer
            buffer.write( struct.pack("4f i", x, y, z, dist, data_ideal[runIndex][4] ) )
            # buffer.write( struct.pack("4f i", x, y, z, data_ideal[runIndex][3], data_ideal[runIndex][4] ) )
            runIndex += 1
            if runIndex>=detailCount:
                runIndex=0

        runIndex = detailCount+shiftCount+1
        if runIndex>=detailCount:
            runIndex=0

        print( 'Export AC ailine ID: ' + str(lineIDX) )
        for i in range(detailCount):
            # write other data unchanged
            # 18 floats
            if int(lineIDX)!=-1:
                L2 = list(data_detail[runIndex])
                # if i==1:
                #     print(str(data_detail[runIndex]))
                #     print(str(L2))
                if int(lineIDX) == 5:
                    L2[int(lineIDX)] = bm.vertices[runIndex].co[2] * 100.0
                elif idx!=1:
                    L2[int(lineIDX)] = bm.vertices[runIndex].co[2] / 100.0
                else:
                    L2[int(lineIDX)] = bm.vertices[runIndex].co[2]
                data_detail[runIndex] = tuple(L2)
                # if i==1:
                #     print(str(L2))
                #     print(str(data_detail[runIndex]))
            data = struct.pack("18f", data_detail[runIndex][0], data_detail[runIndex][1], data_detail[runIndex][2], data_detail[runIndex][3], data_detail[runIndex][4], data_detail[runIndex][5], data_detail[runIndex][6], data_detail[runIndex][7], data_detail[runIndex][8], data_detail[runIndex][9], data_detail[runIndex][10], data_detail[runIndex][11], data_detail[runIndex][12], data_detail[runIndex][13], data_detail[runIndex][14], data_detail[runIndex][15], data_detail[runIndex][16], data_detail[runIndex][17])
            buffer.write(data)
            runIndex += 1
            if runIndex>=detailCount:
                runIndex=0

        # write rest of data unchanged
        buffer.write(data_rest)

    print('Export AC ai-line: success!')
    return {'FINISHED'}
