from __future__ import annotations

import sys
from pathlib import Path

# Cho phép chạy file này trực tiếp mà không cần cài package.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from glb_forge import generate_site, get_site


SITE_KEY = "29-ha-noi/thap-rua-ho-guom"


def main() -> None:
    site = get_site(SITE_KEY)
    result = generate_site(site, PROJECT_ROOT / "output")

    print(f"Đã tạo: {result.path}")
    print(f"Site: {site.registry_key}")
    print(f"Vertices: {result.vertex_count:,}")
    print(f"Materials: {result.material_count:,}")


if __name__ == "__main__":
    main()
