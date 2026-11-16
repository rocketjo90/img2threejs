# Reference planning and evidence

Apply this before assessment and reuse it through modeling, review, and delivery. It
complements [image analysis](image_analysis.md) and the existing suitability gates for
photos, screenshots, scanned drawings, sketches, illustrations, diagrams, and other 2D
sources. A reference may depict an imagined or stylized subject; reconstruct its intended
design without silently replacing it with a physically realistic interpretation.

Keep the evidence proportional to the task: use one compact project note for the reference
index, construction map, shape targets, and unresolved features. Reuse component IDs and
existing spec fields; these instructions introduce no schema fields or automated gates.
Apply assembly and fabrication checks only when the requested result needs them.

## Task intake

At the start of a new reconstruction, establish the following before committing to geometry
or a delivery format. Reuse answers already supplied in the request or conversation. Ask
only missing questions, grouped briefly in plain language; allow multiple intended uses.
Inspect references while waiting, but do not silently choose an unanswered intended use.

1. **Use and delivery:** Is this for a game/real-time viewer, a Blender scene, 3D printing,
   or another destination? Is it static, animated, functional, or decorative? What editable
   source or export is needed? Confirm export support before promising a format.
2. **Style:** Should it faithfully preserve rounded forms and visible details, be simplified,
   or be deliberately low-poly/faceted? The reference or an explicit style request can
   already answer this. Destination and style are separate choices: a printed low-poly
   design keeps its intentional facets; a curved object keeps its intended curves.
3. **Relevant constraints:** For a game, ask about target device/engine, viewing distance,
   and any supplied performance budget. For Blender, establish background versus close-up
   use and editing/animation needs. For printing, establish physical size/units, printer or
   process if known, and whether parts must fit, move, or separate. Do not require users
   to invent technical numbers; propose a reasoned budget after these answers. Label
   unknown constraints and identify which final checks depend on resolving them.
4. **Appearance and review:** Offer geometry review with basic appearance and a Clay toggle,
   explicit clay-only output, or a fully finished result. Distinguish plain clay, simple colors/material properties,
   and image/procedural textures. Do not assume every task needs textures or that every
   user wants an approval stop. An explicit finished-output request already authorizes
   appearance work unless the user also requests an intermediate review.

Record the answers compactly in the project notes and use them to define the quality
contract. If the user delegates a choice, state the chosen assumption and proceed. Revisit
only choices affected by a changed destination, scale, or style.

Keep that brief with the model: selected reference variant, use, style, constraints,
appearance stage, requested checkpoint, and accepted revision. A short follow-up such as
"same approach", "adjust this part", or "surface finish now" inherits the established brief.
For a new subject, carry forward explicitly requested workflow choices but reassess its
references, proportions and object-specific constraints. Do not require the user to restate
the skill name or earlier answers. If intended use remains unanswered, ask before geometry.

### Choose refinement for the destination

Set an explicit triangle target in the existing `performanceBudget.targetTriangles` field
for runtime-oriented outputs, based on the agreed use and complexity. It is a tessellation
input, not a guaranteed final count: measure the built geometry, repeated instances, and
draw calls. Spend triangles on silhouette, curvature, and deformation where they matter.
Do not inflate counts to meet an arbitrary minimum or smooth away intentional facets.

For Blender, prioritize the agreed editing needs, hierarchy, scale, and appearance at the
intended camera distance; a densely triangulated export is not automatically an editable
model. Verify the actual exported/imported result in the destination when available.

