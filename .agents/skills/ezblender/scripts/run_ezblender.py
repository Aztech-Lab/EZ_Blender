#!/usr/bin/env python3
"""Launch EZBlender main.py with a named asset preset."""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

PRESETS = {
    "body": {
        "scene": "blenderalch/starter_blends/body_shapekeys.blend",
        "init": "blenderalch/blender_scripts/shapekeys_examples/bodyshape.py",
        "render": "blenderalch/blender_base/bodyshape_shapekeys.py",
    },
    "face": {
        "scene": "blenderalch/starter_blends/face_animation.blend",
        "init": "blenderalch/blender_scripts/shapekeys_examples/facialshapekeys.py",
        "render": "blenderalch/blender_base/bodyshape_shapekeys.py",
    },
    "wineglass": {
        "scene": "blenderalch/starter_blends/wineglass_shapekeys.blend",
        "init": "blenderalch/blender_scripts/shapekeys_examples/wineglass.py",
        "render": "blenderalch/blender_base/bodyshape_shapekeys.py",
    },
    "lotion": {
        "scene": "blenderalch/starter_blends/lotion.blend",
        "init": "blenderalch/blender_scripts/lighting_examples/lotion.py",
        "render": "blenderalch/blender_base/lighting_adjustments.py",
    },
    "wood": {
        "scene": "blenderalch/starter_blends/BSDF_experiments.blend",
        "init": "blenderalch/blender_scripts/material_examples/infinigen_wood_example.py",
        "render": "blenderalch/blender_base/infinigen_render_materials.py",
    },
    "roses": {
        "scene": "blenderalch/starter_blends/roses.blend",
        "init": "blenderalch/blender_scripts/geonodes_example/roses.py",
        "render": "blenderalch/blender_base/geonodes.py",
    },
}


def _is_package(path: Path) -> bool:
    return (
        (path / "main.py").is_file()
        and (path / "ezblender").is_dir()
        and (path / "blenderalch").is_dir()
    )


def package_root() -> Path:
    """Find EZBlender package whether skill lives under .agents or monorepo .grok."""
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        monorepo = parent / "github" / "EZBlender"
        if _is_package(monorepo):
            return monorepo
        if _is_package(parent):
            return parent
    raise SystemExit(f"Cannot locate EZBlender package from {here}")


def slugify(text: str, max_len: int = 40) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()
    return s[:max_len] or "run"


def main() -> int:
    parser = argparse.ArgumentParser(description="EZBlender preset launcher")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--preset", choices=sorted(PRESETS), default="lotion")
    parser.add_argument("--blender_exe", default="blender")
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--out_dir", default="")
    parser.add_argument("--no_parallel", action="store_true")
    args = parser.parse_args()

    root = package_root()
    preset = PRESETS[args.preset]
    out_dir = args.out_dir or str(Path("output") / f"{args.preset}_{slugify(args.prompt)}")
    if not Path(out_dir).is_absolute():
        out_dir = str(root / out_dir)

    cmd = [
        sys.executable,
        str(root / "main.py"),
        "--prompt",
        args.prompt,
        "--blender_exe",
        args.blender_exe,
        "--scene_blend",
        preset["scene"],
        "--init_script",
        preset["init"],
        "--render_script",
        preset["render"],
        "--model",
        args.model,
        "--out_dir",
        out_dir,
    ]
    if not args.no_parallel:
        cmd.append("--parallel")

    print(f"[ezblender] root={root}")
    print(f"[ezblender] preset={args.preset} out={out_dir}")
    print(f"[ezblender] {' '.join(cmd)}")
    return subprocess.call(cmd, cwd=str(root))


if __name__ == "__main__":
    raise SystemExit(main())
