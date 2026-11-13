# Reference planning and evidence

Apply this before assessment and reuse it through blockout and form refinement. It
complements [image analysis](image_analysis.md) and the existing suitability gates for
photos, screenshots, scanned drawings, sketches, illustrations, diagrams, and other 2D
sources. A reference may depict an imagined or stylized subject; reconstruct its intended
design without silently replacing it with a physically realistic interpretation.

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
4. **Appearance and review:** Offer geometry-only, geometry review before appearance, or
   a fully finished result. Distinguish plain clay, simple colors/material properties,
   and image/procedural textures. Do not assume every task needs textures or that every
   user wants an approval stop. An explicit finished-output request already authorizes
   appearance work unless the user also requests an intermediate review.

Record the answers compactly in the project notes and use them to define the quality
contract. If the user delegates a choice, state the chosen assumption and proceed. Revisit
only choices affected by a changed destination, scale, or style.

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

Provide a plain-material preview with proportions, shape details, and multiple views before
costly surface work. Preserve the source, spec, cameras, assumptions, and pending tasks.
If the user requested approval at this point, wait for their shape feedback before textures;
do not treat elapsed time as approval. Resume the saved model rather than rebuilding it.

Plan later surface requirements without generating textures prematurely. A shape preview
is an intermediate result, not full material fidelity or completed pipeline evidence. Keep
deferred work pending; never mark a required appearance gate passed or globally inapplicable
just to reach the checkpoint. If the current tooling cannot advance without that work,
retain its blocked status and explain the limitation. Geometry-only delivery must be scoped
and labeled honestly. No texture is needed merely to finish an otherwise accepted print mesh.

## 1. Organize the supplied evidence

Inspect the available sources and make a compact index in the project's analysis notes.
For each useful source, record an ID, source location, depicted subject or variant, view,
and what it establishes. Preserve originals and identify derived crops by their parent
source. Distinguish alternate designs, poses, finishes, and revisions before combining
views; do not assume every supplied image depicts the same version.

Choose a small working set covering the silhouette, proportions, depth cues, and important
details. For large sets, use a contact sheet or thumbnails to select candidates, then
inspect originals for measurements and fine features. Reopen other sources when a specific
uncertainty needs them, rather than repeatedly reviewing the entire set. One source is a
valid working set; never invent missing views or count duplicate crops as independent evidence.

For line art, separate outlines, dimension marks, construction lines, shading, and decorative
strokes. A dark line is not automatically a groove; a shaded region is not automatically a
surface color. Preserve stated scale and units in technical drawings. Distorted, incomplete,
or contradictory sources may support only a conditional or stylized reconstruction.

## 2. Check cameras and proportions before fine detail

Choose the intended orientation and record major dimension ratios and a few recognizable
landmarks. Use absolute dimensions only when supported by dimensions or a reliable scale
reference; otherwise use normalized proportions and label the scale as estimated.

Identify whether each view is perspective, orthographic, diagrammatic, or uncertain. Match
the preview camera to the reference before judging shape. Do not distort geometry to
compensate for the wrong camera, crop, or pose. Fix camera framing first, then compare the
silhouette, landmark placement, major thicknesses, negative spaces, and part relationships.

During blockout, compare the simple volume against the selected views; resolve major errors
before spending effort on bevels, lettering, repetition, or other fine detail. Save the
camera settings and repeatable comparison captures for later passes. Existing multi-angle
checks still apply: with only one reference, additional rendered views test plausibility
and continuity, not measured accuracy of unseen sides.

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
