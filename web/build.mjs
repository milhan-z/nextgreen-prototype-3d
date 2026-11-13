import fs from 'fs'; import { execSync } from 'child_process';
const D = new URL('..', import.meta.url).pathname;
fs.writeFileSync(D + 'web/glb_data.js', 'export default "' + fs.readFileSync(D + 'prototype.glb').toString('base64') + '";');
execSync(`npx esbuild ${D}web/main.js --bundle --minify --format=iife --outfile=${D}web/bundle.js`, { cwd: D, stdio: 'inherit' });
const html = fs.readFileSync(D + 'web/shell.html', 'utf8').replace('/*BUNDLE*/', () => fs.readFileSync(D + 'web/bundle.js', 'utf8').replace(/<\/script/g, '<\\/script'));
fs.writeFileSync(D + 'index.html', html); console.log('index.html', (html.length / 1e6).toFixed(1), 'MB');
