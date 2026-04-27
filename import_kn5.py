"""
This script imports a AssettoCorsa KN5 files to Blender.

Usage:
Run this script from "File->Import" menu and then load the desired KN5 file(s).
"""


import bpy, bmesh, os, io, struct, csv, math, configparser, collections, codecs
from mathutils import Vector
from bpy_extras.object_utils import object_data_add

import sys
import subprocess


def get_diffuse_image_from_material(material_name):
    mat = bpy.data.materials.get(material_name)
    # Prüfen, ob Material existiert und Nodes verwendet
    if mat and mat.use_nodes:
        principled = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if principled:
            base_color_input = principled.inputs['Base Color']
            if base_color_input.is_linked:
                connected_node = base_color_input.links[0].from_node
                if connected_node.type == 'TEX_IMAGE' and connected_node.image:
                    return connected_node
    return None

def get_alpha_image_from_material(material_name):
    """
    Sucht nach einem Bild mit Alpha-Kanal innerhalb eines Materials.
    Gibt das Image-Objekt zurück, falls gefunden, sonst None.
    """
    # Material über Namen aus den Blender-Daten abrufen
    mat = bpy.data.materials.get(material_name)
    # Prüfen, ob Material existiert und Nodes verwendet
    if mat and mat.use_nodes:
        for node in mat.node_tree.nodes:
            # Nur Image Texture Nodes mit zugewiesenem Bild prüfen
            if node.type == 'TEX_IMAGE' and node.image:
                img = node.image
                # Validierung: Hat das Bild 4 Kanäle (RGBA) und ist Alpha nicht deaktiviert?
                if img.channels == 4 and img.alpha_mode != 'NONE':
                    return img
    return None

def RemoveAlphaChannel(context, inimatname):
    selected_objs = context.selected_objects.copy()
    for o in selected_objs:
        for s in o.material_slots:
            if s.material.name == inimatname:
                if s.material and s.material.use_nodes:
                    for n in s.material.node_tree.nodes:
                        s.material.blend_method = 'OPAQUE'
                        if 'Alpha' in n.inputs:
                            input_alpha = n.inputs['Alpha']
                            if input_alpha.is_linked:
                                print('material ' + inimatname + ': removing alpha' )
                                links = s.material.node_tree.links
                                for link in links:
                                    if link.to_socket == input_alpha:
                                        links.remove(link)
                            input_alpha.default_value = 1.0

def SetAlphaChannel(context, inimatname):
    selected_objs = context.selected_objects.copy()
    for o in selected_objs:
        for s in o.material_slots:
            if s.material.name == inimatname:
                if s.material and s.material.use_nodes:
                    for n in s.material.node_tree.nodes:
                        if 'Alpha' in n.inputs:
                            links = s.material.node_tree.links
                            nodes = s.material.node_tree.nodes
                            input_alpha = n.inputs['Alpha']
                            # bpy.data.images["Skin_00.dds"].alpha_mode = 'STRAIGHT'
                            if input_alpha.is_linked:
                                # diffuse = get_diffuse_image_from_material(s.material.name)
                                # n.image.filepath = diffuse
                                if n.type == 'TEX_IMAGE' and n.image:
                                    n.image.alpha_mode = 'STRAIGHT'
                                pass
                            else:
                                principled = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
                                if principled:
                                    base_color_input = principled.inputs['Base Color']
                                    if base_color_input.is_linked:
                                        connected_node = base_color_input.links[0].from_node
                                        if connected_node.type == 'TEX_IMAGE' and connected_node.image:
                                            # found Base Color image
                                            # bname=str(os.path.basename(connected_node.image.filepath)).lower()
                                            print('setting alpha to diffuse')
                                            diffuse = get_diffuse_image_from_material(s.material.name)
                                            connected_node.image.alpha_mode = 'STRAIGHT'
                                            # diffuse.alpha_mode = 'STRAIGHT'
                                            shader_node = next((m for m in nodes if m.type == 'BSDF_PRINCIPLED'), None)
                                            links.new(diffuse.outputs['Alpha'], shader_node.inputs['Alpha'])
                            # else:
                            # if not input_alpha.is_linked:
                                # s.material.node_tree.links.new(shader.inputs['Alpha'], n.outputs['Alpha'])
                                # links.new(img_node.outputs['Alpha'], shader_node.inputs['Alpha'])
                                # input_alpha = n.inputs['Alpha']




