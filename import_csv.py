"""
This script imports a AssettoCorsa CSV file to Blender.

Usage:
Run this script from "File->Import" menu and then load the desired CSV file.
"""


import bpy, bmesh, os, struct, csv, math, configparser, codecs
from mathutils import Vector
from bpy_extras.object_utils import object_data_add


def CenterOrigin(scaling):
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.ops.transform.resize(value=(scaling, scaling, scaling))


def distance(point1, point2) -> float:
    """Calculate distance between two points in 3D."""
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2 + (point2[2] - point1[2]) ** 2)


def load(context, filepath, scaling, doDoubleCheck, createFaces, ignoreLastEdge):

    print('import: ' + filepath)

    meshname=os.path.basename(filepath)
    csvfile = open(filepath)
    inFile = csv.reader(csvfile, delimiter=',', quotechar='"')
    # s = csvfile.read()
    # #print(s)
    # if ';' in s:
    # else:
    #     inFile = csv.reader(csvfile, delimiter=',', quotechar='"')

    # if not ',' in csvfile:
    #     inFile = csv.reader(csvfile, delimiter=' ', quotechar='"')
    # else:

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

    skipped = 0
    mesh = 0
    vertC = 0
    points=[]
    edges=[]
    edgeidx=0
    for row in inFile:
        #  column order (1: x, 2: z, 3: y)
        # coords = (float(row[0]),float(row[2]),float(row[1]))
        #print ( row[0] + "   " + row[2] + "   " + row[1] )
        #print ( str(row))
        v = Vector((float(row[0]),float(row[2]),float(row[1])))
        v[0]=v[0]*scaling
        v[1]=v[1]*scaling
        v[2]=-v[2]*scaling
        points.append(v)
        if edgeidx>=1:
            edges.append([edgeidx-1,edgeidx])
        edgeidx+=1


    mesh = 0
    meshname = os.path.basename(filepath)
    mesh = bpy.data.meshes.new(name=meshname)
    mesh.from_pydata( points, edges, [] )
    mesh.update()
    mesh.validate(verbose=True)
    mesh.update(calc_edges=True)
    mesh = object_data_add(bpy.context, mesh)
    meshname = mesh.name # update name, may have .001 or something


        # if mesh==0:
        #     mesh = bpy.data.meshes.new( name=meshname )
        #     mesh.from_pydata( [Vector(coords)], [], [] )
        #     mesh = object_data_add(bpy.context, mesh)
        #     meshname = mesh.name # update name, may have .001 or something
        #     bpy.context.view_layer.objects.active = bpy.data.objects[meshname]
        #     bpy.ops.object.mode_set(mode='EDIT')
        #     vertC = 1
        # else:
        #     mesh = bmesh.from_edit_mesh(bpy.data.objects[meshname].data)
        #     skip = False
        #     if doDoubleCheck:
        #         for ms in mesh.verts:
        #             #if (ms.co[0]-0.01 >= coords[0] and ms.co[0]+0.01 <= coords[0]) and  (ms.co[1]-0.01 >= coords[2] and ms.co[1]+0.01 <= coords[2]) and  (ms.co[2]-0.01 >= coords[1] and ms.co[2]+0.01 <= coords[1]):
        #             if distance(ms.co, coords)<0.1:
        #                 skipped += 1
        #                 skip = True
        #                 break
        #     if not skip:
        #         mesh.verts.new( coords )
        #         mesh.verts.ensure_lookup_table()
        #         mesh.edges.new([mesh.verts[len(mesh.verts)-2],mesh.verts[len(mesh.verts)-1]])
        #         bmesh.update_edit_mesh(bpy.data.objects[meshname].data)

    # # set last edge
    # if not ignoreLastEdge:
    #     if mesh>0:
    #         if mesh.verts[0] and mesh.verts[len(mesh.verts)-1]:
    #             mesh.edges.new( [ mesh.verts[0], mesh.verts[len(mesh.verts)-1] ] )
    #             print('Imported ' + str(len(mesh.verts)) + ' points, points skipped: ' + str(skipped) )

    ##bpy.ops.object.mode_set(mode='OBJECT')
    # CenterOrigin(scaling)

    return {'FINISHED'}

# obj.data.vertices[0].select = True

# filepath = "p:/Steam/steamapps/common/assettocorsa/content/tracks/rt_azure_coast/reverse/data/brkk.csv"
# load(bpy.context, filepath, 0.01, False, False, False)
