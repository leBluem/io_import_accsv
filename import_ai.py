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


def distance(point1, point2) -> float:
    """Calculate distance between two points in 3D."""
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2 + (point2[2] - point1[2]) ** 2)


def CreateMeshFromDataPoints(meshname, idx, data_ideal, data_detail, scaling, ignoreLastEdge):
    # create vertices from ai line data
    mesh = 0
    xl, z, yl, dist, id = data_ideal[len(data_ideal)-1]
    coords=[]
    edges=[]
    edgeidx=0
    maxrange = min(len(data_ideal), len(data_detail))
    for i in range(maxrange):
        x, z, y, dist, id = data_ideal[i]
        if idx!=-1:
            if idx==6 or idx==7:
                direction = -math.degrees( math.atan2(yl - y, x - xl))
                yl = y
                xl = x
                if idx==6:
                    if len(data_detail)>0:
                        _wallLeft = data_detail[i][6]
                        x = x + math.cos((-direction + 90) * math.pi / 180) * _wallLeft
                        y = y - math.sin((-direction + 90) * math.pi / 180) * _wallLeft
                else:
                    if len(data_detail)>0:
                        _wallRight= data_detail[i][7]
                        x = x + math.cos((-direction - 90) * math.pi / 180) * _wallRight
                        y = y - math.sin((-direction - 90) * math.pi / 180) * _wallRight
            elif idx==5:
                if len(data_detail)>0:
                    z = data_detail[i][idx] / 100.0
            elif idx==1:
                if len(data_detail)>0:
                    z = data_detail[i][idx]
            else:
                if len(data_detail)>0:
                    z = data_detail[i][idx] * 100
        coords.append( Vector( (float(x), -float(y), float(z)) ) )
        if i>=0 and i<maxrange-1:
            edges.append([edgeidx,edgeidx+1])
        edgeidx+=1

    # edges.pop()
    if not ignoreLastEdge:
        edges.append([edgeidx-1,0])
        #edges.pop()

    #if i % 1000 == 0:
    #    print(str(i) + "/" + str(len(data_ideal)))

    #if i==0:
    #    print('Import AC ai-line start-pos: ' + str(coords))
    mesh = bpy.data.meshes.new( name=meshname )
    mesh.from_pydata( coords, edges, [] )
    mesh.update()
    mesh.validate(verbose=True)
    mesh.update(calc_edges=True)
    mesh = object_data_add(bpy.context, mesh)
    meshname = mesh.name # update name, may have .001 or something

    bpy.context.view_layer.objects.active = bpy.data.objects[meshname]
    meda = mesh.data
    for i in range(1,len(meda.vertices)):
        meda.vertices[i].select = False
    #bpy.ops.object.mode_set(mode='EDIT')
    # else: # add to existing mesh
    #     mesh = bmesh.from_edit_mesh(bpy.data.objects[meshname].data)
    #     mesh.verts.new(coords)
    #     mesh.verts.ensure_lookup_table()
    #     mesh.edges.new([mesh.verts[len(mesh.verts)-2],mesh.verts[len(mesh.verts)-1]])
    #     bmesh.update_edit_mesh(bpy.data.objects[meshname].data)

    # set last edge
    #if not ignoreLastEdge:
    #    if mesh.verts[0] and mesh.verts[len(mesh.verts)-1]:
    #        mesh.edges.new( [ mesh.verts[0], mesh.verts[len(mesh.verts)-1] ] )

    #bpy.ops.object.mode_set(mode='OBJECT')

    # bpy.ops.view3d.snap_cursor_to_center()
    CenterOrigin(scaling)


