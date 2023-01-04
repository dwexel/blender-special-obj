# SPDX-License-Identifier: GPL-2.0-or-later

bl_info = {
    "name": "Wavefront OBJ format (legacy) (dexter's custom exporter)",
    "author": "Campbell Barton, Bastien Montagne",
    "version": (3, 9, 0),
    "blender": (3, 0, 0),
    "location": "File > Import-Export",
    "description": "Import-Export OBJ, Import OBJ mesh, UV's, materials and textures",
    "warning": "",
    "doc_url": "{BLENDER_MANUAL_URL}/addons/import_export/scene_obj.html",
    "support": 'OFFICIAL',
    "category": "Import-Export",
}

if "bpy" in locals():
    import importlib
    # if "import_obj" in locals():
    #     importlib.reload(import_obj)

    if "export_obj" in locals():
        importlib.reload(export_obj)


import bpy
from bpy.props import (
    BoolProperty,
    FloatProperty,
    StringProperty,
    EnumProperty,
)
from bpy_extras.io_utils import (
    # ImportHelper,
    ExportHelper,
    orientation_helper,
    path_reference_mode,
    axis_conversion,
)

@orientation_helper(axis_forward='-Z', axis_up='Y')
class ExportOBJ(bpy.types.Operator, ExportHelper):
    """Save a Wavefront OBJ File"""

    bl_idname = "export_scene.obj"
    bl_label = "Export OBJ (dexter's custom exporter)"
    bl_options = {'PRESET'}

    filename_ext = ".obj"
    filter_glob: StringProperty(
        default="*.obj;*.mtl",
        options={'HIDDEN'},
    )

    # context group
    use_selection: BoolProperty(
        name="Selection Only",
        description="Export selected objects only",
        default=False,
    )
    use_animation: BoolProperty(
        name="Animation",
        description="Write out an OBJ for each frame",
        default=False,
    )

    # object group
    use_mesh_modifiers: BoolProperty(
        name="Apply Modifiers",
        description="Apply modifiers",
        default=True,
    )
    # extra data group
    use_edges: BoolProperty(
        name="Include Edges",
        description="",
        default=True,
    )
    use_smooth_groups: BoolProperty(
        name="Smooth Groups",
        description="Write sharp edges as smooth groups",
        default=False,
    )
    use_smooth_groups_bitflags: BoolProperty(
        name="Bitflag Smooth Groups",
        description="Same as 'Smooth Groups', but generate smooth groups IDs as bitflags "
        "(produces at most 32 different smooth groups, usually much less)",
        default=False,
    )
    use_normals: BoolProperty(
        name="Write Normals",
        description="Export one normal per vertex and per face, to represent flat faces and sharp edges",
        default=True,
    )
    use_uvs: BoolProperty(
        name="Include UVs",
        description="Write out the active UV coordinates",
        default=True,
    )
    use_materials: BoolProperty(
        name="Write Materials",
        description="Write out the MTL file",
        default=True,
    )
    use_triangles: BoolProperty(
        name="Triangulate Faces",
        description="Convert all faces to triangles",
        default=False,
    )
    use_nurbs: BoolProperty(
        name="Write Nurbs",
        description="Write nurbs curves as OBJ nurbs rather than "
        "converting to geometry",
        default=False,
    )
    use_vertex_groups: BoolProperty(
        name="Polygroups",
        description="",
        default=False,
    )

    # grouping group
    use_blen_objects: BoolProperty(
        name="OBJ Objects",
        description="Export Blender objects as OBJ objects",
        default=True,
    )
    group_by_object: BoolProperty(
        name="OBJ Groups",
        description="Export Blender objects as OBJ groups",
        default=False,
    )
    group_by_material: BoolProperty(
        name="Material Groups",
        description="Generate an OBJ group for each part of a geometry using a different material",
        default=False,
    )
    keep_vertex_order: BoolProperty(
        name="Keep Vertex Order",
        description="",
        default=False,
    )

    global_scale: FloatProperty(
        name="Scale",
        min=0.01, max=1000.0,
        default=1.0,
    )

    path_mode: path_reference_mode

    check_extension = True

    def execute(self, context):
        from . import export_obj

        from mathutils import Matrix
        keywords = self.as_keywords(
            ignore=(
                "axis_forward",
                "axis_up",
                "global_scale",
                "check_existing",
                "filter_glob",
            ),
        )

        global_matrix = (
            Matrix.Scale(self.global_scale, 4) @
            axis_conversion(
                to_forward=self.axis_forward,
                to_up=self.axis_up,
            ).to_4x4()
        )

        keywords["global_matrix"] = global_matrix
        return export_obj.save(context, **keywords)

    def draw(self, context):
        pass


