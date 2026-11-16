"""Exercise the real Blender adapter with synthetic geometry, not a likeness benchmark."""
import argparse
import base64
import importlib.util
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
loader=importlib.util.spec_from_file_location('project',ROOT/'scripts/project.py')
p=importlib.util.module_from_spec(loader);loader.loader.exec_module(p)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--blender',required=True)
    args=parser.parse_args();out=args.out.resolve()
    if out.exists():raise ValueError('Use a new smoke-test directory.')
    out.mkdir(parents=True)
    reference=out/'synthetic-input.png';reference.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII='))
    project=out/'fixture';p.new_project(project,[reference])
    shutil.copyfile(ROOT/'tests/fixture_build.py',project/'build.py')
    spec=p.read(project/'spec.json')
    spec.update(name='Synthetic rounded body and cap',use='software adapter test',style='simple beveled solid',
                reference_roles={'R1':'placeholder input for file handling, not a fidelity reference'},
                parts=[{'id':'body'},{'id':'cap','parent':'body'}],
                critical_features=[{'id':'assembly','references':['R1'],'target':'Engineering fixture: two colored beveled parts; not an image-match test'}])
    spec['render'].update(samples=4,resolution=160)
    spec['views']=[spec['views'][0],spec['views'][3],{'id':'open','direction':[1,-2,1],'hide_parts':['cap']}]
    p.write(project/'spec.json',spec)
    (project/'BRIEF.md').write_text('# Synthetic adapter smoke test\n\nTwo beveled cuboids, colored body and cap, stable named parts and editable bevel modifiers. Tests native execution, material parity and saving; no image accuracy claim.\n',encoding='utf-8')
    p.run_project(project,args.blender,300)
    print(project)


if __name__=='__main__':main()
