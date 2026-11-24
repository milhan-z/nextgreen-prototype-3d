import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import GLB64 from './glb_data.js';
import GEOM from './geom.json';
import VIEWDEF from './views.js';

const qs = new URLSearchParams(location.search);
const RENDER = qs.has('render');
const CLEAN = qs.has('clean');
const M = (x, y, z) => new THREE.Vector3(x / 1000, z / 1000, -y / 1000); // mm model -> three

const W = window.innerWidth, H = window.innerHeight;
const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
function fail(msg) { const l = document.getElementById('load'); if (l) { l.classList.add('err'); l.innerHTML = `<div><b>Model 3D tidak bisa ditampilkan</b>${msg}</div>`; } }
let renderer;
try { renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true }); }
catch (e) { fail('Browser ini tidak menjalankan WebGL. Coba buka di Chrome atau Firefox versi baru, atau lihat gambar render di folder repo.'); throw e; }
renderer.setPixelRatio(RENDER ? 1 : Math.min(2, devicePixelRatio));
renderer.setSize(W, H);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
document.getElementById('view').appendChild(renderer.domElement);

const scene = new THREE.Scene();
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.55;
const camera = new THREE.PerspectiveCamera(32, W / H, 0.05, 200);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = !RENDER;

scene.add(new THREE.HemisphereLight(0xffffff, 0xb8bcc2, 1.1));
const sun = new THREE.DirectionalLight(0xffffff, 2.2);
sun.position.set(6, 12, 7);
sun.target.position.set(3.5, 0, -1.5);
sun.castShadow = true;
sun.shadow.mapSize.set(4096, 4096);
Object.assign(sun.shadow.camera, { left: -9, right: 9, top: 9, bottom: -9, near: 1, far: 40 });
sun.shadow.radius = 4; sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.01;
scene.add(sun, sun.target);

const EDGE = { new: 0x00544f, default: 0x2a2e33, cover: 0x8a9096, plant: 0x2f4a26 };
const groups = {};
const tankMats = [];
function bytes(b64) { const s = atob(b64); const u = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) u[i] = s.charCodeAt(i); return u.buffer; }

new GLTFLoader().parse(bytes(GLB64), '', (gltf) => {
  document.getElementById('load')?.remove();
  const root = gltf.scene;
  root.traverse((o) => {
    if (!o.isMesh) return;
    const nm = (o.name || o.parent?.name || '');
    const [grp, ck] = nm.split('|');
    o.userData.grp = grp; o.userData.ck = ck;
    if (!o.geometry.attributes.normal) o.geometry.computeVertexNormals();
    const src = o.material;
    const transparent = src.transparent || src.opacity < 1;
    const mat = new THREE.MeshStandardMaterial({
      color: src.color, metalness: ck === 'frame' ? 0.55 : 0.0, roughness: ck === 'frame' ? 0.42 : 0.62,
      transparent, opacity: src.opacity, side: THREE.DoubleSide, depthWrite: !transparent,
      polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1,
    });
    if (ck === 'new') { mat.emissive = new THREE.Color(0x00a89f); mat.emissiveIntensity = 0.12; }
    if (ck === 'tank') { mat.roughness = 0.42; mat.metalness = 0.12; tankMats.push(mat); }
    o.material = mat;
    o.castShadow = !transparent && grp !== 'site';
    o.receiveShadow = true;
    if (grp !== 'site') {
      const thr = grp === 'plant' ? 60 : 28;
      const eg = new THREE.EdgesGeometry(o.geometry, thr);
      const col = grp === 'new' ? EDGE.new : grp === 'cover' ? EDGE.cover : grp === 'plant' ? EDGE.plant : EDGE.default;
      const ln = new THREE.LineSegments(eg, new THREE.LineBasicMaterial({ color: col, transparent: true, opacity: grp === 'cover' ? 0.55 : grp === 'plant' ? 0.35 : 0.9 }));
      o.add(ln);
    }
    (groups[grp] ||= []).push(o);
  });
  scene.add(root);
  setView(cur);
  window.__modelReady = true;
}, () => fail('File model rusak saat dibaca. Muat ulang halaman, atau unduh ulang index.html dari repo.'));

