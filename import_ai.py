"""
This script imports AssettoCorsa fast_lane.ai/ideal_line.ai into Blender.

Usage:
Run this script from "File->Import" menu and then load the desired *.ai file.
"""

import bpy, bmesh, os, struct, math, io, traceback
from mathutils import Vector
from bpy_extras.object_utils import object_data_add


def CenterOrigin(scaling):
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.ops.transform.resize(value=(scaling, scaling, scaling))


def distance(point1, point2) -> float:
    """Calculate distance between two points in 3D."""
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2 + (point2[2] - point1[2]) ** 2)


def CreateMeshFromDataPoints(meshname, idx, data_ideal, data_detail, scaling, ignoreLastEdge):
    # create vertices from ai line data
    mesh = 0
    if idx!=-1:
        if idx==2:
            meshname = meshname + str(idx) + '_gas'
        elif idx==3:
            meshname = meshname + str(idx) + '_brake'
        elif idx==5:
            meshname = meshname + str(idx) + '_notbrake'
        elif idx==13:
            meshname = meshname + str(idx) + '_gear'
        else:
            meshname = meshname + str(idx)
    xl, z, yl, dist, id = data_ideal[len(data_ideal)-1]
    for i in range(len(data_ideal)):
        x, z, y, dist, id = data_ideal[i]
        if idx!=-1:
            if idx==6 or idx==7:
                direction = -math.degrees( math.atan2(yl - y, x - xl))
                yl = y
                xl = x
                _wallLeftRight = data_detail[i][idx]
                if idx==6:
                    x = x + math.cos((-direction + 90) * math.pi / 180) * _wallLeftRight
                    y = y - math.sin((-direction + 90) * math.pi / 180) * _wallLeftRight
                else:
                    x = x + math.cos((-direction - 90) * math.pi / 180) * _wallLeftRight
                    y = y - math.sin((-direction - 90) * math.pi / 180) * _wallLeftRight
            elif idx==5:
                z = data_detail[i][idx] / 100.0
            elif idx==1:
                z = data_detail[i][idx]
            else:
                z = data_detail[i][idx] * 100
        coords = ( float(x), -float(y), float(z)  )
        if i % 1000 == 0:
            print(str(i) + "/" + str(len(data_ideal)))

        if i==0:
            print('Import AC ai-line start-pos: ' + str(coords))
        if mesh==0: # create new mesh
            mesh = bpy.data.meshes.new( name=meshname )
            mesh.from_pydata( [Vector(coords)] , [], [] )
            mesh = object_data_add(bpy.context, mesh)
            meshname = mesh.name # update name, may have .001 or something
            bpy.context.view_layer.objects.active = bpy.data.objects[meshname]
            bpy.ops.object.mode_set(mode='EDIT')
        else: # add to existing mesh
            mesh = bmesh.from_edit_mesh(bpy.data.objects[meshname].data)
            mesh.verts.new(coords)
            mesh.verts.ensure_lookup_table()
            mesh.edges.new([mesh.verts[len(mesh.verts)-2],mesh.verts[len(mesh.verts)-1]])
            bmesh.update_edit_mesh(bpy.data.objects[meshname].data)
    # set last edge
    if not ignoreLastEdge:
        if mesh.verts[0] and mesh.verts[len(mesh.verts)-1]:
            mesh.edges.new( [ mesh.verts[0], mesh.verts[len(mesh.verts)-1] ] )
    bpy.ops.object.mode_set(mode='OBJECT')
    print('done!')
    # bpy.ops.view3d.snap_cursor_to_center()
    CenterOrigin(scaling)


def appGetNumberedFilename(sBase, sExt):
    try:
        newname=sBase + sExt
        i=1
        while os.path.isfile(newname) and i<20:
            newname = sBase + '_' + str(i) + sExt
            i+=1
        if i>=20:
            return ''
        return newname
    except:
        print("import ai line: " + traceback.format_exc())


def get_ac_coords(ob):
  ss=str(ob.matrix_world.to_translation()).replace('<Vector (','')
  ss=ss.replace(')>','')
  ss=ss.replace(' ','')
  sss = ss.split(',')
  print(str(round(float(sss[0])*100.0, 4) )+', '
       +str(round(float(sss[2])*100, 4) ) + ', '
       +str(round(float(sss[1])*(-100.0), 4) ) )


