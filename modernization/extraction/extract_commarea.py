#!/usr/bin/env python3
"""Decode the returned GenApp Policy-Issue COMMAREA into the landing JSON record.

WHAT THIS TOOL DOES
    Reads the post-chain COMMAREA capture the harness driver writes, decodes each
    landed value at the offset, length and kind ``copybook_field_map.yml`` records for
    it, derives ``policy_type`` from the request id through the map's
    ``request_routing`` table, normalises the returned ``CA-LASTCHANGED`` value to
    ISO-8601, and writes one landing JSON object carrying exactly the keys the map
    lists under ``landing.field_order``. No amount is derived: each premium and the
    payment are carried through as the digits the record holds, with leading zeros
    stripped, and a premium the derived policy type does not apply to is written as
    null. The four commercial peril codes are never read.

WHICH INPUTS IT ACCEPTS
    --commarea   the post-chain COMMAREA capture: exactly
                 ``COMMAREA_RECORD_LENGTH`` characters, optionally followed by one
                 line ending, in a file of at most ``MAX_CAPTURE_BYTES`` bytes.
    --field-map  the field map supplying every offset, length, kind, routing entry,
                 nullability rule and landing key, in a file of at most
                 ``MAX_FIELD_MAP_BYTES`` bytes (default: ``copybook_field_map.yml``
                 beside this script; every working directory resolves the same
                 default).
    --output     destination path for the landing JSON record; missing parent
                 directories are created.
    --source-system-key
                 the source-system discriminator written to the record. Taken from
                 the ``SOURCE_SYSTEM_KEY`` environment variable when the option is
                 omitted and from ``DEFAULT_SOURCE_SYSTEM_KEY`` when neither is
                 present. It carries 1 to ``MAX_SOURCE_SYSTEM_KEY_CHARACTERS``
                 characters drawn from ASCII letters, digits, underscore, dot and
                 hyphen. The same value forms the ``source_system_key`` element of
                 the landing prefix.
    --allow-nonzero-return-code
                 land the record even when the returned ``CA-RETURN-CODE`` is not
                 ``00``. Without it, any other code of the map's recorded domain is
                 rejected and nothing is written.

WHAT IT WRITES
    One JSON object serialised as a single line terminated by one line feed, holding
    the landing keys in the order the field map lists them. Every value is a JSON
    string or null; no number, boolean, array or nested object is emitted. The record
    is written through a temporary entry in the destination directory and moved onto
    the destination name. On success one summary line naming the destination, the
    request id, the derived policy type, the policy number and the return code
    reaches stdout, and nothing else does.

HOW IT FAILS
    Every failure writes one diagnostic line to stderr and returns a non-zero status:
    2 for a capture that breaches the record contract, 3 for a field map missing a
    member this tool reads or contradicting itself, 4 for an unreadable input, an
    unwritable output or a rejected command line. Diagnostics carry untrusted text
    escaped to one printable 7-bit ASCII line. The tool never prompts and requires no
    TTY. It reads the capture and the field map without modifying either, and writes
    nothing outside the destination the command line names.

WHICH CHARACTER SET IT READS
    The capture is decoded as ``CAPTURE_ENCODING``, the workstation character set the
    local harness writes; a z/OS extract carries the installation CCSID, documented as
    285 by default, and is not decoded by this tool.

WHERE THIS STEP SITS
    Figure 2 - AFTER (BUILT): Canonical Warehouse Bridge and Figure 5 - Validation
    Harness Control Flow, both in modernization/docs/architecture.md.

Decision rationale: see modernization/docs/decision-log.md.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import stat
import sys
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any, NamedTuple, NoReturn

import yaml

_PROGRAM = "extract_commarea"

# Field map used when --field-map is omitted, resolved from this script's own
# directory rather than from the working directory.
_THIS_DIR = Path(__file__).resolve().parent
DEFAULT_FIELD_MAP = _THIS_DIR / "copybook_field_map.yml"

# Repository directory holding this script (modernization/extraction/ -> repository
# root) and the read-only source directory no destination may resolve inside.
REPOSITORY_ROOT = _THIS_DIR.parents[1]
READ_ONLY_SOURCE_ROOT = REPOSITORY_ROOT / "base"

# Record width the capture must carry: the sum of the four level-03 items declared at
# base/src/lgcmarea.cpy:10-13, which are 6 + 2 + 10 + 32482 characters. The field map
# must declare this same width under record.length.
COMMAREA_RECORD_LENGTH = 32500

# Character set the capture is decoded with, and the line endings one trailing line
# ending may consist of.
CAPTURE_ENCODING = "ascii"
_TRAILING_LINE_ENDINGS = ("\r\n", "\n", "\r")

# Bytes one read takes from each input before anything parses it, and the bytes one
# read of an input asks for at a time.
MAX_CAPTURE_BYTES = 64 * 1024
MAX_FIELD_MAP_BYTES = 1024 * 1024
READ_CHUNK_BYTES = 65536

EXIT_OK = 0
EXIT_RECORD_REJECTED = 2
EXIT_FIELD_MAP_INVALID = 3
EXIT_IO_ERROR = 4

# Characters of untrusted text one diagnostic fragment carries before truncation.
MAX_DIAGNOSTIC_CHARACTERS = 64
MAX_DIAGNOSTIC_PATH_CHARACTERS = 160
MAX_DIAGNOSTIC_MESSAGE_CHARACTERS = 200

# Candidate names tried when creating the temporary entry the record is written
# through, and the mode requested for a directory created for the destination.
MAX_TEMPORARY_ATTEMPTS = 8
DIRECTORY_MODE = 0o777

# Item kinds the field map declares under layout.<group>.items[].kind.
KIND_NUMERIC = "numeric_display"
KIND_ALPHANUMERIC = "alphanumeric"
KNOWN_KINDS = (KIND_NUMERIC, KIND_ALPHANUMERIC)

# Values the field map records under fields[].populated_by and fields[].runtime_status.
POPULATED_BY_CHAIN = "chain"
RUNTIME_STATUS_DERIVED = "derived"
RUNTIME_STATUS_WAREHOUSE_ASSIGNED = "warehouse_assigned"

# Group the field map records for the six amount entries.
GROUP_PREMIUM_PAYMENT = "premium_payment"

# The return code the chain writes on a completed policy issue.
RETURN_CODE_SUCCESS = "00"

# Landing keys this tool treats individually. Each must appear in the field map's
# landing.field_order, and each name below is the map's own landing_field value.
LANDING_SOURCE_SYSTEM_KEY = "source_system_key"
LANDING_REQUEST_ID = "request_id"
LANDING_RETURN_CODE = "return_code"
LANDING_POLICY_TYPE = "policy_type"
LANDING_POLICY_NUMBER = "policy_number"
LANDING_LAST_CHANGED = "last_changed"

# Source-system key accepted values and where an omitted option looks for one.
DEFAULT_SOURCE_SYSTEM_KEY = "GENAPP_CLASS_EXEMPLAR"
SOURCE_SYSTEM_KEY_VARIABLE = "SOURCE_SYSTEM_KEY"
MAX_SOURCE_SYSTEM_KEY_CHARACTERS = 64
_SOURCE_SYSTEM_KEY_SHAPE = re.compile(r"\A[A-Za-z0-9_.\-]+\Z")

# Window content accepted for a numeric_display item, and the characters escaped out
# of a diagnostic.
_ASCII_DIGITS = re.compile(r"\A[0-9]+\Z")
_CONTROL_CHARACTERS = re.compile(r"[\x00-\x1f\x7f-\x9f]")

# Timestamp forms accepted for CA-LASTCHANGED, tried in this order. The first is the
# Db2 character form; the rest are ISO-8601 with a T or a space separator. Each is
# tried with and without the fractional-second part.
TIMESTAMP_INPUT_FORMATS = (
    "%Y-%m-%d-%H.%M.%S.%f",
    "%Y-%m-%d-%H.%M.%S",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%d %H:%M:%S",
)

# Separator and precision the normalised timestamp is emitted with.
TIMESTAMP_OUTPUT_SEPARATOR = "T"
TIMESTAMP_OUTPUT_PRECISION = "microseconds"


class ExtractError(Exception):
    """Diagnostic raised by this module, carrying the process status to return."""

    exit_status = EXIT_RECORD_REJECTED


class RecordError(ExtractError):
    """The capture breaches the COMMAREA record contract."""

    exit_status = EXIT_RECORD_REJECTED


class FieldMapError(ExtractError):
    """The field map is missing a member this tool reads or contradicts itself."""

    exit_status = EXIT_FIELD_MAP_INVALID


class InputOutputError(ExtractError):
    """An input cannot be read or the destination cannot be written."""

    exit_status = EXIT_IO_ERROR


class UsageError(ExtractError):
    """The command line omits a required argument or carries a rejected value."""

    exit_status = EXIT_IO_ERROR


def _type_name(value: Any) -> str:
    """Return the type name of ``value`` for use inside a diagnostic."""
    return type(value).__name__


def _escaped_character(character: str) -> str:
    """Return one printable 7-bit ASCII rendering of ``character``."""
    if " " <= character <= "~":
        return character
    codepoint = ord(character)
    if codepoint <= 0xFF:
        return f"\\x{codepoint:02x}"
    if codepoint <= 0xFFFF:
        return f"\\u{codepoint:04x}"
    return f"\\U{codepoint:08x}"


def _one_line(text: str) -> str:
    """Return ``text`` with every control character replaced by an escape."""
    return _CONTROL_CHARACTERS.sub(
        lambda match: _escaped_character(match.group()), text
    )


def _escaped(text: str, limit: int = MAX_DIAGNOSTIC_CHARACTERS) -> str:
    """Return ``text`` as one printable 7-bit ASCII fragment of at most ``limit``.

    Characters past ``limit`` are dropped and the fragment records how many were
    dropped. A fragment never spans more than one line.
    """
    if limit < 1:
        limit = 1
    kept = text[:limit]
    rendered = "".join(_escaped_character(character) for character in kept)
    dropped = len(text) - len(kept)
    if dropped:
        return f"{rendered}...(+{dropped} characters)"
    return rendered


def _shown(value: str, limit: int = MAX_DIAGNOSTIC_CHARACTERS) -> str:
    """Return ``value`` quoted and escaped for a diagnostic."""
    return f"'{_escaped(value, limit)}'"


def _path_shown(path: str | os.PathLike[str]) -> str:
    """Return ``path`` quoted and escaped for a diagnostic."""
    return _shown(os.fspath(path), MAX_DIAGNOSTIC_PATH_CHARACTERS)


def _display(value: Any) -> str:
    """Return any value rendered for a diagnostic, quoting text and naming a type."""
    if isinstance(value, str):
        return _shown(value)
    if value is None or isinstance(value, (bool, int, float)):
        return str(value)
    return f"a {_type_name(value)}"


def _reason(error: BaseException) -> str:
    """Return the reason text of ``error`` as one bounded diagnostic fragment."""
    text = str(error) or _type_name(error)
    return _escaped(text, MAX_DIAGNOSTIC_MESSAGE_CHARACTERS)


def _quote_all(names: Iterable[str]) -> str:
    """Return ``names`` quoted, escaped and joined by a comma, in the order given."""
    return ", ".join(_shown(str(name)) for name in names)


def _window_range(offset: int, length: int) -> str:
    """Return the 1-based inclusive byte range a window covers, as ``first-last``."""
    return f"{offset}-{offset + length - 1}"


def _offending_characters(window: str) -> str:
    """Return the distinct non-digit characters of ``window``, in first-seen order."""
    seen: list[str] = []
    for character in window:
        if character not in "0123456789" and character not in seen:
            seen.append(character)
    return _quote_all(seen)


# ---------------------------------------------------------------------------
# Field map
# ---------------------------------------------------------------------------


class LandingField(NamedTuple):
    """One landing key and the COMMAREA window, where there is one, that supplies it.

    ``offset``, ``length`` and ``kind`` are None for a landing key the map records
    without a ``commarea`` block, which is a key this tool derives rather than reads.
    ``applicable_policy_types`` holds the policy-type letters the map records for the
    entry, ``evidence`` holds the locators it cites, and ``domain`` holds the accepted
    values where the entry records them.
    """

    name: str
    logical_entry: str
    group: str
    runtime_status: str
    populated_by: str | None
    item: str | None
    copybook: str | None
    line: int | None
    pic: str | None
    offset: int | None
    length: int | None
    kind: str | None
    applicable_policy_types: tuple[str, ...]
    evidence: tuple[str, ...]
    domain: tuple[str, ...] = ()

    @property
    def is_read_from_record(self) -> bool:
        """Return True when this key is decoded from a COMMAREA window."""
        return self.offset is not None and self.length is not None

    @property
    def locator(self) -> str:
        """Return the copybook locator of the declaring item, as ``path:line``."""
        if self.copybook and self.line:
            return f"{self.copybook}:{self.line}"
        return self.copybook or "no copybook locator recorded"

    @property
    def described(self) -> str:
        """Return the item, its locator and its byte range for use in a diagnostic."""
        if not self.is_read_from_record:
            return f"landing key {_shown(self.name)}"
        assert self.offset is not None and self.length is not None
        return (
            f"{self.item} ({self.locator}) bytes "
            f"{_window_range(self.offset, self.length)}"
        )


class FieldMap(NamedTuple):
    """Every member of ``copybook_field_map.yml`` this tool reads, already validated.

    ``fields`` is keyed by landing key and excludes the warehouse-assigned key, which
    ``source_system_key_field`` names. ``nullability`` maps a policy-type letter to the
    amount keys populated for it and the amount keys left null for it, with the keys
    the map records as always populated held separately in ``always_populated``.
    """

    path: Path
    record_length: int
    field_order: tuple[str, ...]
    fields: Mapping[str, LandingField]
    routing: Mapping[str, str]
    amount_fields: tuple[str, ...]
    always_populated: frozenset[str]
    nullability: Mapping[str, tuple[frozenset[str], frozenset[str]]]
    return_code_domain: tuple[str, ...]
    source_system_key_field: str
    source_system_key_run_value: str
    chain_populated: frozenset[str]
    unrecognised_request_return_code: str


class _DuplicateRejectingLoader(yaml.SafeLoader):
    """``yaml.SafeLoader`` that refuses a mapping which repeats a key.

    Loading raises ``yaml.constructor.ConstructorError`` naming the repeated key and
    the position it reappears at, instead of resolving that key to its last value. A
    key this loader cannot compare against the keys already seen raises the same error
    class. Every mapping defect reaches the caller as a YAML error.
    """

    def construct_mapping(
        self, node: yaml.MappingNode, deep: bool = False
    ) -> dict[Any, Any]:
        """Build one mapping, raising on a repeated key or a key it cannot compare."""
        seen: set[Any] = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                duplicate = key in seen
                if not duplicate:
                    seen.add(key)
            except TypeError as error:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found unhashable key of type {_type_name(key)}",
                    key_node.start_mark,
                ) from error
            if duplicate:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found duplicate key {_display(key)}",
                    key_node.start_mark,
                )
        return super().construct_mapping(node, deep=deep)


def _path_of(where: str, key: str) -> str:
    """Return the dotted field map path of ``key`` inside the container at ``where``."""
    return f"{where}.{key}" if where else key


def _member(container: Any, key: str, where: str) -> Any:
    """Return ``container[key]``, raising ``FieldMapError`` when it is absent.

    ``where`` is the dotted path of ``container`` inside the field map, empty for the
    document root, and every diagnostic names the dotted path of the member itself.
    """
    if not isinstance(container, Mapping):
        raise FieldMapError(
            f"the field map records {_shown(where) if where else 'its root'} as "
            f"{_display(container)}; a mapping is required"
        )
    if key not in container:
        raise FieldMapError(
            f"the field map is missing {_shown(_path_of(where, key))}"
        )
    return container[key]


def _member_mapping(container: Any, key: str, where: str) -> Mapping[str, Any]:
    """Return a required member that must be a mapping."""
    value = _member(container, key, where)
    if not isinstance(value, Mapping):
        raise FieldMapError(
            f"the field map records {_shown(_path_of(where, key))} as "
            f"{_display(value)}; a mapping is required"
        )
    return value


def _member_sequence(container: Any, key: str, where: str) -> Sequence[Any]:
    """Return a required member that must be a sequence and not text."""
    value = _member(container, key, where)
    if isinstance(value, str) or not isinstance(value, Sequence):
        raise FieldMapError(
            f"the field map records {_shown(_path_of(where, key))} as "
            f"{_display(value)}; a sequence is required"
        )
    return value


def _member_text(container: Any, key: str, where: str) -> str:
    """Return a required member that must be a non-empty string."""
    value = _member(container, key, where)
    if not isinstance(value, str) or not value:
        raise FieldMapError(
            f"the field map records {_shown(_path_of(where, key))} as "
            f"{_display(value)}; a non-empty string is required"
        )
    return value


def _member_integer(container: Any, key: str, where: str, minimum: int = 1) -> int:
    """Return a required member that must be an integer of at least ``minimum``."""
    value = _member(container, key, where)
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise FieldMapError(
            f"the field map records {_shown(_path_of(where, key))} as "
            f"{_display(value)}; an integer of at least {minimum} is required"
        )
    return value


def _text_sequence(container: Any, key: str, where: str) -> tuple[str, ...]:
    """Return a required member that must be a sequence of non-empty strings."""
    values = _member_sequence(container, key, where)
    for position, value in enumerate(values):
        if not isinstance(value, str) or not value:
            raise FieldMapError(
                f"the field map records element {position} of "
                f"{_shown(_path_of(where, key))} as {_display(value)}; a non-empty "
                "string is required"
            )
    return tuple(str(value) for value in values)


def _optional_text_sequence(
    container: Mapping[str, Any], key: str, where: str
) -> tuple[str, ...]:
    """Return a sequence of non-empty strings, or an empty tuple when it is absent."""
    if container.get(key) is None:
        return ()
    return _text_sequence(container, key, where)


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------


def _read_bounded_bytes(path: Path, limit: int, what: str) -> bytes:
    """Return the bytes of one regular file, refusing anything past ``limit``.

    ``what`` names the input inside every diagnostic. The file is opened read-only and
    is never written, truncated or removed. Raises ``InputOutputError`` when the path
    cannot be opened or read, when it is not a regular file, or when it carries more
    than ``limit`` bytes.
    """
    try:
        descriptor = os.open(path, os.O_RDONLY)
    except OSError as error:
        raise InputOutputError(
            f"{what} cannot be opened: {_path_shown(path)}: {_reason(error)}"
        ) from error
    try:
        try:
            status = os.fstat(descriptor)
        except OSError as error:
            raise InputOutputError(
                f"{what} cannot be examined: {_path_shown(path)}: {_reason(error)}"
            ) from error
        if not stat.S_ISREG(status.st_mode):
            raise InputOutputError(
                f"{what} is not a regular file: {_path_shown(path)}"
            )
        chunks: list[bytes] = []
        collected = 0
        try:
            while collected <= limit:
                chunk = os.read(descriptor, READ_CHUNK_BYTES)
                if not chunk:
                    break
                chunks.append(chunk)
                collected += len(chunk)
        except OSError as error:
            raise InputOutputError(
                f"{what} cannot be read: {_path_shown(path)}: {_reason(error)}"
            ) from error
    finally:
        os.close(descriptor)
    if collected > limit:
        raise InputOutputError(
            f"{what} holds more than {limit} bytes: {_path_shown(path)}"
        )
    return b"".join(chunks)


def _without_one_trailing_line_ending(text: str) -> str:
    """Return ``text`` with at most one trailing line ending removed.

    A carriage return and line feed pair counts as one ending. A second ending is
    left in place and reaches the length check as content.
    """
    for ending in _TRAILING_LINE_ENDINGS:
        if text.endswith(ending):
            return text[: -len(ending)]
    return text


def read_commarea(path: Path, record_length: int = COMMAREA_RECORD_LENGTH) -> str:
    """Return the fixed-width record held by the post-chain COMMAREA capture.

    ``path`` names the capture the harness driver writes. It is decoded as
    ``CAPTURE_ENCODING`` rather than by the platform default, at most one trailing
    line ending is removed, and the remainder must hold exactly ``record_length``
    characters, being the width the four level-03 items at
    base/src/lgcmarea.cpy:10-13 declare. The capture is read once and is not
    modified.

    Raises ``InputOutputError`` when the capture cannot be read and ``RecordError``
    when it is not ``CAPTURE_ENCODING`` text or does not carry exactly
    ``record_length`` characters, naming the observed length.
    """
    content = _read_bounded_bytes(path, MAX_CAPTURE_BYTES, "the COMMAREA capture")
    try:
        text = content.decode(CAPTURE_ENCODING)
    except UnicodeDecodeError as error:
        raise RecordError(
            f"the COMMAREA capture is not {CAPTURE_ENCODING} text: "
            f"{_path_shown(path)}: {_reason(error)}"
        ) from error
    record = _without_one_trailing_line_ending(text)
    if len(record) != record_length:
        raise RecordError(
            f"the COMMAREA capture holds {len(record)} characters once one optional "
            f"trailing line ending is removed: {_path_shown(path)}; exactly "
            f"{record_length} characters are required"
        )
    return record


def _layout_windows(
    document: Mapping[str, Any], record_length: int
) -> Mapping[str, tuple[int, int, str]]:
    """Return each layout item's offset, length and kind, keyed by item name.

    Every group under ``layout`` contributes its ``items``. An item repeated with a
    differing offset, length or kind, an unknown kind, or a window reaching past
    ``record_length`` raises ``FieldMapError``.
    """
    groups = _member_mapping(document, "layout", "")
    windows: dict[str, tuple[int, int, str]] = {}
    for group_name, group in groups.items():
        where = f"layout.{group_name}"
        items = _member_sequence(group, "items", where)
        for position, item in enumerate(items):
            item_where = f"{where}.items[{position}]"
            name = _member_text(item, "item", item_where)
            offset = _member_integer(item, "offset", item_where)
            length = _member_integer(item, "length", item_where)
            kind = _member_text(item, "kind", item_where)
            if kind not in KNOWN_KINDS:
                raise FieldMapError(
                    f"the field map records {_shown(f'{item_where}.kind')} as "
                    f"{_shown(kind)}; one of {_quote_all(KNOWN_KINDS)} is required"
                )
            if offset + length - 1 > record_length:
                raise FieldMapError(
                    f"the field map places {name} at bytes "
                    f"{_window_range(offset, length)}, past the {record_length}-"
                    f"character record: {item_where}"
                )
            existing = windows.get(name)
            if existing is not None and existing != (offset, length, kind):
                raise FieldMapError(
                    f"the field map declares {name} twice with differing placement: "
                    f"bytes {_window_range(existing[0], existing[1])} of kind "
                    f"{_shown(existing[2])} and bytes "
                    f"{_window_range(offset, length)} of kind {_shown(kind)}"
                )
            windows[name] = (offset, length, kind)
    if not windows:
        raise FieldMapError("the field map records no item under 'layout'")
    return windows


def _landing_field(
    entry: Mapping[str, Any],
    where: str,
    landing_name: str,
    windows: Mapping[str, tuple[int, int, str]],
) -> LandingField:
    """Return one landing field built from a ``fields`` entry and the layout windows.

    The entry's ``commarea`` block supplies the declaring item and its placement, and
    the item's ``kind`` is taken from the layout windows. A ``commarea`` block naming an
    item the layout does not declare, or recording an offset or length the layout
    contradicts, raises ``FieldMapError``.
    """
    logical_entry = _member_text(entry, "logical_entry", where)
    group = _member_text(entry, "group", where)
    runtime_status = _member_text(entry, "runtime_status", where)
    populated_by = entry.get("populated_by")
    if populated_by is not None and not isinstance(populated_by, str):
        raise FieldMapError(
            f"the field map records {_shown(f'{where}.populated_by')} as "
            f"{_display(populated_by)}; a string or null is required"
        )
    applicable = _optional_text_sequence(entry, "applicable_policy_types", where)
    evidence = _optional_text_sequence(entry, "evidence", where)
    domain = _optional_text_sequence(entry, "domain", where)
    commarea = entry.get("commarea")
    if commarea is None:
        return LandingField(
            name=landing_name,
            logical_entry=logical_entry,
            group=group,
            runtime_status=runtime_status,
            populated_by=populated_by,
            item=None,
            copybook=None,
            line=None,
            pic=None,
            offset=None,
            length=None,
            kind=None,
            applicable_policy_types=applicable,
            evidence=evidence,
            domain=domain,
        )
    commarea_where = f"{where}.commarea"
    item = _member_text(commarea, "item", commarea_where)
    copybook = _member_text(commarea, "copybook", commarea_where)
    line = _member_integer(commarea, "line", commarea_where)
    pic = _member_text(commarea, "pic", commarea_where)
    offset = _member_integer(commarea, "offset", commarea_where)
    length = _member_integer(commarea, "length", commarea_where)
    window = windows.get(item)
    if window is None:
        raise FieldMapError(
            f"the field map records {_shown(f'{commarea_where}.item')} as "
            f"{_shown(item)}, which no 'layout' group declares"
        )
    if (offset, length) != (window[0], window[1]):
        raise FieldMapError(
            f"the field map places {item} at bytes {_window_range(offset, length)} "
            f"under {commarea_where} and at bytes "
            f"{_window_range(window[0], window[1])} under 'layout'"
        )
    return LandingField(
        name=landing_name,
        logical_entry=logical_entry,
        group=group,
        runtime_status=runtime_status,
        populated_by=populated_by,
        item=item,
        copybook=copybook,
        line=line,
        pic=pic,
        offset=offset,
        length=length,
        kind=window[2],
        applicable_policy_types=applicable,
        evidence=evidence,
        domain=domain,
    )


def _landing_fields(
    document: Mapping[str, Any], windows: Mapping[str, tuple[int, int, str]]
) -> Mapping[str, LandingField]:
    """Return every ``fields`` entry carrying a landing key, keyed by that key."""
    entries = _member_sequence(document, "fields", "")
    fields: dict[str, LandingField] = {}
    for position, entry in enumerate(entries):
        where = f"fields[{position}]"
        if not isinstance(entry, Mapping):
            raise FieldMapError(
                f"the field map records {_shown(where)} as {_display(entry)}; a "
                "mapping is required"
            )
        if "landing_field" not in entry:
            raise FieldMapError(
                f"the field map is missing {_shown(f'{where}.landing_field')}"
            )
        landing_name = entry["landing_field"]
        if landing_name is None:
            continue
        if not isinstance(landing_name, str) or not landing_name:
            raise FieldMapError(
                f"the field map records {_shown(f'{where}.landing_field')} as "
                f"{_display(landing_name)}; a non-empty string or null is required"
            )
        if landing_name in fields:
            raise FieldMapError(
                f"the field map records landing key {_shown(landing_name)} on two "
                f"entries, the second at {where}"
            )
        fields[landing_name] = _landing_field(entry, where, landing_name, windows)
    if not fields:
        raise FieldMapError("the field map records no landing key under 'fields'")
    return fields


def _reject_excluded_items(
    document: Mapping[str, Any], fields: Mapping[str, LandingField]
) -> None:
    """Raise ``FieldMapError`` when a landing key reads an item recorded as excluded.

    The ``excluded`` section names the in-scope declarations that carry no target
    column, the four commercial peril codes among them. No landing key may be sourced
    from one of those items.
    """
    entries = _member_sequence(document, "excluded", "")
    excluded: set[str] = set()
    for position, entry in enumerate(entries):
        excluded.add(_member_text(entry, "item", f"excluded[{position}]"))
    for name, field in fields.items():
        if field.item is not None and field.item in excluded:
            raise FieldMapError(
                f"the field map sources landing key {_shown(name)} from "
                f"{field.item}, which it also records under 'excluded' as carrying no "
                "target column"
            )


def _routing(document: Mapping[str, Any]) -> tuple[Mapping[str, str], str]:
    """Return the request-id to policy-type table and the unrecognised return code.

    The table is ``request_routing.map``, whose every entry records a single-character
    uppercase ``policy_type``. The second value is
    ``request_routing.unrecognised_request.return_code``.
    """
    routing_section = _member_mapping(document, "request_routing", "")
    entries = _member_mapping(routing_section, "map", "request_routing")
    table: dict[str, str] = {}
    for request_id, entry in entries.items():
        where = f"request_routing.map.{request_id}"
        if not isinstance(request_id, str) or not request_id:
            raise FieldMapError(
                f"the field map records {_display(request_id)} as a key of "
                "'request_routing.map'; a non-empty string is required"
            )
        policy_type = _member_text(entry, "policy_type", where)
        if len(policy_type) != 1 or not policy_type.isupper():
            raise FieldMapError(
                f"the field map records {_shown(f'{where}.policy_type')} as "
                f"{_shown(policy_type)}; one uppercase character is required"
            )
        table[request_id] = policy_type
    if not table:
        raise FieldMapError(
            "the field map records no entry under 'request_routing.map'"
        )
    unrecognised = _member_mapping(
        routing_section, "unrecognised_request", "request_routing"
    )
    return table, _member_text(
        unrecognised, "return_code", "request_routing.unrecognised_request"
    )


def _amount_fields(
    document: Mapping[str, Any], fields: Mapping[str, LandingField]
) -> tuple[str, ...]:
    """Return the amount landing keys, checked against the entries' recorded group.

    The keys are ``comparison.amount_fields``. Each must be a landing key of kind
    ``numeric_display`` recorded under group ``premium_payment``, and every landing key
    of that group must appear among them.
    """
    comparison = _member_mapping(document, "comparison", "")
    names = _text_sequence(comparison, "amount_fields", "comparison")
    for name in names:
        field = fields.get(name)
        if field is None:
            raise FieldMapError(
                f"the field map lists {_shown(name)} under "
                "'comparison.amount_fields' but records no landing key of that name"
            )
        if field.group != GROUP_PREMIUM_PAYMENT:
            raise FieldMapError(
                f"the field map records landing key {_shown(name)} under group "
                f"{_shown(field.group)} and lists it under "
                f"'comparison.amount_fields'; group {_shown(GROUP_PREMIUM_PAYMENT)} "
                "is required"
            )
        if field.kind != KIND_NUMERIC:
            raise FieldMapError(
                f"the field map records amount {_shown(name)} as kind "
                f"{_display(field.kind)}; kind {_shown(KIND_NUMERIC)} is required"
            )
    grouped = {
        name
        for name, field in fields.items()
        if field.group == GROUP_PREMIUM_PAYMENT
    }
    missing = sorted(grouped - set(names))
    if missing:
        raise FieldMapError(
            f"the field map records {_quote_all(missing)} under group "
            f"{_shown(GROUP_PREMIUM_PAYMENT)} without listing them under "
            "'comparison.amount_fields'"
        )
    return names


def _nullability(
    document: Mapping[str, Any],
    amount_fields: Sequence[str],
    policy_types: Iterable[str],
    fields: Mapping[str, LandingField],
) -> tuple[frozenset[str], Mapping[str, tuple[frozenset[str], frozenset[str]]]]:
    """Return the always-populated amount keys and the per-policy-type split.

    ``product_premium_nullability`` must record every policy type the routing table
    yields, must account for every amount key exactly once per policy type across
    ``always_populated``, ``populated`` and ``null_fields``, must record null as the
    inapplicable value and must refuse zero substitution. The split is checked against
    each amount entry's ``applicable_policy_types`` in both directions.
    """
    section = _member_mapping(document, "product_premium_nullability", "")
    where = "product_premium_nullability"
    if section.get("inapplicable_value") is not None:
        raise FieldMapError(
            f"the field map records {_shown(f'{where}.inapplicable_value')} as "
            f"{_display(section.get('inapplicable_value'))}; null is required"
        )
    if section.get("zero_substitution_permitted") is not False:
        raise FieldMapError(
            f"the field map records {_shown(f'{where}.zero_substitution_permitted')} "
            f"as {_display(section.get('zero_substitution_permitted'))}; false is "
            "required"
        )
    always = frozenset(_text_sequence(section, "always_populated", where))
    unknown = sorted(always - set(amount_fields))
    if unknown:
        raise FieldMapError(
            f"the field map lists {_quote_all(unknown)} under "
            f"{_shown(f'{where}.always_populated')} without listing them as amounts"
        )
    by_type = _member_mapping(section, "by_policy_type", where)
    split: dict[str, tuple[frozenset[str], frozenset[str]]] = {}
    for policy_type in policy_types:
        entry_where = f"{where}.by_policy_type.{policy_type}"
        if policy_type not in by_type:
            raise FieldMapError(f"the field map is missing {_shown(entry_where)}")
        entry = by_type[policy_type]
        populated = frozenset(_optional_text_sequence(entry, "populated", entry_where))
        nulled = frozenset(_optional_text_sequence(entry, "null_fields", entry_where))
        overlap = sorted(populated & nulled)
        if overlap:
            raise FieldMapError(
                f"the field map lists {_quote_all(overlap)} as both populated and null "
                f"under {_shown(entry_where)}"
            )
        accounted = always | populated | nulled
        if accounted != set(amount_fields):
            unaccounted = sorted(set(amount_fields) - accounted)
            foreign = sorted(accounted - set(amount_fields))
            raise FieldMapError(
                f"the field map accounts for {len(accounted)} of the "
                f"{len(amount_fields)} amounts under {_shown(entry_where)}: "
                f"unaccounted {_quote_all(unaccounted) or 'none'}, "
                f"not an amount {_quote_all(foreign) or 'none'}"
            )
        for name in amount_fields:
            applicable = policy_type in fields[name].applicable_policy_types
            populated_here = name in always or name in populated
            if applicable != populated_here:
                raise FieldMapError(
                    f"the field map records amount {_shown(name)} as "
                    f"{'applicable' if applicable else 'inapplicable'} to policy type "
                    f"{_shown(policy_type)} under 'fields' and as "
                    f"{'populated' if populated_here else 'null'} under "
                    f"{_shown(entry_where)}"
                )
        split[policy_type] = (always | populated, nulled)
    return always, split


def load_field_map(path: Path) -> FieldMap:
    """Return the validated field map members this tool reads.

    ``path`` names ``copybook_field_map.yml``. Every offset, length, kind, routing
    entry, landing key, amount key and nullability rule is taken from it; none is
    written into this tool. The document is parsed with a repeated mapping key rejected
    rather than resolved to its last value.

    Raises ``InputOutputError`` when the file cannot be read and ``FieldMapError``
    when it cannot be parsed, is missing a member this tool reads, or contradicts
    itself: a record length other than ``COMMAREA_RECORD_LENGTH``, a landing key
    without either a COMMAREA window or a derived runtime status, a landing order that
    disagrees with the recorded landing keys, a request-routing entry without a
    single-character policy type, an amount outside group ``premium_payment``, a
    nullability split that disagrees with the recorded applicable policy types, a
    landing key sourced from an item the map records under ``excluded``, a
    source-system runtime status other than ``RUNTIME_STATUS_WAREHOUSE_ASSIGNED``, or a
    recorded source-system run value other than ``DEFAULT_SOURCE_SYSTEM_KEY``.
    """
    content = _read_bounded_bytes(path, MAX_FIELD_MAP_BYTES, "the field map")
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise InputOutputError(
            f"the field map is not UTF-8 text: {_path_shown(path)}: {_reason(error)}"
        ) from error
    try:
        document = yaml.load(text, Loader=_DuplicateRejectingLoader)
    except yaml.YAMLError as error:
        raise FieldMapError(
            f"the field map cannot be parsed: {_path_shown(path)}: {_reason(error)}"
        ) from error
    if not isinstance(document, Mapping):
        raise FieldMapError(
            f"the field map is {_display(document)}: {_path_shown(path)}; a mapping is "
            "required"
        )

    record_length = _member_integer(
        _member_mapping(document, "record", ""), "length", "record"
    )
    if record_length != COMMAREA_RECORD_LENGTH:
        raise FieldMapError(
            f"the field map records 'record.length' as {record_length}; "
            f"{COMMAREA_RECORD_LENGTH} is required"
        )

    landing = _member_mapping(document, "landing", "")
    field_order = _text_sequence(landing, "field_order", "landing")
    repeated = sorted({name for name in field_order if field_order.count(name) > 1})
    if repeated:
        raise FieldMapError(
            f"the field map repeats {_quote_all(repeated)} in 'landing.field_order'"
        )

    windows = _layout_windows(document, record_length)
    fields = _landing_fields(document, windows)
    _reject_excluded_items(document, fields)
    routing, unrecognised_return_code = _routing(document)
    amount_fields = _amount_fields(document, fields)
    always_populated, nullability = _nullability(
        document, amount_fields, sorted(set(routing.values())), fields
    )

    key_section = _member_mapping(document, LANDING_SOURCE_SYSTEM_KEY, "")
    source_system_key_field = _member_text(
        key_section, "landing_field", LANDING_SOURCE_SYSTEM_KEY
    )
    source_system_key_run_value = _member_text(
        key_section, "run_value", LANDING_SOURCE_SYSTEM_KEY
    )
    key_runtime_status = _member_text(
        key_section, "runtime_status", LANDING_SOURCE_SYSTEM_KEY
    )
    if key_runtime_status != RUNTIME_STATUS_WAREHOUSE_ASSIGNED:
        raise FieldMapError(
            f"the field map records "
            f"{_shown(f'{LANDING_SOURCE_SYSTEM_KEY}.runtime_status')} as "
            f"{_shown(key_runtime_status)}; "
            f"{_shown(RUNTIME_STATUS_WAREHOUSE_ASSIGNED)} is required"
        )
    if source_system_key_run_value != DEFAULT_SOURCE_SYSTEM_KEY:
        raise FieldMapError(
            f"the field map records "
            f"{_shown(f'{LANDING_SOURCE_SYSTEM_KEY}.run_value')} as "
            f"{_shown(source_system_key_run_value)}; "
            f"{_shown(DEFAULT_SOURCE_SYSTEM_KEY)} is required"
        )

    expected_order = {source_system_key_field, *fields}
    if set(field_order) != expected_order:
        absent = sorted(expected_order - set(field_order))
        extra = sorted(set(field_order) - expected_order)
        raise FieldMapError(
            "the field map's 'landing.field_order' does not match its recorded landing "
            f"keys: absent {_quote_all(absent) or 'none'}, unrecorded "
            f"{_quote_all(extra) or 'none'}"
        )

    for name in (
        LANDING_REQUEST_ID,
        LANDING_RETURN_CODE,
        LANDING_POLICY_TYPE,
        LANDING_POLICY_NUMBER,
        LANDING_LAST_CHANGED,
    ):
        if name not in fields:
            raise FieldMapError(
                f"the field map records no landing key {_shown(name)} under 'fields'"
            )
    for name, field in fields.items():
        if not field.is_read_from_record and field.runtime_status != (
            RUNTIME_STATUS_DERIVED
        ):
            raise FieldMapError(
                f"the field map records landing key {_shown(name)} without a "
                f"'commarea' block and with runtime status "
                f"{_shown(field.runtime_status)}; "
                f"{_shown(RUNTIME_STATUS_DERIVED)} is required to omit the block"
            )
    if fields[LANDING_POLICY_TYPE].is_read_from_record:
        raise FieldMapError(
            f"the field map places landing key {_shown(LANDING_POLICY_TYPE)} at bytes "
            f"{_window_range(*windows[str(fields[LANDING_POLICY_TYPE].item)][:2])}; it "
            "is derived from the request id and is not read from the record"
        )
    if fields[LANDING_REQUEST_ID].kind != KIND_ALPHANUMERIC:
        raise FieldMapError(
            f"the field map records landing key {_shown(LANDING_REQUEST_ID)} as kind "
            f"{_display(fields[LANDING_REQUEST_ID].kind)}; kind "
            f"{_shown(KIND_ALPHANUMERIC)} is required"
        )
    return_code_field = fields[LANDING_RETURN_CODE]
    if return_code_field.kind != KIND_NUMERIC:
        raise FieldMapError(
            f"the field map records landing key {_shown(LANDING_RETURN_CODE)} as kind "
            f"{_display(return_code_field.kind)}; kind {_shown(KIND_NUMERIC)} is "
            "required"
        )
    domain = return_code_field.domain
    if not domain:
        raise FieldMapError(
            f"the field map records no 'domain' for landing key "
            f"{_shown(LANDING_RETURN_CODE)}"
        )
    expected_width = return_code_field.length
    for code in domain:
        if len(code) != expected_width or not _ASCII_DIGITS.fullmatch(code):
            raise FieldMapError(
                f"the field map records {_shown(code)} in the domain of "
                f"{_shown(LANDING_RETURN_CODE)}; {expected_width} digits are required"
            )
    if RETURN_CODE_SUCCESS not in domain:
        raise FieldMapError(
            f"the field map's domain for {_shown(LANDING_RETURN_CODE)} omits "
            f"{_shown(RETURN_CODE_SUCCESS)}"
        )

    return FieldMap(
        path=path,
        record_length=record_length,
        field_order=field_order,
        fields=fields,
        routing=routing,
        amount_fields=amount_fields,
        always_populated=always_populated,
        nullability=nullability,
        return_code_domain=domain,
        source_system_key_field=source_system_key_field,
        source_system_key_run_value=source_system_key_run_value,
        chain_populated=frozenset(
            name
            for name, field in fields.items()
            if field.populated_by == POPULATED_BY_CHAIN
        ),
        unrecognised_request_return_code=unrecognised_return_code,
    )


# ---------------------------------------------------------------------------
# Decoding
# ---------------------------------------------------------------------------


def slice_field(record: str, offset: int, length: int) -> str:
    """Return the window ``record`` holds at 1-based inclusive ``offset``.

    The window is ``record[offset - 1 : offset - 1 + length]``. Raises
    ``FieldMapError`` for an offset or length below one and ``RecordError`` when the
    window reaches past the end of ``record``.
    """
    if offset < 1 or length < 1:
        raise FieldMapError(
            f"a window at offset {offset} of length {length} is not addressable; both "
            "must be at least 1"
        )
    start = offset - 1
    end = start + length
    if end > len(record):
        raise RecordError(
            f"a window at bytes {_window_range(offset, length)} reaches past the "
            f"{len(record)}-character record"
        )
    return record[start:end]


def decode_alphanumeric(window: str) -> str | None:
    """Return ``window`` without leading or trailing spaces, or None when it is blank.

    A window holding only spaces decodes to None, which lands as JSON null rather than
    as an empty string.
    """
    trimmed = window.strip(" ")
    return trimmed or None


def decode_numeric_display(field: LandingField, window: str) -> str:
    """Return the digits of ``window`` with leading zeros stripped.

    ``window`` must hold digits only; all zeros decode to ``'0'`` so at least one digit
    is always carried. Raises ``RecordError`` naming the item, its byte range and the
    characters outside 0-9 when the window holds anything else. No arithmetic is
    applied: the returned text holds the digits the record carries.
    """
    if not _ASCII_DIGITS.fullmatch(window):
        raise RecordError(
            f"{field.described} holds {_shown(window)}, which is not all digits; the "
            f"characters outside 0-9 are {_offending_characters(window)}"
        )
    return window.lstrip("0") or "0"


def decode_window(field: LandingField, record: str) -> str | None:
    """Return one landing value decoded from the record by the field's recorded kind.

    Raises ``FieldMapError`` when the field carries no window or records a kind this
    tool does not decode, and ``RecordError`` when the window content breaches the
    kind.
    """
    if not field.is_read_from_record:
        raise FieldMapError(
            f"the field map records no 'commarea' block for landing key "
            f"{_shown(field.name)}, so it cannot be decoded from the record"
        )
    assert field.offset is not None and field.length is not None
    window = slice_field(record, field.offset, field.length)
    if field.kind == KIND_ALPHANUMERIC:
        return decode_alphanumeric(window)
    if field.kind == KIND_NUMERIC:
        return decode_numeric_display(field, window)
    raise FieldMapError(
        f"the field map records landing key {_shown(field.name)} as kind "
        f"{_display(field.kind)}; one of {_quote_all(KNOWN_KINDS)} is required"
    )


def decode_return_code(field: LandingField, record: str) -> str:
    """Return the returned ``CA-RETURN-CODE`` as a zero-padded string of its own width.

    The window is carried verbatim: a leading zero is never stripped and the value is
    never converted to an integer. Raises ``RecordError`` when the window is not all
    digits or holds a value outside the domain the field map records.
    """
    assert field.offset is not None and field.length is not None
    window = slice_field(record, field.offset, field.length)
    if not _ASCII_DIGITS.fullmatch(window):
        raise RecordError(
            f"{field.described} holds {_shown(window)}, which is not all digits; the "
            f"chain writes one of {_quote_all(field.domain)} there"
        )
    if window not in field.domain:
        raise RecordError(
            f"{field.described} holds {_shown(window)}, which is outside the recorded "
            f"domain {_quote_all(field.domain)}"
        )
    return window


# ---------------------------------------------------------------------------
# Derivation and normalisation
# ---------------------------------------------------------------------------


def derive_policy_type(request_id: str, field_map: FieldMap) -> str:
    """Return the one-character policy type the field map routes ``request_id`` to.

    The routing table is ``request_routing.map`` in the field map, which records the
    request-id to policy-type assignments of the EVALUATE at
    base/src/lgapdb01.cbl:184-207. ``request_id`` is the trimmed ``CA-REQUEST-ID``
    value.

    Raises ``RecordError`` naming the accepted request ids when the table holds no
    entry for ``request_id``. No default letter is substituted and no other source is
    consulted.
    """
    policy_type = field_map.routing.get(request_id)
    if policy_type is None:
        raise RecordError(
            f"the record carries request id {_shown(request_id)}, which the field "
            "map's request routing does not recognise; the routed request ids are "
            f"{_quote_all(sorted(field_map.routing))}, and the chain returns "
            f"{_shown(field_map.unrecognised_request_return_code)} for any other"
        )
    return policy_type


def normalise_timestamp(raw: str, field: LandingField) -> str:
    """Return ``raw`` as an ISO-8601 timestamp with microsecond precision.

    ``raw`` is the trimmed ``CA-LASTCHANGED`` value the chain read back from the POLICY
    row. Every form listed in ``TIMESTAMP_INPUT_FORMATS`` is accepted, in that order:
    the Db2 character form ``YYYY-MM-DD-HH.MM.SS.ffffff`` and the ISO forms using a
    ``T`` or a space separator with colons in the time part, each with or without the
    fractional-second part. The result is emitted as
    ``YYYY-MM-DDTHH:MM:SS.ffffff``; a fractional part shorter than six digits is
    carried at microsecond precision and no value is truncated or rounded.

    Raises ``RecordError`` naming the item, its byte range and the raw characters when
    no accepted form matches, when the calendar values are not a real date and time, or
    when ``raw`` is empty. The current wall-clock time is never substituted.
    """
    if not raw:
        raise RecordError(
            f"{field.described} holds no timestamp; the chain reads one back into it "
            f"from the POLICY row "
            f"({_quote_all(field.evidence) or 'no locator recorded'})"
        )
    for accepted in TIMESTAMP_INPUT_FORMATS:
        try:
            moment = datetime.datetime.strptime(raw, accepted)
        except ValueError:
            continue
        return moment.isoformat(
            sep=TIMESTAMP_OUTPUT_SEPARATOR, timespec=TIMESTAMP_OUTPUT_PRECISION
        )
    raise RecordError(
        f"{field.described} holds {_shown(raw)}, which matches none of the accepted "
        f"timestamp forms {_quote_all(TIMESTAMP_INPUT_FORMATS)}"
    )


def amount_applies(name: str, policy_type: str, field_map: FieldMap) -> bool:
    """Return True when the field map populates amount ``name`` for ``policy_type``.

    The answer is read from ``product_premium_nullability``: the amount keys the map
    records as always populated together with those it lists as populated for this
    policy type. ``load_field_map`` has already confirmed that this split agrees with
    each amount entry's ``applicable_policy_types`` in both directions.

    Raises ``FieldMapError`` when the map records no split for ``policy_type`` or when
    ``name`` is not one of its amount keys.
    """
    if name not in field_map.amount_fields:
        raise FieldMapError(
            f"landing key {_shown(name)} is not one of the field map's amounts "
            f"{_quote_all(field_map.amount_fields)}"
        )
    split = field_map.nullability.get(policy_type)
    if split is None:
        raise FieldMapError(
            f"the field map records no product premium nullability for policy type "
            f"{_shown(policy_type)}; it records "
            f"{_quote_all(sorted(field_map.nullability))}"
        )
    return name in split[0]


def decode_amount(
    field: LandingField, record: str, policy_type: str, field_map: FieldMap
) -> str | None:
    """Return one amount as the digits the record carries, or None when inapplicable.

    An amount the field map does not populate for ``policy_type`` returns None, and its
    window is not read. The product overlays redefine the same bytes, and the window of
    an unselected overlay holds the selected overlay's content. An applicable window is
    validated as all digits and returned with leading zeros stripped. No arithmetic is
    applied: no scaling, rounding, defaulting or unit conversion touches the value.

    Raises ``RecordError`` naming the item and its byte range when an applicable window
    is not all digits.
    """
    if not amount_applies(field.name, policy_type, field_map):
        return None
    assert field.offset is not None and field.length is not None
    return decode_numeric_display(
        field, slice_field(record, field.offset, field.length)
    )


# ---------------------------------------------------------------------------
# Landing record
# ---------------------------------------------------------------------------


def _decode_chain_populated(field: LandingField, record: str) -> str | None:
    """Return one chain-assigned value, or None when the chain left the window blank.

    A window holding only spaces returns None whatever the field's kind. An unassigned
    value reaches the return-code checks as absent rather than as a decoding failure. A
    window holding content is decoded by the field's recorded kind.
    """
    assert field.offset is not None and field.length is not None
    window = slice_field(record, field.offset, field.length)
    if not window.strip(" "):
        return None
    if field.kind == KIND_ALPHANUMERIC:
        return decode_alphanumeric(window)
    return decode_numeric_display(field, window)


def _require_assigned(field: LandingField, value: str | None) -> str:
    """Return ``value``, raising ``RecordError`` when the chain left it unassigned.

    An absent value and a numeric value of only zeros both raise, and the diagnostic
    names the item, its byte range and every locator the field map cites for the field.
    """
    locators = _quote_all(field.evidence) or "no locator recorded"
    if value is None:
        raise RecordError(
            f"{field.described} is blank on a record whose return code is "
            f"{_shown(RETURN_CODE_SUCCESS)}; the chain assigns it, per {locators}"
        )
    if field.kind == KIND_NUMERIC and value == "0":
        raise RecordError(
            f"{field.described} holds only zeros on a record whose return code is "
            f"{_shown(RETURN_CODE_SUCCESS)}; the chain assigns a non-zero value, per "
            f"{locators}"
        )
    return value


def build_landing_record(
    record: str,
    field_map: FieldMap,
    source_system_key: str,
    *,
    allow_nonzero_return_code: bool = False,
) -> dict[str, str | None]:
    """Return the landing record decoded from one post-chain COMMAREA record.

    ``record`` is the fixed-width record ``read_commarea`` returned, ``field_map`` the
    validated map and ``source_system_key`` the discriminator to write. The returned
    mapping holds the field map's ``landing.field_order`` keys, in that order, and
    every value is a string or None. ``allow_nonzero_return_code`` lands a record whose
    returned ``CA-RETURN-CODE`` is not ``RETURN_CODE_SUCCESS``; on such a record a value
    the chain assigns lands as None where its window is blank and as the digits it holds
    where the window carries them; a zero-filled window lands as ``'0'``.

    Raises ``RecordError`` when the request id is not routed, when the return code is
    outside the recorded domain, when the return code is not ``RETURN_CODE_SUCCESS``
    and ``allow_nonzero_return_code`` is not set, when an applicable amount window is
    not all digits, when the returned timestamp cannot be normalised, or when a value
    the chain assigns is unassigned on a record whose return code is
    ``RETURN_CODE_SUCCESS``. Raises ``FieldMapError`` when the assembled keys do not
    match ``landing.field_order`` or a value is not a string or None.
    """
    request_id = decode_window(field_map.fields[LANDING_REQUEST_ID], record)
    if request_id is None:
        raise RecordError(
            f"{field_map.fields[LANDING_REQUEST_ID].described} is blank; the chain "
            "routes on it"
        )
    return_code = decode_return_code(field_map.fields[LANDING_RETURN_CODE], record)
    if return_code != RETURN_CODE_SUCCESS and not allow_nonzero_return_code:
        raise RecordError(
            f"{field_map.fields[LANDING_RETURN_CODE].described} holds "
            f"{_shown(return_code)} rather than {_shown(RETURN_CODE_SUCCESS)}; pass "
            "--allow-nonzero-return-code to land the record as failure evidence"
        )
    policy_type = derive_policy_type(request_id, field_map)

    values: dict[str, str | None] = {}
    for name in field_map.field_order:
        if name == field_map.source_system_key_field:
            values[name] = source_system_key
            continue
        field = field_map.fields[name]
        if name == LANDING_REQUEST_ID:
            values[name] = request_id
        elif name == LANDING_RETURN_CODE:
            values[name] = return_code
        elif name == LANDING_POLICY_TYPE:
            values[name] = policy_type
        elif name in field_map.amount_fields:
            values[name] = decode_amount(field, record, policy_type, field_map)
        elif name in field_map.chain_populated:
            decoded = _decode_chain_populated(field, record)
            if name == LANDING_LAST_CHANGED and decoded is not None:
                decoded = normalise_timestamp(decoded, field)
            values[name] = decoded
        else:
            values[name] = decode_window(field, record)

    if return_code == RETURN_CODE_SUCCESS:
        for name in field_map.field_order:
            if name == LANDING_RETURN_CODE or name not in field_map.chain_populated:
                continue
            _require_assigned(field_map.fields[name], values[name])

    if tuple(values) != field_map.field_order:
        absent = sorted(set(field_map.field_order) - set(values))
        extra = sorted(set(values) - set(field_map.field_order))
        raise FieldMapError(
            "the assembled landing record does not carry the field map's landing "
            f"keys in order: absent {_quote_all(absent) or 'none'}, unexpected "
            f"{_quote_all(extra) or 'none'}"
        )
    for name, value in values.items():
        if value is not None and not isinstance(value, str):
            raise FieldMapError(
                f"the assembled landing record carries {_display(value)} for "
                f"{_shown(name)}; a string or null is required"
            )
    return values


def serialise_record(
    record: Mapping[str, str | None], field_order: Sequence[str]
) -> str:
    """Return the landing record as one JSON line terminated by one line feed.

    The keys are emitted in the order ``record`` carries them, which must be exactly
    ``field_order``. Text is escaped to ASCII and no key is re-sorted. The emitted order
    is the field map's landing order.

    Raises ``FieldMapError`` when the keys do not match ``field_order`` or a value is
    not a string or None.
    """
    if tuple(record) != tuple(field_order):
        raise FieldMapError(
            "the landing record does not carry the field map's landing keys in order: "
            f"expected {_quote_all(field_order)}, carried {_quote_all(record)}"
        )
    for name, value in record.items():
        if value is not None and not isinstance(value, str):
            raise FieldMapError(
                f"the landing record carries {_display(value)} for {_shown(name)}; a "
                "string or null is required"
            )
    return json.dumps(dict(record), ensure_ascii=True) + "\n"


def _created_file_mode() -> int:
    """Return the mode a newly created file requests, with the process umask applied.

    The umask is read by setting it and restoring it immediately. The landed record
    carries the same mode as any other file this bridge creates.
    """
    mask = os.umask(0)
    os.umask(mask)
    return 0o666 & ~mask


def _refuse_read_only_destination(destination: Path) -> None:
    """Raise ``InputOutputError`` when ``destination`` resolves inside base/."""
    absolute = Path(os.path.abspath(destination))
    if absolute == READ_ONLY_SOURCE_ROOT or READ_ONLY_SOURCE_ROOT in absolute.parents:
        raise InputOutputError(
            f"the destination resolves inside the read-only source directory "
            f"{_path_shown(READ_ONLY_SOURCE_ROOT)}: {_path_shown(destination)}"
        )


def write_record(
    record: Mapping[str, str | None], destination: Path, field_order: Sequence[str]
) -> Path:
    """Write the landing record to ``destination`` and return the path written.

    Missing parent directories are created. The serialised line is written to a
    temporary entry in the destination's own directory, flushed to disk and moved onto
    the destination name. A reader never observes a partial record. An existing
    destination is replaced only when it is a regular file and is not a symbolic link.

    Raises ``FieldMapError`` when the record does not match ``field_order`` and
    ``InputOutputError`` when the destination is refused, cannot be created or cannot
    be written.
    """
    text = serialise_record(record, field_order)
    _refuse_read_only_destination(destination)
    if destination.is_symlink():
        raise InputOutputError(
            f"the destination is a symbolic link: {_path_shown(destination)}"
        )
    if destination.exists() and not destination.is_file():
        raise InputOutputError(
            f"the destination exists and is not a regular file: "
            f"{_path_shown(destination)}"
        )
    directory = destination.parent if str(destination.parent) else Path(".")
    try:
        directory.mkdir(mode=DIRECTORY_MODE, parents=True, exist_ok=True)
    except OSError as error:
        raise InputOutputError(
            f"the destination directory cannot be created: {_path_shown(directory)}: "
            f"{_reason(error)}"
        ) from error
    _refuse_read_only_destination(Path(os.path.realpath(directory)) / destination.name)

    encoded = text.encode(CAPTURE_ENCODING)
    mode = _created_file_mode()
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    temporary: Path | None = None
    descriptor = -1
    for attempt in range(MAX_TEMPORARY_ATTEMPTS):
        candidate = directory / f".{destination.name}.{os.getpid()}.{attempt}.tmp"
        try:
            descriptor = os.open(candidate, flags, mode)
        except FileExistsError:
            continue
        except OSError as error:
            raise InputOutputError(
                f"the destination cannot be written through a temporary entry: "
                f"{_path_shown(candidate)}: {_reason(error)}"
            ) from error
        temporary = candidate
        break
    if temporary is None or descriptor < 0:
        raise InputOutputError(
            f"no temporary entry could be created beside the destination after "
            f"{MAX_TEMPORARY_ATTEMPTS} attempts: {_path_shown(destination)}"
        )
    try:
        try:
            written = 0
            while written < len(encoded):
                written += os.write(descriptor, encoded[written:])
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        os.replace(temporary, destination)
        temporary = None
    except OSError as error:
        raise InputOutputError(
            f"the landing record cannot be written: {_path_shown(destination)}: "
            f"{_reason(error)}"
        ) from error
    finally:
        if temporary is not None:
            try:
                os.unlink(temporary)
            except OSError:
                pass
    try:
        directory_descriptor = os.open(directory, os.O_RDONLY)
    except OSError:
        return destination
    try:
        os.fsync(directory_descriptor)
    except OSError:
        pass
    finally:
        os.close(directory_descriptor)
    return destination


def summarise(destination: Path, record: Mapping[str, str | None]) -> str:
    """Return the one-line stdout summary of a written landing record."""

    def shown(name: str) -> str:
        value = record.get(name)
        return "null" if value is None else value

    return (
        f"landed {destination} "
        f"{LANDING_REQUEST_ID}={shown(LANDING_REQUEST_ID)} "
        f"{LANDING_POLICY_TYPE}={shown(LANDING_POLICY_TYPE)} "
        f"{LANDING_POLICY_NUMBER}={shown(LANDING_POLICY_NUMBER)} "
        f"{LANDING_RETURN_CODE}={shown(LANDING_RETURN_CODE)}"
    )


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------


class _CommandLineParser(argparse.ArgumentParser):
    """Command line parser that raises ``UsageError`` instead of printing usage text.

    ``-h`` and ``--help`` keep printing the full help and exiting with status 0. Every
    other command line failure becomes one bounded, control-free diagnostic carried by
    ``UsageError``, which reaches stderr as one line.
    """

    def error(self, message: str) -> NoReturn:
        """Raise ``UsageError`` carrying ``message``, bounded and control-free."""
        raise UsageError(
            "command line rejected: "
            f"{_escaped(message, MAX_DIAGNOSTIC_MESSAGE_CHARACTERS)}; run "
            f"'{_PROGRAM} --help' for the accepted arguments"
        )


def build_arg_parser() -> argparse.ArgumentParser:
    """Return the non-interactive command line parser for this tool."""
    parser = _CommandLineParser(
        prog=_PROGRAM,
        description=(
            "Decode the post-chain GenApp Policy-Issue COMMAREA capture and write the\n"
            "landing JSON record: one object holding the landing keys the field map\n"
            "lists, as JSON strings or null, on one line terminated by one line feed.\n"
            "\n"
            "Exit status: 0 success, 2 capture rejected, 3 field map invalid, 4 input\n"
            "failure, output refused or command line rejected."
        ),
        epilog=(
            "Every offset, length, kind, routing entry, nullability rule and landing "
            "key is read from the field map; none is written into this tool. The "
            "capture must hold exactly "
            f"{COMMAREA_RECORD_LENGTH} characters, optionally followed by one line "
            "ending, and is decoded as "
            f"{CAPTURE_ENCODING}. policy_type is derived from the request id through "
            "the map's request_routing table and is the only derived value; no amount "
            "is derived, and a premium the derived policy type does not apply to is "
            "written as null rather than as a zero. CA-LASTCHANGED is normalised to "
            "ISO-8601 and is never replaced by the current time. Neither input is "
            "modified, and no path outside the destination is written.\n"
            "Every failure writes one control-free line to stderr and returns 2 for a "
            "rejected capture, 3 for an inconsistent field map, or 4 for an unreadable "
            "input, a refused output or a usage error.\n"
            "Decision rationale: modernization/docs/decision-log.md"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--commarea",
        required=True,
        type=Path,
        metavar="PATH",
        help=(
            "post-chain COMMAREA capture written by the harness driver: "
            f"{COMMAREA_RECORD_LENGTH} characters and at most one trailing line ending"
        ),
    )
    parser.add_argument(
        "--field-map",
        default=DEFAULT_FIELD_MAP,
        type=Path,
        metavar="PATH",
        help=(
            "field map supplying every offset, length, kind, routing entry and landing "
            f"key (default: {DEFAULT_FIELD_MAP.name} beside this script)"
        ),
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        metavar="PATH",
        help="destination for the landing JSON record; parent directories are created",
    )
    parser.add_argument(
        "--source-system-key",
        default=None,
        metavar="VALUE",
        help=(
            "source-system discriminator written to the record; defaults to the "
            f"{SOURCE_SYSTEM_KEY_VARIABLE} environment variable, then to "
            f"{DEFAULT_SOURCE_SYSTEM_KEY}. At most "
            f"{MAX_SOURCE_SYSTEM_KEY_CHARACTERS} characters drawn from ASCII letters, "
            "digits, underscore, dot and hyphen"
        ),
    )
    parser.add_argument(
        "--allow-nonzero-return-code",
        action="store_true",
        help=(
            "land the record even when the returned CA-RETURN-CODE is not "
            f"{RETURN_CODE_SUCCESS}; without this flag any other code is rejected"
        ),
    )
    return parser


def resolve_source_system_key(supplied: str | None) -> str:
    """Return the source-system key to write, taking the first value that is present.

    ``supplied`` is the ``--source-system-key`` value, or None when the option was
    omitted, in which case the ``SOURCE_SYSTEM_KEY`` environment variable is consulted
    and then ``DEFAULT_SOURCE_SYSTEM_KEY``. Raises ``UsageError`` when the resolved
    value is empty, longer than ``MAX_SOURCE_SYSTEM_KEY_CHARACTERS`` or carries a
    character outside the accepted set.
    """
    if supplied is not None:
        value = supplied
        origin = "--source-system-key"
    else:
        from_environment = os.environ.get(SOURCE_SYSTEM_KEY_VARIABLE)
        if from_environment is not None:
            value = from_environment
            origin = f"the {SOURCE_SYSTEM_KEY_VARIABLE} environment variable"
        else:
            value = DEFAULT_SOURCE_SYSTEM_KEY
            origin = "the built-in default"
    if not value:
        raise UsageError(f"the source-system key from {origin} is empty")
    if len(value) > MAX_SOURCE_SYSTEM_KEY_CHARACTERS:
        raise UsageError(
            f"the source-system key from {origin} holds {len(value)} characters: "
            f"{_shown(value)}; at most {MAX_SOURCE_SYSTEM_KEY_CHARACTERS} are accepted"
        )
    if not _SOURCE_SYSTEM_KEY_SHAPE.fullmatch(value):
        raise UsageError(
            f"the source-system key from {origin} carries a character outside ASCII "
            f"letters, digits, underscore, dot and hyphen: {_shown(value)}"
        )
    return value


def main(argv: list[str] | None = None) -> int:
    """Decode one capture and write one landing record, returning the exit status.

    ``argv`` defaults to the process arguments. Every diagnostic reaches stderr as one
    control-free line and the success summary reaches stdout the same way. A rejected
    command line is reported through that same single line, without a usage block, and
    returns the status a refused input or output returns, while ``--help`` prints the
    full help and exits with status 0.
    """
    parser = build_arg_parser()
    try:
        args = parser.parse_args(argv)
        source_system_key = resolve_source_system_key(args.source_system_key)
        field_map = load_field_map(args.field_map)
        capture = read_commarea(args.commarea, field_map.record_length)
        record = build_landing_record(
            capture,
            field_map,
            source_system_key,
            allow_nonzero_return_code=args.allow_nonzero_return_code,
        )
        written = write_record(record, args.output, field_map.field_order)
    except ExtractError as error:
        print(f"{_PROGRAM}: {_one_line(str(error))}", file=sys.stderr)
        return error.exit_status

    print(_one_line(summarise(written, record)))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