def load(context, filepath, scaling, importExtraData, createCameras, maxDist, ignoreLastEdge):
    if not os.path.isfile(filepath):
        print("file not found")
        return {'ERROR'}
    filesize = os.stat(filepath).st_size
    with open(filepath, "rb") as buffer:
        print('import: ' + filepath)
        # print(os.path.basename(filepath))
        meshname       = os.path.basename(filepath)

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
        print('excected len: ' + str(detailCount))

        # read ideal-line data
        i=4*5
        c=0
        while i < filesize and c<detailCount:       # 4 floats, one integer
        #for i in range(detailCount):       # 4 floats, one integer
            data_ideal.append(struct.unpack("4f i", buffer.read(4 * 5)))
            i+=4*5
            c+=1
        print('len data_ideal : ' + str(len(data_ideal)))
        if c!=detailCount:
            print('data_ideal  truncated at: ' + str(c) + ' of expected ' + str(detailCount))
        if detailCount>len(data_ideal):
            print('data_detail do NOT match ! ')
            detailCount=len(data_ideal)

        # read more details data
        i+=4*18
        c=0
        while i < filesize:        # 18 floats
        #for i in range(detailCount):        # 18 floats
            #print(str(i))
            data_detail.append(struct.unpack("18f", buffer.read(4 * 18)))
            i+=4*18
            c+=1
        print('len data_detail: ' + str(len(data_detail)))
        if detailCount>len(data_detail):
            print('data_ideal/data_detail do NOT match ! ')
            detailCount=len(data_detail)


        if len(data_ideal)>1:
            xx, zx, yx, _, _ = data_ideal[len(data_ideal)-1]
            px=(xx, zx, yx)
            xx, zx, yx, _, _ = data_ideal[0]
            p1=(xx, zx, yx)
            xx, zx, yx, _, _ = data_ideal[1]
            p2=(xx, zx, yx)
            dist = distance(px,p1)*scaling
            dist2 = distance(p1,p2)*scaling
            ignoreLastEdge = False
            if dist>dist2*2:
                ignoreLastEdge = True
                print("ignore last!")


        #if createCameras:
        #    CreateCameras()


        print('creating meshes...')

        # build mesh from ai line
        if importExtraData:
            print('creating extra lines...')
            CreateMeshFromDataPoints(meshname + "__0_unknown"          , 0, data_ideal, data_detail, scaling, ignoreLastEdge)
            CreateMeshFromDataPoints(meshname + "__1_speed"            , 1, data_ideal, data_detail, scaling, ignoreLastEdge)
            CreateMeshFromDataPoints(meshname + "__2_gas"              , 2, data_ideal, data_detail, scaling, ignoreLastEdge)
            CreateMeshFromDataPoints(meshname + "__3_brake"            , 3, data_ideal, data_detail, scaling, ignoreLastEdge)
            CreateMeshFromDataPoints(meshname + "__4_obsoleteLatG"     , 4, data_ideal, data_detail, scaling, ignoreLastEdge)
            CreateMeshFromDataPoints(meshname + "__5_radius"           , 5, data_ideal, data_detail, scaling, ignoreLastEdge)

            CreateMeshFromDataPoints(meshname + "__8_camber"           , 8, data_ideal, data_detail, scaling, ignoreLastEdge)
            CreateMeshFromDataPoints(meshname + "__9_direction"        , 9, data_ideal, data_detail, scaling, ignoreLastEdge)
            CreateMeshFromDataPoints(meshname + "__10_normalx"         ,10, data_ideal, data_detail, scaling, ignoreLastEdge)
            CreateMeshFromDataPoints(meshname + "__11_normaly"         ,11, data_ideal, data_detail, scaling, ignoreLastEdge)
            CreateMeshFromDataPoints(meshname + "__12_normalz"         ,12, data_ideal, data_detail, scaling, ignoreLastEdge)
            CreateMeshFromDataPoints(meshname + "__13_length"          ,13, data_ideal, data_detail, scaling, ignoreLastEdge)
            CreateMeshFromDataPoints(meshname + "__14_forwardVectorx"  ,14, data_ideal, data_detail, scaling, ignoreLastEdge)
            CreateMeshFromDataPoints(meshname + "__15_forwardVectory"  ,15, data_ideal, data_detail, scaling, ignoreLastEdge)
            CreateMeshFromDataPoints(meshname + "__16_forwardVectorz"  ,16, data_ideal, data_detail, scaling, ignoreLastEdge)
            CreateMeshFromDataPoints(meshname + "__17_tag"             ,17, data_ideal, data_detail, scaling, ignoreLastEdge)

        CreateMeshFromDataPoints(meshname + "_6_border_left"          , 6, data_ideal, data_detail, scaling, ignoreLastEdge)
        CreateMeshFromDataPoints(meshname + "_7_border_right"         , 7, data_ideal, data_detail, scaling, ignoreLastEdge)
        CreateMeshFromDataPoints(meshname + "_0_ideal_line"           ,-1, data_ideal, data_detail, scaling, ignoreLastEdge)
    print('done.')
    return {'FINISHED'}



### for testing inside blender script editor:
### load(bpy.context,
### #"p:/Steam/steamapps/common/assettocorsa/content/tracks/EndlessFloor/ai/fast_lane.ai",
### "p:/Steam/steamapps/common/assettocorsa/content/tracks/rt_bannochbrae/normal/ai/fast_lane.ai",
###    0.01, True, False, False, True)