def buildCameraEntry(cCount, fCamPos, fOrientation, fOrientationUP, lPoT, cPoT, vminFov=30, vmaxFov=50, isFixed=False):
    return ('[CAMERA_' + str(cCount) + ']'
            + '\nNAME=Camera ' + str(cCount)
            + '\nPOSITION=' + fCamPos
            + '\nFORWARD=' + fOrientation
            + '\nUP=' + fOrientationUP
            + '\nMIN_FOV=' + str(vminFov)
            + '\nMAX_FOV=' + str(vmaxFov)
            + '\nIN_POINT=' + str(round(lPoT,6))
            + '\nOUT_POINT=' + str(round(cPoT,6))
            + '\nSHADOW_SPLIT0=50'
            + '\nSHADOW_SPLIT1=250'
            + '\nSHADOW_SPLIT2=1350'
            + '\nNEAR_PLANE=0.1'
            + '\nFAR_PLANE=10000'
            + '\nMIN_EXPOSURE=0.35'
            + '\nMAX_EXPOSURE=0.55'
            + '\nDOF_FACTOR=1'
            + '\nDOF_RANGE=100'
            + '\nDOF_FOCUS=0'
            + '\nDOF_MANUAL=0'
            + '\nSPLINE='
            + '\nSPLINE_ROTATION=0'
            + '\nFOV_GAMMA=0.5'
            + '\nSPLINE_ANIMATION_LENGTH=0'
            + '\nIS_FIXED=' + str(isFixed) + '\n')

def CreateCamerasFromDataPoints(data_ideal, data_detail, scaling, maxDist):
        # create vertices from ai line data
        mesh = 0
        idx = 0
        camidx = 0
        odd = True
        camini = ""
        datalen = len(data_ideal)
        xlast, z, ylast, dist, id = data_ideal[datalen-1]
        for i in range(datalen):
            x, z, y, dist, id = data_ideal[i]
            direction = -math.degrees( math.atan2(ylast - y, x - xlast))
            xlast = x
            ylast = y
            _wallLeft = data_detail[i][6]
            xl = x + math.cos((-direction + 90) * math.pi / 180) * _wallLeft
            yl = y - math.sin((-direction + 90) * math.pi / 180) * _wallLeft
            _wallRight= data_detail[i][7]
            xr = x + math.cos((-direction - 90) * math.pi / 180) * _wallRight
            yr = y - math.sin((-direction - 90) * math.pi / 180) * _wallRight
            cPoT = int(i/datalen)

            if dist>maxDist==0: # create new mesh
                meshname = 'CAMERA_' + str(camidx)
                if odd:
                    coords = ( float(xl), -float(yl), float(z+2)  )
                else:
                    coords = ( float(xr), -float(yr), float(z+2)  )

                # mesh = bpy.data.meshes.new( name=meshname )
                # mesh.from_pydata( [Vector(coords)] , [], [] )
                # mesh = object_data_add(bpy.context, mesh)

                bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=(float(coords[0])*scaling, -float(coords[2])*scaling, float(coords[1])*scaling ), scale=(scaling*5, scaling*5, scaling*5))
                bpy.context.object.name = meshname

                # fOrientation, fOrientationUP
                camini += buildCameraEntry(camidx, get_ac_coords(coords), "0,0,1", "0,1,0", lPoT, cPoT, 30, 50)

                camidx += 1
                odd = not odd
                lPoT = cPoT

            idx += 1

        return camini

        #bpy.ops.object.mode_set(mode='OBJECT')
        ### CenterOrigin(scaling)