// ---------- aliran air (partikel) ----------
const KINDS = GEOM.flowk || GEOM.flow.map(() => 'loop');
const paths = GEOM.flow.map((pts) => { const cp = new THREE.CurvePath(); for (let i = 0; i < pts.length - 1; i++) cp.add(new THREE.LineCurve3(M(...pts[i]), M(...pts[i + 1]))); return cp; });
const flowGroup = new THREE.Group(); scene.add(flowGroup);
const dropGeo = new THREE.SphereGeometry(0.02, 10, 8);
const dropMat = new THREE.MeshBasicMaterial({ color: 0x19c3e6, depthTest: true });
const kindGroups = {};
paths.forEach((cp, k) => {
  const kind = KINDS[k]; const g = (kindGroups[kind] ||= new THREE.Group()); flowGroup.add(g);
  const len = cp.getLength(); const n = Math.max(3, Math.round(len / 0.28));
  for (let i = 0; i < n; i++) { const m = new THREE.Mesh(dropGeo, dropMat); g.add(m); m.userData = { cp, t: i / n, sp: 0.35 / len }; }
});
function updDrops(dt) { for (const g of Object.values(kindGroups)) if (g.visible) for (const m of g.children) { const d = m.userData; d.t = (d.t + d.sp * dt) % 1; m.position.copy(d.cp.getPointAt(d.t)); } }
for (const g of Object.values(kindGroups)) for (const m of g.children) m.position.copy(m.userData.cp.getPointAt(m.userData.t));
const setKind = (k, on) => { if (kindGroups[k]) kindGroups[k].visible = on; };
setKind('over', false);

