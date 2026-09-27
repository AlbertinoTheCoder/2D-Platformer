"""Read project descriptors on disk without starting Unreal or contacting MCP."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    projects = []
    for path in sorted(args.root.rglob("*.uproject")):
        descriptor = json.loads(path.read_text(encoding="utf-8-sig"))
        projects.append({"path": str(path.resolve()),
                         "engine_association": descriptor.get("EngineAssociation"),
                         "modules": descriptor.get("Modules", []),
                         "plugins": descriptor.get("Plugins", []),
                         "has_source": (path.parent / "Source").is_dir(),
                         "has_content": (path.parent / "Content").is_dir()})
    print(json.dumps({"projects": projects, "connected_to_unreal": False}, indent=2))


if __name__ == "__main__":
    main()
