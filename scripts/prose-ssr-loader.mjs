import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import ts from 'typescript';

/** Use the same TS/TSX execution strategy as the existing article SSR checks. */
export function createProseSSRLoader(root) {
  const require = createRequire(import.meta.url);
  const cache = new Map();
  function load(file) {
    if (cache.has(file)) return cache.get(file).exports;
    if (file.endsWith('.css')) return {};
    if (file.endsWith('.json')) return JSON.parse(fs.readFileSync(file, 'utf8'));
    const module = {exports: {}};
    cache.set(file, module);
    const compiled = ts.transpileModule(fs.readFileSync(file, 'utf8'), {
      fileName: file.endsWith('.mjs') ? file.slice(0, -4) + '.js' : file,
      compilerOptions: {module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022,
        jsx: ts.JsxEmit.ReactJSX, esModuleInterop: true},
    }).outputText;
    const localRequire = id => {
      if (!id.startsWith('.') && !id.startsWith('@/')) return require(id);
      const base = id.startsWith('@/') ? path.join(root, id.slice(2)) : path.resolve(path.dirname(file), id);
      const target = [base, base + '.ts', base + '.tsx', base + '.json', path.join(base, 'index.ts')]
        .find(candidate => fs.existsSync(candidate) && fs.statSync(candidate).isFile());
      assert(target, `Cannot resolve ${id} from ${file}`);
      return load(target);
    };
    new Function('require', 'module', 'exports', compiled)(localRequire, module, module.exports);
    return module.exports;
  }
  return load;
}
