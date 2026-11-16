import fs from 'fs'; import { execSync } from 'child_process';
const D = new URL('..', import.meta.url).pathname;
fs.writeFileSync(D + 'web/glb_data.js', 'export default "' + fs.readFileSync(D + 'prototype.glb').toString('base64') + '";');
execSync(`npx esbuild ${D}web/main.js --bundle --minify --format=iife --outfile=${D}web/bundle.js`, { cwd: D, stdio: 'inherit' });
const ff = [['Mitr', 500, 'mitr-latin-500-normal'], ['Mitr', 600, 'mitr-latin-600-normal'], ['Carlito', 400, 'carlito-latin-400-normal'], ['Carlito', 700, 'carlito-latin-700-normal']]
  .map(([f, w, n]) => `@font-face{font-family:"${f}";font-weight:${w};font-style:normal;font-display:swap;src:url(data:font/woff2;base64,${fs.readFileSync(D + 'web/fonts/' + n + '.woff2').toString('base64')}) format("woff2")}`).join('');
const html = fs.readFileSync(D + 'web/shell.html', 'utf8').replace('/*FONTS*/', () => ff).replace('/*BUNDLE*/', () => fs.readFileSync(D + 'web/bundle.js', 'utf8').replace(/<\/script/g, '<\\/script'));
fs.writeFileSync(D + 'index.html', html); console.log('index.html', (html.length / 1e6).toFixed(1), 'MB');
