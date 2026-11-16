import base64
import copy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.util.spec_from_file_location('project', ROOT/'scripts/project.py')
p = importlib.util.module_from_spec(loader); loader.loader.exec_module(p)
PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=')


class ProjectTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=os.environ.get('IMG2BLENDER_TEST_TMPDIR')); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.ref = self.root/'reference.png'; self.ref.write_bytes(PNG)
        self.project = self.root/'new project'; p.new_project(self.project, [self.ref])
        self.spec = p.read(self.project/'spec.json')
        self.spec.update(name='Test fixture', use='scene', style='simple', reference_roles={'R1':'test input'},
                         parts=[{'id':'body'}], critical_features=[{'id':'shape','references':['R1'],'target':'test shape'}])
        p.write(self.project/'spec.json', self.spec)

    def fake_run(self, stage='blockout'):
        state = p.read(p.state_path(self.project)); state.update(stage=stage, status='awaiting-review', latest_run=f'runs/0001-{stage}')
        run = self.project/state['latest_run']; run.mkdir(parents=True, exist_ok=True)
        p.write(run/'spec.json', self.spec)
        images = [f'{v["id"]}-{m}.png' for v in self.spec['views'] for m in ['basic','clay']]
        for name in images: (run/name).write_bytes(PNG)
        p.write(run/'audit.json', {'images':images})
        p.write(run/'result.json', {'passed':True,'source_hashes':p.source_hashes(self.project),'geometryFingerprint':'test-only',
                                  'artifacts':{name:p.digest(run/name) for name in images}})
        p.save(self.project,state)
        report = {'decision':'accept','summary':'Synthetic controller-test result; not visual evidence.', 'images':images,
                  'features':[{'id':'shape','status':'pass','notes':'Test fixture only.'}]}
        file = self.root/'review.json'; p.write(file,report)
        return run, file, report

    def test_fresh_refuses_existing_without_changes(self):
        before = p.digest(self.project/'run-inputs.json')
        with self.assertRaises(ValueError): p.new_project(self.project,[self.ref])
        self.assertEqual(before,p.digest(self.project/'run-inputs.json'))

    def test_reject_code_as_reference(self):
        code=self.root/'model.py';code.write_text('pass')
        with self.assertRaises(ValueError):p.new_project(self.root/'bad',[code])
        self.assertFalse((self.root/'bad').exists())

    def test_empty_scaffold_blocked(self):
        with self.assertRaises(ValueError):p.validate_spec(p.read(ROOT/'assets/spec.json'),p.read(self.project/'run-inputs.json'))

    def test_valid_spec_and_cycle_rejection(self):
        p.validate_spec(self.spec,p.read(self.project/'run-inputs.json'))
        self.spec['parts'][0]['parent']='body'
        with self.assertRaises(ValueError):p.validate_spec(self.spec,p.read(self.project/'run-inputs.json'))

    def test_reference_mutation_detected(self):
        (self.project/'references/R1.png').write_bytes(b'changed')
        with self.assertRaises(ValueError):p.source_hashes(self.project)

    def test_asset_change_invalidates_capture(self):
        asset=self.project/'assets/finish.png';asset.write_bytes(PNG)
        run,file,report=self.fake_run();asset.write_bytes(b'changed')
        with self.assertRaises(ValueError):p.review_project(self.project,file)

    def test_stale_source_blocks_accept_but_allows_refine(self):
        run,file,report=self.fake_run();(self.project/'build.py').write_text('# changed')
        with self.assertRaises(ValueError):p.review_project(self.project,file)
        report['decision']='refine';p.write(file,report)
        self.assertEqual(p.review_project(self.project,file)['status'],'editing')

    def test_modified_image_blocks_review(self):
        run,file,report=self.fake_run();(run/report['images'][0]).write_bytes(b'changed')
        with self.assertRaises(ValueError):p.review_project(self.project,file)

    def test_unseen_or_missing_image_not_accepted(self):
        run,file,report=self.fake_run();report['features'][0]['status']='unseen';p.write(file,report)
        with self.assertRaises(ValueError):p.review_project(self.project,file)
        report['features'][0]['status']='pass';report['images'].pop();p.write(file,report)
        with self.assertRaises(ValueError):p.review_project(self.project,file)

    def test_form_checkpoint_and_explicit_appearance_resume(self):
        run,file,report=self.fake_run('form')
        self.assertEqual(p.review_project(self.project,file)['status'],'awaiting-user')
        with self.assertRaises(ValueError):p.run_project(self.project,'unused')
        state=p.transition(self.project,'approve-geometry','User requested finish after reviewing shape.')
        self.assertEqual((state['stage'],state['status']),('appearance','editing'))

    def test_geometry_only_completes_without_appearance(self):
        self.spec['appearance']='geometry-only';p.write(self.project/'spec.json',self.spec)
        run,file,report=self.fake_run('form')
        self.assertEqual(p.review_project(self.project,file)['status'],'complete')
        state=p.transition(self.project,'approve-geometry','User now requests finish on the completed geometry-only asset.')
        self.assertEqual(state['stage'],'appearance');self.assertNotIn('completed_at',state)

    def test_refinement_limit_stops_and_cannot_resume(self):
        run,file,report=self.fake_run();state=p.read(p.state_path(self.project));state['corrections']={'blockout':2};p.save(self.project,state)
        report['decision']='refine';p.write(file,report)
        self.assertEqual(p.review_project(self.project,file)['status'],'stopped')
        with self.assertRaises(ValueError):p.transition(self.project,'resume','Try again')

    def test_appearance_cannot_be_approved_before_form(self):
        with self.assertRaises(ValueError):p.transition(self.project,'approve-geometry','Finish now')

    def test_geometry_correction_retains_history_and_limits(self):
        run,file,report=self.fake_run('form');p.review_project(self.project,file)
        state=p.transition(self.project,'geometry-correction','User asked to adjust cap width.')
        self.assertEqual(state['stage'],'form');self.assertEqual(state['corrections']['form'],1)
        self.assertEqual(len(state['history']),2);self.assertIn('form',state['accepted'])

    def test_review_cannot_be_recorded_twice(self):
        run,file,report=self.fake_run();p.review_project(self.project,file)
        with self.assertRaises(ValueError):p.review_project(self.project,file)

    def test_appearance_geometry_drift_blocks_run(self):
        run,file,report=self.fake_run('form');p.review_project(self.project,file)
        p.transition(self.project,'approve-geometry','User requests appearance.')
        def fake_launch(binary,runtime,mode,run,log,timeout):
            p.write(run/'audit.json',{'passed':True,'geometryFingerprint':'changed','errors':[]})
            return 0
        # No external executable is run; this isolates the controller's drift gate.
        state=p.read(p.state_path(self.project));state['run_count']=1;p.save(self.project,state)
        with patch.object(p,'launch',side_effect=fake_launch):
            with self.assertRaisesRegex(RuntimeError,'changed accepted geometry'):
                p.run_project(self.project,str(self.ref))
        self.assertEqual(p.read(p.state_path(self.project))['status'],'editing')


if __name__=='__main__':unittest.main()
