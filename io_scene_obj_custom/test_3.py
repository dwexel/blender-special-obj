import bpy
import bmesh

print("----------------")

mesh = bpy.context.object.data
name = "created_attribute"

def make_attribute():
    if name in mesh.attributes.keys():
        print("already there")
    else:
        mesh.attributes.new(name=name, type="INT", domain="POINT")

def remove_attribute():
    att = mesh.attributes[name]
    mesh.attributes.remove(att)


class SetVertexBoolean(bpy.types.Operator):
    # 0 false, 1 true
    """set selected true, unselected false"""
    
    bl_idname = "mesh.set_vertex_boolean"
    bl_label = "Set Vertex Boolean"
    
    def execute(self, context):
        print("---- executing ----")

        # grab current mode
        mode = context.active_object.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # make bmesh
        me = mesh
        bm = bmesh.new()
        bm.from_mesh(me)

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

        bm.to_mesh(me)
        bm.free()        
        bpy.ops.object.mode_set(mode=mode)

        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(SetVertexBoolean.bl_idname)
    self.layout.separator()        


def register():
    make_attribute()
    bpy.utils.register_class(SetVertexBoolean)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.prepend(menu_func)

    
def unregister():
    remove_attribute()
    bpy.utils.unregister_class(SetVertexBoolean)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(menu_func)





if __name__ == "__main__":    
    register()
#    unregister()
    
#    
#    for att in mesh.attributes:
#        print(att)

