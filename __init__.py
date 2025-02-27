bl_info = {
    "name": "Import-Export AC CSV/INI/AI files",
    "author": "leBluem",
    "version": (2,0,0),
    "blender": (2,80,0),
    "location": "File > Import-Export",
    "description": "Import-Export AssettoCorsa CSV/AI or cameras.ini files",
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
    imp.reload(import_ini)
    imp.reload(import_csv)
    imp.reload(import_ai)
    imp.reload(export_ini)
    imp.reload(export_csv)
    imp.reload(export_ai)
else:
    import import_ini
    import import_csv
    import import_ai
    import export_ini
    import export_csv
    import export_ai

import bpy
from bpy.props import (
    StringProperty,
    FloatProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
    CollectionProperty,
)
from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper,
    path_reference_mode,
)


### import


class ImportINI(bpy.types.Operator, ImportHelper):
    """Load a camera.INI File"""
    bl_idname = "import_ini.read"
    bl_label = "Import INI"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".ini"
    filter_glob : StringProperty(
        default="*.ini",
        options={'HIDDEN'},
    )
    files : CollectionProperty(
            name="File Path",
            type=bpy.types.OperatorFileListElement,
            )
    scaling : FloatProperty(
        name="Scale",
        min=0.01, max=100.0,
        default=1.0,
        )
    asMesh : BoolProperty(
        name="mesh/verts (not empties)",
        description = "import as Mesh with connected verts rather than as several empties",
        default=0,
        )

    def execute(self, context):
        if self.files:
            ret = {'CANCELLED'}
            dirname = os.path.dirname(self.filepath)
            for file in self.files:
                path = os.path.join(dirname, file.name)
                # print(path)
                # return import_csv.load(context, path, self.scaling, self.doDoubleCheck, self.createFaces, self.ignoreLastEdge)
                return import_ini.load(context, path, self.scaling, self.asMesh)
                #if import_ai.load(context, path, self.scaling, self.importExtraData, False, 0, False) == {'FINISHED'}:
            return ret
        else:
            return import_ini.load(context, self.properties.filepath, self.scaling, self.asMesh)

    def draw(self, context):
        layout = self.layout
        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "scaling")
        layout.prop(operator, "asMesh")

class ImportCSV(bpy.types.Operator, ImportHelper):
    """Load a CSV File"""
    bl_idname = "import_csv.read"
    bl_label = "Import CSV"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".csv"
    filter_glob : StringProperty(
        default="*.csv;*.ini;*.txt",
        options={'HIDDEN'},
    )
    files : CollectionProperty(
            name="File Path",
            type=bpy.types.OperatorFileListElement,
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
        if self.files:
            ret = {'CANCELLED'}
            dirname = os.path.dirname(self.filepath)
            for file in self.files:
                path = os.path.join(dirname, file.name)
                # print(path)
                return import_csv.load(context, path, self.scaling, self.doDoubleCheck, self.createFaces, self.ignoreLastEdge)
                #if import_ai.load(context, path, self.scaling, self.importExtraData, False, 0, False) == {'FINISHED'}:
            return ret
        else:
            return import_csv.load(context, self.properties.filepath, self.scaling, self.doDoubleCheck, self.createFaces, self.ignoreLastEdge)

    def draw(self, context):
        layout = self.layout
        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "scaling")
        layout.prop(operator, "doDoubleCheck")
        layout.prop(operator, "ignoreLastEdge")
        # layout.prop(operator, "createFaces")


class ImportAI(bpy.types.Operator, ImportHelper):
    """Load fast_lane.ai"""
    bl_idname = "import_ai.read"
    bl_label = "Import AI line"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".ai"
    filter_glob : StringProperty(
        default="*.ai",
        options={'HIDDEN'},
    )
    files : CollectionProperty(
        name="File Path",
        type=bpy.types.OperatorFileListElement,
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

    def execute(self, context):
        if self.files:
            ret = {'CANCELLED'}
            dirname = os.path.dirname(self.filepath)
            for file in self.files:
                path = os.path.join(dirname, file.name)
                # print(path)
                return import_ai.load(context, path, self.scaling, self.importExtraData, False, 0, False)
            return ret
        else:
            #return import_fbx.load(self, context, filepath=self.filepath, **keywords)
            #print("B " + self.properties.filepath)
            return import_ai.load(context, self.properties.filepath, self.scaling, self.importExtraData, False, 0, False)

        # return import_ai.load(context, self.properties.filepath, self.scaling, self.importExtraData)

    def draw(self, context):
        layout = self.layout
        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "scaling")
        layout.prop(operator, "importExtraData")
        ### not finished atm
        #layout.prop(operator, "createCameras")
        #layout.prop(operator, "maxDist")
        #layout.prop(operator, "ignoreLastEdge")




