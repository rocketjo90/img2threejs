"""Regression checks for geometry-first checkpoints and honest delivery/status evidence."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for folder in ("_shared", "stage2_spec", "stage3_build", "stage4_review", "tests"):
    sys.path.insert(0, str(ROOT / "forge" / folder))

from test_textureless_material import DECLARED, _minimal_spec, base_material, quality_first_spec
from test_pipeline import write_png
from validate_sculpt_spec import GEOMETRY_PASSES, validate_spec, validate_look_dev_targets
from generate_threejs_factory import strict_quality_failures, generate, assert_pass_unlocked
from orchestrate_passes import material_pass_gaps, surface_pass_gaps
from workflow_state import new_state, recompute, set_current_pass, status_payload
from project_status import write_project_status


class TexturelessGates(unittest.TestCase):
    def test_valid_flat_material_passes_without_invented_maps_or_wear(self):
        spec = quality_first_spec([base_material(textureless=copy.deepcopy(DECLARED))])
        self.assertEqual(material_pass_gaps(spec), [])
        errors, warnings = [], []
        validate_look_dev_targets(spec, errors, warnings)
        self.assertFalse(any("material-pass" in w or "material '" in w for w in warnings), warnings)

    def test_missing_evidence_cannot_exempt_a_material(self):
        spec = quality_first_spec([base_material(textureless={"declared": True})])
        self.assertTrue(any("textureless.evidence" in gap for gap in material_pass_gaps(spec)))

    def test_conflicting_texture_declaration_still_blocks(self):
        spec = quality_first_spec([base_material(textureless=DECLARED, normal={"strength": 1})])
        self.assertTrue(any("cannot both" in gap for gap in material_pass_gaps(spec)))

    def test_mixed_materials_keep_textured_requirements(self):
        spec = quality_first_spec([base_material(textureless=DECLARED), base_material(id="patterned")])
        gaps = material_pass_gaps(spec)
        self.assertTrue(any("patterned" in gap and "textureResolution" in gap for gap in gaps), gaps)
        self.assertFalse(any("vinyl-fur" in gap for gap in gaps), gaps)

    def test_textureless_does_not_override_failed_material_pipeline(self):
        spec = quality_first_spec([base_material(textureless=DECLARED)])
        spec["materialPipeline"] = {"status": "probe"}
        self.assertTrue(any("materialPipeline" in gap for gap in material_pass_gaps(spec)))

    def test_surface_detail_not_invented_for_textureless_parts(self):
        spec = _minimal_spec()
        self.assertEqual(surface_pass_gaps(spec), [])
        del spec["materials"][0]["textureless"]
        self.assertTrue(surface_pass_gaps(spec))


class GeometryFirst(unittest.TestCase):
    def spec(self):
        spec = _minimal_spec()
        spec.update(quality_first_spec([base_material()]))
        return spec

    def test_appearance_warning_is_deferred_only_in_geometry_passes(self):
        spec = self.spec()
        for pass_id in GEOMETRY_PASSES:
            with self.subTest(pass_id=pass_id):
                _, warnings, failures = strict_quality_failures(spec, pass_id)
                self.assertTrue(any(w.startswith("deferred-appearance:") and "textureResolution" in w for w in warnings))
                self.assertFalse(any("textureResolution" in failure for failure in failures))
        for pass_id in (None, "material-pass", "optimization-pass", "typo"):
            _, _, failures = strict_quality_failures(spec, pass_id)
            self.assertTrue(any("textureResolution" in failure for failure in failures), failures)

    def test_schema_errors_and_geometry_quality_still_block(self):
        spec = self.spec()
        spec["materials"][0]["roughness"] = "invalid"
        spec["componentTree"][0]["material"] = "missing-material"
        errors, _, failures = strict_quality_failures(spec, "blockout")
        self.assertTrue(any("roughness" in error for error in errors), errors)
        self.assertTrue(any("missing-material" in error for error in errors), errors)
        self.assertTrue(any("qualityContract" in failure for failure in failures), failures)

    def test_codegen_geometry_does_not_load_or_synthesise_textures(self):
        for pass_id in GEOMETRY_PASSES:
            source = generate(self.spec(), pass_id)
            self.assertIn("const geometryReview = true;", source)
            self.assertIn("const textures = textureless || geometryReview\n    ? null", source)
        self.assertIn("const geometryReview = false;", generate(self.spec(), "material-pass"))

    def test_future_pass_lock_is_not_relaxed(self):
        with self.assertRaises(ValueError):
            assert_pass_unlocked(self.spec(), "material-pass")

    def test_state_defers_without_claiming_completion_then_requires_appearance(self):
        state = new_state("reference.png", spec="spec.json")
        for entry in state["checklist"]:
            if entry["scope"] == "setup" and entry["id"] not in {"material-evidence", "material-spec-wiring", "projection-appearance", "strict-validation"}:
                entry["status"] = "done"
        set_current_pass(state, "blockout")
        payload = status_payload(state)
        self.assertEqual(payload["currentStep"], "strict-validation")
        self.assertIn("--pass-id blockout", payload["nextCommand"])
        self.assertIn("material-evidence", payload["pending"])
        self.assertIn("material-evidence", payload["deferred"])
        set_current_pass(state, "material-pass")
        payload = status_payload(state)
        self.assertEqual(payload["currentStep"], "material-evidence")
        self.assertEqual(payload["deferred"], [])

    def test_projection_route_plans_without_premature_baking(self):
        state = new_state("reference.png")
        for entry in state["checklist"]:
            if entry["id"] == "projection-route":
                break
            entry["status"] = "done"
        recompute(state)
        self.assertIn("defer texture", status_payload(state)["nextCommand"])


class EvidenceOutputs(unittest.TestCase):
    def test_diagnostic_stdout_is_json_with_or_without_json_flag(self):
        with tempfile.TemporaryDirectory() as directory:
            ref = Path(directory) / "ref.png"
            write_png(ref)
            for flags in ([], ["--json"]):
                result = subprocess.run([sys.executable, str(ROOT / "forge/stage4_review/diagnose_render.py"),
                                         "--reference", str(ref), "--render", str(ref), *flags],
                                        capture_output=True, text=True)
                parsed = json.loads(result.stdout)
                self.assertIn("passed", parsed)
                self.assertIn("STATUS", result.stderr)

    def test_current_snapshot_updates_and_preserves_history(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            spec_path = root / "spec.json"
            spec = {"targetName": "Test", "reviewHistory": [{"passId": "blockout", "action": "continue"}]}
            spec_path.write_text(json.dumps(spec), encoding="utf-8")
            original = copy.deepcopy(spec)
            state = new_state("reference.png")
            write_project_status(root, status_payload(state), spec=spec, spec_path=spec_path)
            spec["reviewHistory"].append({"passId": "blockout", "action": "refine-code"})
            spec_path.write_text(json.dumps(spec), encoding="utf-8")
            payload = write_project_status(root, status_payload(state), spec=spec, spec_path=spec_path)
            self.assertEqual(payload["latestRecordedReviews"]["blockout"]["action"], "refine-code")
            self.assertEqual(spec["reviewHistory"][0], original["reviewHistory"][0])
            self.assertEqual(len(payload["specSha256"]), 64)
            self.assertEqual(json.loads((root / "current-status.json").read_text(encoding="utf-8")), payload)
            self.assertIn("deferred until appearance", (root / "CURRENT_STATUS.md").read_text(encoding="utf-8"))

    def test_next_cli_generates_pre_spec_summary_without_changing_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            state_path.write_text(json.dumps(new_state("reference.png")), encoding="utf-8")
            result = subprocess.run([sys.executable, str(ROOT / "forge/next.py"), "--state", str(state_path)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads((state_path.parent / "current-status.json").read_text(encoding="utf-8"))
            self.assertEqual(report["workflow"]["currentStep"], "image-analysis")
            self.assertIsNone(report["specSha256"])


if __name__ == "__main__":
    unittest.main()
