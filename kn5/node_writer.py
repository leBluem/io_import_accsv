limit=2**16

# Copyright (C) 2014  Thomas Hagnhofer
# edited by leBluem

from exporter_utils import (
    convert_matrix,
    convert_vector3_normal,
    convert_vector3,
    get_active_material_texture_slot,
)
from kn5_writer import KN5Writer
import re

import bmesh
from mathutils import Matrix
import math

import traceback

halfrotmat = Matrix.Rotation(math.pi,4,'X')

KN5_HEADER_BYTES = b"sc6969"
NODES = "nodes"

NODE_CLASS = {
    "Node" : 1,
    "Mesh" : 2,
    "SkinnedMesh" : 3,
}

NODE_SETTINGS = (
    "lodIn",
    "lodOut",
    "layer",
    "castShadows",
    "isVisible",
    "isTransparent",
    "isRenderable",
)

ASSETTO_CORSA_OBJECTS = (
    r"AC_START_\d+",
    r"AC_PIT_\d+",
    r"AC_TIME_\d+_L",
    r"AC_TIME_\d+_R",
    r"AC_HOTLAP_START_\d+",
    r"AC_OPEN_FINISH_R",
    r"AC_OPEN_FINISH_L",
    r"AC_OPEN_START_L",
    r"AC_OPEN_START_R",
    r"AC_AUDIO_.+",
    r"AC_CREW_\d+"
)


