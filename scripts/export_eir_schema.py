from __future__ import annotations

import argparse
import json
from pathlib import Path

from mirage.eir.schema import EIRDocument


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = Path("specs/EIR/eir-0.1.schema.json")
    payload = EIRDocument.model_json_schema()
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.check:
        return 0 if output.exists() and output.read_text(encoding="utf-8") == rendered else 1
    output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
