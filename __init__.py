# ##### BEGIN GPL LICENSE BLOCK #####
#
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
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>

bl_info = {
    "name": "Import AC CSV or AI files",
    "author": "leBluem",
    "version": (0, 3, 0),
    "blender": (2, 80, 0),
    "location": "File > Import",
    "description": "AC CSV or AI files",
    "warning": "",
    "doc_url": "",
    "category": "Import-Export",
}

import sys
import os

# ----------------------------------------------
# Add to Phyton path (once only)
# ----------------------------------------------
path = sys.path
flag = False
for item in path:
    if "io_import_accsv" in item:
        flag = True
if flag is False:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'io_import_accsv'))

# ----------------------------------------------
# Import modules
# ----------------------------------------------
if "bpy" in locals():
    import imp
    imp.reload(import_csv)
    imp.reload(import_ai)
else:
    import import_csv
    import import_ai

import bpy
from bpy.props import (
    StringProperty,
)
from bpy_extras.io_utils import (
    ImportHelper,
    path_reference_mode,
)


class ImportCSV(bpy.types.Operator, ImportHelper):
    """Load a CSV File"""
    bl_idname = "import_csv.read"
    bl_label = "Import CSV"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".csv"
    filter_glob: StringProperty(
        default="*.csv;*.ini",
        options={'HIDDEN'},
    )

    def execute(self, context):
        return import_csv.load(context, self.properties.filepath)

    def draw(self, context):
        pass


class ImportAI(bpy.types.Operator, ImportHelper):
    """Load fast_lane.ai"""
    bl_idname = "import_ai.read"
    bl_label = "Import AI line"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".ai"
    filter_glob: StringProperty(
        default="*.ai",
        options={'HIDDEN'},
    )

    def execute(self, context):
        return import_ai.load(context, self.properties.filepath)

    def draw(self, context):
        pass


def menu_func_import(self, context):
    self.layout.operator(ImportCSV.bl_idname, text="AC side_x.csv (.csv)")
    self.layout.operator(ImportAI.bl_idname, text="AC fast_lane.ai (.ai)")


classes = (
    ImportCSV,
    ImportAI,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
