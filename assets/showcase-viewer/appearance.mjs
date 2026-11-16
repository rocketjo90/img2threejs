/** Material-only comparison. Call after the current model has been constructed.
 * Original materials must be basic reference colors/scalars at a geometry checkpoint.
 * Import with the project's bundler; no runtime dependency or network request here.
 */
export function createAppearanceController(root, { buttons = [], onChange = () => {} } = {}) {
  const records = [];
  const clones = new Map();
  root.traverse((mesh) => {
    if (!mesh.isMesh) return;
    const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
    for (const material of materials) {
      if (!material?.isMeshStandardMaterial || material.displacementMap) {
        throw new Error('Appearance toggle requires Standard/Physical materials without displacement; use geometry for shape.');
      }
    }
    records.push({ mesh, original: mesh.material, materials });
  });
  for (const { materials } of records) {
    for (const original of materials) {
      if (clones.has(original)) continue;
      const clay = original.clone();
      for (const key of Object.keys(clay)) {
        if (clay[key]?.isTexture) clay[key] = null;
      }
      clay.color.set('#b9b7b1');
      clay.emissive.set(0);
      clay.metalness = 0;
      clay.roughness = 0.78;
      clay.opacity = 1;
      clay.transparent = false;
      clay.alphaTest = 0;
      clay.depthWrite = true;
      clay.vertexColors = false;
      // Instance colors otherwise still tint Standard materials even with vertexColors=false.
      // Disable their fragment contribution without touching the instance color buffer.
      clay.onBeforeCompile = (shader) => {
        shader.fragmentShader = shader.fragmentShader.replace('#include <color_fragment>', '');
      };
      clay.customProgramCacheKey = () => 'img2threejs-neutral-clay-v1';
      if (clay.isMeshPhysicalMaterial) {
        clay.transmission = 0;
        clay.clearcoat = 0;
        clay.sheen = 0;
        clay.iridescence = 0;
        clay.anisotropy = 0;
      }
      clay.needsUpdate = true;
      clones.set(original, clay);
    }
  }
  let mode = 'basic';
  let disposed = false;
  function setMode(next) {
    if (disposed) throw new Error('Appearance controller has been disposed.');
    if (!['basic', 'clay'].includes(next)) throw new Error(`Unknown appearance mode: ${next}`);
    for (const { mesh, original, materials } of records) {
      mesh.material = next === 'basic' ? original :
        Array.isArray(original) ? materials.map((m) => clones.get(m)) : clones.get(original);
    }
    mode = next;
    for (const button of buttons) button.setAttribute('aria-pressed', String(button.dataset.appearance === mode));
    onChange(mode);
  }
  const listeners = Array.from(buttons, (button) => {
    const listener = () => setMode(button.dataset.appearance);
    button.addEventListener('click', listener);
    return [button, listener];
  });
  setMode('basic');
  return {
    get mode() { return mode; }, setMode,
    reset() { setMode('basic'); },
    dispose() {
      if (disposed) return;
      setMode('basic');
      for (const [button, listener] of listeners) button.removeEventListener('click', listener);
      for (const material of clones.values()) material.dispose();
      disposed = true;
    },
  };
}