class NodeWriter(KN5Writer):
    def __init__(self, file, context, settings, warnings, material_writer, scaling, basename):
        super().__init__(file)

        self.context = context
        self.selected_obj = context.selected_objects.copy()
        self.settings = settings
        self.warnings = warnings
        self.material_writer = material_writer
        self.scene = self.context.scene
        self.node_settings = []
        self.ac_objects = []
        self.scaling = scaling
        self.basename = basename
        self._node_settings_key = NODE_SETTINGS
        self._init_assetto_corsa_objects()
        self._init_node_settings()

    def _init_node_settings(self):
        print('init nodes')
        self.node_settings = []
        if NODES in self.settings:
            for obj in self.selected_obj:
                self.node_settings.append(NodeSettings(self.settings, obj.name))
            #for node_key in self.settings[NODES]:
            #    self.node_settings.append(NodeSettings(self.settings, node_key))

    def _init_assetto_corsa_objects(self):
        print('init acobjs')
        for obj_name in ASSETTO_CORSA_OBJECTS:
            self.ac_objects.append(re.compile(f"^{obj_name}$"))

    def _is_ac_object(self, name):
        for regex in self.ac_objects:
            if regex.match(name):
                return True
        return False

    def write(self):
        c=0
        self._write_base_node(None, self.basename+'.fbx')
        iObjs = 0
        for obj in self.selected_obj:
            if obj.type == "MESH" or obj.type == "EMPTY":
                iObjs += 1
        print('writing ' + str(iObjs) + ' meshes')

        #for obj in sorted(self.context.blend_data.objects, key=lambda k: len(k.children)):
        for obj in sorted(self.selected_obj, key=lambda k: len(k.children)):
        #for obj in self.selected_obj:
            ###if obj.type == "MESH" or obj.type == "EMPTY":
            if obj.type == "MESH" or obj.type == "EMPTY":
                c+=1
                #if c%20==0:
                # print('\r' + str(c) + ' of ' + str(iObjs) + ' - ' + str(len(obj.data.vertices)) + ' verts: ' + obj.name + '                                                          ', end='')
                # print(str(c) + ' of ' + str(iObjs) + ' - ' + str(len(obj.data.vertices)) + ' verts: ' + obj.name)
                print('  ' + str(c) + ' of ' + str(iObjs) + ' - ' + str(len(obj.data.vertices)) + ' verts: ' + obj.name)
                #self._write_mesh_node(obj)
                self._write_object(obj)
        # print('')

    def _write_object(self, obj):
        if obj.type == "MESH":
            self._write_mesh_node(obj)
        else:
            self._write_base_node(obj, obj.name)
        for child in obj.children:
            self._write_object(child)

    def _any_child_is_mesh(self, obj):
        for child in obj.children:
            if child.type in ["MESH"] or self._any_child_is_mesh(child):
                return True
        return False

    def _write_base_node(self, obj, node_name):
        node_data = {}
        matrix = None
        num_children = 0
        if not obj:
            # print('fbx:'+node_name)
            matrix = Matrix()
            for obj in self.selected_obj:
            #for obj in self.context.blend_data.objects:
                #if not obj.parent and not obj.name.startswith("__"):
                #if not obj.parent:
                num_children += 1
                # if obj.children:
                #     for child in obj.children:
                #         if not child.parent:
                #             num_children += 1
            print('basenode   ---   ' + node_name + ' | ' + str(num_children) + ' objects')

        else:
            if not self._is_ac_object(obj.name) and not self._any_child_is_mesh(obj):
                print('ignoring non mesh/empty: ' + obj.name)
                # msg = f"Unknown logical object '{obj.name}' might prevent other objects from loading.{os.linesep}"
                # msg += "\tRename it to '__{obj.name}' if you do not want to export it."
                # self.warnings.append(msg)

            matrix = convert_matrix(obj.matrix_local)
            num_children = len(obj.children)
            for child in obj.children:
                if not child.parent:
                    num_children += 1

        node_data["name"] = node_name
        node_data["childCount"] = num_children
        node_data["active"] = True
        node_data["transform"] = matrix
        self._write_base_node_data(node_data)

    def _write_base_node_data(self, node_data):
        self._write_node_class("Node")
        self.write_string(node_data["name"])
        self.write_uint(node_data["childCount"])
        self.write_bool(node_data["active"])
        self.write_matrix(node_data["transform"])

    def _write_mesh_node(self, obj):
        divided_meshes = self._split_object_by_materials(obj)
        divided_meshes = self._split_meshes_for_vertex_limit(divided_meshes)
        if obj.parent or len(divided_meshes) > 1:
            node_data = {}
            node_data["name"] = obj.name
            node_data["childCount"] = len(divided_meshes)
            node_data["active"] = True
            transform_matrix = Matrix()
            if obj.parent:
                transform_matrix = convert_matrix(obj.parent.matrix_world.inverted())
            #else:
            #    transform_matrix = convert_matrix(obj.matrix_world)
            node_data["transform"] = transform_matrix
            self._write_base_node_data(node_data)
        node_properties = NodeProperties(obj)
        for node_setting in self.node_settings:
            node_setting.apply_settings_to_node(node_properties)
        if not (NODES in self.settings):
            print('properties not found for ' + obj.name)
        else:
            if obj.name in self.settings[NODES]:
                ### debug
                #print('setting properties for ' + obj.name)
                for prop in self.settings[NODES][obj.name]:
                    ### debug
                    #print(str(prop))
                    if 'lodin'       in prop.lower() or 'lod_in'       in prop.lower():
                        node_properties.lodIn       = self.settings[NODES][obj.name][prop]
                    if 'lodout'      in prop.lower() or 'lod_out'      in prop.lower():
                        node_properties.lodOut      = self.settings[NODES][obj.name][prop]
                    if 'layer'       in prop.lower():
                        node_properties.layer       = self.settings[NODES][obj.name][prop]
                    if 'castshadows' in prop.lower() or 'cast_shadows' in prop.lower():
                        node_properties.castShadows = self.settings[NODES][obj.name][prop]
                    if 'visible'     in prop.lower() or 'isvisible'     in prop.lower() or 'is_visible'     in prop.lower():
                        node_properties.visible     = self.settings[NODES][obj.name][prop]
                    if 'transparent' in prop.lower() or 'istransparent' in prop.lower() or 'is_transparent' in prop.lower():
                        node_properties.transparent = self.settings[NODES][obj.name][prop]
                    if 'renderable'  in prop.lower():
                        node_properties.renderable  = self.settings[NODES][obj.name][prop]
        for mesh in divided_meshes:
            self._write_mesh(obj, mesh, node_properties)

    def _write_node_class(self, node_class):
        self.write_uint(NODE_CLASS[node_class])

    def _write_mesh(self, obj, mesh, node_properties):
        self._write_node_class("Mesh")
        self.write_string(obj.name)
        if len(obj.children)>0:
            print('children: ' +str(len(obj.children)) )
        self.write_uint(len(obj.children))
        is_active = True
        self.write_bool(is_active)
        self.write_bool(node_properties.castShadows)
        self.write_bool(node_properties.visible)
        self.write_bool(node_properties.transparent)
        if len(mesh.vertices) > limit:
            raise Exception(f"Only {limit} vertices per mesh allowed. ('{obj.name}')")
        self.write_uint(len(mesh.vertices))

        c=0
        while c<len(mesh.vertices):
            if c+16<len(mesh.vertices):
                self.write_vector16((mesh.vertices[c   ].co.x*self.scaling, mesh.vertices[c   ].co.y*self.scaling, mesh.vertices[c   ].co.z*self.scaling), mesh.vertices[c   ].normal, mesh.vertices[c   ].uv, mesh.vertices[c   ].tangent,
                                    (mesh.vertices[c+ 1].co.x*self.scaling, mesh.vertices[c+ 1].co.y*self.scaling, mesh.vertices[c+ 1].co.z*self.scaling), mesh.vertices[c+ 1].normal, mesh.vertices[c+ 1].uv, mesh.vertices[c+ 1].tangent,
                                    (mesh.vertices[c+ 2].co.x*self.scaling, mesh.vertices[c+ 2].co.y*self.scaling, mesh.vertices[c+ 2].co.z*self.scaling), mesh.vertices[c+ 2].normal, mesh.vertices[c+ 2].uv, mesh.vertices[c+ 2].tangent,
                                    (mesh.vertices[c+ 3].co.x*self.scaling, mesh.vertices[c+ 3].co.y*self.scaling, mesh.vertices[c+ 3].co.z*self.scaling), mesh.vertices[c+ 3].normal, mesh.vertices[c+ 3].uv, mesh.vertices[c+ 3].tangent,
                                    (mesh.vertices[c+ 4].co.x*self.scaling, mesh.vertices[c+ 4].co.y*self.scaling, mesh.vertices[c+ 4].co.z*self.scaling), mesh.vertices[c+ 4].normal, mesh.vertices[c+ 4].uv, mesh.vertices[c+ 4].tangent,
                                    (mesh.vertices[c+ 5].co.x*self.scaling, mesh.vertices[c+ 5].co.y*self.scaling, mesh.vertices[c+ 5].co.z*self.scaling), mesh.vertices[c+ 5].normal, mesh.vertices[c+ 5].uv, mesh.vertices[c+ 5].tangent,
                                    (mesh.vertices[c+ 6].co.x*self.scaling, mesh.vertices[c+ 6].co.y*self.scaling, mesh.vertices[c+ 6].co.z*self.scaling), mesh.vertices[c+ 6].normal, mesh.vertices[c+ 6].uv, mesh.vertices[c+ 6].tangent,
                                    (mesh.vertices[c+ 7].co.x*self.scaling, mesh.vertices[c+ 7].co.y*self.scaling, mesh.vertices[c+ 7].co.z*self.scaling), mesh.vertices[c+ 7].normal, mesh.vertices[c+ 7].uv, mesh.vertices[c+ 7].tangent,
                                    (mesh.vertices[c+ 8].co.x*self.scaling, mesh.vertices[c+ 8].co.y*self.scaling, mesh.vertices[c+ 8].co.z*self.scaling), mesh.vertices[c+ 8].normal, mesh.vertices[c+ 8].uv, mesh.vertices[c+ 8].tangent,
                                    (mesh.vertices[c+ 9].co.x*self.scaling, mesh.vertices[c+ 9].co.y*self.scaling, mesh.vertices[c+ 9].co.z*self.scaling), mesh.vertices[c+ 9].normal, mesh.vertices[c+ 9].uv, mesh.vertices[c+ 9].tangent,
                                    (mesh.vertices[c+10].co.x*self.scaling, mesh.vertices[c+10].co.y*self.scaling, mesh.vertices[c+10].co.z*self.scaling), mesh.vertices[c+10].normal, mesh.vertices[c+10].uv, mesh.vertices[c+10].tangent,
                                    (mesh.vertices[c+11].co.x*self.scaling, mesh.vertices[c+11].co.y*self.scaling, mesh.vertices[c+11].co.z*self.scaling), mesh.vertices[c+11].normal, mesh.vertices[c+11].uv, mesh.vertices[c+11].tangent,
                                    (mesh.vertices[c+12].co.x*self.scaling, mesh.vertices[c+12].co.y*self.scaling, mesh.vertices[c+12].co.z*self.scaling), mesh.vertices[c+12].normal, mesh.vertices[c+12].uv, mesh.vertices[c+12].tangent,
                                    (mesh.vertices[c+13].co.x*self.scaling, mesh.vertices[c+13].co.y*self.scaling, mesh.vertices[c+13].co.z*self.scaling), mesh.vertices[c+13].normal, mesh.vertices[c+13].uv, mesh.vertices[c+13].tangent,
                                    (mesh.vertices[c+14].co.x*self.scaling, mesh.vertices[c+14].co.y*self.scaling, mesh.vertices[c+14].co.z*self.scaling), mesh.vertices[c+14].normal, mesh.vertices[c+14].uv, mesh.vertices[c+14].tangent,
                                    (mesh.vertices[c+15].co.x*self.scaling, mesh.vertices[c+15].co.y*self.scaling, mesh.vertices[c+15].co.z*self.scaling), mesh.vertices[c+15].normal, mesh.vertices[c+15].uv, mesh.vertices[c+15].tangent
                    )
                c+=16
            else:
                self.write_vector11( (mesh.vertices[c  ].co.x*self.scaling, mesh.vertices[c  ].co.y*self.scaling, mesh.vertices[c  ].co.z*self.scaling), mesh.vertices[c  ].normal, mesh.vertices[c  ].uv, mesh.vertices[c  ].tangent )
                c+=1

        # for vertex in mesh.vertices:
        #     self.write_vector3( (vertex.co.x*self.scaling, vertex.co.y*self.scaling, vertex.co.z*self.scaling) )
        #     self.write_vector3(vertex.normal)
        #     self.write_vector2(vertex.uv)
        #     self.write_vector3(vertex.tangent)

        self.write_uint(len(mesh.indices))
        for i in mesh.indices:
            self.write_ushort(i)
            ### above limit? - well this breaks KN5 format
            ##self.write_uint(i)

        if mesh.material_id is None:
            self.warnings.append(f"No material to mesh '{obj.name}' assigned")
            self.write_uint(0)
        else:
            self.write_uint(mesh.material_id)

        self.write_uint(node_properties.layer) #layer
        self.write_float(node_properties.lodIn) #lodIn
        self.write_float(node_properties.lodOut) #lodOut
        self._write_bounding_sphere(mesh.vertices)
        self.write_bool(node_properties.renderable) #isRenderable

    def _write_bounding_sphere(self, vertices):
        max_x = -999999999
        max_y = -999999999
        max_z = -999999999
        min_x = 999999999
        min_y = 999999999
        min_z = 999999999
        for vertex in vertices:
            co = vertex.co * self.scaling
            if co[0] > max_x:
                max_x = co[0]
            if co[0] < min_x:
                min_x = co[0]
            if co[1] > max_y:
                max_y = co[1]
            if co[1] < min_y:
                min_y = co[1]
            if co[2] > max_z:
                max_z = co[2]
            if co[2] < min_z:
                min_z = co[2]

        sphere_center = [
            min_x + (max_x - min_x) / 2,
            min_y + (max_y - min_y) / 2,
            min_z + (max_z - min_z) / 2
        ]
        sphere_radius = max((max_x - min_x) / 2, (max_y - min_y) / 2, (max_z - min_z) / 2) * 2
        self.write_vector3(sphere_center)
        self.write_float(sphere_radius)


    def _split_object_by_materials(self, obj):
        meshes = []
        mesh_copy = obj.to_mesh()
        try:
            # when failing we must do smth else
            mesh_copy.calc_loop_triangles()
            mesh_copy.calc_tangents()
        except:
            # gone wrong, we have to triangulate
            print('  triangulating : ' + obj.name + '\n' + traceback.format_exc())

            try:
                bm = bmesh.new()
                bm.from_mesh(mesh_copy)
                bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
                # bmesh.ops.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
                bm.to_mesh(mesh_copy)

                # Finish up, write the bmesh back to the mesh
                bm.to_mesh(obj.data)

                bm.free()
                # so now again:
                mesh_copy.calc_loop_triangles()
                mesh_copy.calc_tangents()
            except:
                # gone wrong, we have to triangulate
                print('  triangulating2 : ' + obj.name + '\n' + traceback.format_exc())

        try:
            uv_layer = mesh_copy.uv_layers.active
            matrix = obj.matrix_world
            if not mesh_copy.materials:
                raise Exception(f"Object '{obj.name}' has no material assigned")
            used_materials = set([triangle.material_index for triangle in mesh_copy.loop_triangles])
            for material_index in used_materials:
                if not mesh_copy.materials[material_index]:
                    raise Exception(f"Material slot {material_index} for object '{obj.name}' has no material assigned")
                material_name = mesh_copy.materials[material_index].name
                if material_name.startswith("__"):
                    raise Exception(f"Material '{material_name}' is ignored but is used by object '{obj.name}'")

                vertices = {}
                indices = []
                for triangle in mesh_copy.loop_triangles:
                    if material_index != triangle.material_index:
                        continue
                    vertex_index_for_face = 0
                    face_indices = []
                    for loop_index in triangle.loops:
                        loop = mesh_copy.loops[loop_index]
                        #local_position = matrix @ mesh_copy.vertices[loop.vertex_index].co * self.scaling
                        local_position = matrix @ mesh_copy.vertices[loop.vertex_index].co
                        ####@ halfrotmat   ### * self.scaling
                        converted_position = convert_vector3(local_position)
                        converted_normal = convert_vector3_normal(loop.normal)
                        # converted_normal = loop.normal
                        uv = (0, 0)
                        if uv_layer:
                            uv = uv_layer.data[loop_index].uv
                            uv = (uv[0], -uv[1])
                        else:
                            uv = self._calculate_uvs(obj, mesh_copy, material_index, local_position)
                        tangent = loop.tangent
                        vertex = UvVertex(converted_position, converted_normal, uv, tangent)
                        if vertex not in vertices:
                            new_index = len(vertices)
                            vertices[vertex] = new_index
                        face_indices.append(vertices[vertex])
                        vertex_index_for_face += 1
                    indices.extend((face_indices[1], face_indices[2], face_indices[0]))
                    if len(face_indices) == 4:
                        indices.extend((face_indices[2], face_indices[3], face_indices[0]))
                vertices = [v for v, index in sorted(vertices.items(), key=lambda k: k[1])]
                #vertices = [v for v, index in vertices.items()]
                # print( str(len(vertices)) + ' ' + str(len(indices)) )
                material_id = self.material_writer.material_positions[material_name]
                meshes.append(Mesh(material_id, vertices, indices))
        except:
            # print("triangulation failed")
            print('  triangulating0 : ' + obj.name + '\n' + traceback.format_exc())
            obj.to_mesh_clear()
        return meshes

    def _split_meshes_for_vertex_limit(self, divided_meshes):
        new_meshes = []
        for mesh in divided_meshes:
            if len(mesh.vertices) > limit:
                start_index = 0
                while start_index < len(mesh.indices):
                    vertex_index_mapping = {}
                    new_indices = []
                    for i in range(start_index, len(mesh.indices), 3):
                        start_index += 3
                        face = mesh.indices[i:i+3]
                        for face_index in face:
                            if not face_index in vertex_index_mapping:
                                new_index = len(vertex_index_mapping)
                                vertex_index_mapping[face_index] = new_index
                            new_indices.append(vertex_index_mapping[face_index])
                        if len(vertex_index_mapping) >= limit-3:
                            break
                    verts = [mesh.vertices[v] for v, index in sorted(vertex_index_mapping.items(), key=lambda k: k[1])]
                    #verts = [mesh.vertices[v] for v, index in vertex_index_mapping.items()]
                    new_meshes.append(Mesh(mesh.material_id, verts, new_indices))
            else:
                new_meshes.append(mesh)
        return new_meshes

    def _calculate_uvs(self, obj, mesh, material_id, co):
        size = obj.dimensions
        x = co[0] / size[0]
        y = co[1] / size[1]
        mat = mesh.materials[material_id]
        texture_node = get_active_material_texture_slot(mat)
        if texture_node:
            x *= texture_node.texture_mapping.scale[0]
            y *= texture_node.texture_mapping.scale[1]
            x += texture_node.texture_mapping.translation[0]
            y += texture_node.texture_mapping.translation[1]
        return (x, y)


