# Copyright (C) 2014  Thomas Hagnhofer

import bpy, os, io
from kn5_writer import KN5Writer
from exporter_utils import get_all_texture_nodes


DDS_HEADER_BYTES = b"DDS"


class TextureWriter(KN5Writer):
    def __init__(self, file, context, basedir, settings, warnings):
        super().__init__(file)

        self.selected_obj = context.selected_objects.copy()
        self.available_textures = {}
        self.texture_positions = {}
        self.warnings = warnings
        self.settings = settings
        self.context = context
        self.basedir = basedir
        self.textcount = 0
        self._fill_available_image_textures()
        self.done = []


    def _fill_available_image_textures(self):
        self.available_textures = {}
        self.texture_positions = {}
        position = 0
        print('getting textures from blender objects')
        # need to check against stuff from json
        # basically useless
        all_texture_nodes = get_all_texture_nodes(self.selected_obj)
        for texture_node in all_texture_nodes:
            #if not texture_node.name.startswith("__"):
            if not texture_node.image:
                # self.warnings.append(f"Ignoring texture node without image '{texture_node.image.name}' '{texture_node.name}'")
                print(f"  ignoring texture node without image '{texture_node.image.name}' '{texture_node.name}'\n {texture_node.image.filepath}")
            elif not texture_node.image.pixels:
                # self.warnings.append(f"Ignoring texture node without image data '{texture_node.name}' '{texture_node.image.name}'")
                print(f"  ignoring texture node without image data '{texture_node.image.name}' '{texture_node.name}'\n {texture_node.image.filepath}")
            else:
                self.available_textures[texture_node.image.name] =  texture_node
                self.texture_positions[texture_node.image.name] = position
                position += 1


    def write(self):
        ### reset and count
        self.done = []
        self.write_part(True)

        # write count
        self.textcount = len(self.done)
        self.write_int(self.textcount)

        ### reset and write
        self.done = []
        self.write_part(False)
        print('')


    def write_part(self, onlyCount=True):
        # textures from blender file
        #for texture_name, _position in sorted(self.texture_positions.items(), key=lambda k: k[1]):
        #    self._write_texture(self.available_textures[texture_name], onlyCount)

        # need to check against stuff from blender file
        # textures from json
        for k in self.settings['materials'] :
            for kk in self.settings['materials'][k]['textures']:
                img = self.settings['materials'][k]['textures'][kk]['textureName']
                if os.path.isfile(self.basedir+img):
                    self._write_textureBare(self.basedir, img, onlyCount)
                else:
                    print('not found: ' + self.basedir+img)


    def _write_textureBare(self, sdir, sfile, onlyCount=True):
        if not sfile in self.done:
            self.done.append(sfile)
            if not onlyCount:
                # print('\r' + str(len(self.done)) + ' of ' + str(self.textcount) + ' ' + sfile + '                                                          ', end='')
                print('  ' + str(len(self.done)) + ' of ' + str(self.textcount) + ' ' + sfile)
                is_active = 1
                self.write_int(is_active)
                self.write_string(sfile)
                image_data = io.open(sdir+sfile, 'rb').read()
                self.write_blob(image_data)


    ### unused atm
    def _write_texture(self, texture, onlyCount=True):
        # self.write_string(texture.image.name)
        sname = texture.image.filepath
        if ':/' in sname or ':\\' in sname:
            sname = os.path.basename(sname)
        sname = sname.replace('//','')
        sname = sname.replace('texture\\','')
        sname = sname.replace('\\','')
        if not sname in self.done:
            self.done.append(sname)
            if not onlyCount:
                is_active = 1
                self.write_int(is_active)
                self.write_string(sname)
                image_data = self._get_image_data_from_texture(texture)
                self.write_blob(image_data)


    def _get_image_data_from_texture(self, texture):
        # print('reading ... ' + texture.image.filepath)
        #basename = os.path.basename(texture.image.filepath)
        #dirname = os.path.dirname(texture.image.filepath)
        # texture.image.filepath = '../texture/' + basename

        image_copy = texture.image.copy()
        if not image_copy.packed_file:
            image_copy.pack()
        image_data = image_copy.packed_file.data
        #image_header_magic_bytes = image_data[:3]
        #if image_copy.file_format != "" or image_header_magic_bytes == DDS_HEADER_BYTES:
        return image_data

        # try:
        #     if image_copy.file_format in ("PNG", "DDS", ""):
        #         if not image_copy.packed_file:
        #             image_copy.pack()
        #         image_data = image_copy.packed_file.data
        #         image_header_magic_bytes = image_data[:3]
        #         if image_copy.file_format != "" or image_header_magic_bytes == DDS_HEADER_BYTES:
        #             return image_data
        #     return self._convert_image_to_png(image_copy)
        # finally:
        #     self.context.blend_data.images.remove(image_copy)


    def _convert_image_to_png(self, image):
        if not image.packed_file:
            image.unpack(method="WRITE_LOCAL")
        image.pack()
        return image.packed_file.data
