# img2blender 0.2.0

A standalone Blender-native adaptation of this fork's image reconstruction workflow.
The host AI interprets supplied references and writes Blender Python. Blender runs headless
to produce editable `.blend` files and paired Basic/Clay PNGs, without a web viewer.
It does not require img2threejs to be installed or use a dedicated image-to-mesh AI model.

## Install

Copy this entire `skills/img2blender` directory into your assistant's skills directory
under the name `img2blender`. Keep `SKILL.md`, `scripts`, `assets`, `references`, and the
other supporting files together. For an assistant that imports skill ZIPs, zip this
directory with `img2blender/SKILL.md` at the top-level folder, then import that ZIP.

Install Blender separately. Run the workflow with a Python 3.10+ interpreter; provide
the Blender executable through `--blender`, `BLENDER_BIN`, or PATH. Native validation
has been performed with Blender 5.2.1 LTS on Windows; other Blender versions are unverified.
No API key is required by these scripts.

Start with [SKILL.md](SKILL.md). For example, from this directory:

```powershell
python scripts/project.py new --out <new-project-folder> --reference <primary-image> --reference <secondary-image>
```

The initializer copies references and generic scaffolds. The host AI must inspect the
images, complete the brief/specification, and author the builder before running Blender.
Never use a previous object's geometry as the template for a fresh reconstruction.
Corrections resume the existing project and preserve its review history.

## Review contract

- Reference authority and observed/inferred/unknown status are recorded per feature.
- Openings and recesses need geometric evidence in opaque Clay.
- Important interfaces can declare sampled evaluated-surface checks with expected coverage.
- Assembly origins and axes should support editing; recenter without moving world geometry.
- Basic, Clay, and restored-material audits must pass; native save/reopen checks preserve evidence.
- Geometry-first projects wait for user feedback before detailed finish.

Sampled proximity does not certify penetration, motion clearance or manufacturing fit.
See [feature evidence](references/feature-evidence.md) and
[project contract](references/project-contract.md) for the precise scope and limits.

## Validation

```powershell
python -m unittest discover -s tests -p test_project.py
```

The controller has 16 unit tests. Native Blender contract tests additionally cover mesh,
material, interface coverage, gap detection and Clay validation. See
`tests/blender_contracts.py` and `tests/smoke_blender.py` for their command-line interfaces.
The 0.2.0 update passed 17 native contract checks on Blender 5.2.1 LTS.

This is a fork addition, not an upstream img2threejs release. Apache-2.0 licensing and
source attribution are retained in `LICENSE`, `NOTICE` and `references/provenance.json`.
