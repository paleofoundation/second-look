import argparse,importlib.util,json,hashlib
from pathlib import Path
B=Path(__file__).resolve().parent;spec=importlib.util.spec_from_file_location('reed_ingest',B/'ingest.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=argparse.ArgumentParser();p.add_argument('--require-source-files',action='store_true');args=p.parse_args();c=m.read(B/'CANDIDATE.json');result=m.verify(c)
if args.require_source_files:result['privateFiles']=m.verify_sources(c)
else:result['privateFiles']={'status':'not_checked','reason':'Private source roots are optional for portable metadata/output verification. Use --require-source-files with both documented bindings.'}
print(json.dumps(result,indent=2))