def load(context, filepath, scaling, importExtraData, createCameras, maxDist, ignoreLastEdge):
    with open(filepath, "rb") as buffer:
        print('import: ' + filepath)
        # print(os.path.basename(filepath))
        meshname       = os.path.basename(filepath)
        meshnameBL     = meshname + '_border_left'
        meshnameBR     = meshname + '_border_right'
        meshnameDetail = meshname + '_detail'

        # insert stuff at origin
        # taken from, https://blenderartists.org/t/setting-origin-to-world-centre-using-blender-python/1174798
        if bpy.app.version[1]<80 and bpy.app.version[0]<3:
            bpy.ops.transform.translate(value=(0, 0, 1), constraint_orientation='GLOBAL')
            bpy.context.scene.cursor_location[0], \
            bpy.context.scene.cursor_location[1], \
            bpy.context.scene.cursor_location[2] = 0, 0, 0
        else:
            bpy.ops.transform.translate(value=(0, 0, 1), orient_type='GLOBAL')
            bpy.context.scene.cursor.location = Vector((0.0, 0.0, 0.0))
            bpy.context.scene.cursor.rotation_euler = Vector((0.0, 0.0, 0.0))

        # temporary arrays
        data_ideal = []
        data_detail = []

        # should be at start, but do it anyway
        buffer.seek(0)
        # read header, detailCount is number of data points available
        header, detailCount, u1, u2 = struct.unpack("4i", buffer.read(4 * 4))
        print(filepath)
        print('len: ' + str(detailCount))

        # read ideal-line data
        for i in range(detailCount):       # 4 floats, one integer
            data_ideal.append(struct.unpack("4f i", buffer.read(4 * 5)))
        # read more details data
        for i in range(detailCount):        # 18 floats
            data_detail.append(struct.unpack("18f", buffer.read(4 * 18)))

        # now comes more data, no info available for that

        if createCameras:
            print('creating cameras...')
            camini = CreateCamerasFromDataPoints(data_ideal, data_detail, scaling, maxDist)
            if camini != '':
                sFileDir = os.path.dirname(filepath).replace('\\', '/').replace('/ai', '/data')
                sFileCameras = appGetNumberedFilename(sFileDir + '/cameras', '.ini')
                with io.open(sFileCameras, 'w', encoding='utf-8') as f:
                    f.write(camini)

        else:
            print('creating meshes...')

            # build mesh from ai line
            CreateMeshFromDataPoints(meshnameBL , 6, data_ideal, data_detail, scaling, ignoreLastEdge)
            CreateMeshFromDataPoints(meshnameBR , 7, data_ideal, data_detail, scaling, ignoreLastEdge)
            if importExtraData:
                print('creating extra lines...')
                CreateMeshFromDataPoints(meshnameDetail , 0, data_ideal, data_detail, scaling, ignoreLastEdge)
                CreateMeshFromDataPoints(meshnameDetail , 1, data_ideal, data_detail, scaling, ignoreLastEdge)
                CreateMeshFromDataPoints(meshnameDetail , 2, data_ideal, data_detail, scaling, ignoreLastEdge)
                CreateMeshFromDataPoints(meshnameDetail , 3, data_ideal, data_detail, scaling, ignoreLastEdge)
                CreateMeshFromDataPoints(meshnameDetail , 4, data_ideal, data_detail, scaling, ignoreLastEdge)
                CreateMeshFromDataPoints(meshnameDetail , 5, data_ideal, data_detail, scaling, ignoreLastEdge)
                CreateMeshFromDataPoints(meshnameDetail , 8, data_ideal, data_detail, scaling, ignoreLastEdge)
                CreateMeshFromDataPoints(meshnameDetail , 9, data_ideal, data_detail, scaling, ignoreLastEdge)
                CreateMeshFromDataPoints(meshnameDetail ,10, data_ideal, data_detail, scaling, ignoreLastEdge)
                CreateMeshFromDataPoints(meshnameDetail ,11, data_ideal, data_detail, scaling, ignoreLastEdge)
                CreateMeshFromDataPoints(meshnameDetail ,12, data_ideal, data_detail, scaling, ignoreLastEdge)
                CreateMeshFromDataPoints(meshnameDetail ,13, data_ideal, data_detail, scaling, ignoreLastEdge)
                CreateMeshFromDataPoints(meshnameDetail ,14, data_ideal, data_detail, scaling, ignoreLastEdge)
                CreateMeshFromDataPoints(meshnameDetail ,15, data_ideal, data_detail, scaling, ignoreLastEdge)
                CreateMeshFromDataPoints(meshnameDetail ,16, data_ideal, data_detail, scaling, ignoreLastEdge)
                CreateMeshFromDataPoints(meshnameDetail ,17, data_ideal, data_detail, scaling, ignoreLastEdge)
            CreateMeshFromDataPoints(meshname       ,-1, data_ideal, data_detail, scaling, ignoreLastEdge)


    print('done.')
    return {'FINISHED'}



if __name__ == '__main__':

    filepath = ''
    with open(filepath, "rb") as buffer:
        print('import: ' + filepath)
        # print(os.path.basename(filepath))
        meshname       = os.path.basename(filepath)
        meshnameBL     = meshname + '_border_left'
        meshnameBR     = meshname + '_border_right'
        meshnameDetail = meshname + '_detail'

        # insert stuff at origin
        # taken from, https://blenderartists.org/t/setting-origin-to-world-centre-using-blender-python/1174798
        if bpy.app.version[1]<80 and bpy.app.version[0]<3:
            bpy.ops.transform.translate(value=(0, 0, 1), constraint_orientation='GLOBAL')
            bpy.context.scene.cursor_location[0], \
            bpy.context.scene.cursor_location[1], \
            bpy.context.scene.cursor_location[2] = 0, 0, 0
        else:
            bpy.ops.transform.translate(value=(0, 0, 1), orient_type='GLOBAL')
            bpy.context.scene.cursor.location = Vector((0.0, 0.0, 0.0))
            bpy.context.scene.cursor.rotation_euler = Vector((0.0, 0.0, 0.0))

        # temporary arrays
        data_ideal = []
        data_detail = []

        # should be at start, but do it anyway
        buffer.seek(0)
        # read header, detailCount is number of data points available
        header, detailCount, u1, u2 = struct.unpack("4i", buffer.read(4 * 4))
        print(filepath)
        print('len: ' + str(detailCount))

        # read ideal-line data
        for i in range(detailCount):       # 4 floats, one integer
            data_ideal.append(struct.unpack("4f i", buffer.read(4 * 5)))
        # read more details data
        for i in range(detailCount):        # 18 floats
            data_detail.append(struct.unpack("18f", buffer.read(4 * 18)))

        camini = CreateCamerasFromDataPoints(data_ideal, data_detail, scaling, maxDist)
        if camini != '':
            sFileDir = os.path.dirname(filepath).replace('\\', '/').replace('/ai', '/data')
            sFileCameras = appGetNumberedFilename(sFileDir + '/cameras', '.ini')
            with io.open(sFileCameras, 'w', encoding='utf-8') as f:
                f.write(camini)
