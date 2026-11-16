# Project and runtime contract

Run `scripts/project.py --help` for commands. It uses ordinary Python 3.10+ without external
packages; Blender supplies `bpy`. Tested versions are recorded in the distribution validation
report. Windows paths with spaces must be separate quoted arguments. `run` passes an argument
array to Blender with `--background --factory-startup --disable-autoexec --python-exit-code 1`.
It does not attach to or modify an open Blender session. Only run trusted modeling scripts.

## Files and authoring

- `run-inputs.json`: nominated reference hashes, fresh run ID, start timestamp and tool revision.
- `BRIEF.md`: intended result, authority per feature, observations, estimates, uncertainties.
- `spec.json`: construction/review requirements. Empty name/use/style/parts/features are blocked.
- `parameters.json`: single authoritative source of object-specific dimensions and profiles.
- `build.py`: `build(spec, parameters)` returns a scene-linked `bpy.types.Collection`.
- `assets/`: later texture files or vendored helpers; recursively hashed and copied per attempt.
- `.img2blender/state.json`, `CURRENT_STATUS.md`: ordered stage and acceptance records.
- `runs/NNNN-stage/`: immutable source copies, logs, Basic/Clay PNGs, `model.blend`, audit,
  reopening evidence and timing. Failed attempts remain, and are never reported accepted.

The builder may use normal Blender Python, but no viewer code, UI-area operators, network
downloads, earlier object sources or imports from another reconstruction. Keep authoring
in build.py and parameters.json for complete snapshots. Store any vendored helper modules
or later static textures in project `assets/`; the runner snapshots and hashes them too.
Resolve those paths relative to `Path(__file__).parent` in the builder. External image paths,
movie textures and image sequences are rejected. Static textures are packed into the saved
master and checked on reopening. A `.blend` is native output, not a substitute for the source.

Each model object has `obj['part_id']` set to a declared part ID. Exactly one object per part
also has `obj['part_anchor'] = True`; details share their owner's ID. Anchors may be mesh
objects or empties. A part may declare `parent`; its anchor must descend from that parent's
anchor. Do not create collection instances in the first implementation: they are rejected
until a complete count/identity adapter exists. Evaluated geometry includes mesh, curve,
surface and font objects and realized modifier results through the evaluated depsgraph.
Unrealized instances are rejected; non-rendering construction objects are excluded from counts.

Minimal spec additions after inspecting the reference:

```json
{
  "name": "Reference study", "use": "editable Blender scene", "style": "faithful",
  "appearance": "geometry-first",
  "reference_roles": {"R1": "primary silhouette", "R2": "rear attachment only"},
  "parts": [{"id": "body"}, {"id": "cap", "parent": "body"}],
  "critical_features": [
    {"id": "body-profile", "references": ["R1"], "target": "Match the measured taper"}
  ]
}
```

Retain the template's units/render/views fields. `units.system` is NONE/METRIC/IMPERIAL;
`scale_length` is meters per Blender unit. Record scale confidence separately. A triangle
target is positive and soft: overruns become audit warnings, not automatic fidelity failures.
`render.engine` is CYCLES (CPU default) or BLENDER_EEVEE, never silently substituted on failure.
Material node APIs must match the installed Blender. Clay is a temporary opaque material-slot
replacement; node-based Set Material modifiers need their evaluated materials checked too.
The runner rejects materials used by evaluated faces if they are generated only at evaluation and cannot be overridden safely. Unused evaluated material slots do not fail the gate.
Shader displacement is also rejected because it can change the rendered silhouette outside
the evaluated-mesh fingerprint. Use explicit geometry or modifiers for physical relief.
The fingerprint rounds coordinates and transforms to eight decimal places in scene units;
it is an edit-detection tolerance, not a dimensional-accuracy claim.

