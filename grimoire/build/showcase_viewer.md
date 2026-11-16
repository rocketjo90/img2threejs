# Interactive showcase delivery

This fork defaults to presenting an implemented reconstruction in an object-centered,
responsive viewer, with an offline standalone HTML copy and editable source. This is a
fork presentation convention, inspired by the Dynamite player reconstruction; it is
not a claim that the upstream skill or reference photos prescribed a webpage design.
Use this from the first reviewable model through interaction and final delivery. Existing modeling and quality gates
still apply. Follow explicit user requests for code-only output, integration into an
existing application, a different design, or analysis without implementation instead.

## Presentation

- Give the model most of the space. Use a restrained neutral background, legible system
  fonts, a short object introduction, and a compact inspection panel. Adapt colors and
  copy to the object; do not reuse the player's slogans, branding, or finish choices.
- Preserve the approved Object / Study visual language: warm seamless background, modest
  left introduction, large central object and quiet right controls. No bordered viewport,
  oversized full-width headline or stack of diagnostic cards in the default presentation.
  Reuse this shell across fresh reconstructions; new geometry does not require a new UI.
- Use restrained studio illumination and soft contact shadows with a floor sized to the
  assembly. Fit lights/shadow bounds to the actual model. Avoid harsh long shadows, clipped
  highlights or bloom that conceals edges. Neutral review lighting is separately controlled.
- Keep primary controls visible; put counts, uncertainty notes and validation information
  in `#inspection-panel`. Maintain readable text and keyboard focus rather than copying
  the original viewer's smallest captions exactly.
- On desktop, place introduction, model, and controls alongside one another. On narrow
  screens, put the model between the introduction and controls. Keep controls outside
  the drag surface and avoid horizontal overflow, clipped text, or a tiny canvas.
- Keep source attribution and known approximation limits visible but brief. Only name
  a manufacturer or model when supported by the references. Never expose private paths.
- Presentation lighting may flatter the object, but must not hide geometric errors.
  Match reference cameras and neutral diagnostic settings separately for fidelity review.

The reusable [HTML shell](../../assets/showcase-viewer/index.html) and
[stylesheet](../../assets/showcase-viewer/viewer.css) provide the layout and control
hooks. `forge/new_project.py` copies them to `viewer/`. Adapt object copy and integration,
preserving the visual layout unless the user requests a different one; they are a starter, not a
working reconstruction. The disabled controls deliberately remain inert until the real
model adapter is attached. Do not deliver the shell or a placeholder model as completed work.

Use this viewer throughout the agreed review stages. At a geometry checkpoint, make the
Basic appearance / Clay toggle, useful camera presets and part inspection available; detailed finish
controls can remain absent. Later appearance work updates the same project and part IDs.
Selection, separation, removal and detail ownership must use one assembly hierarchy. A
separate part can share a continuous outer profile with its neighbour. An exploded view
shows the modeled parts; it does not establish missing interiors or physical assembly fit.

## Connect the actual reconstruction

1. Import the generated model factory into the project's normal Three.js entry point.
   Keep renderer, lights, controls, and UI outside that factory. Mount the canvas in
   `#viewport`; measure that element with `ResizeObserver`, updating renderer dimensions
   and camera aspect. Fit the whole object with margin in both desktop and mobile layouts.
2. Attach orbit and zoom controls; wire `[data-view]` buttons to useful reference-aligned
   camera presets. Preserve the model's coordinate convention. Support touch rotation
   and zoom without trapping scrolling elsewhere on the page.
3. Build selection and explosion from one named assembly list. Raycast only model meshes;
   resolve detail hits to their owning assembly and report the part in `#selection`.
   Provide the same selection through `#parts` for keyboard users. Follow
   [geometry patterns](geometry_patterns.md) for pivots, assembly separation and
   `explodeWithParent`; labels, screws, and other integral details move with their parent.
4. Wire `#explode` to assembly separation and `#amount` to the displayed percentage.
   Cache rest transforms, avoid cumulative drift, and keep the exploded assembly in view.
5. Populate `#object-options` only with implemented, relevant controls: reference-supported
   finishes, opening a lid, pressing a mechanism, or removing a cartridge, for example.
   Label inferred motion as illustrative when its mechanics are unknown. Do not invent
   an interior merely to provide an action. Prevent conflicting actions while exploded.
6. Wire `#reset` to restore the initial camera, selection, separation, finish, and action
   states. Enable each control only after its behavior is connected. Replace the loading
   message with interaction instructions on success; show a readable error on failure.
   Remove unused control groups. Give color swatches text alternatives and active states.
7. Preserve keyboard focus indicators, native control labels, sufficient contrast, and
   reduced-motion preferences. Do not rely on hover or color alone to explain state.

### Appearance and reference comparison

Construct the model once with basic source-supported Standard/Physical materials. Import
[`appearance.mjs`](../../assets/showcase-viewer/appearance.mjs) into the project's bundled entry:

