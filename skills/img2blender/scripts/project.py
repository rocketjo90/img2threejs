"""Fresh projects, ordered review state and headless Blender execution (Python 3.10+)."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
STAGES = ['blockout', 'structure', 'form', 'appearance']
INPUTS = ['build.py', 'parameters.json', 'spec.json', 'BRIEF.md']
SAFE = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}$')


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    temporary.replace(path)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_hashes(project):
    result = {name: digest(project / name) for name in INPUTS}
    asset_root = project / 'assets'
    if asset_root.exists():
        for asset in sorted(asset_root.rglob('*')):
            if not asset.is_file(): continue
            if not asset.resolve().is_relative_to(asset_root.resolve()):
                raise ValueError('Asset links may not escape the project assets directory.')
            result[asset.relative_to(project).as_posix()] = digest(asset)
    for entry in read(project / 'run-inputs.json')['references']:
        actual = digest(project / entry['path'])
        if actual != entry['sha256']:
            raise ValueError(f"Reference changed: {entry['id']}; preserve originals and revise the evidence explicitly.")
        result[entry['path']] = actual
    return result


def state_path(project):
    return project / '.img2blender/state.json'


def save(project, state):
    write(state_path(project), state)
    timing = read(project / 'timing.json')
    timing['blenderSeconds'] = round(state['blender_seconds'], 3)
    end = state.get('completed_at') or now()
    timing['elapsedWallSeconds'] = int((datetime.fromisoformat(end) - datetime.fromisoformat(timing['startedAt'])).total_seconds())
    timing['geometryReviewReadyAt'] = state.get('geometry_ready_at')
    timing['geometryApprovedAt'] = state.get('geometry_approved_at')
    timing['completedAt'] = state.get('completed_at')
    write(project / 'timing.json', timing)
    accepted = state.get('accepted', {})
    status = [f"# {state['name']} — current status", '', f"Stage: {state['stage']}",
              f"Status: {state['status']}", f"Latest attempt: {state.get('latest_run') or 'none'}",
              f"Latest accepted run: {next(reversed(accepted.values()), 'none')}",
              f"Corrections: {sum(state['corrections'].values())}/6 total; {state['corrections'].get(state['stage'], 0)}/3 this stage",
              f"Blender execution: {timing['blenderSeconds']} seconds; elapsed wall time: {timing['elapsedWallSeconds']} seconds",
              '', state.get('reason', ''), '',
              ('Selected scope complete.' if state['status'] == 'complete' else
               'Appearance remains pending until the selected scope authorizes it.'),
              'Mesh checks are not fidelity or printing certification.']
    (project / 'CURRENT_STATUS.md').write_text('\n'.join(status) + '\n', encoding='utf-8')


def new_project(destination, references):
    destination = Path(destination).expanduser().resolve()
    if destination.exists():
        raise ValueError('Fresh generation requires a nonexistent destination. Resume existing work instead.')
    if not references:
        raise ValueError('At least one supplied image is required.')
    refs = [Path(p).expanduser().resolve(strict=True) for p in references]
    extensions = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tif', '.tiff', '.gif'}
    for ref in refs:
        if not ref.is_file() or ref.suffix.lower() not in extensions or ref.stat().st_size == 0:
            raise ValueError(f'Expected a nonempty reference image, not model/code: {ref}')
    started = now()
    manifest = {'schemaVersion': 1, 'runId': str(uuid.uuid4()), 'mode': 'fresh', 'startedAt': started,
                'tool': read(ROOT / 'references/provenance.json'), 'priorModelInputs': [],
                'isolation': 'fresh directory only; host context and file access are not isolated', 'references': [],
                'toolFiles': {str(p.relative_to(ROOT)).replace('\\', '/'): digest(p) for p in
                              [ROOT/'SKILL.md', ROOT/'scripts/project.py', ROOT/'scripts/blender_runtime.py',
                               ROOT/'assets/spec.json', ROOT/'assets/build.py']}}
    destination.mkdir(parents=True, exist_ok=False)
    (destination / 'references').mkdir()
    (destination / 'assets').mkdir()
    for i, ref in enumerate(refs, 1):
        relative = f'references/R{i}{ref.suffix.lower()}'
        shutil.copyfile(ref, destination / relative)
        manifest['references'].append({'id': f'R{i}', 'path': relative, 'source': str(ref), 'sha256': digest(ref)})
    for name in ['build.py', 'spec.json']:
        shutil.copyfile(ROOT / 'assets' / name, destination / name)
    write(destination / 'parameters.json', {})
    write(destination / 'run-inputs.json', manifest)
    (destination / 'BRIEF.md').write_text('# Reconstruction brief\n\nRecord the intended use, reference authority, measurements, uncertainty and review checkpoint after inspecting the supplied images.\n', encoding='utf-8')
    write(destination / 'timing.json', {'startedAt': started, 'scope': 'Elapsed wall time includes reference analysis, authoring, review and user waiting. Blender process time is recorded separately.'})
    state = {'schemaVersion': 1, 'name': destination.name, 'stage': 'blockout', 'status': 'editing',
             'run_count': 0, 'corrections': {}, 'technical_failures': 0, 'blender_seconds': 0,
             'history': [], 'accepted': {}, 'reason': 'Inspect references and author the brief/spec/build source.'}
    save(destination, state)
    return manifest


def validate_spec(spec, manifest):
    for key in ['name', 'use', 'style']:
        if not isinstance(spec.get(key), str) or not spec[key].strip():
            raise ValueError(f'Fill spec.{key} from the user brief.')
    if spec.get('appearance') not in ('geometry-first', 'geometry-only', 'finished'):
        raise ValueError('appearance must be geometry-first, geometry-only or finished')
    refs = {r['id'] for r in manifest['references']}
    roles = spec.get('reference_roles', {})
    if not roles or not set(roles) <= refs or not all(isinstance(v, str) and v.strip() for v in roles.values()):
        raise ValueError('Assign reference_roles to supplied reference IDs.')
    parts = spec.get('parts', [])
    ids = [p.get('id', '') for p in parts]
    if not ids or len(set(ids)) != len(ids) or not all(SAFE.fullmatch(i) for i in ids):
        raise ValueError('Declare unique filename-safe part IDs.')
    parents = {p['id']: p.get('parent') for p in parts}
    for part in ids:
        visited = set()
        while part is not None:
            if part in visited or part not in parents:
                raise ValueError('Invalid or cyclic part parent relationship.')
            visited.add(part)
            part = parents[part]
    features = spec.get('critical_features', [])
    if not features or len({f.get('id') for f in features}) != len(features):
        raise ValueError('Declare unique critical_features before construction.')
    for f in features:
        if not SAFE.fullmatch(f.get('id', '')) or not f.get('target') or not f.get('references') or not set(f['references']) <= refs:
            raise ValueError('Each critical feature needs an ID, target and supplied reference IDs.')
    views = spec.get('views', [])
    if len(views) < 2 or len({v.get('id') for v in views}) != len(views):
        raise ValueError('At least two distinct review views are required.')
    if sum(not v.get('hide_parts') for v in views) < 2:
        raise ValueError('At least two assembled review views are required.')
    for view in views:
        if not SAFE.fullmatch(view.get('id', '')) or not set(view.get('hide_parts', [])) <= set(ids):
            raise ValueError('Invalid view ID or hide_parts.')
        keys = ['direction'] if 'direction' in view else ['position', 'target']
        for key in keys:
            values = view.get(key)
            if not isinstance(values, list) or len(values) != 3 or not all(isinstance(n, (int, float)) and math.isfinite(n) for n in values):
                raise ValueError('Each view needs a finite direction or position and target.')
        delta = view.get('direction') or [a-b for a,b in zip(view['position'], view['target'])]
        if sum(v*v for v in delta) < 1e-12:
            raise ValueError('Camera direction cannot be zero.')
        for key in ('lens', 'orthographic_scale'):
            if key in view and (not isinstance(view[key], (float, int)) or not math.isfinite(view[key]) or view[key] <= 0):
                raise ValueError(f'Invalid camera {key}')
    render = spec.get('render', {})
    if render.get('engine') not in ('CYCLES', 'BLENDER_EEVEE'):
        raise ValueError('Choose CYCLES or BLENDER_EEVEE explicitly.')
    for key, lower, upper in [('samples', 1, 4096), ('resolution', 64, 4096)]:
        if not isinstance(render.get(key), int) or not lower <= render[key] <= upper:
            raise ValueError(f'Invalid render {key}.')
    units = spec.get('units', {})
    if units.get('system') not in ('NONE', 'METRIC', 'IMPERIAL') or not isinstance(units.get('scale_length'), (int, float)) or not 0 < units['scale_length'] < 1e9:
        raise ValueError('Set valid scene units and positive scale_length.')
    if not isinstance(spec.get('triangle_target'), int) or spec['triangle_target'] <= 0:
        raise ValueError('Set a positive soft triangle_target.')


def find_blender(argument):
    candidate = argument or os.environ.get('BLENDER_BIN') or shutil.which('blender')
    if not candidate:
        raise ValueError('Blender not found. Supply --blender <executable> or BLENDER_BIN.')
    candidate = Path(candidate).expanduser().resolve(strict=True)
    if not candidate.is_file():
        raise ValueError('Blender executable must be a file.')
    return candidate


def launch(binary, runtime, mode, run, log, timeout):
    command = [str(binary), '--background', '--factory-startup', '--disable-autoexec',
               '--python-exit-code', '1', '--python', str(runtime), '--', mode, str(run)]
    started = time.monotonic()
    flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0) if os.name == 'nt' else 0
    with log.open('w', encoding='utf-8') as handle:
        result = subprocess.run(command, stdout=handle, stderr=subprocess.STDOUT, timeout=timeout,
                                creationflags=flags, cwd=run, shell=False)
    elapsed = time.monotonic() - started
    if result.returncode:
        raise RuntimeError(f'Blender exited {result.returncode}; read {log}')
    return elapsed


def run_project(project, binary, timeout=600):
    state = read(state_path(project))
    if state['status'] != 'editing':
        raise ValueError(f"Cannot build while {state['status']}; inspect CURRENT_STATUS.md.")
    spec = read(project / 'spec.json')
    validate_spec(spec, read(project / 'run-inputs.json'))
    hashes = source_hashes(project)
    binary = find_blender(binary)
    state['run_count'] += 1
    relative = f"runs/{state['run_count']:04d}-{state['stage']}"
    run = project / relative
    run.mkdir(parents=True, exist_ok=False)
    for name in INPUTS:
        shutil.copyfile(project / name, run / name)
    for name in hashes:
        if name.startswith('assets/'):
            (run/name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(project/name, run/name)
    shutil.copyfile(ROOT / 'scripts/blender_runtime.py', run / 'blender_runtime.py')
    write(run / 'request.json', {'stage': state['stage'], 'source_hashes': hashes,
                                'runtime_sha256': digest(run / 'blender_runtime.py'), 'startedAt': now()})
    state['latest_run'] = relative
    state['status'] = 'running'
    state['reason'] = 'Headless Blender build in progress; do not launch another writer.'
    save(project, state)
    start = time.monotonic()
    try:
        launch(binary, run / 'blender_runtime.py', 'build', run, run / 'build.log', timeout)
        audit = read(run / 'audit.json')
        if not audit['passed']:
            raise RuntimeError(f'Mesh audit failed: {audit["errors"]}')
        if state['stage'] == 'appearance' and audit['geometryFingerprint'] != state['geometry_fingerprint']:
            raise RuntimeError('Appearance changed accepted geometry. Record geometry-correction before proceeding.')
        launch(binary, run / 'blender_runtime.py', 'reopen', run, run / 'reopen.log', timeout)
        reopened = read(run / 'reopen.json')
        if not reopened['passed']:
            raise RuntimeError('Saved blend did not reproduce its geometry/materials on reopening.')
        if source_hashes(project) != hashes:
            raise RuntimeError('Sources changed during execution; current inputs differ from the rendered snapshot.')
        files = [*INPUTS, *[n for n in hashes if n.startswith('assets/')],
                 'blender_runtime.py', 'request.json', 'model.blend', 'audit.json', 'clay-audit.json', 'reopen.json', *audit['images']]
        artifacts = {name: digest(run / name) for name in files}
        write(run / 'result.json', {'passed': True, 'source_hashes': hashes, 'artifacts': artifacts,
                                   'geometryFingerprint': audit['geometryFingerprint'], 'finishedAt': now(),
                                   'blenderSeconds': round(time.monotonic() - start, 3)})
        state.update(status='awaiting-review', reason='Inspect the actual reference/render pairs, then record a visual review.', technical_failures=0)
    except Exception as error:
        state['technical_failures'] += 1
        state['status'] = 'stopped' if state['technical_failures'] >= 3 else 'editing'
        state['reason'] = str(error)
        write(run / 'failure.json', {'passed': False, 'error': str(error), 'at': now()})
        raise
    finally:
        state['blender_seconds'] += time.monotonic() - start
        save(project, state)
    return read(run / 'result.json')


def review_project(project, report_path):
    state = read(state_path(project))
    if state['status'] != 'awaiting-review':
        raise ValueError('A successful, unreviewed render is required.')
    report = read(report_path)
    if report.get('decision') not in ('accept', 'refine', 'request-input') or not str(report.get('summary', '')).strip():
        raise ValueError('Provide decision and meaningful summary.')
    run = project / state['latest_run']
    result = read(run / 'result.json')
    if not result['passed']:
        raise ValueError('Cannot accept a failed execution.')
    for name, expected in result['artifacts'].items():
        if digest(run / name) != expected:
            raise ValueError(f'Review artifact changed: {name}')
    if source_hashes(project) != result['source_hashes'] and report['decision'] == 'accept':
        raise ValueError('Sources changed since capture. Record refine, then rerender.')
    spec = read(run / 'spec.json')
    expected_features = {f['id'] for f in spec['critical_features']}
    features = report.get('features', [])
    if len(features) != len(expected_features) or {f.get('id') for f in features} != expected_features:
        raise ValueError('Review every critical feature exactly once.')
    for f in features:
        if f.get('status') not in ('pass', 'fail', 'unseen') or not str(f.get('notes', '')).strip():
            raise ValueError('Each feature needs pass/fail/unseen and a concrete observation.')
    images = report.get('images', [])
    required_images = set(read(run / 'audit.json')['images'])
    if not images or not set(images) <= required_images:
        raise ValueError('Name actual captured images from this run.')
    if report['decision'] == 'accept' and (set(images) != required_images or any(f['status'] != 'pass' for f in features)):
        raise ValueError('Acceptance requires all images and all critical features passed.')
    record = {**report, 'at': now(), 'stage': state['stage'], 'run': state['latest_run'], 'result_sha256': digest(run / 'result.json')}
    state['history'].append(record)
    write(run / 'visual-review.json', record)
    stage = state['stage']
    if report['decision'] == 'refine':
        state['corrections'][stage] = state['corrections'].get(stage, 0) + 1
        limit = state['corrections'][stage] >= 3 or sum(state['corrections'].values()) >= 6
        state['status'] = 'stopped' if limit else 'editing'
    elif report['decision'] == 'request-input':
        state['status'] = 'paused'
    else:
        state['accepted'][stage] = state['latest_run']
        state['status'] = 'editing'
        if stage == 'form':
            state['geometry_fingerprint'] = result['geometryFingerprint']
            state['geometry_ready_at'] = now()
            if spec['appearance'] == 'geometry-first':
                state['status'] = 'awaiting-user'
            elif spec['appearance'] == 'geometry-only':
                state['status'] = 'complete'
            else:
                state['stage'] = 'appearance'
        elif stage == 'appearance':
            state['status'] = 'complete'
        else:
            state['stage'] = STAGES[STAGES.index(stage)+1]
        if state['status'] == 'complete':
            state['completed_at'] = now()
    state['reason'] = report['summary']
    save(project, state)
    return state


def transition(project, action, note):
    state = read(state_path(project))
    if not note.strip():
        raise ValueError('Record the user instruction or correction reason.')
    if action == 'approve-geometry':
        if state['status'] != 'awaiting-user' and not (state['status'] == 'complete' and state['stage'] == 'form' and 'form' in state['accepted']):
            raise ValueError('No geometry approval checkpoint is pending.')
        state.update(stage='appearance', status='editing', geometry_approved_at=now())
        state.pop('completed_at', None)
    elif action == 'resume':
        if state['status'] != 'paused':
            raise ValueError('Resume applies only to a clarification pause, not hard stops.')
        state['status'] = 'editing'
    elif action == 'geometry-correction':
        if state['status'] not in ('awaiting-user', 'complete', 'editing') or 'form' not in state['accepted']:
            raise ValueError('Geometry correction requires a previously reviewed form checkpoint.')
        state['corrections']['form'] = state['corrections'].get('form', 0) + 1
        if state['corrections']['form'] >= 3 or sum(state['corrections'].values()) >= 6:
            state.update(status='stopped', reason='Correction limit reached; revise the brief with the user.')
            save(project, state)
            raise ValueError(state['reason'])
        state.update(stage='form', status='editing')
        state.pop('completed_at', None)
        state['accepted'].pop('appearance', None)
    state['reason'] = note
    state['history'].append({'at': now(), 'action': action, 'note': note})
    save(project, state)
    return state


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('new'); p.add_argument('--out', required=True, type=Path); p.add_argument('--reference', action='append', required=True, type=Path)
    for command in ('status', 'run', 'review', 'approve-geometry', 'resume', 'geometry-correction'):
        p = sub.add_parser(command); p.add_argument('--project', required=True, type=Path)
        if command == 'run':
            p.add_argument('--blender'); p.add_argument('--timeout', type=int, default=600)
        if command == 'review': p.add_argument('--report', type=Path, required=True)
        if command in ('approve-geometry', 'resume', 'geometry-correction'): p.add_argument('--note', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'new': result = new_project(args.out, args.reference)
        else:
            project = args.project.expanduser().resolve(strict=True)
            if args.command == 'status':
                result = read(state_path(project)); save(project, result)
            elif args.command == 'run': result = run_project(project, args.blender, args.timeout)
            elif args.command == 'review': result = review_project(project, args.report)
            else: result = transition(project, args.command, args.note)
        print(json.dumps(result, indent=2))
        return 3 if result.get('status') == 'stopped' else 0
    except (ValueError, OSError, RuntimeError, subprocess.TimeoutExpired, KeyError) as error:
        print(f'img2blender: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
