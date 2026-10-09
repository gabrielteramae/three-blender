import json
import tempfile
import unittest
from pathlib import Path

from three_blender.export import export_site, load_scene, validate_scene, write_viewer


ROOT = Path(__file__).resolve().parents[1]


class ExportTests(unittest.TestCase):
    def test_example_scene(self):
        scene = load_scene(ROOT / "examples" / "studio.json")
        self.assertEqual(len(scene["objects"]), 4)
        self.assertEqual(scene["objects"][2]["name"], "lampada")

    def test_rejects_non_positive_scale(self):
        with self.assertRaises(ValueError):
            validate_scene({"objects": [{"type": "box", "scale": [1, 0, 1]}]})

    def test_viewer_pinches(self):
        scene = load_scene(ROOT / "examples" / "studio.json")
        with tempfile.TemporaryDirectory() as tmp:
            out = export_site(scene, tmp)
            write_viewer(out)
            source = (out / "viewer.js").read_text(encoding="utf-8")
            self.assertIn("pinchDist", source)

    def test_rejects_unknown_type(self):
        with self.assertRaises(ValueError):
            validate_scene({"objects": [{"type": "torus", "name": "x"}]})

    def test_writes_site(self):
        scene = load_scene(ROOT / "examples" / "studio.json")
        with tempfile.TemporaryDirectory() as tmp:
            out = export_site(scene, tmp)
            write_viewer(out)
            html = (out / "index.html").read_text(encoding="utf-8")
            payload = json.loads((out / "scene.json").read_text(encoding="utf-8"))
            self.assertIn("viewer.js", html)
            self.assertIn("Estúdio", html)
            self.assertTrue((out / "viewer.js").exists())
            self.assertEqual(payload["objects"][0]["type"], "box")


if __name__ == "__main__":
    unittest.main()
