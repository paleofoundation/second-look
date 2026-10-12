import {build} from 'esbuild';
import {mkdtemp,rm} from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
const dir=await mkdtemp(path.join(os.tmpdir(),'physician-packet-check-'));
try{const file=path.join(dir,'test.mjs');await build({entryPoints:['tests/physician-packets/access.test.tsx'],bundle:true,platform:'node',format:'esm',outfile:file,jsx:'automatic',banner:{js:"import {createRequire} from 'node:module';const require=createRequire(import.meta.url);"}});await import(file);}finally{await rm(dir,{recursive:true,force:true});}
