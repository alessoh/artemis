/* Hero illustration: a rock-salt crystal lit like daylight.
   Built with Three.js; bundled by scripts/build_site.py into public/assets/lattice.js.
   Pauses when off screen, respects reduced motion, and can be turned by dragging. */
import {
  ACESFilmicToneMapping, Color, CylinderGeometry, DirectionalLight, Fog, Group, InstancedMesh, Matrix4,
  MeshStandardMaterial, PMREMGenerator, PerspectiveCamera, Quaternion, SRGBColorSpace, Scene, SphereGeometry,
  Vector3, WebGLRenderer,
} from "three";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

const host = document.getElementById("lattice");
const fallback = document.getElementById("lattice-fallback");

function supportsWebGL() {
  try {
    const c = document.createElement("canvas");
    return !!(window.WebGLRenderingContext && (c.getContext("webgl2") || c.getContext("webgl")));
  } catch (_) { return false; }
}

if (host && supportsWebGL()) {
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const renderer = new WebGLRenderer({ antialias: true, alpha: true, powerPreference: "low-power" });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setClearColor(0x000000, 0);
  renderer.toneMapping = ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.outputColorSpace = SRGBColorSpace;
  host.appendChild(renderer.domElement);
  renderer.domElement.setAttribute("aria-hidden", "true");

  const scene = new Scene();
  const camera = new PerspectiveCamera(32, 1, 0.1, 100);
  camera.position.set(0, 0.4, 15.5);

  // Soft studio reflections plus one warm "sun" from the upper left.
  const pmrem = new PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  pmrem.dispose();
  const sun = new DirectionalLight(0xfff0d4, 1.6);
  sun.position.set(-6, 9, 7);
  scene.add(sun);
  // Back layers fade toward the page color, which gives depth.
  scene.fog = new Fog(0xf4f6f9, 14.5, 26);

  const crystal = new Group();
  scene.add(crystal);

  const N = 3;                // atoms per edge
  const a = 2.0;              // spacing
  const offset = ((N - 1) * a) / 2;
  const positions = [];
  for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) for (let k = 0; k < N; k++) {
    positions.push({ p: new Vector3(i * a - offset, j * a - offset, k * a - offset), metal: (i + j + k) % 2 === 0 });
  }

  const metals = positions.filter((x) => x.metal);
  const anions = positions.filter((x) => !x.metal);
  const sphere = new SphereGeometry(1, 40, 28);
  const metalMesh = new InstancedMesh(sphere, new MeshStandardMaterial({ color: new Color("#2b3a6b"), roughness: 0.28, metalness: 0.15, envMapIntensity: 0.9 }), metals.length);
  const anionMesh = new InstancedMesh(sphere, new MeshStandardMaterial({ color: new Color("#cfae72"), roughness: 0.42, metalness: 0.0, envMapIntensity: 0.8 }), anions.length);
  const m = new Matrix4();
  metals.forEach((x, idx) => { m.makeScale(0.32, 0.32, 0.32).setPosition(x.p); metalMesh.setMatrixAt(idx, m); });
  anions.forEach((x, idx) => { m.makeScale(0.44, 0.44, 0.44).setPosition(x.p); anionMesh.setMatrixAt(idx, m); });
  crystal.add(metalMesh, anionMesh);

  // Bonds between nearest neighbours.
  const bonds = [];
  positions.forEach((u, i) => positions.forEach((v, j) => {
    if (j <= i) return;
    if (Math.abs(u.p.distanceTo(v.p) - a) < 1e-3) bonds.push([u.p, v.p]);
  }));
  const rod = new CylinderGeometry(0.045, 0.045, 1, 12);
  const bondMesh = new InstancedMesh(rod, new MeshStandardMaterial({ color: new Color("#9fa9bb"), roughness: 0.55, metalness: 0.1 }), bonds.length);
  const up = new Vector3(0, 1, 0), q = new Quaternion(), dir = new Vector3(), mid = new Vector3(), scale = new Vector3();
  bonds.forEach(([u, v], idx) => {
    dir.subVectors(v, u);
    const len = dir.length();
    q.setFromUnitVectors(up, dir.normalize());
    mid.addVectors(u, v).multiplyScalar(0.5);
    scale.set(1, len, 1);
    m.compose(mid, q, scale);
    bondMesh.setMatrixAt(idx, m);
  });
  crystal.add(bondMesh);
  crystal.rotation.set(0.42, -0.62, 0);

  function resize() {
    const w = host.clientWidth || 400, h = host.clientHeight || 400;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  resize();
  window.addEventListener("resize", resize);

  // Drag to turn the crystal.
  let dragging = false, lastX = 0, lastY = 0, velY = reduceMotion ? 0 : 0.0021, velX = 0;
  const el = renderer.domElement;
  el.style.touchAction = "pan-y";
  el.style.cursor = "grab";
  el.addEventListener("pointerdown", (e) => { dragging = true; lastX = e.clientX; lastY = e.clientY; el.style.cursor = "grabbing"; el.setPointerCapture(e.pointerId); });
  el.addEventListener("pointermove", (e) => {
    if (!dragging) return;
    const dx = e.clientX - lastX, dy = e.clientY - lastY;
    lastX = e.clientX; lastY = e.clientY;
    crystal.rotation.y += dx * 0.008;
    crystal.rotation.x = Math.max(-1.1, Math.min(1.1, crystal.rotation.x + dy * 0.006));
    velY = dx * 0.0006; velX = dy * 0.0004;
    if (!running) renderer.render(scene, camera);
  });
  const release = () => { dragging = false; el.style.cursor = "grab"; };
  el.addEventListener("pointerup", release);
  el.addEventListener("pointercancel", release);

  let running = false, visible = true, frame = 0;
  const base = reduceMotion ? 0 : 0.0021;
  function tick() {
    if (!running) return;
    if (!dragging) {
      crystal.rotation.y += velY;
      crystal.rotation.x += velX;
      velY += (base - velY) * 0.02;
      velX *= 0.95;
    }
    renderer.render(scene, camera);
    frame = requestAnimationFrame(tick);
  }
  function setRunning(on) {
    if (on === running) return;
    running = on;
    if (on) frame = requestAnimationFrame(tick); else cancelAnimationFrame(frame);
  }
  renderer.render(scene, camera);
  if (fallback) fallback.hidden = true;

  if (!reduceMotion) {
    if ("IntersectionObserver" in window) {
      new IntersectionObserver((entries) => { visible = entries[0].isIntersecting; setRunning(visible && !document.hidden); }).observe(host);
    }
    document.addEventListener("visibilitychange", () => setRunning(visible && !document.hidden));
    setRunning(true);
  } else {
    // Still allow dragging with reduced motion, rendering only on demand.
    el.addEventListener("pointermove", () => { if (dragging) renderer.render(scene, camera); });
  }
}
