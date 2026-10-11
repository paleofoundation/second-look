"""Read-only validation of a closed candidate graph; never imports or changes evidence."""
import json,pathlib,importlib.util,argparse,sys
p=argparse.ArgumentParser();p.add_argument('candidate');a=p.parse_args()
try:
 spec=importlib.util.spec_from_file_location('pilot_checks','work/evidence/validate.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 c=json.loads(pathlib.Path(a.candidate).read_text(),object_pairs_hook=m.unique)
 assert c.get('synthetic') is False,'Synthetic fixture cannot be an evidence candidate'
 allowed=[pathlib.Path('work/ingest').resolve(),pathlib.Path('work/evidence/raw').resolve()]
 for f in c['manifest']['files']:
  path=pathlib.Path(f['path']).resolve();assert any(path.is_relative_to(root) for root in allowed),'Candidate source path outside approved staging/source roots'
 m.validate(c,production=False)
 print(json.dumps({'status':'PASS','scope':'Schema, graph, source hashes and version checks; pilot-specific four numeric expectations skipped','imported':False,'source_audit':'Separate source-backed verification still required'}))
except Exception as e:
 print(json.dumps({'status':'HOLD','reason':str(e),'imported':False}));sys.exit(1)
