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
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
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
function bytes(b64) { const s = atob(b64); const u = new Uint8Array(s.length); for (let i = 0; i < s.length; i++) u[i] = s.charCodeAt(i); return u.buffer; }

new GLTFLoader().parse(bytes(GLB64), '', (gltf) => {
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
});

// ---------- aliran air (partikel) ----------
const paths = GEOM.flow.map((pts) => { const cp = new THREE.CurvePath(); for (let i = 0; i < pts.length - 1; i++) cp.add(new THREE.LineCurve3(M(...pts[i]), M(...pts[i + 1]))); return cp; });
const flowGroup = new THREE.Group(); scene.add(flowGroup);
const dropGeo = new THREE.SphereGeometry(0.02, 10, 8);
const dropMat = new THREE.MeshBasicMaterial({ color: 0x19c3e6, depthTest: true });
const drops = [];
paths.forEach((cp) => {
  const len = cp.getLength(); const n = Math.max(3, Math.round(len / 0.28));
  for (let i = 0; i < n; i++) { const m = new THREE.Mesh(dropGeo, dropMat); flowGroup.add(m); drops.push({ m, cp, t: i / n, sp: 0.35 / len }); }
});
function updDrops(dt) { for (const d of drops) { d.t = (d.t + d.sp * dt) % 1; d.m.position.copy(d.cp.getPointAt(d.t)); } }
updDrops(0);

// ---------- callout ----------
const G = GEOM.anchors;
const CALL = [
  { id: 1, t: 'Atap 18 m²', s: 'plastik UV bening, belum ada talang', a: G.roof },
  { id: 2, t: 'Talang + kasa ~1 mm', s: 'baru, di kedua sisi panjang', a: G.gutter },
  { id: 3, t: 'First flush (~9 L dibuang)', s: '0,5 L per m² atap', a: G.ff },
  { id: 4, t: 'Tandon tertutup', s: 'kelas 1.100 L, gelap, di luar dinding kasa', a: G.tank },
  { id: 5, t: 'Filter 120 sampai 200 mesh', s: 'sebelum masuk bak lantai', a: G.filter },
  { id: 6, t: 'Cek pH dan TDS', s: 'pH meter + TDS pen', a: G.table },
  { id: 7, t: 'Campur AB mix di tong/bak yang ada', s: 'tong diberi tutup (usulan)', a: G.drum },
  { id: 8, t: 'Ke tanaman (Dutch Bucket, tetes)', s: 'selang PE hitam 16 mm + selang mikro', a: G.drip },
  { id: 'a', t: 'Selang taman, isi manual dari sumur (perkiraan)', s: '', a: G.hose, sub: true },
  { id: 'b', t: 'Pelimpah', s: '', a: G.over, sub: true },
  { id: 'c', t: 'Lubang angin berkasa', s: '', a: G.vent, sub: true },
  { id: 'd', t: 'Kran di atas dasar', s: '', a: G.tap, sub: true },
  { id: 'e', t: 'Bak lantai bertutup (sudah ada)', s: '', a: G.res, sub: true },
  { id: 'f', t: 'Pompa celup (perkiraan, sudah ada)', s: '', a: G.pump, sub: true },
  { id: 'g', t: 'Ball valve gagang merah (sudah ada)', s: '', a: G.valve, sub: true },
  { id: 'h', t: 'Pipa balik PVC putih (sudah ada)', s: '', a: G.ret, sub: true },
  { id: 'i', t: 'Kabel pompa turun dari rangka (sudah ada)', s: '', a: G.cable, sub: true },
  { id: 'j', t: 'Pipa isi PVC dari atas (sudah ada)', s: '', a: G.fillpipe, sub: true },
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
  camera.position.set(...v.pos); controls.target.set(...v.tgt); camera.fov = v.fov; camera.updateProjectionMatrix(); controls.update();
  document.querySelectorAll('#ui button[data-v]').forEach((b) => b.classList.toggle('on', b.dataset.v === name));
}
window.setView = setView;
let labelsOn = true;
const tmp = new THREE.Vector3();
function updLabels() {
  const v = VIEWS[cur]; const w = renderer.domElement.clientWidth, h = renderer.domElement.clientHeight;
  for (const c of CALL) {
    const show = labelsOn && v.show.includes(c.id) && !(CLEAN && c.sub);
    tmp.copy(c.v).project(camera);
    const vis = show && tmp.z < 1;
    c.el.style.display = vis ? '' : 'none'; c.line.style.display = c.dot.style.display = vis ? '' : 'none';
    if (!vis) continue;
    const x = (tmp.x * 0.5 + 0.5) * w, y = (-tmp.y * 0.5 + 0.5) * h;
    const o = (v.off && v.off[c.id]) || [80, -80];
    const lx = x + o[0], ly = y + o[1];
    const bw = c.el.offsetWidth, bh = c.el.offsetHeight;
    let left = o[0] >= 0 ? lx : lx - bw;
    left = Math.max(24, Math.min(w - bw - 24, left));
    let top = Math.max(96, Math.min(h - 100 - bh, ly - bh / 2));
    c.el.style.left = left + 'px'; c.el.style.top = top + 'px';
    const ex = x < left ? left : (x > left + bw ? left + bw : x), ey = top + bh / 2;
    c.line.setAttribute('x1', x); c.line.setAttribute('y1', y);
    c.line.setAttribute('x2', ex); c.line.setAttribute('y2', ey);
    c.dot.setAttribute('cx', x); c.dot.setAttribute('cy', y);
    c.line.setAttribute('class', c.sub ? 'sub' : ''); c.dot.setAttribute('class', c.sub ? 'sub' : '');
  }
}
window.setFlow = (on) => { flowGroup.visible = on; };
window.setLabels = (on) => { labelsOn = on; };


document.querySelectorAll('#ui button[data-v]').forEach((b) => b.onclick = () => setView(b.dataset.v));
const tg = (id, fn) => { const e = document.getElementById(id); if (e) e.onchange = () => fn(e.checked); };
tg('tLabels', window.setLabels); tg('tFlow', window.setFlow);
tg('tCover', (on) => window.setGroup('cover', on)); tg('tPlant', (on) => window.setGroup('plant', on));
if (RENDER) document.body.classList.add('render');
if (CLEAN) { document.body.classList.add('clean'); flowGroup.visible = false; }
setView(qs.get('view') || 'overview');

const clock = new THREE.Clock();
function loop() {
  const dt = clock.getDelta();
  if (!RENDER) updDrops(dt);
  controls.update(); renderer.render(scene, camera); updLabels();
  requestAnimationFrame(loop);
}
loop();
window.renderOnce = () => { controls.update(); renderer.render(scene, camera); updLabels(); };
addEventListener('resize', () => { camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); renderer.setSize(innerWidth, innerHeight); });
