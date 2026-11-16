// Run: IMG2THREEJS_THREE_MODULE=/absolute/path/to/three.module.js node --test <this file>
// On Windows set $env:IMG2THREEJS_THREE_MODULE first. Real Three.js; no fake materials.
import assert from 'node:assert/strict';
import test from 'node:test';
import { pathToFileURL } from 'node:url';
import { createAppearanceController } from './appearance.mjs';

test('material toggles preserve geometry, hierarchy, instance data and source materials', {
  skip: !process.env.IMG2THREEJS_THREE_MODULE && 'Set IMG2THREEJS_THREE_MODULE to run the real Three.js contract',
}, async () => {
  const T = await import(pathToFileURL(process.env.IMG2THREEJS_THREE_MODULE).href);
  const root = new T.Group();
  const geometry = new T.BoxGeometry();
  const texture = new T.Texture();
  const material = new T.MeshPhysicalMaterial({ color: '#8b2020', map: texture, transmission: .7, transparent: true, opacity: .5 });
  const mesh = new T.Mesh(geometry, [material, material]);
  mesh.position.set(1, 2, 3);
  root.add(mesh);
  const instances = new T.InstancedMesh(geometry, material, 2);
  instances.setMatrixAt(1, new T.Matrix4().makeTranslation(2, 0, 0));
  instances.setColorAt(1, new T.Color('#0000ff'));
  root.add(instances);
  const originalArray = mesh.material;
  const source = JSON.stringify(material.toJSON());
  const shape = () => JSON.stringify(root.children.map((m) => ({
    id: m.uuid, parent: m.parent.uuid, geometry: m.geometry.uuid,
    vertices: Array.from(m.geometry.attributes.position.array),
    indices: Array.from(m.geometry.index.array), position: m.position.toArray(),
    quaternion: m.quaternion.toArray(), scale: m.scale.toArray(), visible: m.visible,
    count: m.count, instances: m.instanceMatrix && Array.from(m.instanceMatrix.array),
    instanceColors: m.instanceColor && Array.from(m.instanceColor.array),
  })));
  const before = shape();
  const controller = createAppearanceController(root);
  assert.equal(controller.mode, 'basic');
  for (let i = 0; i < 3; i++) {
    controller.setMode('clay');
    assert.equal(mesh.material[0], instances.material);
    assert.equal(mesh.material[0].map, null);
    assert.equal(mesh.material[0].transmission, 0);
    assert.equal(mesh.material[0].transparent, false);
    assert.equal(shape(), before);
    controller.reset();
    assert.equal(mesh.material, originalArray);
    assert.equal(instances.material, material);
    assert.equal(JSON.stringify(material.toJSON()), source);
  }
  assert.throws(() => controller.setMode('unknown'));
  controller.setMode('clay');
  let disposed = 0;
  mesh.material[0].addEventListener('dispose', () => disposed++);
  controller.dispose();
  assert.equal(disposed, 1);
  assert.equal(mesh.material, originalArray);
  assert.equal(shape(), before);
  const unsupported = new T.Mesh(geometry, new T.ShaderMaterial());
  assert.throws(() => createAppearanceController(unsupported));
  material.displacementMap = texture;
  assert.throws(() => createAppearanceController(root));
});
