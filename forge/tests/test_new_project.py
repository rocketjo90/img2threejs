import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("new_project", ROOT / "forge/new_project.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class FreshProjectTests(unittest.TestCase):
    def test_reference_only_start_and_resume_protection(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            ref = base / "reference.png"
            ref.write_bytes(b"reference-fixture")  # This helper records inputs, not image admission.
            (base / "old-model.ts").write_text("must not copy")
            target = base / "new"
            manifest = module.create_project(target, [ref, ref])
            self.assertFalse((target / "old-model.ts").exists())
            self.assertEqual(manifest["priorModelInputs"], [])
            self.assertEqual(len(list((target / "references").iterdir())), 2)
            self.assertEqual(manifest["references"][0]["sha256"], hashlib.sha256(ref.read_bytes()).hexdigest())
            self.assertEqual((target / "viewer/appearance.mjs").read_bytes(), (ROOT / "assets/showcase-viewer/appearance.mjs").read_bytes())
            state_path = target / ".img2threejs/state.json"
            state = state_path.read_bytes()
            self.assertIsInstance(json.loads(state), dict)
            with self.assertRaises(ValueError):
                module.create_project(target, [ref])
            self.assertEqual(state_path.read_bytes(), state)
            second = module.create_project(base / "second", [ref])
            self.assertNotEqual(second["runId"], manifest["runId"])

    def test_invalid_inputs_leave_no_project(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            old = base / "model.ts"
            old.write_text("model")
            for refs in ([], [old], [base / "missing.png"]):
                with self.assertRaises((ValueError, OSError)):
                    module.create_project(base / "new", refs)
                self.assertFalse((base / "new").exists())


if __name__ == "__main__":
    unittest.main()
