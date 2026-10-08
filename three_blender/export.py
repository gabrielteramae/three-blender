from __future__ import annotations

import json
from pathlib import Path

KINDS = {"box", "sphere", "cylinder", "cone"}


def load_scene(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return validate_scene(data)


def validate_scene(data: dict) -> dict:
    if not isinstance(data, dict):
        raise ValueError("a cena precisa ser um objeto JSON")
    objects = data.get("objects")
    if not isinstance(objects, list) or not objects:
        raise ValueError("a cena precisa de uma lista objects")
    clean = []
    for index, obj in enumerate(objects):
        kind = obj.get("type")
        if kind not in KINDS:
            raise ValueError(f"objeto {index}: tipo {kind!r} não suportado")
        name = str(obj.get("name") or f"{kind}-{index + 1}")
        color = str(obj.get("color") or "#e3a15a")
        if not color.startswith("#") or len(color) not in (4, 7):
            raise ValueError(f"objeto {name}: cor inválida")
        position = _vec(obj.get("position"), (0, 0.5, 0), name)
        scale = _vec(obj.get("scale"), (1, 1, 1), name)
        clean.append(
            {
                "type": kind,
                "name": name,
                "color": color,
                "position": position,
                "scale": scale,
            }
        )
    camera = data.get("camera") or {}
    return {
        "name": str(data.get("name") or "cena"),
        "camera": {
            "position": _vec(camera.get("position"), (4.2, 2.4, 5.4), "camera"),
            "target": _vec(camera.get("target"), (0, 0.6, 0), "camera"),
        },
        "objects": clean,
    }


def _vec(value, default, label: str) -> list[float]:
    if value is None:
        return [float(n) for n in default]
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError(f"{label}: vetor precisa ter 3 números")
    return [float(n) for n in value]


def export_site(scene: dict, out_dir: str | Path) -> Path:
    scene = validate_scene(scene)
    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)
    (target / "scene.json").write_text(json.dumps(scene, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (target / "index.html").write_text(_html(scene["name"]), encoding="utf-8")
    return target


def _esc(title: str) -> str:
    return (
        title.replace("&", "\u0026amp;")
        .replace("<", "\u0026lt;")
        .replace(">", "\u0026gt;")
        .replace('"', "\u0026quot;")
    )


def _html(title: str) -> str:
    safe = _esc(title)
    return f"""<!doctype html>
<html lang="pt">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{safe}</title>
  <style>
    html, body {{ margin: 0; height: 100%; background: #0c0d10; color: #f4f0e8; font-family: sans-serif; }}
    canvas {{ width: 100%; height: 100%; display: block; touch-action: none; }}
  </style>
  <script type="importmap">
    {{ "imports": {{ "three": "https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js" }} }}
  </script>
</head>
<body>
  <canvas id="view"></canvas>
  <script type="module" src="./viewer.js"></script>
</body>
</html>
"""


VIEWER_JS = r"""import * as THREE from "three";

const canvas = document.querySelector("#view");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
const scene = new THREE.Scene();
scene.background = new THREE.Color("#0c0d10");
const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
scene.add(new THREE.AmbientLight("#f4f0e8", 0.55));
const sun = new THREE.DirectionalLight("#f4f0e8", 1.4);
sun.position.set(4, 8, 3);
scene.add(sun);
scene.add(new THREE.GridHelper(10, 10, "#3a342c", "#241f1a"));

const response = await fetch("./scene.json");
const data = await response.json();
const target = new THREE.Vector3(...data.camera.target);
camera.position.set(...data.camera.position);
camera.lookAt(target);

const geo = {
  box: () => new THREE.BoxGeometry(1, 1, 1),
  sphere: () => new THREE.SphereGeometry(0.5, 32, 24),
  cylinder: () => new THREE.CylinderGeometry(0.5, 0.5, 1, 28),
  cone: () => new THREE.ConeGeometry(0.5, 1, 28),
};
for (const obj of data.objects) {
  const mesh = new THREE.Mesh(
    geo[obj.type](),
    new THREE.MeshStandardMaterial({ color: obj.color, roughness: 0.55 }),
  );
  mesh.position.set(...obj.position);
  mesh.scale.set(...obj.scale);
  mesh.name = obj.name;
  scene.add(mesh);
}

let theta = 0.8;
let phi = 1.05;
let radius = camera.position.distanceTo(target);
function apply() {
  const sp = Math.sin(phi);
  camera.position.set(
    target.x + radius * sp * Math.sin(theta),
    target.y + radius * Math.cos(phi),
    target.z + radius * sp * Math.cos(theta),
  );
  camera.lookAt(target);
}
apply();

const pointers = new Map();
canvas.addEventListener("pointerdown", (event) => {
  canvas.setPointerCapture(event.pointerId);
  pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
});
canvas.addEventListener("pointerup", (event) => pointers.delete(event.pointerId));
canvas.addEventListener("pointercancel", (event) => pointers.delete(event.pointerId));
canvas.addEventListener("pointermove", (event) => {
  const prev = pointers.get(event.pointerId);
  if (!prev) return;
  const dx = event.clientX - prev.x;
  const dy = event.clientY - prev.y;
  prev.x = event.clientX;
  prev.y = event.clientY;
  if (event.shiftKey || pointers.size > 1) return;
  theta -= dx * 0.008;
  phi = Math.min(Math.PI - 0.08, Math.max(0.08, phi + dy * 0.008));
  apply();
});
canvas.addEventListener("wheel", (event) => {
  event.preventDefault();
  radius = Math.min(40, Math.max(1.2, radius * Math.exp(event.deltaY * 0.001)));
  apply();
}, { passive: false });

function frame() {
  const w = canvas.clientWidth || 1;
  const h = canvas.clientHeight || 1;
  if (canvas.width !== Math.floor(w * renderer.getPixelRatio()) || canvas.height !== Math.floor(h * renderer.getPixelRatio())) {
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  renderer.render(scene, camera);
  requestAnimationFrame(frame);
}
frame();
"""


def write_viewer(out_dir: str | Path) -> None:
    Path(out_dir, "viewer.js").write_text(VIEWER_JS, encoding="utf-8")