```js
const appearance = createAppearanceController(model, {
  buttons: document.querySelectorAll('[data-appearance]'),
  onChange: () => render(),
});
// The viewer's Reset handler also calls appearance.reset().
```

Import `createAppearanceController` from the copied helper. Enable the enclosing fieldset
after integration. The helper restores original material references exactly, handles material
arrays and shared materials, and disposes only its own clay clones. It never constructs or
changes geometry, cameras, selection, visibility, transforms or action state. Recreate/dispose
the controller when replacing the model or its material set. Standard/Physical materials
without displacement are supported; custom shader deformation needs a reviewed adapter.
Clay is opaque and removes maps/emission/metallic response; opening covers or inspection
transparency is a separate explicit control. Do not mutate the stored basic materials while
the controller is active. Detailed finish is a later, separately reviewed material set.

The helper's real-Three.js regression test is `assets/showcase-viewer/appearance.test.mjs`.
Set `IMG2THREEJS_THREE_MODULE` to the absolute path of the project's `three.module.js`, then
run `node --test assets/showcase-viewer/appearance.test.mjs` from the skill root. Without that
dependency the test reports a skip, not a pass. Also verify both appearances in the browser
with the project's Three.js version; the clay shader suppresses instance-color tinting.

Populate `#reference-panel` with an approved embedded image/crop and a matched-camera preset;
remove it if references cannot be distributed. Comparison uses fixed neutral light and a plain
background, with presentation floor/shadows disabled when they contaminate silhouette review.
Record the camera and appearance mode. Returning to presentation restores the previous camera
and lighting. The template supplies the panel, not automatic camera solving or image matching.

## Deterministic evidence

Implement an explicit capture mode, such as `?capture=1`, which applies the shell's
`capture` class to `body`, hides presentation UI, and gives the canvas the full viewport.
Wait for resize and render completion before capture. Set the specified camera, assembly
state, seed, and lighting; disable automatic motion and controls updates for the capture.
Expose a readiness signal only after assets and the first settled frame are ready.
Follow [render capture](../feedback/render_capture.md) and the existing review gates.
Capture-mode screenshots establish model evidence; also inspect normal desktop/mobile
screenshots to establish that the actual delivered viewer works.

Reuse the existing capture and render-manifest tooling where it supports the project.
Record the camera, assembly state and source revision for each comparison. Reuse unaffected
evidence only when its inputs are unchanged and the gate permits it; refresh views affected
by a geometry, camera, material or lighting change. Always verify the final packaged viewer.
This is an execution guideline, not a claim that automatic incremental validation exists.

## Build and delivery

Default deliverables are a standalone HTML viewer, an editable source project (including
the reconstruction spec), a preview image, and a source archive with run instructions.
Omit dependency caches and private references from the archive unless explicitly requested.
Preserve required library license notices. Clearly describe estimated dimensions and
unverified details; completed software checks do not establish physical accuracy.

Build the project first, then bundle its real JavaScript, CSS, and required assets into
the HTML using a supported bundler or a verified project-specific packaging step. Ensure
there are no runtime imports, fetches, fonts, textures, or other resources that depend on
a development server or CDN. Avoid ad hoc text replacement of arbitrary script contents.
If offline packaging is unavailable, retain the working served project as an interim result
and state that default delivery remains incomplete. Do not call it standalone/offline or
silently substitute that format. An explicit user choice of hosted/integrated output overrides
the default. Reuse a proven bundling setup rather than reconstructing the viewer each time.

Before delivery:

- Run the project's typecheck/build and existing model gates.
- Inspect the real model at desktop and phone widths, including normal and exploded states.
- Exercise orbit/zoom, every view, part selection, separation, reset, and every optional
  action or finish. Check that details follow parts and reset works after combined actions.
- Switch Basic → Clay → Basic after orbiting and separating parts. Verify geometry/index
  buffers, hierarchy, transforms and instance data are identical before/after, and basic
  materials restore exactly. Inspect both renders; a screenshot count alone is not evidence.
  Verify the reference panel and matched view if included, including return to presentation.
- Check keyboard access, resize behavior, browser errors, and failed resource requests.
- Open the final standalone file directly with networking disabled, repeat its controls,
  and confirm that the rendered result matches the served version. Check the packaged
  file, not just the development server or an HTML page claiming offline support.

Save `delivery-review.json` beside the final artifact, containing its filename and SHA-256,
source revision, chosen delivery format, test date, and checks for direct-file/offline load,
model readiness, console errors, failed/external requests, desktop/mobile layout and each
implemented control. Record `passed`, `failed` or `not-tested` with evidence for each check;
include served-versus-packaged visual parity. Hash the file after the final packaging edit.
A missing or untested required check is not a pass. Reference this report as evidence for
the `viewer-delivery` state step (new projects); older checklists still require this delivery
review under these instructions. The report records real browser tests, not a static HTML
scan or an assertion that bundling succeeded. It does not certify model fidelity.

Report what was actually checked and any remaining limitation. The shell saves repeated
layout work; it never substitutes for model-specific geometry, controls, or verification.