class NodeProperties:
    def __init__(self, node):
        ###ac_node = node.assettoCorsa
        self.name = node.name
        self.lodIn = 0 ###ac_node.lodIn
        self.lodOut = 0 ###ac_node.lodOut
        self.layer = 0 ###ac_node.layer
        self.castShadows = True ###ac_node.castShadows
        self.visible = True ###ac_node.visible
        self.transparent = False ###ac_node.transparent
        self.renderable = True ###ac_node.renderable


class NodeSettings:
    def __init__(self, settings, node_settings_key):
        self._settings = settings
        self._node_settings_key = node_settings_key
        self._node_name_matches = [node_settings_key]

    def apply_settings_to_node(self, node):
        for setting in NODE_SETTINGS:
            setting_val = self._get_node_setting(setting)
            if setting_val is not None:
                setattr(node, setting, setting_val)

    def _get_node_setting(self, setting):
        if setting in self._settings[NODES][self._node_settings_key]:
            #print('found: ' + setting + ' = ' + str( self._settings[NODES][self._node_settings_key][setting]) )
            return self._settings[NODES][self._node_settings_key][setting]
        # print('not found: ' + setting)
        return None


class UvVertex:
    def __init__(self, co, normal, uv, tangent):
        self.co = co             # 3*4
        self.normal = normal     #
        self.uv = uv             #
        self.tangent = tangent   #
        self.hash = None         #

    def __hash__(self):
        if not self.hash:
            self.hash = hash(
                hash(self.co[0])      ^   hash(self.co[1])      ^    hash(self.co[2])     ^
                hash(self.normal[0])  ^   hash(self.normal[1])  ^    hash(self.normal[2]) ^
                hash(self.uv[0])      ^   hash(self.uv[1])      ^
                hash(self.tangent[0]) ^   hash(self.tangent[1]) ^   hash(self.tangent[2])    )
        return self.hash

    def __eq__(self, other):
        if self.co[0] != other.co[0] or self.co[1] != other.co[1] or self.co[2] != other.co[2]:
            return False
        if self.normal[0] != other.normal[0] or self.normal[1] != other.normal[1] or self.normal[2] != other.normal[2]:
            return False
        if self.uv[0] != other.uv[0] or self.uv[1] != other.uv[1]:
            return False
        if (self.tangent[0] != other.tangent[0]
                or self.tangent[1] != other.tangent[1]
                or self.tangent[2] != other.tangent[2]):
            return False
        return True


class Mesh:
    def __init__(self, material_id, vertices, indices):
        self.material_id = material_id
        self.vertices = vertices
        self.indices = indices
