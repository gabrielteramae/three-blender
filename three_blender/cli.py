import argparse
import sys
from pathlib import Path

from three_blender.export import export_site, load_scene, write_viewer


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera um site interativo a partir de scene.json")
    parser.add_argument("scene", help="arquivo JSON da cena")
    parser.add_argument("-o", "--out", default="site", help="pasta de saída")
    args = parser.parse_args()
    scene = load_scene(args.scene)
    out = export_site(scene, args.out)
    write_viewer(out)
    print(f"site em {Path(out).resolve()}")
    print("abra com: python -m http.server -d", out)


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