// ---------- simulasi hujan ----------
const SIM = GEOM.sim;
const S = { rate: 0, mm: 0, ff: 0, vol: 0, t: 0, speed: 3600, use: false, over: false, tong: 0, bak: 0, batch: 0, events: [], dryNoted: false, pulseOut: 0, pulseDump: 0 };
document.documentElement.style.setProperty('--inlet-top', ((1 - SIM.inlet_frac) * 100).toFixed(1) + '%');
// air di dalam tandon
const waterMat = new THREE.MeshStandardMaterial({ color: 0x1c9be0, roughness: 0.25, metalness: 0, transparent: true, opacity: 0.85 });
const waters = SIM.tanks.map(([x, y]) => {
  const m = new THREE.Mesh(new THREE.CylinderGeometry(SIM.R / 1000, SIM.R / 1000, 1, 48), waterMat);
  m.userData.base = M(x, y, SIM.base); m.visible = false; scene.add(m); return m;
});
function storeMesh(spec) {
  const m = new THREE.Mesh(new THREE.CylinderGeometry(spec.r / 1000, spec.r / 1000, 1, 40), waterMat);
  m.userData.spec = spec; m.visible = false; scene.add(m); return m;
}
const tongWater = storeMesh(SIM.tong);
const bakWater = storeMesh(SIM.bak);
// garis hujan
const RAIN_N = 2600;
const rr = SIM.roof; const rx0 = -1.2, rx1 = 9.0, rz0 = -4.2, rz1 = 2.0; // meter, area jatuhnya hujan
const rainPos = new Float32Array(RAIN_N * 6);
const rainGeo = new THREE.BufferGeometry(); rainGeo.setAttribute('position', new THREE.BufferAttribute(rainPos, 3));
const rainMat = new THREE.LineBasicMaterial({ color: 0x5f86a8, transparent: true, opacity: 0.55 });
const rain = new THREE.LineSegments(rainGeo, rainMat); rain.frustumCulled = false; rain.visible = false; scene.add(rain);
const rainY = new Float32Array(RAIN_N), rainFloor = new Float32Array(RAIN_N);
function roofZ(xm, zm) { // tinggi permukaan atap (m) di titik (x, -y), atau 0 di luar atap
  const x = xm * 1000, y = -zm * 1000;
  if (x < rr.x0 || x > rr.x1 || y < rr.y0 || y > rr.y1) return 0;
  const ym = (rr.y0 + rr.y1) / 2; return (rr.he + (rr.hr - rr.he) * (1 - Math.abs(y - ym) / (ym - rr.y0))) / 1000;
}
function seedDrop(i, top) {
  const x = rx0 + Math.random() * (rx1 - rx0), z = rz0 + Math.random() * (rz1 - rz0);
  rainPos[i * 6] = rainPos[i * 6 + 3] = x; rainPos[i * 6 + 2] = rainPos[i * 6 + 5] = z;
  rainY[i] = top ? 6 + Math.random() * 1.5 : rainFloor[i] + Math.random() * 7; rainFloor[i] = roofZ(x, z);
}
for (let i = 0; i < RAIN_N; i++) { rainFloor[i] = 0; seedDrop(i, false); }
function updRain(dt) {
  const active = Math.round(RAIN_N * Math.min(1, S.rate / 50 + 0.15)); const L = 0.10 + S.rate / 600;
  for (let i = 0; i < RAIN_N; i++) {
    if (i >= active) { rainPos[i * 6 + 1] = rainPos[i * 6 + 4] = -50; continue; }
    rainY[i] -= 9 * dt; if (rainY[i] < rainFloor[i]) seedDrop(i, true);
    rainPos[i * 6 + 1] = rainY[i] + L; rainPos[i * 6 + 4] = rainY[i];
  }
  rainGeo.attributes.position.needsUpdate = true;
}
const $ = (id) => document.getElementById(id);
const fmt = (n, d = 0) => n.toLocaleString('id-ID', { maximumFractionDigits: d, minimumFractionDigits: d });
$('capNote').textContent = '±' + fmt(SIM.usable_l) + ' L';
function setGlass(on) {
  if (!tankMats.length) return;
  for (const m of tankMats) { m.transparent = on; m.opacity = on ? 0.22 : 1; m.depthWrite = !on; m.needsUpdate = true; }
  waters.forEach((w) => (w.visible = on && S.vol > 1));
  const e = $('tGlass'); if (e) e.checked = on;
}
function stamp() {
  const day = Math.floor(S.t / 24), hh = Math.floor(S.t % 24), mi = Math.floor((S.t * 60) % 60);
  return `hari ${day}, ${String(hh).padStart(2, '0')}:${String(mi).padStart(2, '0')}`;
}
function logEv(text) {
  S.events.unshift({ when: stamp(), text });
  if (S.events.length > 4) S.events.length = 4;
  const log = $('log');
  log.innerHTML = S.events.map((e) => `<p><b>${e.when}</b> ${e.text}</p>`).join('');
}
function pulse(key) { S[key] = 1.6 * S.speed / 3600; }
function takeFromTank(liters) {
  const can = Math.max(0, S.vol - SIM.dead_l);
  const take = Math.min(liters, can);
  S.vol -= take;
  return take;
}
function refillTong() {
  const need = SIM.tong_l - S.tong;
  if (need < 1) return 0;
  const take = takeFromTank(need);
  if (take < 1) return 0;
  S.tong += take;
  S.batch += 1;
  pulse('pulseOut');
  const kurang = take < need - 1 ? ` Tandon hanya mengalirkan ${fmt(take)} L.` : '';
  logEv(`Batch ${S.batch}: kran tandon dibuka, tong diisi ${fmt(take)} L, lalu ditutup.${kurang} Tambah sebagian air sumur (volume belum diukur). Tuang AB mix, cek EC dan pH di tong biru.`);
  return take;
}
function dumpTong(fromEmpty) {
  if (S.tong < 1) return 0;
  const moved = S.tong;
  S.bak = Math.min(SIM.bak_l, S.bak + moved);
  S.tong = 0;
  pulse('pulseDump');
  logEv(fromEmpty
    ? `Bak kosong. Kran tong dibuka, ${fmt(moved)} L larutan turun ke bak.`
    : `Bak habis. Kran tong dibuka, ${fmt(moved)} L larutan turun ke bak.`);
  return moved;
}
let servicing = false;
function serviceBatch() {
  if (servicing) return;
  servicing = true;
  if (S.bak > 1) { servicing = false; return; }
  if (S.tong > 1) {
    dumpTong(false);
    if (refillTong()) S.dryNoted = false;
    else if (!S.dryNoted) {
      logEv('Tong sudah turun ke bak. Tandon tidak cukup untuk mengisi tong lagi. Air sumur masih bisa dipakai (cara isi belum dicek).');
      S.dryNoted = true;
    }
  } else if (S.vol > SIM.dead_l + 1) {
    if (refillTong() > 1 && S.bak <= 1) { dumpTong(true); refillTong(); }
    S.dryNoted = S.bak <= 1 && S.tong <= 1;
  } else if (!S.dryNoted) {
    logEv('Bak dan tong kosong. Air tandon tidak cukup mengalir. Air sumur masih bisa dipakai (cara isi belum dicek).');
    S.dryNoted = true;
  }
  servicing = false;
}
function placeStore(mesh, liters, cap) {
  const spec = mesh.userData.spec;
  const f = Math.max(0, Math.min(1, liters / cap));
  const h = Math.max(0.002, (spec.h / 1000) * Math.max(f, 0.001));
  mesh.scale.y = h;
  mesh.position.copy(M(spec.x, spec.y, spec.z)).add(new THREE.Vector3(0, h / 2, 0));
  mesh.visible = f > 0.01;
}
function updSim(dtReal) {
  const hrs = (dtReal * S.speed) / 3600;
  if (S.rate > 0 || S.use) S.t += hrs;
  if (S.rate > 0) {
    const mm = S.rate * hrs; S.mm += mm;
    let inL = mm * SIM.roof_m2 * SIM.coef;
    const ffNeed = Math.max(0, SIM.ff_l - S.ff);
    const toFF = Math.min(ffNeed, inL); S.ff += toFF; inL -= toFF;
    const room = Math.max(0, SIM.usable_l - S.vol);
    const into = Math.min(room, inL);
    S.vol += into;
    S.over = inL - into > 0.05 && S.rate > 0;
  } else S.over = false;
  if (S.use) {
    const before = S.bak;
    S.bak = Math.max(0, S.bak - SIM.use_lpd * hrs / 24);
    if (S.bak <= 0.5 && (before > 0.5 || S.tong > 1 || (S.vol > SIM.dead_l + 1 && !S.dryNoted))) serviceBatch();
  }
  if (S.pulseOut > 0) S.pulseOut = Math.max(0, S.pulseOut - hrs);
  if (S.pulseDump > 0) S.pulseDump = Math.max(0, S.pulseDump - hrs);
  const drawable = Math.max(0, S.vol - SIM.dead_l);
  const hMm = S.vol / SIM.l_per_mm;
  waters.forEach((w) => {
    const h = Math.max(0.002, hMm / 1000);
    w.scale.y = h; w.position.copy(w.userData.base).add(new THREE.Vector3(0, h / 2, 0));
    w.visible = !!tankMats[0]?.transparent && S.vol > 1;
  });
  placeStore(tongWater, S.tong, SIM.tong_l);
  placeStore(bakWater, S.bak, SIM.bak_l);
  $('lv1').style.height = $('lv2').style.height = (S.vol / SIM.nominal_l * 100) + '%';
  $('vol').innerHTML = fmt(S.vol) + ' <span>L</span>';
  $('mm').textContent = fmt(S.mm, 1) + ' mm';
  $('ff').textContent = fmt(S.ff, 1) + ' / ' + fmt(SIM.ff_l, 0) + ' L';
  $('clk').textContent = stamp();
  $('days').textContent = fmt(drawable / SIM.use_lpd, 0) + ' hari';
  $('tong').textContent = fmt(S.tong) + ' / ' + fmt(SIM.tong_l, 0) + ' L';
  $('bak').textContent = fmt(S.bak) + ' / ' + fmt(SIM.bak_l, 0) + ' L';
  $('batch').textContent = String(S.batch);
  const st = $('stat');
  let msg, cls = '';
  if (S.over) { msg = 'Muka air sampai lubang masuk, di bawah talang. Lebihnya keluar lewat pelimpah 2 inci.'; cls = 'full'; }
  else if (S.rate > 0 && S.ff < SIM.ff_l) { msg = 'Hujan baru: 9 L pertama masuk first flush, lalu direset kalau hujan berhenti dan mulai lagi.'; cls = 'wet'; }
  else if (S.rate > 0) { msg = 'Air lewat tabung filter 4 inci, masuk tandon 1. Pipa bawah ikut mengisi tandon 2.'; cls = 'wet'; }
  else if (S.use && S.dryNoted && S.bak < 1) { msg = 'Cadangan yang bisa mengalir habis. Air sumur masih bisa dipakai, cara isinya belum dicek.'; cls = 'batch'; }
  else if (S.use && S.bak > 1) { msg = 'Bak dipakai tiap hari. Tandon tidak mengalir terus. Tong menunggu bak habis.'; cls = 'batch'; }
  else if (S.use && S.pulseOut > 0) { msg = 'Tong diisi dari tandon. Kran tandon ditutup sebelum AB mix. Cek EC dan pH di tong biru.'; cls = 'batch'; }
  else if (S.use && S.pulseDump > 0) { msg = 'Bak habis. Larutan tong biru turun ke bak.'; cls = 'batch'; }
  else if (S.use) msg = 'Bak dan tong kosong. Isi tandon dulu, atau nyalakan hujan.';
  else msg = S.vol > 1 ? 'Hujan berhenti. Air tersimpan di tandon. Bagian di atas lubang masuk tidak terisi.' : 'Pilih intensitas hujan untuk mulai mengisi tandon.';
  st.textContent = msg; st.className = 'status ' + cls;
  const flowOn = flowGroup.visible;
  if (flowOn) {
    const simOn = S.rate > 0 || S.use || S.vol > 1 || S.tong > 1 || S.bak > 1;
    const ffOpen = S.ff < SIM.ff_l - 0.05;
    setKind('rain', simOn ? S.rate > 0 : true);
    setKind('ff', simOn ? S.rate > 0 && ffOpen : true);
    setKind('fill', simOn ? S.rate > 0 && !ffOpen && !S.over : true);
    setKind('link', simOn ? S.rate > 0 && S.vol > 1 : true);
    setKind('over', S.over);
    setKind('out', simOn ? S.pulseOut > 0 : true);
    setKind('dump', simOn ? S.pulseDump > 0 : true);
    setKind('loop', simOn ? S.use && S.bak > 1 : true);
  }
  rain.visible = S.rate > 0;
}
function setRain(r) {
  if (r > 0 && S.rate === 0) S.ff = 0;
  S.rate = r; $('rainLbl').textContent = r + ' mm/jam';
  $('ff').textContent = fmt(S.ff, 1) + ' / ' + fmt(SIM.ff_l, 0) + ' L';
  document.querySelectorAll('#rain button').forEach((b) => b.setAttribute('aria-pressed', +b.dataset.r === r));
  if (r > 0 && !S.glassTouched) setGlass(true);
}
window.setRain = setRain;

