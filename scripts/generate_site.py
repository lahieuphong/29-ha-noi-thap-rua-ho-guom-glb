from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from glb_forge import generate_site, get_site


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate one heritage site GLB by registry key.")
    parser.add_argument("site_key", help="Dạng key: 29-ha-noi/thap-rua-ho-guom")
    args = parser.parse_args()

    site = get_site(args.site_key)
    result = generate_site(site, PROJECT_ROOT / "output")

    print(f"Generated file: {result.path}")
    print(f"{site.registry_key} vertices: {result.vertex_count:,}")
    print(f"{site.registry_key} materials: {result.material_count:,}")


if __name__ == "__main__":
    main()
