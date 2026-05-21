from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = ROOT / "family_tree_src"
DATA_PATH = SRC_ROOT / "data" / "tree.json"
OUTPUT_PATH = ROOT / "family-tree" / "index.html"

sys.path.insert(0, str(SRC_ROOT))

from family_tree.export_html import export_html
from family_tree.storage import load, validate_data, raw_data


def build(data_path: Path = DATA_PATH, output_path: Path = OUTPUT_PATH) -> Path:
    tree = load(data_path)
    return export_html(tree, output_path)


def validate(data_path: Path = DATA_PATH) -> None:
    validate_data(raw_data(data_path))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and build the website family tree page."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    build_parser = sub.add_parser("build", help="Validate data and generate the public page")
    build_parser.add_argument("--data", default=str(DATA_PATH), help="Source JSON path")
    build_parser.add_argument("--output", default=str(OUTPUT_PATH), help="Output HTML path")

    validate_parser = sub.add_parser("validate", help="Validate the source JSON only")
    validate_parser.add_argument("--data", default=str(DATA_PATH), help="Source JSON path")

    args = parser.parse_args()

    if args.command == "build":
        output = build(Path(args.data), Path(args.output))
        print(f"Wrote {output}")
        return 0

    if args.command == "validate":
        validate(Path(args.data))
        print(f"Validated {Path(args.data)}")
        return 0

    raise AssertionError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
