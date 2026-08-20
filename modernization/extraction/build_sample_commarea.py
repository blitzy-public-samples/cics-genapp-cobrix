#!/usr/bin/env python3
"""Build one executable GenApp Policy-Issue COMMAREA record from a sample definition.

WHAT THIS TOOL DOES
    Reads a flat JSON sample definition, validates it against the
    ``sample_definition_contract`` recorded in ``copybook_field_map.yml``, and writes a
    single fixed-width record of exactly 32,500 characters followed by one newline.

WHICH INPUTS IT ACCEPTS
    --sample     one sample definition JSON document, keyed by COMMAREA item name.
    --field-map  the field map supplying every offset, length and kind
                 (default: ``copybook_field_map.yml`` beside this script).
    --output     destination path for the generated record.

HOW FIELDS ARE PLACED
    The buffer starts as spaces at the length declared by ``record.length``. Placement
    covers the base ``layout`` groups plus the one overlay group that
    ``request_routing`` selects for the sample's request id. Items carrying a
    ``redefined_by`` list are not placed; the items that redefine them are placed
    instead. A ``numeric_display`` window receives the supplied value right-justified
    and zero-padded, and all zeros when the sample omits the item. An ``alphanumeric``
    window receives the supplied value left-justified and space-padded, and stays
    spaces when the sample omits the item. The record is always emitted at the full
    declared length of 32,500 characters.

HOW IT FAILS
    Every failure writes one diagnostic line to stderr and returns a non-zero status:
    2 for a rejected sample definition, 3 for an internally inconsistent field map,
    4 for an unreadable input or an unwritable output. The tool never prompts and
    requires no TTY. On success it writes one summary line to stdout.

Decision rationale for this component: modernization/docs/decision-log.md
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import sys
import tempfile
from collections.abc import Iterable
from pathlib import Path
from typing import Any, NamedTuple

import yaml

_PROGRAM = "build_sample_commarea"

# Field map used when --field-map is omitted, resolved from this script's own directory.
_THIS_DIR = Path(__file__).resolve().parent
DEFAULT_FIELD_MAP = _THIS_DIR / "copybook_field_map.yml"

EXIT_OK = 0
EXIT_SAMPLE_REJECTED = 2
EXIT_FIELD_MAP_INVALID = 3
EXIT_IO_ERROR = 4

# Item kinds recorded by the field map's layout entries.
KIND_NUMERIC = "numeric_display"
KIND_ALPHANUMERIC = "alphanumeric"

# Runtime statuses recorded by the field map's logical field entries.
POPULATED_BY_REQUEST = "request"
POPULATED_BY_CHAIN = "chain"

# Justification values recorded by sample_definition_contract.value_justification.
JUSTIFY_LEFT = "left"
JUSTIFY_RIGHT = "right"

# Character classes permitted in a supplied value, matched with fullmatch: ASCII digits
# 0-9 for a numeric item, printable 7-bit ASCII for an alphanumeric item.
_ASCII_DIGITS = re.compile(r"[0-9]*")
_PRINTABLE_ASCII = re.compile(r"[\x20-\x7E]*")


class BuildError(Exception):
    """Diagnostic raised by this module, carrying the process status to return."""

    exit_status = EXIT_SAMPLE_REJECTED


class SampleError(BuildError):
    """The sample definition breaches the sample definition contract."""

    exit_status = EXIT_SAMPLE_REJECTED


class FieldMapError(BuildError):
    """The field map is missing a required section or is internally inconsistent."""

    exit_status = EXIT_FIELD_MAP_INVALID


class InputOutputError(BuildError):
    """Raised when an input cannot be read or the output cannot be written."""

    exit_status = EXIT_IO_ERROR


class Routing(NamedTuple):
    """Request routing resolved for one sample definition."""

    request_id: str
    policy_type: str
    overlay: str


class Window(NamedTuple):
    """One placeable byte window taken from a field map layout entry."""

    item: str
    group: str
    offset: int
    length: int
    kind: str

    @property
    def end_byte(self) -> int:
        """Return the 1-based position of the window's last character."""
        return self.offset + self.length - 1


def _type_name(value: Any) -> str:
    """Return the type name of ``value`` for use inside a diagnostic."""
    return type(value).__name__


def _quote_all(names: Iterable[str]) -> str:
    """Return ``names`` sorted, quoted and comma separated."""
    return ", ".join(f"'{name}'" for name in sorted(names))


