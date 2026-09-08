"""Backward-compatible import facade for document flattening utilities."""

from entities.document.flattening import (
    FlatJsonCollisionError,
    flatten_json,
    flatten_json_text,
    unflatten_json,
    unflatten_json_text,
)

__all__ = [
    "FlatJsonCollisionError",
    "flatten_json",
    "flatten_json_text",
    "unflatten_json",
    "unflatten_json_text",
]
