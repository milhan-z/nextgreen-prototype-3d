import { chromium } from 'playwright-core';
const D = new URL('..', import.meta.url).pathname;
const views = process.argv.slice(2).filter((a) => a !== 'clean').length ? process.argv.slice(2).filter((a) => a !== 'clean') : (process.argv.includes('clean') ? [] : ['overview', 'side', 'interior', 'station', 'corner']);
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
p.on('pageerror', (e) => console.log('ERR', e.message)); p.on('console', (m) => m.type() === 'error' && console.log('CONSOLE', m.text()));
await p.goto('file://' + D + 'index.html?render=1');
await p.waitForFunction(() => window.__modelReady, null, { timeout: 120000 });
const names = { overview: 'render-1-overview', side: 'render-2-samping', interior: 'render-3-dalam', station: 'render-4-stasiun-air', corner: 'render-6-sudut-tong' };
for (const v of views) {
  await p.evaluate((v) => { setView(v); renderOnce(); }, v);
  await p.waitForTimeout(800);
  await p.screenshot({ path: D + names[v] + '.png' }); console.log('saved', v);
}
if (!process.argv.slice(2).length || process.argv.includes('clean')) {
  await p.goto('file://' + D + 'index.html?render=1&clean=1');
  await p.waitForFunction(() => window.__modelReady, null, { timeout: 120000 });
  await p.evaluate(() => { setView('overview'); renderOnce(); }); await p.waitForTimeout(800);
  await p.screenshot({ path: D + 'src/iso-sheet.png' }); console.log('saved clean');
}
await b.close();