class OBJ_PT_export_include(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Include"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "EXPORT_SCENE_OT_obj"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        col = layout.column(heading="Limit to")
        col.prop(operator, 'use_selection')

        col = layout.column(heading="Objects as", align=True)
        col.prop(operator, 'use_blen_objects')
        col.prop(operator, 'group_by_object')
        col.prop(operator, 'group_by_material')

        layout.separator()

        layout.prop(operator, 'use_animation')


class OBJ_PT_export_transform(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Transform"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "EXPORT_SCENE_OT_obj"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, 'global_scale')
        layout.prop(operator, 'path_mode')
        layout.prop(operator, 'axis_forward')
        layout.prop(operator, 'axis_up')


class OBJ_PT_export_geometry(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Geometry"
    bl_parent_id = "FILE_PT_operator"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "EXPORT_SCENE_OT_obj"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, 'use_mesh_modifiers')
        layout.prop(operator, 'use_smooth_groups')
        layout.prop(operator, 'use_smooth_groups_bitflags')
        layout.prop(operator, 'use_normals')
        layout.prop(operator, 'use_uvs')
        layout.prop(operator, 'use_materials')
        layout.prop(operator, 'use_triangles')
        layout.prop(operator, 'use_nurbs', text="Curves as NURBS")
        layout.prop(operator, 'use_vertex_groups')
        layout.prop(operator, 'keep_vertex_order')



def menu_func_export(self, context):
    self.layout.operator(ExportOBJ.bl_idname, text=ExportOBJ.bl_label)


# custom print
# problem: blender restricting context?
import builtins as __builtin__

def console_print(*args, **kwargs):
    context = bpy.context
    for a in context.screen.areas:
        if a.type == 'CONSOLE':
            c = {}
            c['area'] = a
            c['space_data'] = a.spaces.active
            c['region'] = a.regions[-1]
            c['window'] = context.window
            c['screen'] = context.screen
            s = " ".join([str(arg) for arg in args])
            for line in s.split("\n"):
                bpy.ops.console.scrollback_append(c, text=line)

def print(*args, **kwargs):
    """Console print() function."""
    console_print(*args, **kwargs) # to py consoles
    __builtin__.print(*args, **kwargs) # to system console



# custom vertex creation
import bmesh
name = "created_attribute"

def make_attribute(mesh):
    if name in mesh.attributes.keys():
        print("attribute %s already exists in mesh" % name)
    else:
        mesh.attributes.new(name=name, type="INT", domain="POINT")


# def remove_attribute(mesh):
#     mesh.attributes.remove(mesh.attributes[name])


class SetVertexBoolean(bpy.types.Operator):
    """set selected 1, unselected 0"""
    
    bl_idname = "mesh.set_vertex_boolean"
    bl_label = "Set Vertex 0/1"

    def execute(self, context):
        mode = context.active_object.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        mesh = context.object.data
        make_attribute(mesh)

        bm = bmesh.new()
        bm.from_mesh(mesh)

        int_layers = bm.verts.layers.int
        layer = int_layers[name]
        
        for v in bm.verts:
            if v.select:
                v[layer] = 1
            else:
                v[layer] = 0

        for v in bm.verts:
            value = v[layer]
            print(value)

        bm.to_mesh(mesh)
        bm.free()
        bpy.ops.object.mode_set(mode=mode)

        return {'FINISHED'}

def vertex_menu_func(self, context):
    self.layout.operator(SetVertexBoolean.bl_idname)
    self.layout.separator()        



classes = (
    ExportOBJ,
    OBJ_PT_export_include,
    OBJ_PT_export_transform,
    OBJ_PT_export_geometry,
    SetVertexBoolean,
)




def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.prepend(vertex_menu_func)




def unregister():
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(vertex_menu_func)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