### export

class ExportINI(bpy.types.Operator, ExportHelper):
    """Save a camera.INI File"""
    bl_idname = "export_ini.write"
    bl_label = "Export AC INI"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".ini"
    filter_glob : StringProperty(
        default="*.ini",
        options={'HIDDEN'},
    )
    scaling : FloatProperty(
        name="Scale",
        min=0.01, max=100.0,
        default=1.0,
        )
    reverse : BoolProperty(
        name="reverse",
        description = "save in reverse order",
        default=0,
        )

    def execute(self, context):
        return export_ini.save(context, self.properties.filepath, self.scaling, self.reverse)

    def draw(self, context):
        layout = self.layout
        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "scaling")
        # unsused atm
        #layout.prop(operator, "reverse")

class ExportCSV(bpy.types.Operator, ExportHelper):
    """Save a CSV File"""
    bl_idname = "export_csv.write"
    bl_label = "Export AC CSV"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".csv"
    filter_glob : StringProperty(
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
    skipPoTColumn: BoolProperty(
        name="skip PoT, save only x,y,z",
        description = "for ie camera splines or just plain csv files",
        default=0,
        )

    def execute(self, context):
        return export_csv.save(context, self.properties.filepath, self.scaling, self.shiftCount, self.reverse, self.conv2Curve2mesh, self.skipPoTColumn)

    def draw(self, context):
        layout = self.layout
        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "scaling")
        layout.prop(operator, "shiftCount")
        layout.prop(operator, "reverse")
        layout.prop(operator, "conv2Curve2mesh")
        layout.prop(operator, "skipPoTColumn")

class ExportAI(bpy.types.Operator, ExportHelper):
    """Save fast_lane.ai"""
    bl_idname = "export_ai.write"
    bl_label = "Export AC AI line"
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".ai"
    filter_glob : StringProperty(
        default="*.ai",
        options={'HIDDEN'},
    )
    files : CollectionProperty(
            name="File Path",
            type=bpy.types.OperatorFileListElement,
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
    reverse : BoolProperty(
        name="reverse (applied to mesh!)",
        description = "save in reverse order",
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

    def draw(self, context):
        layout = self.layout
        sfile = context.space_data
        operator = sfile.active_operator
        layout.prop(operator, "scaling")
        layout.prop(operator, "reverse")
        layout.prop(operator, "lineIDX")

    def execute(self, context):
        # return export_ai.save(context, self.properties.filepath, self.shiftCount, self.lineIDX, self.reverse)
        if self.files:
            ret = {'CANCELLED'}
            dirname = os.path.dirname(self.filepath)
            for file in self.files:
                lpath = os.path.join(dirname, file.name).lower()
                if not "left" in lpath and not "right" in lpath:
                    return export_ai.save(context, lpath, self.shiftCount, self.lineIDX, self.scaling, self.reverse)
            return ret
        else:
            return export_ai.save(context, self.properties.filepath, self.shiftCount, self.lineIDX, self.scaling, self.reverse)
            #return export_ai.save(context, self.properties.filepath, self.scaling, self.importExtraData)
            # return export_fbx.load(self, context, filepath=self.filepath, **keywords)
            # return import_ai.load(context, self.properties.filepath, self.scaling, self.importExtraData)





def menu_func_import(self, context):
    self.layout.operator(ImportINI.bl_idname, text="AC camera_x.ini (.ini)")
    self.layout.operator(ImportCSV.bl_idname, text="AC side_x.csv (.csv)")
    self.layout.operator(ImportAI.bl_idname, text="AC fast_lane.ai (.ai)")

def menu_func_export(self, context):
    self.layout.operator(ExportINI.bl_idname, text="AC camera_x.ini (.ini)")
    self.layout.operator(ExportCSV.bl_idname, text="AC side_x.csv (.csv)")
    self.layout.operator(ExportAI.bl_idname, text="AC fast_lane.ai (.ai)")


classes = (
    ImportINI,
    ImportCSV,
    ImportAI,
    ExportINI,
    ExportCSV,
    ExportAI,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

