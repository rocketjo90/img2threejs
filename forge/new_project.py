#!/usr/bin/env python3
"""Start a reference-only reconstruction; never import an earlier object's code."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import uuid

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "forge" / "_shared"))
from workflow_state import new_state, save_state, WorkflowStateError


def create_project(destination: Path, references: list[Path], profile: str = "generic") -> dict:
    destination = destination.expanduser().resolve()
    if destination.exists():
        raise ValueError("Fresh generation requires a new, nonexistent directory; resume existing work with forge/next.py.")
    if not references:
        raise ValueError("At least one reference image is required.")
    sources = [p.expanduser().resolve(strict=True) for p in references]
    supported = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}
    for source in sources:
        if not source.is_file() or source.suffix.lower() not in supported:
            raise ValueError(f"Expected a reference image, not model/code: {source.name}")
    entries = []
    for i, source in enumerate(sources, 1):
        entries.append({"id": f"R{i}", "path": f"references/R{i}{source.suffix.lower()}",
                        "sha256": hashlib.sha256(source.read_bytes()).hexdigest()})
    # Validate the profile and prepare state before creating anything on disk.
    state = new_state(str(destination / entries[0]["path"]), profile=profile,
                      spec=str(destination / "object-sculpt-spec.json"))
    manifest = {"schemaVersion": 1, "runId": str(uuid.uuid4()), "mode": "fresh",
                "references": entries, "referenceAuthority": "Assign per feature in the new brief; ordering alone is not authority.",
                "priorModelInputs": [], "isolation": "workspace-only; host context/filesystem isolation is not enforced",
                "viewerTemplate": {}}
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "references").mkdir()
    for source, entry in zip(sources, entries):
        shutil.copyfile(source, destination / entry["path"])
    template = ROOT / "assets" / "showcase-viewer"
    (destination / "viewer").mkdir()
    for name in ("index.html", "viewer.css", "appearance.mjs"):
        source = template / name
        shutil.copyfile(source, destination / "viewer" / name)
        manifest["viewerTemplate"][name] = hashlib.sha256(source.read_bytes()).hexdigest()
    (destination / "run-inputs.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    save_state(destination / ".img2threejs" / "state.json", state)
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--reference", type=Path, action="append", required=True)
    parser.add_argument("--profile", default="generic")
    args = parser.parse_args(argv)
    try:
        manifest = create_project(args.out, args.reference, args.profile)
    except (OSError, ValueError, WorkflowStateError) as error:
        print(f"new project error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
