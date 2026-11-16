# Print adapter experiment — reference for later work

Archived from review of a November 2026 rocket reconstruction made with this fork in
Claude. This is an optional engineering reference, not part of the default image-to-Three.js
workflow, an instruction to start printing, or a certified manufacturing recipe.

## Useful architecture

The display model and a separate print model reused the same geometric profiles and
parameter source. Three.js remained the reconstruction engine. Headless Blender processed
the requested print meshes downstream, including voxel remeshing and STL export.
This preserved rapid browser iteration without treating a shaded display mesh as a
manufacturable solid. Keep accepted geometry and destination overrides separately versioned.

## What the experiment prepared

- An explicitly chosen 170 mm overall size, with units carried into millimeter exports.
- A ten-part kit and an alternative one-piece version, assembled and print-oriented STLs,
  a multi-object 3MF plate, assembly/exploded/section previews, and separate decal artwork.
- Inward wall-thickness adjustments, nose and tip spigots, cockpit supports, a closed end
  cap and locating features, and printable replacements for floating display-only details.
- Enlarged fine features and coarser knurling, plus inspection of interference and gaps.

These are examples of destination-specific decisions, not defaults for other subjects.
Wall thickness, tessellation, joints, clearance, orientation and support strategy depend
on material, process, printer, object scale and intended assembly. Do not copy the example's
numbers or artistic cockpit into another reconstruction.

## Evidence and limitations

The saved project reports described closed meshes and no detected surface intersections.
The independent review checked STL structure/counts and inspected previews, but did not
rerun every mesh audit, slice the kit, or physically print/test-fit it. The kit totaled
approximately 1.48 million triangles; this is not evidence of dimensional accuracy.

Surface-intersection tests plus sampled nearest-surface gaps do not establish containment,
insertion paths, retention or assembly access. A nominal wall or clearance is not its
measured minimum. Remeshing may soften seams, thin features or mating interfaces: compare
the converted result to the accepted source, including critical sections and silhouettes.
Keep mesh validity, geometric fit, slicer review and physical test-print results separate.

## When printing is explicitly requested later

Confirm units/scale, printer/process/material and separate-versus-one-piece intent. Derive
an adapter from the shared parameters, documenting every print override. Verify exported
solids and critical features, then inspect the actual sliced artifact and test mating
features before claiming practical fit. Preserve editable source, export settings,
source/output hashes, preview sections and the limits of every check. Do not infer that
screen-space smooth shading or texture/normal detail creates printable geometry.
