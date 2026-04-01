"""Check well-formedness of a lines / PageXML file (optional helper for external line tools).

Does not validate the full PAGE XML XSD — only parses XML and reports common line-related
element counts (namespace-agnostic). For protocol transcription YAML, use validate_schema.py.
"""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from typing import List, Tuple


def _count_by_local_name(root: ET.Element, local: str) -> int:
    """Count elements whose tag local name is ``local`` (strip ``{namespace}``)."""
    n = 0
    for el in root.iter():
        tag = el.tag
        if tag.startswith("{"):
            tag = tag.split("}", 1)[-1]
        if tag == local:
            n += 1
    return n


def validate_lines_xml(
    path: str, *, require_text_line: bool
) -> Tuple[bool, List[str], dict]:
    """Parse XML and collect stats. Returns (ok, messages, stats)."""
    msgs: List[str] = []
    stats: dict = {}
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        return False, [f"XML parse error: {e}"], {}
    except OSError as e:
        return False, [f"could not read file: {e}"], {}

    root = tree.getroot()
    stats["text_line"] = _count_by_local_name(root, "TextLine")
    stats["text_region"] = _count_by_local_name(root, "TextRegion")
    stats["line"] = _count_by_local_name(root, "Line")

    ok = True
    if stats["text_line"] == 0 and stats["line"] == 0:
        msgs.append(
            "warning: no TextLine or Line elements found "
            "(file is well-formed XML but may not be PAGE XML / lines export)"
        )
    if require_text_line and stats["text_line"] == 0:
        ok = False
        msgs.append("error: --require-text-line set but no TextLine elements found")

    return ok, msgs, stats


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Check XML well-formedness and count PAGE-style TextLine elements "
        "(optional helper; not a substitute for validate_schema.py on YAML transcripts)."
    )
    ap.add_argument("xml_file", help="Path to XML / PageXML lines file")
    ap.add_argument(
        "--require-text-line",
        action="store_true",
        help="Fail if no TextLine elements are present (stricter PageXML check)",
    )
    args = ap.parse_args()

    ok, msgs, stats = validate_lines_xml(args.xml_file, require_text_line=args.require_text_line)
    for m in msgs:
        print(m, file=sys.stderr)
    if stats:
        print(
            "text_line={text_line} text_region={text_region} line={line}".format(**stats)
        )
    if not ok:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
