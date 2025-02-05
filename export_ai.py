"""
This script exports a AssettoCorsa fast_lane.ai/ideal_line.ai from Blender (not for walls, use AC-csv reading with shift!).

Usage:
Run this script from "File->Export" menu to save desired *.ai file.
"""

from genericpath import isfile
from shutil import copyfile
import bpy, bmesh, os, struct, math
from mathutils import Vector


def distance(point1, point2) -> float:
    """Calculate distance between two points in 3D."""
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2 + (point2[2] - point1[2]) ** 2)


def save(context, filepath, shiftCount, lineIDX, scaling, reverse):
    selected_obj = bpy.context.selected_objects.copy()
    # if len(selected_obj)!=1 and len(selected_obj)!=3:
    #     print('Select only one object!')
    #     return {'CANCELED'}

    bm = 0
    bmL = 0
    bmR = 0
    if len(selected_obj)>=3:
        filepart = os.path.basename(filepath).lower()
        for ob2 in selected_obj:
            if    'left' in ob2.name.lower() and ob2.name.lower().startswith(filepart):
                bmL = ob2.data
            elif 'right' in ob2.name.lower() and ob2.name.lower().startswith(filepart):
                bmR = ob2.data
            elif 'ideal' in ob2.name.lower() and ob2.name.lower().startswith(filepart):
                bm = bmesh.new()
                ob = context.active_object
                bm = bpy.context.object.data

        if (bmL==0 or bmR==0 or bm==0):
            print("Could not find 'ideal/left/right', select both borders and idealline last, so its selected!")
            return {'CANCELED'}
        if (len(bm.vertices)!=len(bmL.vertices) or
            len(bm.vertices)!=len(bmR.vertices) ):
            print("Length of ideal line/borders dont match!")
            return {'CANCELED'}
    elif len(selected_obj)==1:
        bm = bmesh.new()
        ob = context.active_object
        bm = bpy.context.object.data
    else:
        return {'CANCELED'}

    if len(bm.vertices) < 2:
        print('Not enough vertices!')
        return {'CANCELED'}

    # temporary arrays
    data_ideal = []
    data_detail = []
    data_rest = []

    header = 0
    detailCount = 0
    u1 = 0
    u2 = 0

    if os.path.isfile(filepath):
        filesize = os.stat(filepath).st_size
        if filesize>24:
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
        else:
            print('... overwriting file ...')

    current_mode = bpy.context.object.mode
    if current_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode = 'OBJECT')


    # check if ai line data count matches our vertices
    ### if len(bm.vertices) == detailCount:
    dist = 0.0
    if len(bm.vertices) != detailCount:
        if detailCount>0:
            print('Vertex count does not match!')
            print('  points ailine: ' + str(detailCount) )
        print('  points mesh  : ' + str(len(bm.vertices)) )
        detailCount = len(bm.vertices)

        print('... creating NEW basic AI line (load that in ksEditor) ...')
        print('file           : ' + filepath )
        if os.path.isfile(filepath):
            i=0
            copyfilepath = filepath+'copy'+str(i)
            while os.path.isfile(copyfilepath):
                i+=1
                copyfilepath = filepath+'copy'+str(i)
            print('backup         : ' + copyfilepath )
            copyfile(filepath, copyfilepath)

        #return {'AI-line point count and vertex-count of selected mesh dont match!'}
        with open(filepath, "wb") as buffer:
            # header
            buffer.write(struct.pack("4i", 7, detailCount, 0, 0))

            lastOne = bm.vertices[len(bm.vertices)-1].co
            lastco = lastOne
            distTotal = 0.0

            runIndex = detailCount+shiftCount+1
            if runIndex>=detailCount:
                runIndex=0

            # 4 floats, 1 int * detailCount
            for i in range(detailCount):
                x =  bm.vertices[runIndex].co[0] * scaling
                y =  bm.vertices[runIndex].co[1] * scaling
                z =  bm.vertices[runIndex].co[2] * scaling
                if i>0:
                    distTotal += distance(bm.vertices[runIndex].co, lastco) * scaling
                else:
                    distTotal = 0
                lastco = bm.vertices[runIndex].co
                buffer.write(struct.pack("4f i", x, z, -y, dist, i))
                runIndex += 1
                if runIndex>=detailCount:
                    runIndex=0

            print('  length: ' + str(round(distTotal,1)) +'m' )
            runIndex = detailCount+shiftCount+1
            if runIndex>=detailCount:
                runIndex=0

            distL=0.2
            distR=0.2
            if (bmL!=0 and bmR!=0):
                distL = distance(bm.vertices[runIndex].co,bmL.vertices[runIndex].co)
                distR = distance(bm.vertices[runIndex].co,bmR.vertices[runIndex].co)

            # 18 floats * detailCount
            for i in range(detailCount):
                extArr = [0,0,0,0,0,0,distL,distR,0,0,0,0,0,0,0,0,0,0]
                if i == 0 :
                    extArr[0] = 1.40129846432481e-45 * detailCount
                for f in extArr:
                    buffer.write(struct.pack("f",f))

    else:
        print('... changing EXISTING AI line ...')
        print('file     : ' + filepath )
        print('  points : ' + str(detailCount) )

        ## dissect data from temporary arrays and write changed data
        with open(filepath, "wb") as buffer:
            buffer.write(struct.pack("4i", header, detailCount, u1, u2))

            runIndex = detailCount+shiftCount+1
            if runIndex>=detailCount:
                runIndex=0
            print('  1st index: ' + str(runIndex))

            lastOne = bm.vertices[len(bm.vertices)-1].co
            lastco = lastOne
            # we need this to not have 1.0 as pointOfTrack in last dataset
            distTotal = distance(bm.vertices[0].co, lastOne)
            # run to get complete length
            for v in bm.vertices:
                distTotal += distance(v.co, lastco)
                lastco = v.co

            print('  length: ' + str(round(distTotal, 1)) + 'm')

            # 4 floats, 1 int * detailCount
            dist = 0.0
            for i in range(detailCount):

                if int(lineIDX)!=-1:
                    # if lineIDX just read current values from orig ai-line
                    x, y, z, dist, id = data_ideal[i]
                    buffer.write( struct.pack("4f i", x, y, z, dist, data_ideal[runIndex][4] ) )
                else:
                    # coords = ( float(x), -float(y), float(z)  )
                    x =  bm.vertices[runIndex].co[0] * scaling
                    y =  bm.vertices[runIndex].co[1] * scaling
                    z =  bm.vertices[runIndex].co[2] * scaling
                    buffer.write( struct.pack("4f i", x, z, -y, dist, data_ideal[runIndex][4] ) )
                    dist += distance((x,y,z), lastco)
                    lastco = (x,y,z)

                runIndex += 1
                if runIndex>=detailCount:
                    runIndex=0


            runIndex = detailCount+shiftCount+1
            if runIndex>=detailCount:
                runIndex=0

            # 18 floats * detailCount
            for i in range(detailCount):
                if int(lineIDX)!=-1:
                    L2 = list(data_detail[runIndex])
                    if int(lineIDX) == 5:
                        L2[int(lineIDX)] = bm.vertices[runIndex].co[2] * 100.0
                    elif int(lineIDX) != 1:
                        L2[int(lineIDX)] = bm.vertices[runIndex].co[2] / 100.0
                    else:
                        L2[int(lineIDX)] = bm.vertices[runIndex].co[2]
                    data_detail[runIndex] = tuple(L2)

                distL = data_detail[runIndex][6]
                distR = data_detail[runIndex][7]
                if (bmL!=0 and bmR!=0):
                    distL = distance(bm.vertices[runIndex].co,bmL.vertices[runIndex].co)
                    distR = distance(bm.vertices[runIndex].co,bmR.vertices[runIndex].co)

                data = struct.pack("18f",
                          data_detail[runIndex][0] , data_detail[runIndex][1] , data_detail[runIndex][2],
                          data_detail[runIndex][3] , data_detail[runIndex][4] , data_detail[runIndex][5],
                          distL                    , distR                    , data_detail[runIndex][8],
                          data_detail[runIndex][9] , data_detail[runIndex][10], data_detail[runIndex][11],
                          data_detail[runIndex][12], data_detail[runIndex][13], data_detail[runIndex][14],
                          data_detail[runIndex][15], data_detail[runIndex][16], data_detail[runIndex][17])
                buffer.write(data)
                runIndex += 1
                if runIndex>=detailCount:
                    runIndex=0

            # write rest of data unchanged
            buffer.write(data_rest)

    bpy.ops.object.mode_set ( mode = current_mode )

    print('... done!')
    return {'FINISHED'}


### use live in blender-script-editor
# filepath='p:/Steam/steamapps/common/assettocorsa/apps/python/CamInfo/fast_lane2.ai'
# filepath='p:/Steam/steamapps/common/assettocorsa/content/tracks/rt_bannochbrae/normal/ai/fast_lane.ai'
# save(bpy.context, filepath, 0, 0, False)
