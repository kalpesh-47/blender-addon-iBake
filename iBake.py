bl_info = {
    "name": "iBake",
    "author": "Kalpesh Sompura",
    "version": (1, 0),
    "blender": (3, 6, 0),
    "location": "View3D",
    "description": "Bakes textures from high poly mesh onto low poly mesh",
    "warning": "",
    "doc_url": "",
    "category": "Tool",
}


import bpy

class SimpleAddonPanel(bpy.types.Panel):
    bl_label = "iBake"
    bl_idname = "PT_SimpleAddon"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Add-On'

    def draw(self, context):
        layout = self.layout

        # Source Object Dropdown
        layout.label(text="Select Source Object:")
        layout.prop_search(context.scene, "source_object", bpy.data, "objects")

        # Target Object Dropdown
        layout.label(text="Select Target Object:")
        layout.prop_search(context.scene, "target_object", bpy.data, "objects")

        # Prepare Button
        layout.label(text="Select Target Object from Outliner and then press 'Prepare' button.", icon="INFO")
        layout.operator("object.prepare_objects", text="Prepare")
        
        # Bake Button
        #layout.label(text="Save Image after ", icon="INFO")
        layout.operator("object.bake_objects", text="Bake")

class PrepareObjectsOperator(bpy.types.Operator):
    bl_idname = "object.prepare_objects"
    bl_label = "Prepare Objects"

    def execute(self, context):
        source_obj_name = context.scene.source_object
        target_obj_name = context.scene.target_object
        
        source_obj = bpy.data.objects.get(source_obj_name)
        target_obj = bpy.data.objects.get(target_obj_name)
        
        if source_obj and target_obj:
            # Modify source object's material
            source_material = source_obj.data.materials[0]
            image_texture_node_source = source_material.node_tree.nodes.get("Image Texture")
            output_node_source = source_material.node_tree.nodes.get("Material Output")
            source_material.node_tree.links.new(image_texture_node_source.outputs['Color'], output_node_source.inputs['Surface'])
            
            # Clear existing materials from the target object
            target_obj.data.materials.clear()

            # Create a new material
            material = bpy.data.materials.new(name="TextureMaterial")
            target_obj.data.materials.append(material)

            # Enable nodes for the active material
            bpy.context.object.active_material.use_nodes = True

            # Get the Principled BSDF shader node
            principled_node = material.node_tree.nodes.get("Principled BSDF")

            # Add an Image Texture node
            image_texture_node = material.node_tree.nodes.new(type='ShaderNodeTexImage')

            # Create a new image
            new_image = bpy.data.images.new(name="Hello World", width=2048, height=2048)
            image_texture_node.image = new_image

            # Link the Image Texture node to the Base Color input of Principled BSDF
            material.node_tree.links.new(image_texture_node.outputs['Color'], principled_node.inputs['Base Color'])

            # Smart UV Project unwrapping
            bpy.context.view_layer.objects.active = target_obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.smart_project(angle_limit=66)
            bpy.ops.object.mode_set(mode='OBJECT')
            
            
            # Set up baking settings
            bpy.context.scene.render.engine = 'CYCLES'
            bpy.context.scene.cycles.device = 'GPU'
            bpy.context.scene.cycles.use_denoising = False
            bpy.context.scene.cycles.samples = 1
            bpy.context.scene.cycles.bake_type = 'EMIT'
            bpy.context.scene.render.bake.use_selected_to_active = True
            bpy.context.scene.render.bake.cage_extrusion = 0.1
            
                    
            self.report({'INFO'}, f"Baked {source_obj.name}'s texture onto {target_obj.name} and unwrapped UVs")
        else:
            self.report({'WARNING'}, "Source or target object not found")
        
        return {'FINISHED'}
    
class BakeObjectsOperator(bpy.types.Operator):
    bl_idname = "object.bake_objects"
    bl_label = "Bake Objects"

    def execute(self, context):
        # Access the values stored by the Object Selection Tool addon
        source_obj_name = context.scene.source_object
        target_obj_name = context.scene.target_object

        source_obj = bpy.data.objects.get(source_obj_name)
        target_obj = bpy.data.objects.get(target_obj_name)

        if source_obj and target_obj:
            # Clear the current selection
            bpy.ops.object.select_all(action='DESELECT')
            
            # Select the specified objects
            source_obj.select_set(True)
            target_obj.select_set(True)
            
            # Set the active object to the second object
            bpy.context.view_layer.objects.active = target_obj
            
            # Set up baking settings
            bpy.context.scene.render.engine = 'CYCLES'
            bpy.context.scene.cycles.device = 'GPU'
            bpy.context.scene.cycles.use_denoising = False
            bpy.context.scene.cycles.samples = 1
            bpy.context.scene.cycles.bake_type = 'EMIT'
            bpy.context.scene.render.bake.use_selected_to_active = True
            bpy.context.scene.render.bake.cage_extrusion = 0.1
            bpy.ops.object.bake(type='EMIT')

        

            self.report({'INFO'}, f"Baked {source_obj.name}'s texture onto {target_obj.name} and unwrapped UVs")
        else:
            self.report({'WARNING'}, "Source or target object not found")

        return {'FINISHED'}

def register():
    bpy.types.Scene.source_object = bpy.props.StringProperty()
    bpy.types.Scene.target_object = bpy.props.StringProperty()
    bpy.utils.register_class(SimpleAddonPanel)
    bpy.utils.register_class(PrepareObjectsOperator)
    bpy.utils.register_class(BakeObjectsOperator)

def unregister():
    bpy.utils.unregister_class(SimpleAddonPanel)
    bpy.utils.unregister_class(PrepareObjectsOperator)
    bpy.utils.unregister_class(BakeObjectsOperator)
    del bpy.types.Scene.source_object
    del bpy.types.Scene.target_object

if __name__ == "__main__":
    register()