For printing, select mesh refinement from physical size, curvature fidelity, and the
chosen process's capabilities rather than automatically choosing the largest triangle
count. Inspect exported curves and feature sizes; shading smoothness on screen is not
evidence of a smooth printable mesh. Check units, closed/manifold solids as appropriate,
intersections, wall thickness, and required clearances, then review the slicer result.
Texture or normal-map detail alone does not create printable relief: requested physical
features must be geometry. Printer unknown means printer-specific suitability remains
unverified. See [Autodesk's mesh refinement guidance](https://files.upskill-dev.autodesk.com/public/fusion360-intro-design-manufacturing-associate/210715_SbS_L1-07_Export-an-STL-file.pdf)
and [Blender's print inspection tools](https://extensions.blender.org/add-ons/print3d-toolbox/).

For multiple uses, keep a shared procedural source and derive destination-specific variants
with separate checks. A browser preview supports inspection; it does not replace the
requested game asset, Blender deliverable, or printable file. Existing export/profile
contracts still govern supported conversions; these intake instructions add no exporters.

### When geometry-first review is selected

Provide basic reference colors/scalar materials and a Clay toggle with proportions, shape
details, and multiple views before costly surface work; honor an explicit clay-only request.
Use the same geometry in both modes. Preserve source, spec, cameras, assumptions and pending tasks.
If the user requested approval at this point, wait for their shape feedback before textures;
do not treat elapsed time as approval. Resume the saved model rather than rebuilding it.

An explicit request to continue with appearance authorizes that stage for the current
revision. Preserve the geometry checkpoint and its outstanding uncertainties; permission
to texture does not prove dimensional accuracy or close unrelated defects. Apply appearance
to the same source and hierarchy, with a plain-material comparison still available.

Plan later surface requirements without generating textures prematurely. A shape preview
is an intermediate result, not full material fidelity or completed pipeline evidence. Keep
deferred work pending; never mark a required appearance gate passed or globally inapplicable
just to reach the checkpoint. Use pass-scoped strict validation for the three geometry
passes; the generic state checklist leaves extraction/wiring/baking pending until appearance.
Any other hard stop still applies. Geometry-only delivery must be scoped
and labeled honestly. No texture is needed merely to finish an otherwise accepted print mesh.

## 1. Organize the supplied evidence

Inspect the available sources and make a compact index in the project's analysis notes.
For each useful source, record an ID, source location, depicted subject or variant, view,
and what it establishes. Preserve originals and identify derived crops by their parent
source. Distinguish alternate designs, poses, finishes, and revisions before combining
views; do not assume every supplied image depicts the same version.

Record the depicted state where relevant: assembled, disassembled, exploded, cutaway,
damaged, partially covered, or posed differently. Note which components cover others and
which surfaces a cutaway exposes artificially. An opening visible beneath a removed cover
need not be visible in the assembled result. Preserve intentional damage when requested;
do not combine intact and damaged references into an undocumented hybrid.

Choose a small working set covering the silhouette, proportions, depth cues, and important
details. For large sets, use a contact sheet or thumbnails to select candidates, then
inspect originals for measurements and fine features. Reopen other sources when a specific
uncertainty needs them, rather than repeatedly reviewing the entire set. One source is a
valid working set; never invent missing views or count duplicate crops as independent evidence.

### Feature-specific reference authority

Keep a compact table in project notes: feature/component ID, authoritative source and crop,
variant/assembly state, decision, uncertainty, and affected review views. One image need not
govern every feature. For example, a drawing may control proportions, a photo the finish,
another view an attachment, and an explicit user request an invented interior. Never blend
different variants merely because all images were attached together.

When the user changes the target, revise the affected comparison contract and preserve the
old one as superseded. Refresh affected geometry/cameras/masks and review evidence; do not
keep judging against an obsolete target and accumulating waivers. This does not authorize
deleting a failure, changing a recorded score or bypassing a hard stop. Required tool fields
must match the active target; keep unsupported per-feature metadata in a versioned sidecar.
If a tool only supports one global reference, use it for that stated diagnostic scope and
perform the remaining feature comparisons separately, reporting the limitation.

For line art, separate outlines, dimension marks, construction lines, shading, and decorative
strokes. A dark line is not automatically a groove; a shaded region is not automatically a
surface color. Preserve stated scale and units in technical drawings. Distorted, incomplete,
or contradictory sources may support only a conditional or stylized reconstruction.

## 2. Check cameras and proportions before fine detail

Choose the intended orientation and record major dimension ratios and a few recognizable
landmarks. Use absolute dimensions only when supported by dimensions or a reliable scale
reference; otherwise use normalized proportions and label the scale as estimated.

Before choosing detailed geometry, set measurable targets for identity-defining shapes:
dimension ratios, landmark offsets, inclinations, thicknesses where supported, and curve
profiles. Associate each target with evidence and an appropriate uncertainty or acceptance
range; do not invent precision from blurry or perspective-distorted sources. Drive related
features from shared parameters rather than independently estimated coordinates.

Choose geometry that can express those profiles, rather than accepting the nearest
primitive's shape. Set curvature refinement by visible contour error at the intended view
or physical deviation at print scale, alongside any runtime triangle budget. Inspect the
actual polygon outline: smooth normals and textures cannot repair an incorrect contour.
Keep deliberate facets when they are part of the requested style.

Identify whether each view is perspective, orthographic, diagrammatic, or uncertain. Match
the preview camera to the reference before judging shape. Do not distort geometry to
compensate for the wrong camera, crop, or pose. Fix camera framing first, then compare the
silhouette, landmark placement, major thicknesses, negative spaces, and part relationships.

During blockout, compare the simple volume against the selected views; resolve major errors
before spending effort on bevels, lettering, repetition, or other fine detail. Save the
camera settings and repeatable comparison captures for later passes. Existing multi-angle
checks still apply: with only one reference, additional rendered views test plausibility
and continuity, not measured accuracy of unseen sides.

### Repeatable measurement and comparison record

For shapes that benefit from fitting, retain raw image samples/landmarks (source hash,
crop/resize transform, pixel coordinate origin, image dimensions) separately from normalized
coordinates and the fitted curve. Record axis direction, station positions, radii/widths,
fit method and residuals in pixels or normalized units. Use the simplest curve that preserves
identity-defining contour changes; do not fit noise or smooth intentional facets. A tiny
2D fitting residual is not proof of exact 3D reconstruction.

Save the comparison camera projection, pose, target, FOV or orthographic scale, render size,
object transform and assembly state. Identify inferred camera/depth parameters separately
from observed 2D samples and dimensioned measurements. Match framing before changing shape.

Record how silhouette masks were obtained, exclusions (background, ground shadow, props,
occluders), transparency treatment and alignment. Keep masks alongside comparison captures.
Use the same policy for revisions being scored against the same target; when it changes,
rerun the baseline or label scores incomparable. Never describe silhouette overlap as a
percentage of total model accuracy. Include context views for attachments and neighboring
parts, not only cropped close-ups of the corrected component.

If a stylized drawing uses incompatible perspectives, name the conflict and choose a
documented interpretation. Ask for clarification when that choice materially changes the
design; do not imply a unique recoverable 3D form. Early comparisons supplement the existing
pass gates and do not replace them or authorize skipping a required pass.

## 3. Separate observations, inferences, and unknowns

Keep a short evidence ledger alongside the reference index. For each important feature or
dimension, record its component/spec ID, source ID and region, interpretation, and status:

- **Observed:** directly depicted or explicitly dimensioned. Note blur, occlusion, or other
  limits; a visible outline does not by itself establish depth or physical size.
- **Inferred:** a modeling choice derived from symmetry, adjacent views, convention, or
  plausible construction. State the basis and any alternative that materially affects shape.
- **Unknown:** not established by the supplied evidence, such as an unseen rear surface,
  interior, thickness, material, or mechanism.

These labels describe certainty; they do not instruct the renderer to hide geometry.
Use a simple, explicit approximation for unknown regions when necessary to complete the
form. Do not invent detailed mechanisms or claim measured fidelity there. Request another
view or a design decision only when the ambiguity prevents a useful result.

Update affected entries when new evidence or user corrections arrive. Carry their source
references into supported spec evidence fields; keep additional notes beside the spec
rather than inventing schema fields. Reviews and delivery should distinguish verified
visible features from inferred completion. A passed software or visual gate does not turn
an inference into an observation.

For each important hole, seam, recess, or protrusion, record the supporting source region
or explicit design requirement; otherwise label the interpretation as inferred or unknown.
Distinguish through-openings, shallow relief, shadows, painted marks, and gaps between
overlapping parts. Resolve conflicting interpretations before building dependent details,
or document the chosen approximation and its consequences. When a review flags an error,
reopen the relevant original source and check its depicted state before changing geometry;
an earlier model or critique is not independent evidence. Explicit user design changes
still govern the intended result.

## 4. Map construction before detailed modeling

Create a compact construction map of the major components or continuous regions. Record
their boundaries, shape/profile, depth or thickness where relevant, openings, and how they
join, overlap, contain, or conceal one another. Distinguish physical parts from decorative
surface regions and modeling subdivisions; a material boundary need not be a physical seam.
For continuous or organic subjects, describe connected volumes and layers without inventing
mechanical joints. A single-piece subject may need only one entry.

Use this map to choose the component hierarchy and geometry strategy before fine detail.
Keep a cover, the structure behind it, and openings in each distinct when they affect the
requested result. Do not replace layered construction with one silhouette-sized opening.
Mark components as included, simplified, omitted by scope, or unresolved so missing parts
cannot silently become a finished assembly. Hidden internals are not required for every
visual asset; use simple documented completion unless evidence or intended use requires more.

For each identity-defining part, review its own contour, its relationship to neighbours,
and its effect on the assembled silhouette against the applicable references. Record only
the decisive relationships: alignment, relative height/width, seam position, containment,
overlap, repetition, or intended profile continuity. Use shared profiles where the reference
supports continuity while retaining separate physical parts. Preserve deliberate steps and
gaps. Group-origin proximity alone does not establish correct placement of child geometry.

## 5. Validate interfaces when parts must fit or move

For a physical assembly or functional mechanism, record each required mating pair, its
shared alignment references, contacting surfaces, clearance, retention method, and assembly
direction. Distinguish observed original construction from adaptations made for the new
use or manufacturing process. Choose tolerances for the intended scale/process; do not
reuse one universal clearance across unrelated parts.

Check matching holes/posts, seats, fastening access, insertion paths, and required motion
before decorating them. A plausible-looking mount is not a verified fastening system;
absence of overlap alone does not prove retention or that a part can be inserted. Leave
unverified interfaces provisional. Do not invent hardware or functional mechanisms for a
visual-only reconstruction. Digital checks and nominal thicknesses do not establish
physical fit, minimum thickness everywhere, or successful fabrication.

## 6. Review structure and the delivered artifact

At the appropriate geometry pass, inspect plain-material views of the complete subject
and relevant exposed components or layers. Compare references and renders in matching
assembly states, poses, and cameras. Use exposed views to check construction and the complete
view to check occlusion, silhouette, and attachment; one does not substitute for the other.
Review only the hidden structure required by scope. Record unresolved critical features
in the existing pass review rather than letting a polished material conceal them.

Keep reference-derived expectations separate from the runtime inventory. Compare the built
parts to those expectations; do not rewrite required features to match what happened to be
built. Change the expected design only with new evidence or a documented scope decision.
A good global silhouette score cannot overrule an incorrect identity-defining relationship.
After a correction, recheck the affected part in isolation and in its assembled context.

For requested exports, inspect the actual files in a compatible destination when available.
Reimport and check scale, orientation, part coverage, curves, and destination-specific
geometry requirements. For multipart delivery, reconstruct the assembled placement from
saved transforms and render the exported parts together as well as separately. Printing
orientations must not replace the recorded assembly transforms. Use a part manifest to
distinguish required pieces, quantities, alternatives, and nonprinting reference objects.

Keep one authoritative procedural design with reproducible destination-specific changes.
Record export adaptations in the source/spec or a versioned transformation recipe tied to
that source; do not leave fit corrections only in an edited output file. Regenerate affected
previews after adaptations, or label earlier previews explicitly. Tie review evidence to
the delivered revision using filenames and hashes or equivalent version identifiers.

These are inspection requirements, not new exporter capabilities or replacements for
existing target contracts. If destination inspection is unavailable, state which checks
were actually performed and leave fidelity there unverified. Distinguish visual accuracy,
mesh integrity, digital assembly fit, slicer review, and physical testing in delivery claims.
