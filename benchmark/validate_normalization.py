"""Validate standalone normalizationOutput per normalization-protocol/ docs.

Not part of validate_schema.py — diplomatic transcription validation is unchanged.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, List, Tuple

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

# Supported add-on protocol versions (normalization-protocol/NORMALIZATION_PROTOCOL.md)
VALID_NORMALIZATION_PROTOCOL_VERSIONS = ("norm-1.0.0", "norm-1.1.0")

# norm-1.0.0 policy keys (no editorialLevel)
REQUIRED_POLICY_KEYS_LEGACY = (
    "orthographyTarget",
    "abbreviationHandling",
    "lineBreakHandling",
    "registerNotes",
)

# norm-1.1.0+ adds required editorialLevel (see NORMALIZATION_PROTOCOL §2)
REQUIRED_POLICY_KEYS_V11 = ("editorialLevel",) + REQUIRED_POLICY_KEYS_LEGACY

VALID_EDITORIAL_LEVELS = (
    "mechanical",
    "conservative_editorial",
    "scholarly_editorial",
)

VALID_LINE_BREAK_HANDLING = ("preserve", "reflow_to_spaces", "other")


def _req(d: Dict[str, Any], key: str, errors: List[str]) -> Any:
    if key not in d:
        errors.append(f"missing required field: {key}")
        return None
    return d[key]


def validate_normalization_output(
    root: Dict[str, Any],
    diplomatic_segments_by_id: Dict[int, str] | None = None,
) -> Tuple[bool, List[str]]:
    """Validate a normalizationOutput dict.

    If *diplomatic_segments_by_id* is provided (segmentId -> exact segment text),
    each normalizedSegments[].diplomaticText must match.
    """
    errors: List[str] = []

    nv = root.get("normalizationProtocolVersion")
    if nv not in VALID_NORMALIZATION_PROTOCOL_VERSIONS:
        errors.append(
            f"normalizationProtocolVersion must be one of {VALID_NORMALIZATION_PROTOCOL_VERSIONS}, "
            f"got {nv!r}"
        )

    src = root.get("source")
    if not isinstance(src, dict):
        errors.append("source must be an object")
    else:
        _req(src, "sourcePageId", errors)
        _req(src, "sourceProtocolVersion", errors)

    pol = root.get("normalizationPolicy")
    if not isinstance(pol, dict):
        errors.append("normalizationPolicy must be an object")
    else:
        policy_keys = (
            REQUIRED_POLICY_KEYS_V11
            if nv == "norm-1.1.0"
            else REQUIRED_POLICY_KEYS_LEGACY
        )
        for k in policy_keys:
            _req(pol, k, errors)
        el = pol.get("editorialLevel")
        if el is not None and el not in VALID_EDITORIAL_LEVELS:
            errors.append(
                f"normalizationPolicy.editorialLevel must be one of {VALID_EDITORIAL_LEVELS}, "
                f"got {el!r}"
            )
        lb = pol.get("lineBreakHandling")
        if lb is not None and lb not in VALID_LINE_BREAK_HANDLING:
            errors.append(
                f"normalizationPolicy.lineBreakHandling must be one of {VALID_LINE_BREAK_HANDLING}, "
                f"got {lb!r}"
            )

    meta = root.get("metadata")
    if not isinstance(meta, dict):
        errors.append("metadata must be an object")
    else:
        _req(meta, "modelId", errors)
        _req(meta, "timestamp", errors)
        _req(meta, "notes", errors)

    nsegs = root.get("normalizedSegments")
    if not isinstance(nsegs, list) or len(nsegs) == 0:
        errors.append("normalizedSegments must be a non-empty list")
    else:
        seen_ids: set[int] = set()
        for i, row in enumerate(nsegs):
            if not isinstance(row, dict):
                errors.append(f"normalizedSegments[{i}] must be an object")
                continue
            sid = row.get("segmentId")
            if sid is None or not isinstance(sid, int):
                errors.append(f"normalizedSegments[{i}].segmentId must be an integer")
            else:
                if sid in seen_ids:
                    errors.append(f"duplicate segmentId {sid} in normalizedSegments")
                seen_ids.add(sid)
            _req(row, "diplomaticText", errors)
            _req(row, "normalizedText", errors)
            _req(row, "alignmentNotes", errors)

            if (
                diplomatic_segments_by_id is not None
                and isinstance(sid, int)
                and sid in diplomatic_segments_by_id
            ):
                dt = row.get("diplomaticText")
                expected = diplomatic_segments_by_id[sid]
                if isinstance(dt, str) and dt != expected:
                    errors.append(
                        f"normalizedSegments segmentId {sid}: diplomaticText must exactly "
                        f"match diplomatic segment text"
                    )

    ok = len(errors) == 0
    return ok, errors


def _load_yaml_or_json(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    if path.endswith(".json"):
        return json.loads(raw)
    if yaml is None:
        raise RuntimeError("PyYAML is required for .yaml files: pip install pyyaml")
    return yaml.safe_load(raw)


def _extract_transcription_output(data: Any) -> Dict[str, Any] | None:
    if not isinstance(data, dict):
        return None
    if "transcriptionOutput" in data:
        inner = data["transcriptionOutput"]
        return inner if isinstance(inner, dict) else None
    return data if "segments" in data else None


def _extract_normalization_output(data: Any) -> Dict[str, Any] | None:
    if not isinstance(data, dict):
        return None
    if "normalizationOutput" in data:
        inner = data["normalizationOutput"]
        return inner if isinstance(inner, dict) else None
    return data if "normalizationProtocolVersion" in data else None


def _segments_by_id(trans_root: Dict[str, Any]) -> Dict[int, str]:
    out: Dict[int, str] = {}
    segs = trans_root.get("segments")
    if not isinstance(segs, list):
        return out
    for seg in segs:
        if not isinstance(seg, dict):
            continue
        sid = seg.get("segmentId")
        text = seg.get("text")
        if isinstance(sid, int) and isinstance(text, str):
            out[sid] = text
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate normalizationOutput YAML/JSON (add-on protocol)."
    )
    parser.add_argument(
        "normalization_file",
        help="Path to file containing normalizationOutput",
    )
    parser.add_argument(
        "--transcript",
        metavar="PATH",
        help="Optional diplomatic transcript file to cross-check diplomaticText",
    )
    args = parser.parse_args()

    data = _load_yaml_or_json(args.normalization_file)
    norm_root = _extract_normalization_output(data)
    if norm_root is None:
        print("Could not find normalizationOutput in file", file=sys.stderr)
        return 2

    diplomatic_map: Dict[int, str] | None = None
    if args.transcript:
        tdata = _load_yaml_or_json(args.transcript)
        tout = _extract_transcription_output(tdata)
        if tout is None:
            print("Could not find transcriptionOutput in transcript file", file=sys.stderr)
            return 2
        diplomatic_map = _segments_by_id(tout)

    ok, errs = validate_normalization_output(norm_root, diplomatic_map)
    if not ok:
        for e in errs:
            print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