def _section(container: dict[str, Any], key: str, where: str) -> Any:
    """Return ``container[key]``, or raise ``FieldMapError`` naming what is missing."""
    if key not in container:
        raise FieldMapError(f"{where}: required section '{key}' is missing")
    return container[key]


def _mapping_section(container: dict[str, Any], key: str, where: str) -> dict[str, Any]:
    """Return a mapping section of the field map."""
    value = _section(container, key, where)
    if not isinstance(value, dict):
        raise FieldMapError(
            f"{where}: section '{key}' must be a mapping, found {_type_name(value)}"
        )
    return value


def _sequence_section(container: dict[str, Any], key: str, where: str) -> list[Any]:
    """Return a sequence section of the field map."""
    value = _section(container, key, where)
    if not isinstance(value, list):
        raise FieldMapError(
            f"{where}: section '{key}' must be a sequence, found {_type_name(value)}"
        )
    return value


def _positive_int(container: dict[str, Any], key: str, where: str) -> int:
    """Return a positive integer member of a field map mapping."""
    value = container.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise FieldMapError(
            f"{where}: '{key}' must be a positive integer, found {value!r}"
        )
    return value


def load_field_map(path: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    """Load the field map and confirm the sections this builder reads are present.

    ``path`` defaults to ``copybook_field_map.yml`` in this script's directory. The
    returned document is the parsed YAML mapping.
    """
    map_path = Path(path) if path is not None else DEFAULT_FIELD_MAP
    try:
        text = map_path.read_text(encoding="utf-8")
    except OSError as error:
        raise InputOutputError(
            f"cannot read field map '{map_path}': {error.strerror or error}"
        ) from error

    try:
        document = yaml.safe_load(text)
    except yaml.YAMLError as error:
        raise FieldMapError(
            f"field map '{map_path}' is not valid YAML: {error}"
        ) from error

    if not isinstance(document, dict):
        raise FieldMapError(
            f"field map '{map_path}' must be a mapping, found {_type_name(document)}"
        )

    where = f"field map '{map_path}'"
    record = _mapping_section(document, "record", where)
    _positive_int(record, "length", f"{where} record")

    layout = _mapping_section(document, "layout", where)
    if not layout:
        raise FieldMapError(f"{where}: section 'layout' declares no groups")
    for group_name in layout:
        group = _mapping_section(layout, group_name, f"{where} layout")
        _sequence_section(group, "items", f"{where} layout group '{group_name}'")

    routing = _mapping_section(document, "request_routing", where)
    _mapping_section(routing, "map", f"{where} request_routing")
    _sequence_section(document, "supported_request_ids", where)
    _sequence_section(document, "supported_samples", where)
    _sequence_section(document, "fields", where)
    _mapping_section(document, "sample_definition_contract", where)
    return document


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Build an object from JSON key/value pairs, rejecting a repeated key."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SampleError(f"sample definition repeats key '{key}'")
        result[key] = value
    return result


def load_sample(path: str | os.PathLike[str]) -> dict[str, str]:
    """Read one sample definition and confirm it is a flat object of string values."""
    sample_path = Path(path)
    try:
        text = sample_path.read_text(encoding="utf-8")
    except OSError as error:
        raise InputOutputError(
            f"cannot read sample definition '{sample_path}': {error.strerror or error}"
        ) from error

    try:
        document = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except json.JSONDecodeError as error:
        raise SampleError(
            f"sample definition '{sample_path}' is not valid JSON: {error.msg} "
            f"at line {error.lineno} column {error.colno}"
        ) from error

    if not isinstance(document, dict):
        raise SampleError(
            f"sample definition '{sample_path}' must be a JSON object, "
            f"found {_type_name(document)}"
        )

    for key, value in document.items():
        if not isinstance(value, str):
            raise SampleError(
                f"sample definition '{sample_path}': value for key '{key}' must be a "
                f"string, found {_type_name(value)}"
            )
    return document


def _request_id_item(field_map: dict[str, Any]) -> str:
    """Return the COMMAREA item name that request routing evaluates."""
    item = field_map["request_routing"].get("evaluated_item")
    if not isinstance(item, str) or not item:
        raise FieldMapError(
            "field map request_routing: 'evaluated_item' must be a non-empty string, "
            f"found {item!r}"
        )
    return item


def _overlay_group_names(field_map: dict[str, Any]) -> set[str]:
    """Return every layout group name that request routing selects as an overlay."""
    names: set[str] = set()
    for request_id, entry in field_map["request_routing"]["map"].items():
        if not isinstance(entry, dict):
            raise FieldMapError(
                f"field map request_routing.map entry '{request_id}' must be a "
                f"mapping, found {_type_name(entry)}"
            )
        overlay = entry.get("overlay")
        if overlay is None:
            continue
        if not isinstance(overlay, str) or not overlay:
            raise FieldMapError(
                f"field map request_routing.map entry '{request_id}': 'overlay' must "
                f"be a non-empty string or null, found {overlay!r}"
            )
        names.add(overlay)
    return names


def _supported_samples(field_map: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Return the supported sample entries keyed by request id."""
    entries: dict[str, dict[str, Any]] = {}
    for position, entry in enumerate(field_map["supported_samples"], start=1):
        if not isinstance(entry, dict):
            raise FieldMapError(
                f"field map supported_samples entry {position} must be a mapping, "
                f"found {_type_name(entry)}"
            )
        request_id = entry.get("request_id")
        if not isinstance(request_id, str) or not request_id:
            raise FieldMapError(
                f"field map supported_samples entry {position}: 'request_id' must be "
                f"a non-empty string, found {request_id!r}"
            )
        if request_id in entries:
            raise FieldMapError(
                f"field map supported_samples declares request id '{request_id}' "
                "more than once"
            )
        entries[request_id] = entry

    if not entries:
        raise FieldMapError("field map supported_samples declares no sample")

    declared = {str(one) for one in field_map["supported_request_ids"]}
    if declared != set(entries):
        raise FieldMapError(
            f"field map supported_request_ids ({_quote_all(declared)}) does not match "
            f"supported_samples ({_quote_all(entries)})"
        )
    return entries


def _group_order(layout: dict[str, Any], name: str) -> tuple[int, str]:
    """Return the sort key of a layout group, taken from its ``order`` member."""
    order = layout[name].get("order")
    if isinstance(order, bool) or not isinstance(order, int):
        raise FieldMapError(
            f"field map layout group '{name}': 'order' must be an integer, "
            f"found {order!r}"
        )
    return (order, name)


def _group_windows(layout: dict[str, Any], name: str) -> list[Window]:
    """Return the placeable windows of one layout group, in declaration order.

    An item carrying a non-empty ``redefined_by`` list is excluded; the items that
    redefine it are placed in its bytes instead.
    """
    windows: list[Window] = []
    for position, item in enumerate(layout[name]["items"], start=1):
        if not isinstance(item, dict):
            raise FieldMapError(
                f"field map layout group '{name}' item {position} must be a mapping, "
                f"found {_type_name(item)}"
            )
        declared = item.get("item")
        if not isinstance(declared, str) or not declared:
            raise FieldMapError(
                f"field map layout group '{name}' item {position}: 'item' must be a "
                f"non-empty string, found {declared!r}"
            )
        if item.get("redefined_by"):
            continue
        kind = item.get("kind")
        if kind not in (KIND_NUMERIC, KIND_ALPHANUMERIC):
            raise FieldMapError(
                f"field map layout item '{declared}': 'kind' must be "
                f"'{KIND_NUMERIC}' or '{KIND_ALPHANUMERIC}', found {kind!r}"
            )
        where = f"field map layout item '{declared}'"
        windows.append(
            Window(
                item=declared,
                group=name,
                offset=_positive_int(item, "offset", where),
                length=_positive_int(item, "length", where),
                kind=kind,
            )
        )
    return windows


def _layout_windows(field_map: dict[str, Any], routing: Routing) -> list[Window]:
    """Return the placeable windows of the base groups plus the resolved overlay.

    Groups are visited in ascending ``order``. A group named by any routing entry as an
    overlay is a base group for no request, so only the resolved overlay is added to the
    groups that carry no overlay role.
    """
    layout = field_map["layout"]
    overlays = _overlay_group_names(field_map)
    if routing.overlay not in layout:
        raise FieldMapError(f"field map layout declares no group '{routing.overlay}'")

    selected = [
        name for name in layout if name == routing.overlay or name not in overlays
    ]
    windows: list[Window] = []
    for name in sorted(selected, key=lambda group: _group_order(layout, group)):
        windows.extend(_group_windows(layout, name))
    if not windows:
        raise FieldMapError(
            f"field map layout selects no placeable item for request id "
            f"'{routing.request_id}'"
        )
    return windows


def _window_index(windows: Iterable[Window]) -> dict[str, Window]:
    """Return the windows keyed by upper-case item name for case-insensitive lookup."""
    index: dict[str, Window] = {}
    for window in windows:
        existing = index.get(window.item.upper())
        if existing is not None:
            raise FieldMapError(
                f"field map layout declares item '{window.item}' in both group "
                f"'{existing.group}' and group '{window.group}'"
            )
        index[window.item.upper()] = window
    return index


def _unselected_overlay_items(
    field_map: dict[str, Any], routing: Routing
) -> dict[str, tuple[str, str]]:
    """Return items declared only by the overlays this request does not select.

    The result maps the upper-case item name to the declared spelling and the group
    that declares it.
    """
    layout = field_map["layout"]
    selected = {window.item.upper() for window in _layout_windows(field_map, routing)}
    others: dict[str, tuple[str, str]] = {}
    for name in sorted(_overlay_group_names(field_map) - {routing.overlay}):
        if name not in layout:
            continue
        for window in _group_windows(layout, name):
            key = window.item.upper()
            if key not in selected:
                others.setdefault(key, (window.item, name))
    return others


def _sample_request_id(field_map: dict[str, Any], sample: dict[str, str]) -> str:
    """Return the request id the sample supplies for the routing-evaluated item."""
    item = _request_id_item(field_map)
    matches = [key for key in sample if key.upper() == item.upper()]
    if not matches:
        raise SampleError(f"sample definition does not supply required item '{item}'")
    if len(matches) > 1:
        raise SampleError(
            f"keys {_quote_all(matches)} all name item '{item}'; supply it once"
        )
    return sample[matches[0]]


def resolve_overlay(field_map: dict[str, Any], request_id: str) -> Routing:
    """Resolve the routing that ``request_id`` selects.

    The request id must be declared under ``supported_samples``. The overlay group and
    the policy-type letter come from ``request_routing.map`` and are cross-checked
    against the ``supported_samples`` entry and the overlay's own layout group.
    """
    supported = _supported_samples(field_map)
    if request_id not in supported:
        raise SampleError(
            f"{_request_id_item(field_map)} '{request_id}' is not a generated sample; "
            f"the supported request ids are {_quote_all(supported)}"
        )

    entry = field_map["request_routing"]["map"].get(request_id)
    if not isinstance(entry, dict):
        raise FieldMapError(
            f"field map request_routing.map has no entry for request id '{request_id}'"
        )

    overlay = entry.get("overlay")
    if not isinstance(overlay, str) or not overlay:
        raise FieldMapError(
            f"field map request_routing.map entry '{request_id}' selects no overlay "
            f"group, found {overlay!r}"
        )
    policy_type = entry.get("policy_type")
    if not isinstance(policy_type, str) or len(policy_type) != 1:
        raise FieldMapError(
            f"field map request_routing.map entry '{request_id}': 'policy_type' must "
            f"be a single character, found {policy_type!r}"
        )

    sample_entry = supported[request_id]
    for member, resolved in (("overlay", overlay), ("policy_type", policy_type)):
        stated = sample_entry.get(member)
        if stated is not None and stated != resolved:
            raise FieldMapError(
                f"field map supported_samples entry '{request_id}' states {member} "
                f"{stated!r} while request_routing.map resolves {resolved!r}"
            )

    group = _mapping_section(field_map["layout"], overlay, "field map layout")
    if group.get("policy_type") != policy_type:
        raise FieldMapError(
            f"field map layout group '{overlay}' states policy_type "
            f"{group.get('policy_type')!r} while request_routing.map resolves "
            f"{policy_type!r}"
        )
    return Routing(request_id=request_id, policy_type=policy_type, overlay=overlay)


def _logical_entries(field_map: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the logical field entries recorded under ``fields``."""
    entries: list[dict[str, Any]] = []
    for position, entry in enumerate(field_map["fields"], start=1):
        if not isinstance(entry, dict):
            raise FieldMapError(
                f"field map fields entry {position} must be a mapping, "
                f"found {_type_name(entry)}"
            )
        entries.append(entry)
    return entries


def _commarea_item(entry: dict[str, Any]) -> str | None:
    """Return the COMMAREA item a logical entry declares, or None when it has none."""
    commarea = entry.get("commarea")
    if not isinstance(commarea, dict):
        return None
    item = commarea.get("item")
    return item if isinstance(item, str) and item else None


def _items_populated_by(field_map: dict[str, Any], status: str) -> dict[str, str]:
    """Return the items whose logical entry records ``populated_by`` as ``status``."""
    items: dict[str, str] = {}
    for entry in _logical_entries(field_map):
        if entry.get("populated_by") != status:
            continue
        item = _commarea_item(entry)
        if item:
            items[item.upper()] = item
    return items


def _required_items(field_map: dict[str, Any], routing: Routing) -> dict[str, str]:
    """Return the items a sample must supply for the resolved policy type.

    An entry applies when it records ``populated_by: request`` and its
    ``applicable_policy_types`` covers the resolved policy-type letter. The keys named
    by ``sample_definition_contract.required_keys`` are added to that set.
    """
    required: dict[str, str] = {}
    for entry in _logical_entries(field_map):
        if entry.get("populated_by") != POPULATED_BY_REQUEST:
            continue
        applicable = entry.get("applicable_policy_types")
        if isinstance(applicable, list) and routing.policy_type not in applicable:
            continue
        item = _commarea_item(entry)
        if item:
            required[item.upper()] = item

    contract_keys = field_map["sample_definition_contract"].get("required_keys") or []
    for name in contract_keys:
        if isinstance(name, str) and name:
            required.setdefault(name.upper(), name)
    return required


def _check_value(window: Window, key: str, value: str) -> None:
    """Confirm one supplied value fits its window and holds permitted characters."""
    if len(value) > window.length:
        raise SampleError(
            f"value supplied under key '{key}' for item '{window.item}' is "
            f"{len(value)} characters, longer than the declared length "
            f"{window.length}"
        )
    if window.kind == KIND_NUMERIC:
        if not _ASCII_DIGITS.fullmatch(value):
            raise SampleError(
                f"value {value!r} for numeric item '{window.item}' must contain "
                "digits 0-9 only"
            )
        return
    if not _PRINTABLE_ASCII.fullmatch(value):
        offender = next(
            char for char in value if not 0x20 <= ord(char) <= 0x7E
        )
        raise SampleError(
            f"value for alphanumeric item '{window.item}' contains {offender!r} at "
            f"position {value.index(offender) + 1} (code point {ord(offender)}), "
            "outside printable 7-bit ASCII"
        )


def validate_sample(
    field_map: dict[str, Any], sample: dict[str, str], routing: Routing
) -> dict[str, str]:
    """Validate one sample definition and return its accepted values.

    Keys are matched against the field map without regard to case and the result is
    keyed by the spelling the field map declares. Raises ``SampleError`` naming the
    offending key when the sample breaches the sample definition contract, and
    ``FieldMapError`` when the map itself is inconsistent.
    """
    windows = _window_index(_layout_windows(field_map, routing))
    unselected = _unselected_overlay_items(field_map, routing)
    chain_items = _items_populated_by(field_map, POPULATED_BY_CHAIN)
    required = _required_items(field_map, routing)

    contradictory = set(required) & set(chain_items)
    if contradictory:
        raise FieldMapError(
            "field map records "
            f"{_quote_all(required[key] for key in contradictory)} as both request "
            "supplied and chain populated"
        )
    unplaceable = [name for key, name in required.items() if key not in windows]
    if unplaceable:
        raise FieldMapError(
            f"field map requires {_quote_all(unplaceable)} for policy type "
            f"'{routing.policy_type}' but declares no layout window for it"
        )

    accepted: dict[str, str] = {}
    supplied_under: dict[str, str] = {}
    for key, value in sample.items():
        lookup = key.upper()
        window = windows.get(lookup)
        if window is None:
            elsewhere = unselected.get(lookup)
            if elsewhere is not None:
                raise SampleError(
                    f"key '{key}' names item '{elsewhere[0]}' of overlay "
                    f"'{elsewhere[1]}', which request id '{routing.request_id}' does "
                    f"not select; the selected overlay is '{routing.overlay}'"
                )
            raise SampleError(
                f"key '{key}' names no item declared for request id "
                f"'{routing.request_id}'"
            )
        if lookup in chain_items:
            raise SampleError(
                f"key '{key}' names item '{window.item}', which the chain assigns; a "
                "sample definition must not supply it"
            )
        previous = supplied_under.get(lookup)
        if previous is not None:
            raise SampleError(
                f"keys '{previous}' and '{key}' both name item '{window.item}'; "
                "supply it once"
            )
        _check_value(window, key, value)
        supplied_under[lookup] = key
        accepted[window.item] = value

    absent = [name for key, name in required.items() if key not in supplied_under]
    if absent:
        raise SampleError(
            f"sample definition for request id '{routing.request_id}' does not supply "
            f"required item(s) {_quote_all(absent)}"
        )
    return accepted


def _record_length(field_map: dict[str, Any]) -> int:
    """Return the record length the field map declares."""
    return _positive_int(field_map["record"], "length", "field map record")


def _fill_rules(field_map: dict[str, Any]) -> dict[str, tuple[str, str]]:
    """Return the padding character and justification recorded for each item kind."""
    where = "field map sample_definition_contract"
    contract = field_map["sample_definition_contract"]
    padding = _mapping_section(contract, "value_padding", where)
    justification = _mapping_section(contract, "value_justification", where)

    rules: dict[str, tuple[str, str]] = {}
    for kind in (KIND_NUMERIC, KIND_ALPHANUMERIC):
        character = padding.get(kind)
        if not isinstance(character, str) or len(character) != 1:
            raise FieldMapError(
                f"{where}.value_padding['{kind}'] must be a single character, "
                f"found {character!r}"
            )
        side = justification.get(kind)
        if side not in (JUSTIFY_LEFT, JUSTIFY_RIGHT):
            raise FieldMapError(
                f"{where}.value_justification['{kind}'] must be '{JUSTIFY_LEFT}' or "
                f"'{JUSTIFY_RIGHT}', found {side!r}"
            )
        rules[kind] = (character, side)
    return rules


def _placed_characters(
    window: Window, value: str | None, rules: dict[str, tuple[str, str]]
) -> str:
    """Return the exact characters to write into one window.

    A supplied value is justified and padded as ``sample_definition_contract`` records
    for the window's kind. An absent value yields a window filled with that kind's
    padding character, which for a numeric window is the digit zero.
    """
    character, side = rules[window.kind]
    text = value if value is not None else ""
    if len(text) > window.length:
        raise SampleError(
            f"value for item '{window.item}' is {len(text)} characters, longer than "
            f"the declared length {window.length}"
        )
    if window.kind == KIND_NUMERIC and not _ASCII_DIGITS.fullmatch(text):
        raise SampleError(
            f"value {text!r} for numeric item '{window.item}' must contain "
            "digits 0-9 only"
        )
    if side == JUSTIFY_RIGHT:
        return text.rjust(window.length, character)
    return text.ljust(window.length, character)


def render_record(
    field_map: dict[str, Any], routing: Routing, values: dict[str, str]
) -> str:
    """Render the fixed-width record for one validated sample definition.

    Every window of the base groups and of the resolved overlay is written from the
    field map's own offsets and lengths. Numeric windows receive digits, alphanumeric
    windows receive their value or the padding character, and any byte no window claims
    stays a space. The result always carries the full length recorded by
    ``record.length``, which is 32,500 characters.

    Raises ``FieldMapError`` when two windows overlap, when a window falls outside the
    record, or when the assembled record does not match the declared length.
    """
    length = _record_length(field_map)
    rules = _fill_rules(field_map)
    windows = _layout_windows(field_map, routing)

    placeable = {window.item.upper() for window in windows}
    unplaceable = [item for item in values if item.upper() not in placeable]
    if unplaceable:
        raise SampleError(
            f"no layout window under request id '{routing.request_id}' for "
            f"value(s) {_quote_all(unplaceable)}"
        )

    supplied = {item.upper(): value for item, value in values.items()}
    buffer = [" "] * length
    furthest: Window | None = None
    for window in sorted(windows, key=lambda entry: (entry.offset, entry.item)):
        if window.end_byte > length:
            raise FieldMapError(
                f"field map layout item '{window.item}' spans bytes {window.offset}-"
                f"{window.end_byte}, outside the record length {length}"
            )
        if furthest is not None and window.offset <= furthest.end_byte:
            raise FieldMapError(
                f"field map layout items '{furthest.item}' (bytes {furthest.offset}-"
                f"{furthest.end_byte}) and '{window.item}' (bytes {window.offset}-"
                f"{window.end_byte}) claim the same bytes"
            )
        text = _placed_characters(window, supplied.get(window.item.upper()), rules)
        buffer[window.offset - 1 : window.end_byte] = list(text)
        if furthest is None or window.end_byte > furthest.end_byte:
            furthest = window

    record = "".join(buffer)
    if len(record) != length:
        raise FieldMapError(
            f"rendered record is {len(record)} characters, expected {length}"
        )
    return record


def _default_file_mode() -> int:
    """Return the mode a plainly created file receives under the current umask."""
    mask = os.umask(0)
    os.umask(mask)
    return 0o666 & ~mask


def write_record(
    path: str | os.PathLike[str], record: str, expected_length: int
) -> Path:
    """Write ``record`` to ``path`` as one line closed by a single newline.

    The record must already hold ``expected_length`` characters and only 7-bit ASCII.
    Parent directories are created, the characters are written to a temporary file in
    the destination directory and moved into place, and the result is read back and
    compared byte for byte before the destination path is returned.
    """
    if len(record) != expected_length:
        raise FieldMapError(
            f"record is {len(record)} characters, expected {expected_length}; "
            "refusing to write"
        )
    if not record.isascii():
        offender = next(character for character in record if not character.isascii())
        raise SampleError(
            f"record holds {offender!r} at position {record.index(offender) + 1}, "
            "outside 7-bit ASCII; refusing to write"
        )

    destination = Path(path)
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise InputOutputError(
            f"cannot create directory '{destination.parent}': "
            f"{error.strerror or error}"
        ) from error

    partial: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="ascii",
            newline="\n",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".partial",
            delete=False,
        ) as handle:
            partial = handle.name
            handle.write(record)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(partial, _default_file_mode())
        os.replace(partial, destination)
        partial = None
    except OSError as error:
        if partial is not None:
            # Delete the temporary file, then report the original failure.
            with contextlib.suppress(OSError):
                os.unlink(partial)
        raise InputOutputError(
            f"cannot write record to '{destination}': {error.strerror or error}"
        ) from error

    payload = (record + "\n").encode("ascii")
    try:
        written = destination.read_bytes()
    except OSError as error:
        raise InputOutputError(
            f"cannot read back '{destination}': {error.strerror or error}"
        ) from error
    if written != payload:
        detail = (
            f"holds {len(written)} bytes, expected {len(payload)}"
            if len(written) != len(payload)
            else "content differs from the rendered record"
        )
        raise InputOutputError(f"'{destination}' {detail} after writing")
    return destination


def build_arg_parser() -> argparse.ArgumentParser:
    """Return the non-interactive command line parser for this tool."""
    parser = argparse.ArgumentParser(
        prog=_PROGRAM,
        description=(
            "Validate one GenApp Policy-Issue sample definition and write the "
            "corresponding COMMAREA record of exactly 32,500 characters."
        ),
        epilog="Decision rationale: modernization/docs/decision-log.md",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--sample",
        required=True,
        type=Path,
        metavar="PATH",
        help="sample definition JSON document to build the record from",
    )
    parser.add_argument(
        "--field-map",
        default=None,
        type=Path,
        metavar="PATH",
        help=(
            "field map supplying every offset, length and kind "
            "(default: copybook_field_map.yml beside this script)"
        ),
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        metavar="PATH",
        help=(
            "destination path for the generated record; parent directories are "
            "created as needed"
        ),
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="suppress the summary line written to stdout on success",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Build one COMMAREA record and return the process exit status."""
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    try:
        field_map = load_field_map(args.field_map)
        sample = load_sample(args.sample)
        routing = resolve_overlay(field_map, _sample_request_id(field_map, sample))
        values = validate_sample(field_map, sample, routing)
        record = render_record(field_map, routing, values)
        written = write_record(args.output, record, _record_length(field_map))
    except BuildError as error:
        print(f"{_PROGRAM}: {error}", file=sys.stderr)
        return error.exit_status

    if not args.quiet:
        print(
            f"built {written} request_id={routing.request_id} "
            f"overlay={routing.overlay} characters={len(record)}"
        )
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
