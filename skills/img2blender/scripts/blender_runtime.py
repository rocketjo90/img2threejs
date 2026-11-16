"""Run only with Blender --background --python-exit-code 1 --python this.py -- build|reopen RUN."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import time
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, payload):
    path.write_text(json.dumps(payload, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def signature(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, allow_nan=False, separators=(',', ':')).encode()).hexdigest()


def mat_signature(objects):
    payload = []
    for obj in sorted(objects, key=lambda o:o.name):
        row = {'object': obj.name, 'slots': []}
        for slot in obj.material_slots:
            mat = slot.material
            material = {'name': mat.name if mat else None, 'link': slot.link}
            if mat:
                material.update(color=list(mat.diffuse_color), roughness=mat.roughness, metallic=mat.metallic, nodes=[])
                if mat.use_nodes:
                    for node in sorted(mat.node_tree.nodes, key=lambda n:n.name):
                        inputs = []
                        for socket in node.inputs:
                            if hasattr(socket, 'default_value'):
                                value = socket.default_value
                                if isinstance(value, (float, int, bool, str)): inputs.append([socket.name, value])
                                else:
                                    try: inputs.append([socket.name, list(value)])
                                    except TypeError: inputs.append([socket.name, getattr(value, 'name', None)])
                        material['nodes'].append([node.name, node.bl_idname, inputs])
                    material['links'] = sorted([l.from_node.name, l.from_socket.name, l.to_node.name, l.to_socket.name] for l in mat.node_tree.links)
            row['slots'].append(material)
        payload.append(row)
    return signature(payload)


def audit_interfaces(collection, spec):
    """Measure nominated evaluated vertices against an actual evaluated surface."""
    checks = spec.get('interfaces', [])
    if not isinstance(checks, list):
        return {'passed': False, 'status': 'failed', 'checks': [], 'errors': ['interfaces must be a list']}
    rows, errors, seen = [], [], set()
    objects = {o.name:o for o in collection.all_objects}
    deps = bpy.context.evaluated_depsgraph_get()
    for item in checks:
        try:
            key = item['id']
            if not isinstance(key, str) or not key or key in seen: raise ValueError('unique interface ID required')
            seen.add(key)
            limit = item['max_gap']; count = item.get('min_samples', 3)
            if isinstance(limit, bool) or not isinstance(limit, (int,float)) or not math.isfinite(limit) or limit < 0:
                raise ValueError('max_gap must be finite and nonnegative in world scene units')
            if isinstance(count, bool) or not isinstance(count, int) or count < 3: raise ValueError('min_samples must be at least 3')
            probe, surface = objects[item['probe_object']], objects[item['surface_object']]
            if probe == surface or probe.type != 'MESH' or surface.type != 'MESH': raise ValueError('two distinct mesh objects required')
            group = probe.vertex_groups.get(item['vertex_group'])
            if group is None: raise ValueError('contact vertex group missing')
            pe, se = probe.evaluated_get(deps), surface.evaluated_get(deps)
            pm, sm = pe.to_mesh(), se.to_mesh()
            try:
                vertices = [probe.matrix_world@v.co for v in pm.vertices if any(g.group == group.index and g.weight >= .5 for g in v.groups)]
                if len(vertices) < count: raise ValueError(f'contact coverage {len(vertices)} below {count}')
                tree = BVHTree.FromPolygons([surface.matrix_world@v.co for v in sm.vertices], [list(f.vertices) for f in sm.polygons])
                distances = [tree.find_nearest(v)[3] for v in vertices]
                if any(d is None or not math.isfinite(d) for d in distances): raise ValueError('surface distance could not be evaluated')
                maximum = max(distances); passed = maximum <= limit
                rows.append({'id':key, 'samples':len(vertices), 'maximum_gap':maximum, 'max_gap':limit, 'passed':passed})
                if not passed: errors.append(f'{key}: surface gap {maximum:.8g} exceeds {limit:.8g}')
            finally:
                pe.to_mesh_clear(); se.to_mesh_clear()
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f'Interface evidence invalid: {exc}')
    return {'status':'failed' if errors else ('passed' if checks else 'not-applicable'),
            'passed':not errors if checks or errors else None, 'checks':rows, 'errors':errors,
            'limits':'Unsigned sampled surface proximity only; not penetration, motion, manufacturing fit or full collision certification.'}


def require_mode_audit(actual, expected, mode, restore_materials=False):
    if not actual['passed']: raise ValueError(f'{mode} audit failed: ' + '; '.join(actual['errors']))
    if actual['geometryFingerprint'] != expected['geometryFingerprint']: raise ValueError(f'{mode} changed evaluated geometry.')
    if restore_materials and actual['materialFingerprint'] != expected['materialFingerprint']:
        raise ValueError(f'{mode} changed material slots.')


def audit_model(collection, spec):
    objects = sorted(collection.all_objects, key=lambda o:o.name)
    expected = {p['id']:p for p in spec['parts']}
    anchors = {}
    errors, warnings, rows, fingerprints = [], [], [], []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    depsgraph.update()
    if any(instance.is_instance and instance.parent and instance.parent.original in objects for instance in depsgraph.object_instances):
        errors.append('Evaluated instances are unsupported: realize them into named geometry before review.')
    total = 0
    for obj in objects:
        part = obj.get('part_id')
        if part not in expected:
            errors.append(f'{obj.name}: undeclared or missing part_id')
        if obj.get('part_anchor'):
            if part in anchors: errors.append(f'Duplicate anchor: {part}')
            anchors[part] = obj
        if obj.instance_type == 'COLLECTION': errors.append(f'{obj.name}: collection instances unsupported')
        world = [round(v, 8) for row in obj.matrix_world for v in row]
        if not all(math.isfinite(v) for v in world): errors.append(f'{obj.name}: nonfinite transform')
        record = {'name': obj.name, 'part': part, 'parent': obj.parent.name if obj.parent else None,
                  'world': world, 'hidden': obj.hide_render, 'type': obj.type}
        if obj.type not in ('MESH', 'CURVE', 'SURFACE', 'FONT') or obj.hide_render:
            fingerprints.append(record)
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            if mesh is None or not len(mesh.vertices):
                errors.append(f'{obj.name}: empty evaluated mesh'); continue
            mesh.calc_loop_triangles()
            triangles = len(mesh.loop_triangles)
            total += triangles
            points = [[round(v, 8) for v in vertex.co] for vertex in mesh.vertices]
            if not all(math.isfinite(c) for point in points for c in point): errors.append(f'{obj.name}: nonfinite vertex')
            degenerate = sum(t.area <= 1e-14 for t in mesh.loop_triangles)
            if degenerate: errors.append(f'{obj.name}: {degenerate} zero-area triangles')
            incidence = {}
            for poly in mesh.polygons:
                for edge in poly.edge_keys:
                    edge = tuple(sorted(edge)); incidence[edge] = incidence.get(edge, 0) + 1
            boundary = sum(count == 1 for count in incidence.values())
            nonmanifold = sum(count > 2 for count in incidence.values())
            if boundary or nonmanifold: warnings.append(f'{obj.name}: {boundary} boundary edges, {nonmanifold} edges with more than two incident faces; assess for intended use')
            if not len(obj.material_slots) or any(s.material is None for s in obj.material_slots):
                errors.append(f'{obj.name}: assign Basic materials to every slot before review')
            for slot in obj.material_slots:
                mat = slot.material
                if mat and mat.use_nodes and any(link.to_node.type == 'OUTPUT_MATERIAL' and link.to_socket.name == 'Displacement' for link in mat.node_tree.links):
                    errors.append(f'{obj.name}: shader displacement is outside evaluated-mesh parity; use explicit geometry/modifiers for relief')
            original_mats = {s.material.original.name_full for s in obj.material_slots if s.material}
            used_indices = {face.material_index for face in mesh.polygons}
            if any(index >= len(mesh.materials) or mesh.materials[index] is None or
                   mesh.materials[index].original.name_full not in original_mats for index in used_indices):
                errors.append(f'{obj.name}: evaluated-only material cannot be safely overridden for Clay')
            record.update(vertices=points, polygons=[list(p.vertices) for p in mesh.polygons])
            rows.append({'object': obj.name, 'part': part, 'vertices': len(mesh.vertices), 'triangles': triangles,
                         'boundaryEdges': boundary, 'nonManifoldEdges': nonmanifold, 'zeroAreaTriangles': degenerate})
            fingerprints.append(record)
        finally:
            evaluated.to_mesh_clear()
    for part, definition in expected.items():
        if part not in anchors:
            errors.append(f'Missing anchor: {part}'); continue
        parent = definition.get('parent')
        if parent:
            cursor = anchors[part].parent
            while cursor and cursor != anchors.get(parent): cursor = cursor.parent
            if cursor is None: errors.append(f'{part}: anchor is not parented beneath {parent}')
        if not any(row['part'] == part for row in rows): warnings.append(f'{part}: no visible evaluated surface of its own; verify this is an intentional grouping anchor')
    if not total: errors.append('Model has no evaluated triangles')
    if total > spec['triangle_target']: warnings.append(f"{total} triangles exceed soft target {spec['triangle_target']}")
    interfaces = audit_interfaces(collection, spec)
    errors.extend(interfaces['errors'])
    return {'passed': not errors, 'errors': errors, 'warnings': warnings, 'triangles': total, 'parts': sorted(anchors), 'interfaces':interfaces,
            'objects': rows, 'geometryFingerprint': signature(fingerprints), 'materialFingerprint': mat_signature(objects),
            'limits': ['No automatic reference likeness judgment', 'No self-intersection or wall-thickness certification',
                       'No physical assembly-fit or printer validation', 'Instances unsupported and rejected']}


def configure_scene(spec, collection):
    scene = bpy.context.scene
    scene.unit_settings.system = spec['units']['system']
    scene.unit_settings.scale_length = spec['units']['scale_length']
    scene.render.engine = spec['render']['engine']
    if scene.render.engine == 'CYCLES':
        scene.cycles.device = 'CPU'
        scene.cycles.samples = spec['render']['samples']
        scene.cycles.use_denoising = True
    scene.render.resolution_x = scene.render.resolution_y = spec['render']['resolution']
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = False
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 4
    scene.world = bpy.data.worlds.new('Review World')
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get('Background')
    background.inputs['Color'].default_value = (.78, .78, .78, 1)
    background.inputs['Strength'].default_value = .7
    points = []
    bpy.context.view_layer.update()
    for obj in collection.all_objects:
        if obj.type in ('MESH', 'CURVE', 'SURFACE', 'FONT') and not obj.hide_render:
            evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
            points.extend(evaluated.matrix_world @ Vector(corner) for corner in evaluated.bound_box)
    if not points: raise ValueError('No visible model bounds.')
    low = Vector(tuple(min(p[i] for p in points) for i in range(3)))
    high = Vector(tuple(max(p[i] for p in points) for i in range(3)))
    center = (low+high)/2
    radius = max((high-low).length/2, .001)
    for name, direction, energy, size in [('Key', (-3, -4, 5), 850, 4), ('Fill', (3, 1, 2), 400, 3)]:
        light = bpy.data.lights.new(name, 'AREA'); light.energy = energy*radius*radius; light.shape = 'DISK'; light.size = size*radius
        obj = bpy.data.objects.new(name, light); scene.collection.objects.link(obj)
        obj.location = center + Vector(direction)*radius
        obj.rotation_euler = (center-obj.location).to_track_quat('-Z', 'Y').to_euler()
    cameras = []
    for view in spec['views']:
        data = bpy.data.cameras.new(view['id']); data.lens = view.get('lens', 50)
        data.clip_start = max(radius/10000, .000001); data.clip_end = radius*10000
        obj = bpy.data.objects.new('Review '+view['id'], data); scene.collection.objects.link(obj)
        target = Vector(view.get('target', center))
        if 'position' in view: obj.location = view['position']
        else: obj.location = center + Vector(view['direction']).normalized() * (radius/math.sin(data.angle/2)*1.15)
        obj.rotation_euler = (target-obj.location).to_track_quat('-Z', 'Y').to_euler()
        if 'orthographic_scale' in view: data.type = 'ORTHO'; data.ortho_scale = view['orthographic_scale']
        cameras.append(obj)
    return cameras


def render_views(run, spec, collection, cameras, mode):
    images = []
    originals = {obj:obj.hide_render for obj in collection.all_objects}
    try:
        for view, camera in zip(spec['views'], cameras):
            for obj in collection.all_objects: obj.hide_render = originals[obj] or obj.get('part_id') in view.get('hide_parts', [])
            bpy.context.scene.camera = camera
            filename = f'{view["id"]}-{mode}.png'
            bpy.context.scene.render.filepath = str(run/filename)
            bpy.context.scene.render.use_stamp = False
            bpy.ops.render.render(write_still=True)
            if not (run/filename).is_file(): raise RuntimeError(f'Render missing: {filename}')
            images.append(filename)
    finally:
        for obj, hidden in originals.items(): obj.hide_render = hidden
        bpy.context.view_layer.update()
    return images


def build(run):
    started = time.monotonic()
    spec = read(run/'spec.json'); params = read(run/'parameters.json')
    spec['_stage'] = read(run/'request.json')['stage']
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    loader = importlib.util.spec_from_file_location('current_object_builder', run/'build.py')
    module = importlib.util.module_from_spec(loader); loader.loader.exec_module(module)
    collection = module.build(spec, params)
    if not isinstance(collection, bpy.types.Collection) or not any(c == collection for c in bpy.context.scene.collection.children_recursive):
        raise ValueError('build() must return a collection linked to the active scene.')
    # Blender creates internal Render Result / Viewer Node images even in factory startup.
    used_images = [image for image in bpy.data.images if image.users and image.source != 'VIEWER']
    for image in used_images:
        if image.source == 'FILE':
            source = Path(bpy.path.abspath(image.filepath)).resolve()
            if not source.is_file() or not source.is_relative_to((run/'assets').resolve()):
                raise ValueError('File textures must be stored in the snapshotted project assets directory.')
        elif image.source != 'GENERATED':
            raise ValueError(f'Image {image.name} uses unsupported {image.source}; sequences/movies require a separate adapter.')
    bpy.context.scene['img2blender_collection'] = collection.name
    bpy.context.scene['img2blender_stage'] = spec['_stage']
    bpy.context.view_layer.update()
    audit = audit_model(collection, spec)
    audit['blenderVersion'] = bpy.app.version_string
    audit['images'] = []
    write(run/'audit.json', audit)
    if not audit['passed']: raise ValueError('; '.join(audit['errors']))
    cameras = configure_scene(spec, collection)
    images = render_views(run, spec, collection, cameras, 'basic')
    objects = list(collection.all_objects)
    materials = [(obj, [slot.material for slot in obj.material_slots]) for obj in objects if hasattr(obj.data, 'materials')]
    clay = bpy.data.materials.new('Review Clay'); clay.diffuse_color = (.55, .55, .55, 1); clay.use_nodes = True
    bsdf = clay.node_tree.nodes.get('Principled BSDF'); bsdf.inputs['Base Color'].default_value = (.55, .55, .55, 1); bsdf.inputs['Roughness'].default_value = .8
    try:
        for obj, slots in materials:
            for slot in obj.material_slots: slot.material = clay
        during = audit_model(collection, spec)
        write(run/'clay-audit.json', during)
        require_mode_audit(during, audit, 'Clay')
        images += render_views(run, spec, collection, cameras, 'clay')
    finally:
        for obj, slots in materials:
            for slot, material in zip(obj.material_slots, slots): slot.material = material
        bpy.context.view_layer.update()
    after = audit_model(collection, spec)
    require_mode_audit(after, audit, 'Basic restoration', restore_materials=True)
    bpy.data.materials.remove(clay)
    bpy.context.scene.camera = cameras[0]
    bpy.context.scene['img2blender_geometry_fingerprint'] = audit['geometryFingerprint']
    bpy.context.scene['img2blender_run_seconds'] = time.monotonic()-started
    # Process-local preference only: headless saves need no desktop thumbnail/cache writes.
    bpy.context.preferences.filepaths.file_preview_type = 'NONE'
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(run/'model.blend'), check_existing=False)
    audit.update(images=images, clayGeometryParity=True, basicMaterialsRestored=True,
                 renderSeconds=time.monotonic()-started, cameras=[{'id':v['id'], 'matrix':list(sum((list(row) for row in c.matrix_world), [])), 'type':c.data.type, 'lens':c.data.lens, 'orthoScale':c.data.ortho_scale} for v,c in zip(spec['views'], cameras)])
    write(run/'audit.json', audit)


def reopen(run):
    bpy.ops.wm.open_mainfile(filepath=str(run/'model.blend'), load_ui=False)
    scene = bpy.context.scene
    collection = bpy.data.collections[scene['img2blender_collection']]
    actual = audit_model(collection, read(run/'spec.json')); expected = read(run/'audit.json')
    unpacked = [image.name for image in bpy.data.images if image.users and image.source == 'FILE' and not image.packed_file]
    write(run/'reopen.json', {'passed': not unpacked and actual['passed'] and actual['geometryFingerprint']==expected['geometryFingerprint'] and actual['materialFingerprint']==expected['materialFingerprint'],
                             'geometryFingerprint': actual['geometryFingerprint'], 'materialFingerprint': actual['materialFingerprint'],
                             'blenderVersion': bpy.app.version_string, 'errors': actual['errors'], 'unpackedImages': unpacked})


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--')+1:]
    mode, directory = args
    run = Path(directory).resolve(strict=True)
    if mode == 'build': build(run)
    elif mode == 'reopen': reopen(run)
    else: raise ValueError('Expected build or reopen')
