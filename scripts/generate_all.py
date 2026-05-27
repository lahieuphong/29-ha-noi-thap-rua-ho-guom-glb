from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from glb_forge import generate_site, iter_sites


def main() -> None:
    output_dir = PROJECT_ROOT / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    for site in iter_sites():
        result = generate_site(site, output_dir)

        print(f"Generated file: {result.path}")
        print(f"{site.registry_key} vertices: {result.vertex_count:,}")
        print(f"{site.registry_key} materials: {result.material_count:,}")


if __name__ == "__main__":
    main()
