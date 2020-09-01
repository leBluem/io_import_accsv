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
    "name": "Import-Export AC CSV or AI files",
    "author": "leBluem",
    "version": (0, 8, 0),
    "blender": (2, 80, 0),
    "location": "File > Import-Export",
    "description": "Import-Export AssettoCorsa CSV and AI files",
    "warning": "requires Blender v2.8",
    "doc_url": "https://github.com/leBluem/io_import_accsv",
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
    imp.reload(export_csv)
    imp.reload(export_ai)
else:
    import import_csv
    import import_ai
    import export_csv
    import export_ai

import bpy
from bpy.props import (
    StringProperty,
    FloatProperty,
    IntProperty,
    BoolProperty,
)
from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper,
    path_reference_mode,
)


### import

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
    scaling: FloatProperty(
            name="Scale",
            min=0.001, max=1000.0,
            default=1.0,
            )
    doDoubleCheck: BoolProperty(
            name="doDoubleCheck (very slow)",
            description = "check for miss placed values from csv and skip them",
            default=0,
            )
    def execute(self, context):
        return import_csv.load(context, self.properties.filepath, self.scaling, self.doDoubleCheck)
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "scaling")
        layout.prop(operator, "doDoubleCheck")


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
    scaling: FloatProperty(
            name="Scale",
            min=0.001, max=1000.0,
            default=1.0,
            )
    def execute(self, context):
        return import_ai.load(context, self.properties.filepath, self.scaling)
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "scaling")


### export

class ExportCSV(bpy.types.Operator, ExportHelper):
    """Save a CSV File"""
    bl_idname = "export_csv.write"
    bl_label = "Export AC CSV"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".csv"
    filter_glob: StringProperty(
        default="*.csv;*.ini",
        options={'HIDDEN'},
    )
    scaling: FloatProperty(
            name="Scale",
            min=0.001, max=1000.0,
            default=1.0,
            )
    shiftCount: IntProperty(
            name="shiftCount",
            description = "start at vertex index",
            min=-999999, max=999999,
            default=0,
            )
    reverse: BoolProperty(
            name="reverse",
            description = "save in reverse order",
            default=0,
            )
    def execute(self, context):
        return export_csv.save(context, self.properties.filepath, self.scaling, self.shiftCount, self.reverse)
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "scaling")
        layout.prop(operator, "shiftCount")
        layout.prop(operator, "reverse")


class ExportAI(bpy.types.Operator, ExportHelper):
    """Save fast_lane.ai"""
    bl_idname = "export_ai.write"
    bl_label = "Export AC AI line"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".ai"
    filter_glob: StringProperty(
        default="*.ai",
        options={'HIDDEN'},
    )
    scaling: FloatProperty(
            name="Scale",
            min=0.001, max=1000.0,
            default=1.0,
            )
    shiftCount: IntProperty(
            name="shiftCount",
            min=-999999, max=999999,
            default=0,
            )
    def execute(self, context):
        return export_ai.save(context, self.properties.filepath, self.shiftCount)
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
        sfile = context.space_data
        operator = sfile.active_operator
        layout.prop(operator, "scaling")
        # layout.prop(operator, "shiftCount")


def menu_func_import(self, context):
    self.layout.operator(ImportCSV.bl_idname, text="AC side_x.csv (.csv)")
    self.layout.operator(ImportAI.bl_idname, text="AC fast_lane.ai (.ai)")

def menu_func_export(self, context):
    self.layout.operator(ExportCSV.bl_idname, text="AC side_x.csv (.csv)")
    self.layout.operator(ExportAI.bl_idname, text="AC fast_lane.ai (.ai)")


classes = (
    ImportCSV,
    ImportAI,
    ExportCSV,
    ExportAI,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