Each view needs a filename-safe ID and either a nonzero `direction` (auto-fit perspective)
or explicit `position` and `target`. Optional `orthographic_scale` selects orthographic
projection; `lens` defaults to 50mm. `hide_parts` lists intentionally removed assemblies.
At least two assembled views are required; use more for critical/rear details. All views are
rendered twice. Cameras, lighting and geometry stay fixed between Basic and Clay. The saved
master restores Basic materials, normal part visibility and the first review camera.

## Review records

For declared surface contacts, add `interfaces` to the spec. Each entry requires a unique
`id`, `probe_object`, `surface_object`, `vertex_group`, finite nonnegative `max_gap` in world
scene units and optional `min_samples` (at least3, default3). The two names resolve to distinct
delivered meshes. The probe's named vertex group marks real contact vertices; evaluated group
weights >=0.5 select samples after modifiers. The runner measures nearest distances to the
other evaluated surface, fails missing/empty coverage or excess gap, and persists results in
Basic and `clay-audit.json`. Example:

```json
{"interfaces":[{"id":"mount-contact","probe_object":"Mount","surface_object":"Shell",
"vertex_group":"contact","max_gap":0.001,"min_samples":8}]}
```

This is unsigned sampled proximity, not an interior/penetration, full collision or motion test.
Declare separate evidence for those concerns when required. An empty list is explicitly
not-applicable, not verified fit. Nominate surface contacts during planning instead of omitting
them to avoid a failed gate. Use contextual feature review for non-contact clearances.

Part certainty (observed/inferred/unknown) belongs in the spec/brief independently of pass/fail.
Local frames should be stored in parameters and implemented as useful assembly origins; check
world-geometry preservation when changing origins. Merely having a named empty at the world
origin does not prove this requirement.

After opening the actual PNGs, write a report such as:

```json
{
  "decision": "refine",
  "summary": "The cap overhang is too broad against R1; reduce its radial offset.",
  "images": ["front-basic.png", "front-clay.png", "right-basic.png"],
  "features": [{"id": "body-profile", "status": "fail", "notes": "Describe the observed discrepancy."}]
}
```

Image names resolve only inside the latest run. Acceptance requires every configured image
to be listed and every critical feature reviewed as pass. The scripts validate those records
and file hashes; they cannot prove that an agent visually inspected an image. Source changes
invalidate an unrecorded acceptance. A refinement records the failed review before allowing
the next attempt. Technical run failures consume a separate three-attempt retry allowance.
The stage order and correction counters cannot be skipped by the ordinary CLI.

`request-input` pauses until `resume --note <user-answer>` records the clarification. Reaching
the correction limit is stopped rather than paused; do not start a fresh run merely to evade
it. Agree a revised scope/strategy with the user and retain the prior evidence.

At form acceptance, geometry-first waits for `approve-geometry --note <user-instruction>`.
Geometry-only completes; finished continues to appearance. The accepted form fingerprint
also supports a later explicit finish request through `approve-geometry`, reopening the
completed geometry-only run without discarding its geometry or reviews. The form fingerprint
must match appearance geometry. If a shape change is required, use
`geometry-correction --note <reason>` to return to form, retaining counts/history and the
old acceptance. Complete only after the relevant reviews; no hidden final stage is invented.

## Check boundaries and timing

The audit checks component coverage/parenting, finite evaluated coordinates, positive geometry,
triangle counts, zero-area faces, edge incidence, material availability and material-only Clay
parity. Mesh fingerprints include world transforms, parents, evaluated positions and topology.
The saved `.blend` is reopened in a separate process and compared with that fingerprint.
Geometry-node instances are rejected, not omitted from counts. Watertight solids, collision,
wall thickness, physical assembly fit, UV quality, rig deformation and likeness require
additional relevant evidence. Treat every unimplemented check as untested.

`timing.json` separates total elapsed wall time from accumulated Blender process seconds.
It freezes geometry-review-ready/approved and completed timestamps when those events occur;
user waiting time is included in total wall time, not attributed to GPU/CPU modeling time.
No API token/cost estimate is invented. Run results include actual Blender version and hashes.
