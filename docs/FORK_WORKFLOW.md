# This fork's reconstruction workflow

This fork extends img2threejs v2.0.1 with Windows support, an interactive showcase,
reference planning, task intake, and construction/export review. These are cumulative
parts of the tool. The upstream skill supplies staged procedural modeling, specifications
and review utilities; the host AI interprets references, writes/refines code and judges
visual evidence. Object-specific procedural code is expected, not a competing workflow.

## Working sequence

1. **Establish the brief.** Read the actual installed skill and identify its source/revision
   when starting a project or comparing hosts. The upstream version number alone cannot
   distinguish fork additions. Ask only unanswered questions about use, style, relevant
   constraints and appearance/review preferences; follow
   [task intake](../grimoire/intake/reference_planning.md#task-intake).
2. **Prepare evidence and construction.** Choose the primary variant and useful views,
   distinguish assembly states, record observed/inferred/unknown features, match cameras
   and establish major proportions. Define component relationships and a refinement budget
   appropriate to the destination. Keep this compact and proportional to the subject.
   Record authority per feature: proportions, appearance, attachments and user-designed
   additions can have different sources. Preserve raw measurements separately from fitted
   profiles and inferred camera/depth choices. Use one comparison protocol per active target.
3. **Build procedural Three.js in stages.** Follow the existing state, specification,
   generation and review gates. Reuse constructors and parameters where they express the
   reference correctly. Hand refinement is part of the process; preserve its decisions in
   supported spec fields or referenced versioned source before regeneration. Do not silently
   substitute an unrelated implementation for the validated model.
   Apply the [construction discipline](../grimoire/build/geometry_patterns.md#construction-discipline)
   for coordinate frames, curvature sampling, seam continuity, inspection transparency and
   consolidation of accepted corrections.
4. **Review geometry in the viewer.** When geometry-first review is selected, deliver the
   plain model with reference comparisons and relevant assembled/exposed views. Check each
   important part against both its neighbours and the reference. Respect the requested
   checkpoint; save the source, hierarchy, cameras and outstanding work for resumption.
5. **Continue with the selected appearance.** Geometry-only, simple materials and detailed
   textures are distinct outcomes. Add appearance when authorized, preserving accepted
   geometry and checking material boundaries, transparency and source-supported markings.
   Identify invented aging or other artistic interpretation. A finished-output request can
   already authorize this stage without another approval stop.
6. **Deliver and verify for the chosen use.** Retain the
   [interactive viewer and source](../grimoire/build/showcase_viewer.md). Apply Game, Blender
   or Print requirements only to requested destinations and supported exports. Keep visual
   fidelity, mesh validity, assembly fit and physical testing as separate claims.
   The default viewer is a fully contained HTML file, tested directly with networking disabled,
   plus editable source. A served/CDN-dependent viewer is an incomplete default delivery;
   report the limitation instead of silently changing the requested format.

## Shared source and destination adapters

Keep dimensions, profile stations, coordinate frames, part IDs and attachment transforms in
one parameter source imported by the model and any explicitly requested export adapter.
Represent destination changes as named overrides with reasons; do not fork unrelated copies
of the object's dimensions. Record the source revision/hash and overrides with each output.
Inspect silhouette, seams and attachment locations after conversion; topology repair,
decimation or remeshing must not silently move accepted features. The browser model remains
the geometry-review artifact. This contract adds no automatic exporter or print stage.

The [archived print-adapter notes](PRINT_ADAPTER_REFERENCE.md) preserve a later experiment
for future requested printing work. They are outside the default reconstruction workflow.

## Stage-aware validation and current status

`validate_sculpt_spec.py --strict-quality --pass-id <current-pass>` defers appearance quality
warnings only for blockout, structural-pass and form-refinement. Full validation remains the
default without a pass ID. The generator uses its requested/unlocked pass automatically;
it still rejects schema errors, shallow geometry specifications and locked future passes.
Do not use `--allow-nonstrict` for production. Deferred requirements remain visible and are
checked again when entering appearance. Generic state defers material extraction/wiring and
projection baking; other profiles retain their domain admission order. Declared textureless materials need supporting
evidence, real colors/scalar response and no contradictory texture fields; textured materials
retain their requirements. Neutral/reference renders still judge appearance.

Every `forge/next.py --state ...` refreshes `CURRENT_STATUS.md` and `current-status.json`
beside the state file, including current pass/step, pending/deferred work, stop reason,
latest recorded actions and the spec hash. Keep human decisions and dated history in separate
notes and link to this generated summary rather than leaving a stale status at their top.
These files summarize records; they do not validate screenshots, grant approval or certify
the current source against an old review. Do not change state/history to make a summary pass.
Keep stdout JSON parseable (`diagnose_render.py` writes status logs to stderr). Parse saved
JSON before accepting it as evidence; never concatenate logs into an assessment file.

Three.js remains this skill's construction and review path. Blender refinement or an
img2blender implementation is an explicitly chosen, separate route, not an automatic
replacement. A Blender destination does not require opening Blender before Three.js
modeling; inspecting a requested import may require it later. A future application can
use a general-purpose AI API to direct these same operations. Neither a commercial
image-to-3D generator nor a local AI model is required by this workflow.

## Corrections and efficient resumption

Resume with `forge/next.py` and the saved brief. Separate correction of an existing defect
from an added component, destination or appearance stage. Preserve accepted work and edit
the affected parameters/parts; inspect their dependencies before assuming they are isolated.
Reuse reference analysis, cameras, viewer code and unchanged assets. Do not reset counters,
discard failures or bypass a hard stop to accommodate a scope extension; report tooling
limitations and retain the changed scope in project notes.

Acceptance belongs to the reviewed revision. Keep evidence paths and revision identifiers
with reviews and mark affected earlier conclusions superseded in the project notes. An
old `continue` entry is not proof about changed geometry. Missing comparisons, unreadable
captures or contradictory `passed`/`nextAction` results remain unresolved; report them
instead of choosing the favourable field. These are manual review requirements until the
corresponding automation is implemented. Do not present them as new automated gates.

## Evaluating improvements

Compare three layers: the identified upstream baseline, this fork's additions, and the
agent's execution on a particular reconstruction. Check Git history or content hashes;
a directory name or unchanged version label is insufficient provenance. Credit existing
fork features rather than proposing them again. Distinguish inherited validator defects,
missing automation, and failure to follow instructions already present.

For speed/accuracy comparisons, hold references, scope, appearance stage and acceptance
criteria constant. Measure time to accepted geometry, corrective work, AI usage when
available, and destination usability. User-requested additions are scope changes, not
automatically failed iterations. File size, triangle count and screenshot count alone do
not establish speed or fidelity. See the [fork engineering backlog](../ROADMAP.md#fork-workflow-follow-up).