def ScanFBXINI(context, THEFILE):
    if not os.path.isfile(THEFILE):
        print('.FBX.ini not found: ' + THEFILE)
    else:
        matsBlender=[]
        matsB=[]
        c=0
        selected_objs = bpy.context.selected_objects.copy()
        # selected_objs = bpy.context.o

        for o in selected_objs:
            for s in o.material_slots:
                if not s.material.name in matsBlender:
                    if s.material and s.material.use_nodes:
                        matsBlender.append(s.material.name)
                        matsB.append(s.material)

        # for s in bpy.data.materials:
        #     if not s.name in matsBlender:
        #         if s.use_nodes:
        #             matsBlender.append(s.name)
        #             matsB.append(s)

        print('reading ' + THEFILE)
        fbxini = configparser.ConfigParser({}, collections.OrderedDict, empty_lines_in_values=False, strict=False, allow_no_value=True, inline_comment_prefixes=(";","#","/","_","|"), comment_prefixes=(";","#","/","_","|"))
        fbxini.optionxform=str # keep upper/lower case
        fbxini.read(THEFILE)
        fbxmatcnt = 0
        if fbxini.has_section('MATERIAL_LIST'):
            fbxmatcnt = int(fbxini.get('MATERIAL_LIST','COUNT'))

        print('Blender materials: ' + str(len(matsBlender)))
        matsdone=[]
        for i in range(len(matsBlender)):
            BlenderMat=matsBlender[i]
            found = False
            for j in range(fbxmatcnt):
                matsect = 'MATERIAL_'+str(j)
                if fbxini.has_section(matsect):
                    inimatname = fbxini.get(matsect,'NAME')
                    if BlenderMat == inimatname and not inimatname in matsdone:
                        matsdone.append(inimatname)
                        found = True

                        sBlendVal = '0'
                        sTestVal = '0'
                        sTex0 = ''
                        if fbxini.has_option(matsect,'ALPHABLEND'):
                            sBlendVal = fbxini.get(matsect,'ALPHABLEND')
                        if fbxini.has_option(matsect,'ALPHATEST'):
                            sTestVal = fbxini.get(matsect,'ALPHATEST')
                        if fbxini.has_option(matsect,'RES_0_TEXTURE'):
                            sTex0 = fbxini.get(matsect,'RES_0_TEXTURE').lower()

                        if sBlendVal == '1' or sTestVal == '1':
                            if matsB[i].blend_method != 'BLEND':
                                print('material ' + inimatname + ': ' + matsB[i].blend_method + ' -> ' + 'BLEND')
                                ### set Alpha channel image
                                matsB[i].blend_method = 'BLEND'
                            SetAlphaChannel(context, inimatname)
                        else:
                            if matsB[i].blend_method != 'OPAQUE':
                                print('material ' + inimatname + ': ' + matsB[i].blend_method + ' -> ' + 'OPAQUE')
                                ### remove Alpha channel image
                                matsB[i].blend_method = 'OPAQUE'
                            # if get_alpha_image_from_material(inimatname)!=None:
                            RemoveAlphaChannel(context, inimatname)

                        # check if diffuse image is still same
                        nodes = matsB[i].node_tree.nodes
                        principled = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
                        if principled:
                            base_color_input = principled.inputs['Base Color']
                            if base_color_input.is_linked:
                                connected_node = base_color_input.links[0].from_node
                                if connected_node.type == 'TEX_IMAGE' and connected_node.image:
                                    bname=str(os.path.basename(connected_node.image.filepath)).lower()
                                    if sBlendVal == '0' and sTestVal == '0':
                                        connected_node.image.alpha_mode = 'NONE'
                                    bdir=os.path.dirname(connected_node.image.filepath)
                                    if sTex0!='' and bname!=sTex0 and os.path.isfile(bdir + sTex0):
                                        print('Setting new image: '+bdir + sTex0 )
                                        connected_node.image.filepath = bdir + sTex0
                                        ### no
                                        ### SetAlphaChannel(context, inimatname)

            if not found:
                print("material '" + BlenderMat + "' not found in .ini")
        print('Done scanning ' + str(fbxmatcnt) + ' FBXINI materials')


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

    if __name__ == "__main__":
        ### standalone ###
        kn52fbx = os.path.dirname(bpy.context.space_data.text.filepath) + "/kn52fbx/kn52fbx.exe"
    else:
        ### called from __init__ ###
        kn52fbx = os.path.dirname(__file__) + "/kn52fbx/kn52fbx.exe"


    #print(kn52fbx)
    if not os.path.isfile(kn52fbx):
        print ("not found in addon folder: " + kn52fbx)
        return {"'CANCELLED"}

    blend_dir = os.path.dirname(filepath)
    if blend_dir not in sys.path:
        sys.path.append(blend_dir)

    ### snapshot folder
    dirs1 = getDirs(os.path.dirname(filepath))
    #print(dirs1)

    print("Running " + kn52fbx + " " + filepath)

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
            bpy.ops.import_scene.fbx(filepath=fbx, global_scale = scaling, axis_forward='X', axis_up='Z',use_custom_normals=False)
            ### ### Export blend file
            ### # bpy.ops.wm.save_mainfile( )
            # CenterOrigin(scaling)

            ### fix transparent materials
            ##ScanFBXINI(bpy.context, fbx+'.ini')

            return {'FINISHED'}

    return {"CANCELLED"}


if __name__ == "__main__":
    ##### for testing inside blender script editor
    filepath = "p:/Steam/steamapps/common/assettocorsa/content/cars/ks_mazda_mx5_cup/unp_mazda_mx5_lod_a.kn5/Mazda_MX5_lod_A.fbx"

    ####load(bpy.context, filepath, 1.0)
    ScanFBXINI(bpy.context, filepath+'.ini')

    pass