// ---------- callout ----------
const G = GEOM.anchors;
const CALL = [
  { id: 1, t: 'Atap 18 m²', s: 'plastik UV bening, belum ada talang', a: G.roof },
  { id: 2, t: 'Talang + kasa SS304', s: 'dua sisi panjang, bukaan perkiraan', a: G.gutter },
  { id: 3, t: 'First flush + tabung 4 inci', s: '9 L dibuang, tabung media tidur', a: G.ff },
  { id: 4, t: '2 tandon Filtra TB 2500', s: 'hitam, 2 × 2.650 L. Di atas lubang masuk tidak terisi', a: G.tank },
  { id: 5, t: 'Pipa 1 inci ke tong biru', s: 'kran, screen filter 120 mesh', a: G.filter },
  { id: 6, t: 'Cek EC dan pH di tong biru', s: 'meter dan papan SOP, setelah AB mix', a: G.sop },
  { id: 7, t: 'Campur AB mix di tong biru', s: 'tong terbuka, ball valve ke bak saat bak habis', a: G.drum },
  { id: 8, t: 'Ke tanaman (Dutch Bucket, tetes)', s: 'selang PE hitam 16 mm + selang mikro', a: G.drip },
  { id: 'a', t: 'Air sumur ke tong biru (perkiraan)', s: 'pompa atau manual, belum dicek', a: G.sumur, sub: true },
  { id: 'b', t: 'Pelimpah 2 inci, moncong bawaan', s: '', a: G.over, sub: true },
  { id: 'c', t: 'Lubang angin berkasa', s: '', a: G.vent, sub: true },
  { id: 'k', t: 'Pipa sambung bawah antar tandon', s: '', a: G.link, sub: true },
  { id: 'd', t: 'Kran tandon', s: '', a: G.tap, sub: true },
  { id: 's', t: 'Kran sampel pada pipa 1 inci', s: '', a: G.sample, sub: true },
  { id: 'e', t: 'Bak bawah tanah (sudah ada)', s: '', a: G.res, sub: true },
  { id: 'f', t: 'Pompa celup (perkiraan, sudah ada)', s: '', a: G.pump, sub: true },
  { id: 'g', t: 'Ball valve tong ke bak (sudah ada)', s: '', a: G.valve, sub: true },
  { id: 'h', t: 'Pipa balik PVC putih (sudah ada)', s: '', a: G.ret, sub: true },
  { id: 'i', t: 'Kabel pompa turun dari rangka (sudah ada)', s: '', a: G.cable, sub: true },
];
const overlay = document.getElementById('labels');
const svg = document.getElementById('leaders');
CALL.forEach((c) => {
  const el = document.createElement('div');
  el.className = 'callout' + (c.sub ? ' sub' : '');
  el.innerHTML = (c.sub ? '' : `<span class="num">${c.id}</span>`) + `<span class="txt"><b>${c.t}</b>${c.s ? `<i>${c.s}</i>` : ''}</span>`;
  overlay.appendChild(el);
  const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
  const dot = document.createElementNS('http://www.w3.org/2000/svg', 'circle'); dot.setAttribute('r', 4);
  svg.append(line, dot);
  Object.assign(c, { el, line, dot, v: M(...c.a) });
});

