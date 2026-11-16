"""Synthetic two-part engineering fixture; not an image reconstruction example."""
import bpy


def build(spec, parameters):
    collection = bpy.data.collections.new('Fixture Model')
    bpy.context.scene.collection.children.link(collection)
    for name, location, scale, color in [
        ('body', (0, 0, .4), (.6, .4, .8), (.12, .34, .58, 1)),
        ('cap', (0, 0, .86), (.68, .48, .12), (.65, .20, .06, 1)),
    ]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=location)
        obj = bpy.context.object; obj.name = name
        obj.scale = scale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        for owner in list(obj.users_collection): owner.objects.unlink(obj)
        collection.objects.link(obj)
        bevel = obj.modifiers.new('Editable corner bevel', 'BEVEL'); bevel.width = .025; bevel.segments = 3
        obj['part_id'] = name; obj['part_anchor'] = True
        material = bpy.data.materials.new(name+' Basic'); material.diffuse_color = color; material.use_nodes = True
        material.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value = color
        material.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value = .38
        obj.data.materials.append(material)
        if name == 'body': body = obj
        else:
            matrix = obj.matrix_world.copy(); obj.parent = body; obj.matrix_world = matrix
    return collection
