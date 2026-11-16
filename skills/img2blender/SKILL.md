---
name: img2blender
description: Reconstruct an object or character from supplied images using staged Blender Python modeling and headless Blender renders. Use for editable Blender assets, reference-led geometry review, and requested export preparation. Produces native blend files and review images without a browser viewer.
license: Apache-2.0
metadata:
  version: "0.2.0"
---

# img2blender

Build the model in Blender using Python. Run Blender in background mode; no GUI, browser,
Three.js viewer, commercial image-to-3D service or local AI model is required. The host AI
interprets references, authors the object-specific modeling code and inspects renders.
The scripts manage fresh projects, native execution, evidence and review checkpoints;
they are not an automatic image-to-mesh inference engine.

This is the Blender adaptation of our img2threejs fork workflow at `5c2aa65`.
Read [workflow.md](references/workflow.md) before a new subject, and
[project-contract.md](references/project-contract.md) before authoring or running code.
Apply [feature evidence](references/feature-evidence.md) when planning or reviewing geometry:
negative space, actual surface contact and useful local origins need their own evidence.
The source relationship and intentional differences are recorded in
[provenance.json](references/provenance.json). It does not depend on img2threejs being installed.

## Start or resume

Reuse known choices: intended use, reference variant, style, scale/constraints and appearance
checkpoint. Ask only material unanswered questions. A request for an editable Blender scene
already establishes the destination. A printing request needs physical dimensions before
print-qualified delivery; it does not imply the highest possible polygon count.

For a new reconstruction, including a fresh attempt at the same object:

```powershell
py scripts/project.py new --out <new-folder> --reference <primary-image> --reference <secondary-image>
py scripts/project.py status --project <folder>
```

Run these commands from the skill directory or use absolute script paths. The initializer
refuses existing destinations, copies nominated references and generic templates only, and
records input hashes, run ID and start time. Never copy a previous object's fitted profiles,
mesh, builder or spec into a fresh run. Reuse generic utilities and the user's requirements.
A new directory does not prove isolated AI memory; label that limitation in benchmarks.
For ordinary corrections, additional parts or finish work, resume the existing project.

## Construct and review

1. Inspect the actual references. Write `BRIEF.md`, `spec.json` and `parameters.json`:
   reference authority per feature, assembly state, raw image measurements, inferred depth,
   component relationships, critical shape targets, cameras and a suitable refinement budget.
   Use observed/inferred/unknown labels; unknown does not mean invisible.
2. Author `build.py` using the documented `build(spec, parameters)` contract. Return a named
   model collection, with stable part IDs. Keep dimensions in the parameter file, preserve
   parent relationships and editable modifiers where useful. Initial scaffolds deliberately
   fail until real object code and a brief have been supplied.
3. Run the current stage, using the installed Blender executable:

   ```powershell
   py scripts/project.py run --project <folder> --blender "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
   ```

   `BLENDER_BIN` or Blender on PATH can replace `--blender`. No shell command concatenation
   or visible Blender window is used. Each attempt gets an immutable numbered directory,
   source snapshots, Basic/Clay PNGs, `.blend`, mesh audit, reopened-file check and timing.
   Read `CURRENT_STATUS.md` after failures; do not reset state to bypass a stop.
4. Open the renders and compare them with references. Inspect every critical part together
   with its neighbors: silhouette, seams, curvature, holes/recesses, contact, clearance and
   exposed/assembled states. Use a matched camera before judging proportions. Extra views
   can temporarily hide an explicitly nominated cover; do not invent hidden machinery.
5. Write a visual review JSON **after inspection**, then record it:

   ```powershell
   py scripts/project.py review --project <folder> --report <review.json>
   ```

   Choose `accept`, `refine`, or `request-input`. Automatic mesh checks do not establish
   reference fidelity. Acceptance is bound to current inputs and the actual run artifacts.
   Stages are blockout → structure → form → appearance. Appearance is deferred until the
   agreed checkpoint allows it. Correction limits are three per stage and six overall;
   reaching either stops the run for a revised user brief, not a counter reset.

## Geometry first, no viewer

Default `appearance: geometry-first` produces reference-based simple materials plus neutral
opaque Clay renders of the same geometry. These are paired images, not an interactive toggle.
The runner temporarily replaces material slots for Clay and restores them exactly; it checks
evaluated geometry, hierarchy and transforms before/after. Transparent-cover removal is a
separate camera option. Basic materials need no texture maps, decals, scratches or aging.

At accepted form review, stop for the user's geometry feedback. Leave appearance pending.
When the user approves proceeding, record their instruction and resume:

```powershell
py scripts/project.py approve-geometry --project <folder> --note "User approved geometry and requested finish."
```

`geometry-only` completes after form review; `finished` already authorizes appearance.
An appearance change must preserve accepted geometry. The runner reports geometry drift;
use an explicitly recorded correction instead of concealing it as surface work.

## Deliver

Provide the actual saved `.blend`, editable Python/spec/parameters, review PNGs and current
status/timing reports. Link the latest accepted run, not an unreviewed last attempt. Review
time, wall-clock time and Blender execution time are distinct measurements. No HTML viewer
is produced. Keep original references private unless sharing them is requested.

The saved scene is reopened in a separate background Blender process and its evaluated
geometry compared before acceptance. Retain failed runs and report checks that are partial.
Print/game exports are additional requested operations: see the destination section in
[workflow.md](references/workflow.md). This version does not claim automatic rigging,
certified printing, every export format, or parity with img2threejs's domain plugins.