// ---------- tampilan ----------
window.setGroup = (g, on) => (groups[g] || []).forEach((o) => (o.visible = on));
const VIEWS = VIEWDEF;
let cur = 'overview';
function setView(name) {
  const v = VIEWS[name]; cur = name;
  ['cover', 'plant', 'reslid'].forEach((g) => window.setGroup(g, !(v.hide || []).includes(g)));
  const nt = document.getElementById('note'); if (nt) { nt.textContent = v.note || ''; nt.style.display = v.note ? '' : 'none'; }
  camera.position.set(...v.pos); controls.target.set(...v.tgt); camera.fov = v.fov; baseFov = v.fov; applyOffset(); controls.update();
  document.querySelectorAll('#views button').forEach((b) => b.setAttribute('aria-pressed', b.dataset.v === name));
}
window.setView = setView;
let baseFov = 34;
function applyOffset() {
  const w = innerWidth, h = innerHeight, d = RIGHT > 24 ? RIGHT - 24 : 0;
  camera.aspect = w / h;
  camera.fov = w / h < 1.6 ? Math.min(75, baseFov * (1 + (1.6 - w / h) * 0.75)) : baseFov;
  if (d) camera.setViewOffset(w + d, h, d, 0, w, h); else camera.clearViewOffset();
  camera.updateProjectionMatrix();
}
let labelsOn = true;
const tmp = new THREE.Vector3();
let RIGHT = 24; const fitRight = () => { const u = document.getElementById('ui'); RIGHT = (!RENDER && u && innerWidth > 820 && !u.classList.contains('closed')) ? u.offsetWidth + 40 : 24; }; fitRight(); addEventListener('resize', fitRight);
function updLabels() {
  const v = VIEWS[cur]; const w = renderer.domElement.clientWidth, h = renderer.domElement.clientHeight;
  const tEl = document.getElementById('title'), iEl = document.getElementById('info'), uEl = document.getElementById('ui');
  const TOPLIM = (tEl && tEl.offsetParent ? tEl.getBoundingClientRect().bottom : 0) + 10;
  let BOTLIM = h - 16;
  if (iEl && iEl.offsetParent) BOTLIM = iEl.getBoundingClientRect().top - 10;
  else if (uEl && innerWidth <= 820 && getComputedStyle(uEl).display !== 'none') BOTLIM = uEl.getBoundingClientRect().top - 10;
  for (const c of CALL) {
    const show = labelsOn && v.show.includes(c.id) && !(CLEAN && c.sub) && !(c.sub && w < 820);
    tmp.copy(c.v).project(camera);
    const vis = show && tmp.z < 1;
    c.el.style.display = vis ? '' : 'none'; c.line.style.display = c.dot.style.display = vis ? '' : 'none';
    if (!vis) continue;
    const x = (tmp.x * 0.5 + 0.5) * w, y = (-tmp.y * 0.5 + 0.5) * h;
    const o = (v.off && v.off[c.id]) || [80, -80];
    const lx = x + o[0], ly = y + o[1];
    const bw = c.el.offsetWidth, bh = c.el.offsetHeight;
    let left = o[0] >= 0 ? lx : lx - bw;
    left = Math.max(24, Math.min(w - bw - RIGHT, left));
    let top = Math.max(TOPLIM, Math.min(BOTLIM - bh, ly - bh / 2));
    c.el.style.left = left + 'px'; c.el.style.top = top + 'px';
    const ex = x < left ? left : (x > left + bw ? left + bw : x), ey = top + bh / 2;
    c.line.setAttribute('x1', x); c.line.setAttribute('y1', y);
    c.line.setAttribute('x2', ex); c.line.setAttribute('y2', ey);
    c.dot.setAttribute('cx', x); c.dot.setAttribute('cy', y);
    c.line.setAttribute('class', c.sub ? 'sub' : ''); c.dot.setAttribute('class', c.sub ? 'sub' : '');
  }
}
window.setFlow = (on) => { flowGroup.visible = on; };
window.isolate = (re) => { const r = new RegExp(re, 'i'); for (const list of Object.values(groups)) for (const o of list) { const nm = o.name || o.parent?.name || ''; o.visible = r.test(nm); } };
window.frame = (pos, tgt, fov) => { camera.position.set(...pos); controls.target.set(...tgt); camera.fov = baseFov = fov; applyOffset(); controls.update(); };
window.setLabels = (on) => { labelsOn = on; };


