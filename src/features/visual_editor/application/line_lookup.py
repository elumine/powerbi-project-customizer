from __future__ import annotations

import json


def line_for_json_path(text: str, path: list[str | int]) -> int:
    if not path:
        return 1

    flat_key = ".".join(f"[{part}]" if isinstance(part, int) else str(part) for part in path)
    encoded_flat_key = json.dumps(flat_key, ensure_ascii=False)
    for line_number, line in enumerate(text.splitlines(), start=1):
        if encoded_flat_key in line and ":" in line:
            return line_number

    key_candidates = [part for part in reversed(path) if isinstance(part, str)]
    if not key_candidates:
        return 0

    leaf_key = key_candidates[0]
    encoded_key = json.dumps(leaf_key, ensure_ascii=False)
    for line_number, line in enumerate(text.splitlines(), start=1):
        if encoded_key in line and ":" in line:
            return line_number
    return 0

