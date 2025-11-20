"""
This script imports a AssettoCorsa KN5 files to Blender.

Usage:
Run this script from "File->Import" menu and then load the desired KN5 file(s).
"""


import bpy, bmesh, os, struct, csv, math, configparser, codecs
from mathutils import Vector
from bpy_extras.object_utils import object_data_add

import sys
import subprocess

def getFBX(subdirectory=''):
    if subdirectory:
        path = subdirectory
    else:
        path = os.getcwd()
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.lower().endswith('.fbx'):
                print("found: " + os.path.join(root, f))
                return os.path.join(root, f)
    return ""

def getDirs(subdirectory=''):
    d=[]
    if subdirectory:
        path = subdirectory
    else:
        path = os.getcwd()
    for root, dirs, files in os.walk(path):
        if dirs!='':
            d.append(dirs)
            # print(dirs)
            return d
    return d


def CenterOrigin(scaling):
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
    bpy.ops.transform.resize(value=(scaling, scaling, scaling))


def distance(point1, point2) -> float:
    """Calculate distance between two points in 3D."""
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2 + (point2[2] - point1[2]) ** 2)


def load(context, filepath, scaling):
    ##addondir = os.path.dirname(__file__
    #print(bpy.context.space_data.text.filepath)

    ### standalone ###
    # kn52fbx = os.path.dirname(bpy.context.space_data.text.filepath) + "/kn52fbx/kn52fbx.exe"

    ### called from __init__ ###
    kn52fbx = os.path.dirname(__file__) + "/kn52fbx/kn52fbx.exe"


    #print(kn52fbx)
    if not os.path.isfile(kn52fbx):
        print ("not found in addon folder: " + kn52fbx)
        return {"'CANCELLED"}

    print("Running " + kn52fbx + " " + filepath)

    blend_dir = os.path.dirname(filepath)
    if blend_dir not in sys.path:
        sys.path.append(blend_dir)

    ### snapshot folder
    dirs1 = getDirs(os.path.dirname(filepath))
    #print(dirs1)

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = 5 # SW_SHOW
    p=subprocess.Popen( [kn52fbx, "-x", filepath], startupinfo=startupinfo )
    exitcode = p.wait()
    # if exitcode:
    #     return {"CANCELLED", ""}

    ### snapshot folder again
    dirs2 = getDirs(os.path.dirname(filepath))
    print(dirs2)
    fbx=""
    if len(dirs2[0])<=len(dirs1[0]):
        print("Could not find exported files. Stop! " + os.path.dirname(filepath))
    else:
        for i in range(len(dirs2[0])):
            if i>=len(dirs1[0]) or (not dirs2[0][i] in dirs1[0]):
                ### new folder found, get the only fbx file that should be there
                print("searching " + os.path.dirname(filepath) +'/'+ dirs2[0][i])
                fbx = getFBX(os.path.dirname(filepath) +'/'+ dirs2[0][i])
                print("fbx: " + fbx)
                break

        if not os.path.isfile(fbx):
            print("No fbx file found! " + os.path.dirname(filepath))
        else:
            print("Importing " + fbx)


            # bpy.ops.object.mode_set(mode='OBJECT')
            # obj.data.vertices[0].select = True

            # insert stuff at origin
            # taken from, https://blenderartists.org/t/setting-origin-to-world-centre-using-blender-python/1174798
            if bpy.app.version[1]<80 and bpy.app.version[0]<3:
                # bpy.ops.transform.translate(value=(0, 0, 1), constraint_orientation='GLOBAL')
                bpy.context.scene.cursor_location[0], \
                bpy.context.scene.cursor_location[1], \
                bpy.context.scene.cursor_location[2] = 0, 0, 0
            else:
                # bpy.ops.transform.translate(value=(0, 0, 1), orient_type='GLOBAL')
                bpy.context.scene.cursor.location = Vector((0.0, 0.0, 0.0))
                bpy.context.scene.cursor.rotation_euler = Vector((0.0, 0.0, 0.0))


            ### Import FBX
            bpy.ops.import_scene.fbx( filepath=fbx, global_scale = scaling, axis_forward='X', axis_up='Z',use_custom_normals=False)
            ### ### Export blend file
            ### # bpy.ops.wm.save_mainfile( )
            # CenterOrigin(scaling)
            return {'FINISHED'}


    return {"CANCELLED"}


##### for testing inside blender script editor
# filepath = "p:/Steam/steamapps/common/assettocorsa/content/tracks/rt_azure_coast/reverse/data/brkk.csv"
## filepath = "p:\\Steam\\steamapps\\common\\assettocorsa\\content\\tracks\\fn_bahrain\\fn_bahrain_2008.kn5"
## load(bpy.context, filepath, 0.01)
