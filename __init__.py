# ##### BEGIN GPL LICENSE BLOCK #####
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
# ##### END GPL LICENSE BLOCK #####
# <pep8-80 compliant>

bl_info = {
    "name": "Import-Export AC CSV or AI files",
    "author": "leBluem",
    "version": (1, 5, 0),
    "blender": (2, 80, 0),
    "location": "File > Import-Export",
    "description": "Import-Export AssettoCorsa CSV and AI files",
    "warning": "requires Blender v2.8 or above",
    "category": "Import-Export",
    "doc_url": "https://github.com/leBluem/io_import_accsv",
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
    EnumProperty,
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
    filter_glob = StringProperty(
        default="*.csv;*.ini",
        options={'HIDDEN'},
    )
    scaling : FloatProperty(
        name="Scale",
        min=0.01, max=100.0,
        default=1.0,
        )
    doDoubleCheck : BoolProperty(
        name="doDoubleCheck (very slow)",
        description = "check for miss placed values from csv and skip them",
        default=0,
        )
    # unused atm
    createFaces : BoolProperty(
        name = "create face after 4 verts",
        default = 0,
        description = "text"
        )
    ignoreLastEdge : BoolProperty(
        name = "dont connect first/last verts",
        default = 0,
        description = "usefull when importing A2B stuff"
        )

    def execute(self, context):
        return import_csv.load(context, self.properties.filepath, self.scaling, self.doDoubleCheck, self.createFaces, self.ignoreLastEdge)

    def draw(self, context):
        layout = self.layout
        if bpy.app.version[1]>=80:
            layout.use_property_split = True
            layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "scaling")
        layout.prop(operator, "doDoubleCheck")
        # layout.prop(operator, "createFaces")
        layout.prop(operator, "ignoreLastEdge")


class ImportAI(bpy.types.Operator, ImportHelper):
    """Load fast_lane.ai"""
    bl_idname = "import_ai.read"
    bl_label = "Import AI line"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".ai"
    filter_glob = StringProperty(
        default="*.ai",
        options={'HIDDEN'},
    )
    scaling : FloatProperty(
        name="Scale",
        min=0.01, max=100.0,
        default=1.0,
        )
    importExtraData : BoolProperty(
        name = "import all 18 ai line datasets",
        default = 0,
        description = "if you want to see how data looks; not recommended"
        )
    # unused atm
    createCameras : BoolProperty(
        name = "create cameras.ini from ai-line",
        default = 0,
        description = "meshes created for observation"
        )
    # unused atm
    maxDist : FloatProperty(
        name="Min Distance btw cameras",
        min=1.0, max=1000.0,
        default=350.0
        )
    ignoreLastEdge : BoolProperty(
        name = "dont connect first/last verts",
        default = 0,
        description = "usefull when importing A2B stuff"
        )

    def execute(self, context):
        return import_ai.load(context, self.properties.filepath, self.scaling, self.importExtraData, self.createCameras, self.maxDist, self.ignoreLastEdge)
    def draw(self, context):
        layout = self.layout
        if bpy.app.version[1]>=80:
            layout.use_property_split = True
            layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "scaling")
        layout.prop(operator, "importExtraData")
        ### not finished atm
        #layout.prop(operator, "createCameras")
        #layout.prop(operator, "maxDist")
        layout.prop(operator, "ignoreLastEdge")


### export

class ExportCSV(bpy.types.Operator, ExportHelper):
    """Save a CSV File"""
    bl_idname = "export_csv.write"
    bl_label = "Export AC CSV"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".csv"
    filter_glob = StringProperty(
        default="*.csv;*.ini",
        options={'HIDDEN'},
    )
    scaling : FloatProperty(
        name="Scale",
        min=0.01, max=100.0,
        default=1.0,
        )
    shiftCount : IntProperty(
        name="shiftCount",
        description = "start at vertex index",
        min=-999999, max=999999,
        default=0,
        )
    reverse : BoolProperty(
        name="reverse",
        description = "save in reverse order",
        default=0,
        )
    conv2Curve2mesh: BoolProperty(
        name="sort by converting to curve",
        description = "sort by using curves, but at least 0 must be correct ",
        default=0,
        )

    def execute(self, context):
        return export_csv.save(context, self.properties.filepath, self.scaling, self.shiftCount, self.reverse, self.conv2Curve2mesh)

    def draw(self, context):
        layout = self.layout
        if bpy.app.version[1]>=80:
            layout.use_property_split = True
            layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "scaling")
        layout.prop(operator, "shiftCount")
        layout.prop(operator, "reverse")
        layout.prop(operator, "conv2Curve2mesh")


class ExportAI(bpy.types.Operator, ExportHelper):
    """Save fast_lane.ai"""
    bl_idname = "export_ai.write"
    bl_label = "Export AC AI line"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".ai"
    filter_glob = StringProperty(
        default="*.ai",
        options={'HIDDEN'},
    )
    scaling : FloatProperty(
        name="Scale",
        min=0.01, max=100.0,
        default=1.0,
        description='',
        )
    shiftCount : IntProperty(
        name="shiftCount",
        min=-999999, max=999999,
        description='not a good idea for ai-line, ai-line will probably be broken after this',
        default=0,
        )
    lineIDX : EnumProperty(
        name='ailine IDX',
        description='ID in ai line, none for AI-line itself',
        items=[('-1',  "none",  "none"),
                ('0',  "0",  "0"),
                ('1',  "1",  "1"),
                ('2',  "2",  "2"),
                ('3',  "3",  "3"),
                ('4',  "4",  "4"),
                ('5',  "5",  "5"),
                ('6',  "6",  "6"),
                ('7',  "7",  "7"),
                ('8',  "8",  "8"),
                ('9',  "9",  "9"),
                ('10', "10", "10"),
                ('11', "11", "11"),
                ('12', "12", "12"),
                ('13', "13", "13"),
                ('14', "14", "14"),
                ('15', "15", "15"),
                ('16', "16", "16"),
                ('17', "17", "17")],
        default='-1'
        )

    def execute(self, context):
        return export_ai.save(context, self.properties.filepath, self.shiftCount, self.lineIDX)
    def draw(self, context):
        layout = self.layout
        if bpy.app.version[1]>=80:
            layout.use_property_split = True
            layout.use_property_decorate = False  # No animation.
        sfile = context.space_data
        operator = sfile.active_operator
        layout.prop(operator, "scaling")
        layout.prop(operator, "shiftCount")
        layout.prop(operator, "lineIDX")


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
    if bpy.app.version[1]<80:
        bpy.types.INFO_MT_file_import.append(menu_func_import)
        bpy.types.INFO_MT_file_export.append(menu_func_export)
    else:
        bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
        bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    if bpy.app.version[1]<80:
        bpy.types.INFO_MT_file_import.remove(menu_func_import)
        bpy.types.INFO_MT_file_export.remove(menu_func_export)
    else:
        bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
        bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
