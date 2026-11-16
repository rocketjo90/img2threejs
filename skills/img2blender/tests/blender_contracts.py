"""Native audit regression tests. Run with Blender --background --python this.py -- output.json."""
import importlib.util
import json
from pathlib import Path
import sys
import bpy

ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    loader=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(loader);loader.loader.exec_module(module);return module
runtime=load('runtime',ROOT/'scripts/blender_runtime.py')
fixture=load('fixture',ROOT/'tests/fixture_build.py')
spec=json.loads((ROOT/'assets/spec.json').read_text())
spec['parts']=[{'id':'body'},{'id':'cap','parent':'body'}]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
collection=fixture.build(spec,{})
bpy.context.view_layer.update()
results={}
def audit():
    bpy.context.view_layer.update();return runtime.audit_model(collection,spec)
def check(name,condition):
    results[name]=bool(condition)
    if not condition:raise AssertionError(name)
baseline=audit();check('valid-beveled-mesh',baseline['passed'] and baseline['triangles']>24)
body=bpy.data.objects['body'];cap=bpy.data.objects['cap']
body['part_anchor']=False;check('missing-anchor-blocked',not audit()['passed']);body['part_anchor']=True
old_parent=cap.parent;cap.parent=None;check('wrong-parent-blocked',not audit()['passed']);cap.parent=old_parent
body['part_id']='unexpected';check('unknown-part-blocked',not audit()['passed']);body['part_id']='body'
saved=body.data.materials[0];body.data.materials.clear();check('missing-material-blocked',not audit()['passed']);body.data.materials.append(saved)
nodes=saved.node_tree.nodes;node=nodes.new('ShaderNodeDisplacement');output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL');saved.node_tree.links.new(node.outputs['Displacement'],output.inputs['Displacement'])
check('shader-displacement-blocked',not audit()['passed']);nodes.remove(node)
before=audit()['geometryFingerprint'];body.location.x+=.01;check('shape-drift-detected',audit()['geometryFingerprint']!=before);body.location.x-=.01
before=audit()['geometryFingerprint'];saved.diffuse_color=(.8,.1,.1,1);check('color-preserves-geometry',audit()['geometryFingerprint']==before)
check('restored-fixture-valid',audit()['passed'])

# A material-only failure must stop Clay review even when geometry matches.
failed=dict(baseline, passed=False, errors=['Synthetic material-override failure'])
try:
    runtime.require_mode_audit(failed,baseline,'Clay')
    check('clay-failure-enforced',False)
except ValueError:check('clay-failure-enforced',True)
data=bpy.data.meshes.new('Contact probe');data.from_pydata([(-.1,-.1,.8),(.1,-.1,.8),(.1,.1,.8),(-.1,.1,.8)],[],[(0,1,2,3)])
probe=bpy.data.objects.new('Contact probe',data);collection.objects.link(probe)
group=probe.vertex_groups.new(name='contact');group.add([0,1,2,3],1,'REPLACE')
spec['interfaces']=[{'id':'mount','probe_object':probe.name,'surface_object':'body','vertex_group':'contact','max_gap':.0001,'min_samples':4}]
bpy.context.view_layer.update()
check('measured-contact-passes',runtime.audit_interfaces(collection,spec)['passed'])
probe.location.z=.05;bpy.context.view_layer.update()
check('surface-gap-blocked',not runtime.audit_interfaces(collection,spec)['passed'])
probe.location.z=0;group.remove([0,1,2,3]);bpy.context.view_layer.update()
check('empty-contact-coverage-blocked',not runtime.audit_interfaces(collection,spec)['passed'])
group.add([0,1,2,3],1,'REPLACE');spec['interfaces'][0]['max_gap']=float('nan')
check('nonfinite-contact-tolerance-blocked',not runtime.audit_interfaces(collection,spec)['passed'])
spec['interfaces']=[]
check('no-contacts-not-applicable',runtime.audit_interfaces(collection,spec)['status']=='not-applicable')
collection.objects.unlink(probe)
# Boolean TRANSFER can introduce an evaluated-only material; INDEX may retain the
# extra slot unused. Reject actual face use, not harmless unused slots.
bpy.ops.mesh.primitive_cube_add(size=1,location=(.24,.03,.42))
cutter=bpy.context.object;cutter.dimensions=(.22,.19,.16)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
cutter.hide_render=True
foreign=bpy.data.materials.new('Cutter only material');cutter.data.materials.append(foreign)
boolean=body.modifiers.new('Material regression','BOOLEAN');boolean.object=cutter;boolean.operation='DIFFERENCE';boolean.solver='EXACT';boolean.material_mode='TRANSFER'
check('used-evaluated-only-material-blocked',any('evaluated-only material' in e for e in audit()['errors']))
boolean.material_mode='INDEX'
check('unused-boolean-material-allowed',audit()['passed'])
destination=Path(sys.argv[sys.argv.index('--')+1]);destination.write_text(json.dumps({'passed':all(results.values()),'blenderVersion':bpy.app.version_string,'checks':results},indent=2),encoding='utf-8')
print(json.dumps(results))