document.querySelectorAll('#views button').forEach((b) => b.onclick = () => setView(b.dataset.v));
const tg = (id, fn) => { const e = document.getElementById(id); if (e) e.onchange = () => fn(e.checked); };
tg('tLabels', window.setLabels); tg('tFlow', window.setFlow);
tg('tCover', (on) => window.setGroup('cover', on)); tg('tPlant', (on) => window.setGroup('plant', on));
tg('tUse', (on) => { S.use = on; }); tg('tGlass', (on) => { S.glassTouched = true; setGlass(on); });
document.querySelectorAll('#rain button').forEach((b) => b.onclick = () => setRain(+b.dataset.r));
document.querySelectorAll('#speed button').forEach((b) => b.onclick = () => { S.speed = +b.dataset.s; document.querySelectorAll('#speed button').forEach((x) => x.setAttribute('aria-pressed', x === b)); });
$('bFull').onclick = () => { S.vol = SIM.usable_l; S.ff = SIM.ff_l; S.dryNoted = false; if (!S.glassTouched) setGlass(true); };
$('bReset').onclick = () => {
  Object.assign(S, { mm: 0, ff: 0, vol: 0, t: 0, tong: 0, bak: 0, batch: 0, dryNoted: false, pulseOut: 0, pulseDump: 0, over: false });
  S.events = []; $('log').innerHTML = '<p>Belum ada kejadian batch.</p>'; setRain(0);
};
const mobile = () => innerWidth <= 820;
let panelOpen = !mobile();
function setPanel(open) {
  panelOpen = open; $('ui').classList.toggle('open', open); $('ui').classList.toggle('closed', !open);
  $('uiHead').setAttribute('aria-expanded', open);
  $('uiHint').textContent = open ? (mobile() ? 'Ketuk untuk tutup' : 'Sembunyikan') : (mobile() ? 'Ketuk untuk buka' : 'Tampilkan');
  fitRight(); applyOffset();
}
$('uiHead').onclick = () => setPanel(!panelOpen);
addEventListener('keydown', (e) => { if (e.key === 'Escape' && panelOpen && mobile()) { setPanel(false); $('uiHead').focus(); } });
let wasMobile = mobile();
addEventListener('resize', () => { if (mobile() !== wasMobile) { wasMobile = mobile(); setPanel(!wasMobile); } });
setPanel(panelOpen);
if (REDUCED && !RENDER) { const f = $('tFlow'); f.checked = false; flowGroup.visible = false; }
if (RENDER) document.body.classList.add('render');
if (CLEAN) { document.body.classList.add('clean'); flowGroup.visible = false; }
setView(qs.get('view') || 'overview');

const clock = new THREE.Clock();
function loop() {
  const dt = clock.getDelta();
  if (!RENDER) { updSim(Math.min(dt, 0.1)); updDrops(dt); if (S.rate > 0) updRain(REDUCED ? 0 : Math.min(dt, 0.05)); }
  controls.update(); renderer.render(scene, camera); updLabels();
  requestAnimationFrame(loop);
}
loop();
window.renderOnce = () => { controls.update(); renderer.render(scene, camera); updLabels(); };
addEventListener('resize', () => { fitRight(); applyOffset(); renderer.setSize(innerWidth, innerHeight); });
