# Reference-led Blender reconstruction

## Intake and evidence

Carry forward established use, style, primary variant, appearance stage and constraints.
Ask only missing decisions that change the deliverable. Choose polygon density for camera
distance, editing needs, intended curves and destination. Report evaluated triangles after
modifiers and instances, not only control-cage faces. A soft target is not an accuracy score.
Blender deliverables should keep useful topology and modifiers; do not triangulate the master
simply to reach a number. Low-poly style can be correct for any destination, including print.

Inspect each nominated reference before modeling. Name which image governs silhouette,
appearance, rear attachment or user-designed changes. Separate variants and assembled,
disassembled, open, damaged and cutaway states. Keep raw pixel readings apart from inferred
camera pose, fitted curves and depth. Known-size items constrain scale only with recorded
source and uncertainty. Do not average conflicting variants into a fictional object.

Make a compact construction map: stable part IDs, boundaries, local coordinate frames,
parent relationships, openings, thickness where known, and important interfaces. Record a
hole as observed, explicitly requested or inferred. Distinguish through-holes from recesses,
shadows, decoration and openings concealed by another part. Uncertain parts remain visible
unless a documented inspection state removes them. Hidden mechanisms should be simplified
or left unresolved rather than invented in detail.

## Modeling in Blender

Use native mesh, curve, extrusion, bevel, boolean and modifier operations appropriate to the
shape. Prefer a small set of shared profile/interface parameters over independent estimates
for adjoining components. Keep physical pieces separate even when their outer contour is
continuous. Preserve intentional steps, offsets and seams. Allocate profile samples by
curvature and projected error; linear subdivisions alone do not make a cone round at its tip.

Put named objects into the returned model collection. Keep helpers and cutters outside it or
in a separate linked helper collection, hidden from rendering; do not tag them as delivered
parts. Keep modifier dependencies in the saved scene. Use deterministic random seeds.
Do not delete assets in the user's open Blender session: every run starts a separate factory
startup background process. The authoring script must not open another blend file or load a
previous object's mesh during a fresh reconstruction.

Review important components both isolated where useful and in their assembled context.
Measure actual surface contact/clearance at interfaces; bounding-box overlap is insufficient.
Check mirrored geometry's handedness and normals. Record frame conversions and any applied
transforms, especially for future exports. Do not silently bake away editability to repair
a render. Basic colors and scalar material response are enough during geometry work.

## Review and efficient iteration

Use fixed, versioned cameras for comparisons. The runner's auto-fit cameras are convenient
inspection views, not solved reference cameras. Author an explicit position, target and
orthographic scale or lens for meaningful reference matching. Change cameras only with a
recorded reason. Check front/side/back and views exposing critical thickness or attachments.
Create exposed views by naming `hide_parts`; keep them separate from normal assembly views.

Review actual Basic and Clay images before writing judgments. Compare cropped critical
features in addition to whole-object silhouette. Record each critical feature as pass/fail/
unseen and identify the images inspected. Unseen is not passed. A mesh audit can pass for
the wrong shape; a beautiful render can hide invalid geometry. Do not prefill acceptance,
recycle generic comments or report a percentage of accuracy from an image-mask metric.

First solve silhouette and construction at modest render cost. Reuse the current brief,
cameras and reference analysis for corrections. Keep revisions immutable and mark changed
conclusions superseded. The first implementation rerenders all configured views per run;
incremental view caching is a future optimization, not a claimed feature. Do not suppress
failed gates or reset correction counts. Stop with a clear unresolved issue at the limit.

Geometry-first approval is a real checkpoint. Appearance never implicitly authorizes changing
accepted shapes. If finish reveals a geometry defect, record that correction explicitly;
the tool detects geometry drift and requires another geometry review. Elapsed time is never
approval. A finished-output request can already authorize the appearance stage.

## Native deliverables and destinations

The native master is the saved, reopened `.blend`, with editable source and named parts.
The default output includes paired PNGs and JSON/Markdown evidence; it has no web viewer.
Headless execution uses Blender's [command-line interface](https://docs.blender.org/manual/en/latest/advanced/command_line/).

Game exports require the requested format, scale, pivots, evaluated polygon budget, supported
materials and a destination import check. Print exports require physical units, appropriate
closed solids, minimum feature and wall thickness, intersections, clearances and exported
file inspection. Texture relief alone is not physical geometry. Validate in a slicer when
printing is requested; physical fit remains unverified until tested. The included audit
reports edge manifold counts and degenerate triangles, but does not certify thickness,
self-intersection, assembly motion or printing. Open surfaces can be legitimate scene assets.

Export only when requested and when the installed Blender supports the format. Keep export
overrides separate from the native parameters, record their reasons, and reopen/import the
actual export to check silhouette, seams, hierarchy and scale. Preserve the accepted master.
No export adapter, rigging system, domain plugin or image-to-mesh service is installed by
this skill. Organic subjects may require more explicit sculpting work; do not imply the
included generic fixture establishes arbitrary-subject accuracy.
