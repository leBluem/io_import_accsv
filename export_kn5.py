# Copyright (C) 2014  Thomas Hagnhofer
# edited by leBluem

import os, time
import bpy
from bpy.props import BoolProperty, StringProperty
from bpy_extras.io_utils import ExportHelper
import traceback

from kn5.exporter_utils import read_settings
from kn5.kn5_writer import KN5Writer
from kn5.texture_writer import TextureWriter
from kn5.material_writer import MaterialWriter
from kn5.node_writer import NodeWriter


KN5_HEADER_BYTES = b"sc6969"

class KN5FileWriter(KN5Writer):
    def __init__(self, file, context, basedir, basename, settings, warnings, scaling):
        super().__init__(file)

        self.file_version = 5
        self.context = context
        self.basedir = basedir
        self.basename = basename
        self.settings = settings
        self.warnings = warnings
        self.scaling = scaling

    def write(self):
        self.file.write(KN5_HEADER_BYTES)
        self.write_uint(self.file_version)
        texture_writer = TextureWriter(self.file, self.context, self.basedir, self.settings, self.warnings)
        texture_writer.write()
        material_writer = MaterialWriter(self.file, self.context, self.settings, self.warnings)
        material_writer.write()
        node_writer = NodeWriter(self.file, self.context, self.settings, self.warnings, material_writer, self.scaling, self.basename)
        node_writer.write()


def save(context, filepath, scaling):
    result = {'FINISHED'}
    warnings = []
    try:
        basedir = os.path.dirname(filepath) + '\\texture\\'
        basename = os.path.basename(filepath).lower().replace('.kn5', '')
        settings = read_settings(context, filepath, basename)

        if settings == {} :
            print('!! cannot continue without json or fbx.ini !!!')
        else:
            print('opening ' + filepath)
            output_file = open(filepath, "wb")
            try:
                t1=time.time()

                kn5_writer = KN5FileWriter(output_file, context, basedir, 'FBX: '+basename, settings, warnings, scaling)
                kn5_writer.write()

                print(str( round(time.time()-t1,1)) + ' seconds')
                print(os.linesep.join(warnings) + "\n... export successfull!")
            finally:
                print('  export KN5 error : ' + traceback.format_exc())
                if not output_file is None:
                    output_file.close()
    except:
        print(os.linesep.join(warnings) + '\n  export KN5 error : ' + traceback.format_exc())
        result = {"CANCELLED"}

        try:
            os.remove(filepath)
        except:
            pass

    return result
