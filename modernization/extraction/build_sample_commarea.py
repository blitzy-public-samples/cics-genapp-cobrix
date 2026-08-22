#!/usr/bin/env python3
"""Build one executable GenApp Policy-Issue COMMAREA record from a sample definition.

WHAT THIS TOOL DOES
    Reads a flat JSON sample definition, validates it against the
    ``sample_definition_contract`` recorded in ``copybook_field_map.yml``, and writes a
    single fixed-width record of exactly 32,500 characters followed by one newline.

WHICH INPUTS IT ACCEPTS
    --sample       one sample definition JSON document, keyed by COMMAREA item name,
                   holding at most 65,536 bytes of UTF-8 text (``MAX_SAMPLE_BYTES``).
    --field-map    the field map supplying every offset, length and kind, holding at
                   most 1,048,576 bytes of UTF-8 text (``MAX_FIELD_MAP_BYTES``)
                   (default: ``copybook_field_map.yml`` beside this script).
    --output       destination path for the generated record.
    --output-root  existing directory inside the validated generated-output root that
                   the destination must resolve inside, replacing that root as the
                   directory every write descends from; no directory outside it is
                   accepted.

    Both documents are read under the byte bound above before anything parses them, and
    both are parsed with a repeated key rejected at every nesting level. The sample
    definition's text is handed to ``json.loads``, whose own recursion guard rejects
    text nested past it, and the object that parse returns is then rejected when it
    nests more than ``MAX_DOCUMENT_DEPTH`` containers or expands past
    ``MAX_DOCUMENT_NODES`` values. The field map is bounded to the same depth while its
    nodes are composed, where neither a YAML alias nor a merge key is accepted, and the
    mapping that composition returns is bounded again by nesting and value count.

WHICH FIELD MAP MEMBERS ARE FIXED
    Loading confirms, before any routing, rendering or allocation, that
    ``record.length`` and ``sample_definition_contract.emitted_record_length`` are
    both 32,500, that ``value_padding`` is the digit zero for ``numeric_display`` and
    one space for ``alphanumeric``, that ``value_justification`` is right for
    ``numeric_display`` and left for ``alphanumeric``, that ``fill_by_kind`` is
    ``zeros`` for ``numeric_display`` and ``spaces`` for ``alphanumeric``, and that
    every layout item flagged ``chain_required_numeric`` records kind
    ``numeric_display``. Loading also
    confirms the container and element types of every member this builder reads: each
    ``layout`` group name and each ``request_routing.map`` request id is a non-empty
    string, and ``sample_definition_contract.required_keys``, where it is recorded, is a
    sequence whose every element is a non-empty string. Members this builder does not
    read are ignored.
    --self-test    run the built-in case matrix instead of building a record; it accepts
                   no --sample and no --output.

    Every path argument must be UTF-8 text free of control characters, and its ``.``
    and ``..`` components are collapsed without consulting the filesystem, so no
    symbolic link is followed while the argument is normalised. A path read by this
    tool must sit inside ``modernization/extraction/`` or
    ``modernization/harness/build/``. The generated record is written inside
    ``modernization/harness/build/``, or inside the directory ``--output-root`` names,
    which must itself resolve inside that same ``modernization/harness/build/``
    directory; no destination and no root outside it is accepted, the system temporary
    directory included. An existing destination is replaced only when it is a regular
    file and is not a symbolic link. Both read directories are composed by name from the
    repository root two levels above this script's own directory; every working
    directory yields the same two directories. A symbolic link among the components of
    either directory, or among the components of a path argument below it, is refused
    rather than followed. Each input is opened once, with the leaf refused when it is a
    symbolic link, and is read from that one open descriptor. The complete file status
    of that descriptor is examined before any byte is read: the inode carries exactly
    one link, and it sits on the device its authorised input directory sits on. The
    record is written to a temporary file created inside the destination directory,
    moved onto the destination name and read back through one descriptor held open on
    that directory. The built-in self-test runs in this process and keeps every scratch
    document it reads and every destination it offers inside one private run directory
    ``modernization/harness/build/builder-selftest/<run>``, which it creates and removes
    through descriptors held on its parents and which is therefore covered by the read
    and write roots above; no command line names it and nothing of it survives the run.
    Every fixture entry, subdirectory, FIFO and symbolic link below that run directory
    is created, read, listed, renamed and removed relative to the descriptor held on it
    and never through a resolved pathname. Where a run under test must be handed a
    pathname, the destination argument names the entry below ``/proc/self/fd/<held
    descriptor>``, so it follows the held directory rather than the visible name, and
    the input and output-root arguments, which this tool refuses to reach through a
    symbolic-link component, name the canonical path; the held directory is confirmed to
    still carry the recorded device and inode, and to still be named by the entry it was
    created under, immediately before and immediately after every such handoff. The
    closing removal empties and removes the originally held directory, found through the
    held descriptor's own pathname, and reports a failure when the visible run name was
    replaced after the directory was acquired.

HOW FIELDS ARE PLACED
    The buffer starts as spaces at ``COMMAREA_RECORD_LENGTH`` characters. Placement
    covers the base ``layout`` groups plus the one overlay group that
    ``request_routing`` selects for the sample's request id. Items carrying a
    ``redefined_by`` list are not placed; the items that redefine them are placed
    instead. A ``numeric_display`` window receives the supplied value right-justified
    and zero-padded, and all zeros when the sample omits the item. An ``alphanumeric``
    window receives the supplied value left-justified and space-padded, and stays
    spaces when the sample omits the item. A window the chain assigns receives the
    content ``sample_definition_contract.chain_populated_items`` states for it instead:
    the padding character of its kind across the whole window where the entry records a
    ``fill``, or the literal it records as its ``seed``. That section is required to
    hold exactly one entry per logical entry recording ``populated_by: chain``, each
    entry's ``kind`` must be the kind the layout declares for the item, and a ``seed``
    must be as long as the window, must hold digits only for a numeric window and must
    stand outside the ``domain`` the item's logical entry declares, so a seeded window
    holds no value the chain produces. The assembled record is compared with that stated
    content before it is written. The record is always emitted at
    ``COMMAREA_RECORD_LENGTH`` characters followed by one newline, and the field map
    must declare that same length under both ``record.length`` and
    ``sample_definition_contract.emitted_record_length``.

WHAT A SAMPLE DEFINITION MAY NOT CONTAIN
    An unknown key, a key of an overlay the request id does not select, a key the
    chain assigns, a key naming one of the ``PROTECTED_FILL_ITEMS`` filler or padding
    items, a repeated key, two keys that name one item, a non-string value, an empty
    value, a value longer than the declared item length, a non-digit value for a
    numeric item, or a character outside printable 7-bit ASCII for an alphanumeric
    item. Each input must be one regular file. Documents above ``MAX_SAMPLE_BYTES``,
    above ``MAX_SAMPLE_KEYS`` keys, nested deeper than ``MAX_DOCUMENT_DEPTH``
    containers or expanding past ``MAX_DOCUMENT_NODES`` values are rejected unread or
    unused, as is a field map above ``MAX_FIELD_MAP_BYTES`` or breaching the same
    nesting limits. A document holding a container that appears inside itself is
    rejected, and a field map that repeats a mapping key or carries a key this tool
    cannot compare is rejected rather than resolved to its last value.

WHAT --self-test CHECKS
    It parses ``base/src/lgcmarea.cpy`` for every item offset, length and kind without
    reading the field map, compares that parse with the field map's exercised layout
    entries in both directions, asserts each fixture's exact supplied key set, the
    fill or the stated chain-populated content of every window it omits and its rendered
    bytes against a table of literal expected window contents, confirms that
    ``chain_populated_items``, the logical entries, the copybook parse and that table
    state the same pre-execution content, and runs the failure matrix: mutated field
    maps, including a chain-populated seed inside its declared domain, a seed of the
    wrong length, a non-digit seed for a numeric window, a chain-populated item missing
    from the section and a foreign item present in it, rejected sample definitions,
    including two keys that name one item by differing
    case, a record one character short of and one character past the emitted length
    offered to the writer, an unwritable output, an unreadable field map, an input that
    is not a regular file, a rerun comparison, a non-zero commercial status placement,
    a full-width commercial address, the motor record's inactive commercial windows,
    short values of both kinds, a numeric justification mutation compared byte for byte
    against the literal window it moves, a protected filler's fill mutation, an output
    root outside the validated generated-output root, an output root reached through a
    symbolic link, a destination reached through a symbolic link that leaves that root,
    the removal of a scratch subtree through held descriptors, the replacement of a
    private run directory's visible name by a symbolic link naming a canary directory
    outside it, which must refuse the pathname handoff, keep every write inside the held
    directory, land one whole record a run writes below the held descriptor's own
    pathname there as well, leave the canary empty and still remove the originally held
    directory, and the literal cases, withheld statements and dbt test of the field
    map's product premium nullability claim. Every case prints one line, and a failing
    case leaves status 5.

WHICH VALUES IT ACCEPTS
    A required item must be supplied with one or more characters. An optional item may
    be omitted, which leaves its window filled with the padding character of its kind;
    a key present with an empty string is rejected instead, and the diagnostic names the
    key and asks for it to be omitted. A supplied value no longer than its declared length holds ASCII digits for a
    ``numeric_display`` item and printable 7-bit ASCII for an ``alphanumeric`` item; it
    stays within ``moved_to_max_value`` where the layout records the host declaration
    the chain moves it into, and is a real calendar date written as YYYY-MM-DD where the
    layout records ``value_semantics: iso_date``.

HOW IT FAILS
    Every failure writes one diagnostic line to stderr and returns a non-zero status:
    2 for a rejected sample definition, 3 for an internally inconsistent field map,
    4 for an unreadable input or an unwritable output, 5 for a failed self-test case.
    Diagnostics carry untrusted text escaped to one printable 7-bit ASCII line. The
    tool never prompts and requires no TTY. On success it writes one summary line to
    stdout.

GENERATED-OUTPUT POLICY
    One policy governs every path this bridge writes: a generated record or translated
    copy resolves inside ``modernization/harness/build/`` and a generated evidence log
    resolves inside ``modernization/validation/artifacts/``. That build directory is
    itself validated before anything is written: it must canonicalise to exactly
    ``modernization/harness/build`` under the canonical repository directory that holds
    this script, and no component from that repository directory down to it may be a
    symbolic link. An explicitly designated root replaces it only while resolving inside
    that same validated directory, so no path this tool writes ever leaves
    ``modernization/``. Every destination is canonicalised through its symbolic links
    before anything is created; a symbolic link, an existing non-regular target and
    every path under the repository's ``base/`` directory are refused, no authored or
    source path is reachable, and every value carried into a diagnostic or an evidence
    record is escaped to one control-free line. This tool enforces the policy for
    generated records; ``modernization/validation/verify_readonly.sh`` enforces it for
    evidence logs.

WHERE IT WRITES
    The destination is canonicalised and must resolve inside the validated
    ``modernization/harness/build`` directory described above, unless --output-root
    names an existing directory that contains it, carries no symbolic-link component
    and resolves inside that same validated directory. A root resolving anywhere else,
    the system temporary directory and a directory whose trailing components merely
    spell ``modernization/harness/build`` included, is refused. A destination resolving
    inside the repository must resolve inside the validated
    ``modernization/harness/build`` directory whichever root is in force, and a
    destination resolving inside the repository's ``base/`` directory is refused.
    A destination that is a symbolic link, that already exists as anything other than a
    regular file, or whose canonical form leaves the allowed root is refused before any
    directory is created and before any temporary entry is written.

    The write itself runs through descriptors alone. The directory the destination is
    reached from is opened while the destination is validated, one single component at a
    time and following no symbolic link at any level: the canonical repository directory
    holding this script, descended from the filesystem root, under the default root, and
    --output-root itself, descended from the descriptor held on
    ``modernization/harness/build``, when one is named. That
    descriptor is confirmed to still hold the directory the canonical path names, is the
    only object the write descends from, and the anchor is never resolved as a pathname
    again. Every directory below it is created where absent and opened by single
    component relative to the descriptor above it, so a symbolic link is refused at
    every level. The temporary entry is created exclusively relative to the descriptor
    holding the destination, flushed to the device, renamed onto the destination name
    through that same descriptor, and read back through it for a byte-for-byte
    comparison with the 32,501 bytes rendered.

HOW IT FAILS
    Every failure writes one diagnostic to stderr as a single line free of control
    characters and of complete supplied values, and returns a non-zero status: 2 for a
    rejected sample definition, 3 for an internally inconsistent field map, 4 for an
    unreadable input, a refused output or a usage error. The tool never prompts and
    requires no TTY. ``--help`` prints the full help and exits with status 0. On success
    it writes one summary line to stdout.

Decision rationale for this component belongs to modernization/docs/decision-log.md.
"""

from __future__ import annotations

import argparse
import contextlib
import copy
import datetime
import io
import json
import os
import re
import stat
import sys
from collections.abc import Callable, Iterable, Iterator
from pathlib import Path
from typing import Any, NamedTuple, NoReturn, TypeVar

import yaml

_PROGRAM = "build_sample_commarea"

# Field map used when --field-map is omitted, resolved from this script's own directory.
_THIS_DIR = Path(__file__).resolve().parent
DEFAULT_FIELD_MAP = _THIS_DIR / "copybook_field_map.yml"

# Repository directory that holds this script, taken from the script's own location
# (modernization/extraction/ -> repository root), and the generated-output root every
# destination resolving inside that repository must stay under.
REPOSITORY_ROOT = _THIS_DIR.parents[1]
DEFAULT_OUTPUT_ROOT = REPOSITORY_ROOT / "modernization" / "harness" / "build"

# Sample definitions this tool is exercised with, beside the field map.
SAMPLE_INPUT_DIR = _THIS_DIR / "sample_input"
MOTOR_SAMPLE_DEFINITION = SAMPLE_INPUT_DIR / "commarea_01amot.json"
COMMERCIAL_SAMPLE_DEFINITION = SAMPLE_INPUT_DIR / "commarea_01acom.json"

# The read-only copybook that declares the record, two directories above this script.
COMMAREA_COPYBOOK = _THIS_DIR.parent.parent / "base" / "src" / "lgcmarea.cpy"

# Emitted record width: the sum of the four level-03 items declared at
# base/src/lgcmarea.cpy:10-13, which are 6 + 2 + 10 + 32482 characters.
COMMAREA_RECORD_LENGTH = 32500

# Name the same fixed width carries where the generated-output policy refers to it,
# and the width record.length and sample_definition_contract.emitted_record_length must
# both declare.
RECORD_LENGTH = COMMAREA_RECORD_LENGTH

EXIT_OK = 0
EXIT_SAMPLE_REJECTED = 2
EXIT_FIELD_MAP_INVALID = 3
EXIT_IO_ERROR = 4
EXIT_SELF_TEST_FAILED = 5

# Bounds applied to each input document before and during parsing: the bytes one read
# takes, the keys a sample definition may declare, the container nesting a document may
# reach and the values it may expand to.
MAX_FIELD_MAP_BYTES = 1024 * 1024
MAX_SAMPLE_BYTES = 64 * 1024
MAX_SAMPLE_KEYS = 256
MAX_DOCUMENT_DEPTH = 32
MAX_DOCUMENT_NODES = 100_000

# Flags that open one input without blocking on a pipe, socket or device.
_NON_BLOCKING_READ = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0)

# Characters of untrusted text one diagnostic fragment carries before truncation.
MAX_DIAGNOSTIC_CHARACTERS = 48
MAX_DIAGNOSTIC_PATH_CHARACTERS = 160
MAX_DIAGNOSTIC_MESSAGE_CHARACTERS = 200

# Candidate names tried when creating the temporary entry the record is written through.
MAX_TEMPORARY_ATTEMPTS = 8

# Mode requested for a directory created below the anchor; the umask applies to it.
DIRECTORY_MODE = 0o777

# Bytes read back from the destination in one os.read call during verification.
READ_BACK_CHUNK_BYTES = 65536

# Item kinds recorded by the field map's layout entries.
KIND_NUMERIC = "numeric_display"
KIND_ALPHANUMERIC = "alphanumeric"

# Kind reported by the copybook parse for an item declared without a PICTURE clause.
KIND_GROUP = "group"

# Runtime statuses recorded by the field map's logical field entries.
POPULATED_BY_REQUEST = "request"
POPULATED_BY_CHAIN = "chain"

# Justification values recorded by sample_definition_contract.value_justification.
JUSTIFY_LEFT = "left"
JUSTIFY_RIGHT = "right"

# Padding character and justification each item kind must record under
# sample_definition_contract.value_padding and value_justification.
FIXED_PADDING = {KIND_NUMERIC: "0", KIND_ALPHANUMERIC: " "}
FIXED_JUSTIFICATION = {KIND_NUMERIC: JUSTIFY_RIGHT, KIND_ALPHANUMERIC: JUSTIFY_LEFT}

# Value semantics a layout item records; iso_date marks a calendar date value.
SEMANTICS_ISO_DATE = "iso_date"
KNOWN_VALUE_SEMANTICS = (SEMANTICS_ISO_DATE,)

# Fill labels the field map records for a window left at its padding character.
FILL_LABEL_SPACES = "spaces"
FILL_LABEL_ZEROS = "zeros"

# Fill label each item kind must record under sample_definition_contract.fill_by_kind
# and under every chain_populated_items entry that records a fill instead of a seed.
FILL_LABEL_BY_KIND = {
    KIND_NUMERIC: FILL_LABEL_ZEROS,
    KIND_ALPHANUMERIC: FILL_LABEL_SPACES,
}

# The two members a chain_populated_items entry chooses between: the padding character
# of its kind across the whole window, or the literal the entry records.
CHAIN_CONTENT_FILL = "fill"
CHAIN_CONTENT_SEED = "seed"

# Section of sample_definition_contract that states the content of every window the
# chain assigns, one entry per logical entry recording populated_by chain.
CHAIN_POPULATED_SECTION = "chain_populated_items"

# Filler and padding items of base/src/lgcmarea.cpy: CA-E-PADDING-DATA at line 54,
# CA-H-FILLER at 63, CA-M-FILLER at 75, CA-B-FILLER at 94 and CA-C-FILLER at 103. A
# sample definition may not supply them and their windows stay spaces.
PROTECTED_FILL_ITEMS = frozenset(
    {
        "CA-E-PADDING-DATA",
        "CA-H-FILLER",
        "CA-M-FILLER",
        "CA-B-FILLER",
        "CA-C-FILLER",
    }
)

# Character classes permitted in a supplied value, matched with fullmatch: one or more
# ASCII digits 0-9 for a numeric item, one or more printable 7-bit ASCII characters for
# an alphanumeric item, and the YYYY-MM-DD shape for an iso_date item. An omitted item
# is filled by _placed_characters instead.
_DIGITS = "0123456789"
_ASCII_DIGITS = re.compile(r"[0-9]+")
_PRINTABLE_ASCII = re.compile(r"[\x20-\x7E]+")
_ISO_DATE_SHAPE = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})")

# C0 controls, DEL and C1 controls, rejected outright in a path argument and escaped in
# every other value a diagnostic quotes.
_CONTROL_CHARACTERS = re.compile(r"[\x00-\x1f\x7f-\x9f]")


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


class UsageError(BuildError):
    """The command line omits a required argument or names an unknown one."""

    exit_status = EXIT_IO_ERROR


class SelfTestError(BuildError):
    """Raised when the self-test cannot run its cases at all."""

    exit_status = EXIT_SELF_TEST_FAILED


class Routing(NamedTuple):
    """Request routing resolved for one sample definition."""

    request_id: str
    policy_type: str
    overlay: str


class Window(NamedTuple):
    """One placeable byte window taken from a field map layout entry.

    ``semantics`` carries the item's ``value_semantics`` when it records one.
    ``moved_to``, ``moved_to_pic`` and ``moved_to_max_value`` carry the host declaration
    the chain moves the item's value into and the largest whole number that declaration
    holds, for the items whose layout entry records them.
    """

    item: str
    group: str
    offset: int
    length: int
    kind: str
    semantics: str | None = None
    moved_to: str | None = None
    moved_to_pic: str | None = None
    moved_to_max_value: int | None = None

    @property
    def end_byte(self) -> int:
        """Return the 1-based position of the window's last character."""
        return self.offset + self.length - 1

    @property
    def host_declaration(self) -> str:
        """Return the host declaration recorded for this window, name then PICTURE."""
        return f"{self.moved_to} PIC {self.moved_to_pic}"


def _type_name(value: Any) -> str:
    """Return the type name of ``value`` for use inside a diagnostic."""
    return type(value).__name__


def _escaped_character(character: str) -> str:
    """Return one character unchanged when printable ASCII, otherwise as an escape."""
    code = ord(character)
    if 0x20 <= code <= 0x7E:
        return character
    if code <= 0xFF:
        return f"\\x{code:02x}"
    return f"\\u{code:04x}"


def _one_line(text: str) -> str:
    """Return ``text`` with every control and non-ASCII character shown as an escape."""
    return "".join(_escaped_character(character) for character in text)


def _escaped(text: str, limit: int = MAX_DIAGNOSTIC_CHARACTERS) -> str:
    """Return ``text`` quoted for a diagnostic, bounded and free of control characters.

    Every character outside printable 7-bit ASCII becomes an escape, a single quote and
    a backslash are escaped, and text longer than ``limit`` characters is truncated with
    a trailing ellipsis. Used for every fragment taken from an input document: sample
    keys, request ids, field map member names and item spellings.
    """
    rendered = [
        "\\" + character if character in ("'", "\\") else _escaped_character(character)
        for character in text[:limit]
    ]
    ellipsis = "..." if len(text) > limit else ""
    body = "".join(rendered)
    return f"'{body}{ellipsis}'"


def _shown(value: Any) -> str:
    """Return one value taken from an input document, rendered for a diagnostic.

    A string is escaped and bounded, a scalar is shown by value, and any other value is
    named by its type without any of its content.
    """
    if isinstance(value, str):
        return _escaped(value)
    if value is None or isinstance(value, (bool, int, float)):
        return repr(value)
    return f"a {_type_name(value)}"


def _path_shown(path: str | os.PathLike[str]) -> str:
    """Return one filesystem path quoted for a diagnostic, bounded and control-free."""
    return _escaped(os.fspath(path), MAX_DIAGNOSTIC_PATH_CHARACTERS)


def _display(value: Any) -> str:
    """Return ``value`` as one quoted, printable 7-bit ASCII fragment.

    Every value interpolated into a diagnostic passes through here: sample definition
    keys, item names, supplied values, file paths and failure reasons. ``ascii``
    escapes any character outside 7-bit ASCII, and each remaining control character is
    replaced by its ``\\xNN`` form, so the caller's message stays one printable line.

    >>> _display("BAD\\nKEY")
    "'BAD\\\\nKEY'"
    """
    return "".join(
        character if 0x20 <= ord(character) <= 0x7E else f"\\x{ord(character):02x}"
        for character in ascii(value)
    )


def _reason(error: BaseException) -> str:
    """Return the reason text of ``error`` as one printable ASCII fragment."""
    strerror = getattr(error, "strerror", None)
    return _display(strerror if strerror else str(error))


def _quote_all(names: Iterable[str]) -> str:
    """Return ``names`` sorted, escaped, quoted and comma separated."""
    return ", ".join(_display(name) for name in sorted(names))


class _DuplicateRejectingLoader(yaml.SafeLoader):
    """``yaml.SafeLoader`` that refuses a mapping which repeats a key.

    Loading raises ``yaml.constructor.ConstructorError`` naming the repeated key and
    the position it reappears at, instead of resolving that key to its last value. A
    key this loader cannot compare against the keys already seen raises the same error
    class, so every mapping defect reaches the caller as a YAML error.
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


# Sentinel returned when a container's children are exhausted during the walk below.
_EXHAUSTED = object()


def _container_children(node: Any) -> Iterable[Any] | None:
    """Return the child values of a mapping or sequence, or None for a scalar."""
    if isinstance(node, dict):
        return node.values()
    if isinstance(node, (list, tuple)):
        return node
    return None


def _document_depth(document: Any, where: str, invalid: type[BuildError]) -> int:
    """Return the deepest container nesting level of ``document``.

    The walk is iterative and measures a document nested past any Python recursion
    limit without raising. A scalar has depth 0, a flat mapping or sequence has
    depth 1. Every container on the way down is held by identity, so a container
    reached from inside itself raises ``invalid`` instead of walking forever, and the
    walk stops with ``invalid`` once it has visited ``MAX_DOCUMENT_NODES`` values, so
    an alias graph that expands past that count is rejected rather than followed.
    """
    children = _container_children(document)
    if children is None:
        return 0
    deepest = 1
    visits = 1
    open_containers: list[tuple[int, Iterator[Any]]] = [(id(document), iter(children))]
    on_path = {id(document)}
    while open_containers:
        holder, remaining = open_containers[-1]
        child = next(remaining, _EXHAUSTED)
        if child is _EXHAUSTED:
            open_containers.pop()
            on_path.discard(holder)
            continue
        visits += 1
        if visits > MAX_DOCUMENT_NODES:
            raise invalid(
                f"{where} expands to more than {MAX_DOCUMENT_NODES} values, above the "
                f"value count this tool reads"
            )
        grandchildren = _container_children(child)
        if grandchildren is None:
            continue
        if id(child) in on_path:
            raise invalid(
                f"{where} holds a container that appears inside itself; this tool "
                f"reads no self-referential document"
            )
        open_containers.append((id(child), iter(grandchildren)))
        on_path.add(id(child))
        deepest = max(deepest, len(open_containers))
    return deepest


# Directories a path this tool reads must sit inside, each composed by name from the
# canonical repository directory that holds this script: the extraction directory that
# carries the field map and the packaged sample definitions, and the generated-output
# root that carries a record an earlier run wrote.
_READ_ROOT_COMPONENTS = (
    ("modernization", "extraction"),
    ("modernization", "harness", "build"),
)


def _refuse_control_characters(
    path: str | os.PathLike[str], what: str, refusal: str
) -> None:
    """Refuse a path argument whose text carries a control character.

    C0 controls, DEL and C1 controls are rejected outright rather than escaped, so no
    path this tool opens can carry a byte that a diagnostic or an evidence record would
    have to neutralise. The position reported is 1-based and the text itself is escaped
    for display. ``refusal`` closes the diagnostic.
    """
    text = os.fspath(path)
    if not isinstance(text, str):
        text = os.fsdecode(text)
    found = _CONTROL_CHARACTERS.search(text)
    if found is not None:
        raise InputOutputError(
            f"{what} {_path_shown(path)} holds a control character at position "
            f"{found.start() + 1}; a path argument is text free of control characters; "
            f"{refusal}"
        )


def _validated_read_roots() -> tuple[Path, ...]:
    """Return the directories a path this tool reads must sit inside.

    Each root is composed by name from the canonical repository directory that holds
    this script, so every working directory yields the same directories, and no
    component from that repository directory down to a root may be a symbolic link. A
    root that is absent is returned unchanged and authorises nothing, because no path
    can resolve inside a directory that does not exist.
    """
    repository = _canonical_path(REPOSITORY_ROOT)
    roots: list[Path] = []
    for components in _READ_ROOT_COMPONENTS:
        root = repository.joinpath(*components)
        _refuse_symbolic_component(root, repository, "read root", "refusing to read")
        roots.append(root)
    return tuple(roots)


def _authorising_read_root(
    canonical: Path, roots: tuple[Path, ...], what: str, shown: str
) -> Path:
    """Return the first root in ``roots`` that contains ``canonical``.

    A path equal to a root is a directory rather than an input and is refused with every
    path that resolves outside all of them, naming the directories a read is confined to
    so the caller learns the rule and not only the refusal.
    """
    for root in roots:
        if canonical != root and canonical.is_relative_to(root):
            return root
    named = ", ".join(_path_shown(root) for root in roots)
    raise InputOutputError(
        f"cannot read {what} {shown}: it resolves to {_path_shown(canonical)}, and a "
        f"path this tool reads must sit inside {named}; refusing to read"
    )


class _OpenedInput(NamedTuple):
    """One input opened for a single bounded read: its descriptor and file status."""

    descriptor: int
    status: os.stat_result


def _opened_input(
    path: Path, what: str, roots: tuple[Path, ...], invalid: type[BuildError]
) -> _OpenedInput:
    """Return one descriptor for ``path``, confined to the authorised read roots.

    The path is made absolute, which collapses its ``.`` and ``..`` components without
    consulting the filesystem, refused when its text carries a control character, and
    refused when any component from the filesystem root down to it is a symbolic link,
    so no link is ever followed. Its canonical form must sit inside one authorised read
    root. The directory holding it is then opened one component at a time from the
    filesystem root without following a symbolic link, and the leaf is opened as one
    single name relative to that directory with ``O_NOFOLLOW`` and without blocking, so
    a pipe, socket or device cannot stall the open and a leaf that became a symbolic
    link is refused rather than followed. The complete status of that one descriptor is
    read before any byte is taken: it must report a regular file reached by exactly one
    link, sitting on the device of the read root that authorised it. Anything else
    raises ``invalid``; a path outside the roots, an unopenable component and an
    unopenable leaf raise ``InputOutputError``. The descriptor returned is the caller's
    to close, and every refusal after the open closes it before raising.
    """
    shown = _display(str(path))
    _refuse_control_characters(path, what, "refusing to read")
    given = _absolute_path(path)
    _refuse_symbolic_component(given, Path(given.anchor), what, "refusing to read")
    canonical = _canonical_path(given)
    root = _authorising_read_root(canonical, roots, what, shown)
    try:
        authorised = os.stat(root, follow_symlinks=False)
    except OSError as error:
        raise InputOutputError(
            f"cannot read {what} {shown}: the authorised directory "
            f"{_path_shown(root)} cannot be examined: {_reason(error)}"
        ) from error

    directory = _opened_by_components(
        canonical.parent, f"directory holding {what}", "refusing to read"
    )
    try:
        descriptor = os.open(
            canonical.name, _NON_BLOCKING_READ | os.O_NOFOLLOW, dir_fd=directory
        )
    except OSError as error:
        raise InputOutputError(
            f"cannot read {what} {shown}: {_reason(error)}"
        ) from error
    finally:
        with contextlib.suppress(OSError):
            os.close(directory)

    try:
        status = os.fstat(descriptor)
        if not stat.S_ISREG(status.st_mode):
            raise invalid(
                f"{what} {shown} is not a regular file; this tool reads one regular "
                f"file per input"
            )
        if status.st_nlink != 1:
            raise invalid(
                f"{what} {shown} is reached by {status.st_nlink} names, and this tool "
                f"reads a file reached by exactly one"
            )
        if status.st_dev != authorised.st_dev:
            raise invalid(
                f"{what} {shown} sits on a device other than the one holding the "
                f"authorised directory {_path_shown(root)}, so it is not the file that "
                f"directory holds"
            )
    except BaseException:
        with contextlib.suppress(OSError):
            os.close(descriptor)
        raise
    return _OpenedInput(descriptor=descriptor, status=status)


class _BoundedInput(NamedTuple):
    """One input taken by a single bounded read: its exact bytes and their text."""

    payload: bytes
    text: str


def _read_limited_input(
    path: Path,
    limit: int,
    what: str,
    invalid: type[BuildError],
    roots: tuple[Path, ...],
) -> _BoundedInput:
    """Return the bytes and UTF-8 text of ``path``, reading at most ``limit`` bytes.

    The path is opened once by ``_opened_input``, which confines it to ``roots``,
    follows no symbolic link and takes the complete status of the one descriptor it
    returns before any byte is read, so a pipe, socket or device is rejected before any
    content is taken and a file whose size changes after the examination, or whose
    directory entry understates it, cannot exceed the limit unnoticed. Anything that is
    not a regular file raises ``invalid``, as does content above ``limit`` bytes, naming
    the observed size and the limit, and content that is not UTF-8 text. A path that
    cannot be opened or read raises ``InputOutputError``. The returned bytes and text
    are the content that one read took, so a caller needing either form opens the path
    no second time.
    """
    opened = _opened_input(path, what, roots, invalid)
    descriptor = opened.descriptor
    chunks: list[bytes] = []
    entry_size = opened.status.st_size
    try:
        pending = limit + 1
        while pending > 0:
            chunk = os.read(descriptor, pending)
            if not chunk:
                break
            chunks.append(chunk)
            pending -= len(chunk)
    except OSError as error:
        raise InputOutputError(
            f"cannot read {what} {_display(str(path))}: {_reason(error)}"
        ) from error
    finally:
        os.close(descriptor)

    payload = b"".join(chunks)
    if len(payload) > limit:
        observed = max(len(payload), entry_size)
        raise invalid(
            f"{what} {_display(str(path))} holds at least {observed} bytes, above the "
            f"{limit} byte limit this tool reads"
        )
    try:
        return _BoundedInput(payload=payload, text=payload.decode("utf-8"))
    except UnicodeError as error:
        raise invalid(
            f"{what} {_display(str(path))} is not valid UTF-8 text: {_reason(error)}"
        ) from error


def _section(container: dict[str, Any], key: str, where: str) -> Any:
    """Return ``container[key]``, or raise ``FieldMapError`` naming what is missing."""
    if key not in container:
        raise FieldMapError(f"{where}: required section {_shown(key)} is missing")
    return container[key]


def _mapping_section(container: dict[str, Any], key: str, where: str) -> dict[str, Any]:
    """Return a mapping section of the field map."""
    value = _section(container, key, where)
    if not isinstance(value, dict):
        raise FieldMapError(
            f"{where}: section {_shown(key)} must be a mapping, "
            f"found {_type_name(value)}"
        )
    return value


def _sequence_section(container: dict[str, Any], key: str, where: str) -> list[Any]:
    """Return a sequence section of the field map."""
    value = _section(container, key, where)
    if not isinstance(value, list):
        raise FieldMapError(
            f"{where}: section {_shown(key)} must be a sequence, "
            f"found {_type_name(value)}"
        )
    return value


def _positive_int(container: dict[str, Any], key: str, where: str) -> int:
    """Return a positive integer member of a field map mapping."""
    value = container.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise FieldMapError(
            f"{where}: '{key}' must be a positive integer, found {_display(value)}"
        )
    return value


def _check_string_keys(section: dict[Any, Any], what: str, where: str) -> None:
    """Confirm every key of one field map mapping is a non-empty string.

    ``what`` names one key in the diagnostic and ``where`` names the section that
    carries it. A key of any other type, and an empty one, each raise ``FieldMapError``
    naming the offending key, so every later lookup, sort and diagnostic works on the
    string keys the contract declares.
    """
    for key in section:
        if not isinstance(key, str) or not key:
            raise FieldMapError(
                f"{where}: every {what} must be a non-empty string, "
                f"found {_display(key)}"
            )


def _check_string_sequence(container: dict[str, Any], key: str, where: str) -> None:
    """Confirm one optional member is a sequence of non-empty strings when recorded.

    An absent member and a member recorded as null are both accepted, exactly as the
    member's consumers treat them. Every other value must be a sequence whose every
    element is a non-empty string; a container of any other type, and an element that is
    not a non-empty string, each raise ``FieldMapError`` naming the member and, for an
    element, its position.
    """
    value = container.get(key)
    if value is None:
        return
    if not isinstance(value, list):
        raise FieldMapError(
            f"{where}: '{key}' must be a sequence of non-empty strings when recorded, "
            f"found {_type_name(value)}"
        )
    for position, element in enumerate(value, start=1):
        if not isinstance(element, str) or not element:
            raise FieldMapError(
                f"{where}: '{key}' element {position} must be a non-empty string, "
                f"found {_display(element)}"
            )


class _FieldMapLoader(_DuplicateRejectingLoader):
    """Duplicate-rejecting loader that additionally refuses an alias and deep nesting.

    Mapping construction rejects a repeated key exactly as
    ``_DuplicateRejectingLoader`` does. Node composition additionally rejects every
    alias, so no anchor can expand a document behind the bounds this tool reads, and
    bounds nesting to ``MAX_DOCUMENT_DEPTH`` levels while the nodes are composed. Each
    refusal raises ``FieldMapError`` naming the offending anchor or the line that
    carries it.
    """

    def __init__(self, stream: Any) -> None:
        super().__init__(stream)
        self._depth = 0

    def compose_node(self, parent: Any, index: Any) -> Any:
        """Compose one node, refusing an alias and bounding the nesting depth."""
        if self.check_event(yaml.events.AliasEvent):
            event = self.peek_event()
            raise FieldMapError(
                f"field map refers to anchor '*{_display(str(event.anchor))}' at line "
                f"{event.start_mark.line + 1}; an alias is not accepted"
            )
        self._depth += 1
        if self._depth > MAX_DOCUMENT_DEPTH:
            raise FieldMapError(
                f"field map nests deeper than the accepted {MAX_DOCUMENT_DEPTH} levels "
                f"at line {self.peek_event().start_mark.line + 1}"
            )
        try:
            return super().compose_node(parent, index)
        finally:
            self._depth -= 1

    def construct_mapping(self, node: Any, deep: bool = False) -> dict[Any, Any]:
        """Construct one mapping, refusing the merge key as well as a repeated key."""
        for key_node, _value_node in node.value:
            if (
                isinstance(key_node, yaml.nodes.ScalarNode)
                and key_node.tag == "tag:yaml.org,2002:merge"
            ):
                raise FieldMapError(
                    "field map uses the merge key '<<' at line "
                    f"{key_node.start_mark.line + 1}; a merge key is not accepted"
                )
        return super().construct_mapping(node, deep)


def _check_chain_numeric_kinds(field_map: dict[str, Any]) -> None:
    """Confirm every ``chain_required_numeric`` layout item records the numeric kind."""
    where = "field map layout"
    layout = _mapping_section(field_map, "layout", "field map")
    for group_name in layout:
        group = _mapping_section(layout, group_name, where)
        for position, item in enumerate(
            _sequence_section(group, "items", f"{where} group {_display(group_name)}"),
            start=1,
        ):
            if not isinstance(item, dict):
                raise FieldMapError(
                    f"{where} group {_display(group_name)} item {position} must be a "
                    f"mapping, found {_display(item)}"
                )
            if not item.get("chain_required_numeric"):
                continue
            if item.get("kind") != KIND_NUMERIC:
                raise FieldMapError(
                    f"{where} item {_display(item.get('item'))} is flagged "
                    f"'chain_required_numeric' and must record kind '{KIND_NUMERIC}', "
                    f"found {_display(item.get('kind'))}"
                )


def _check_fixed_contract(field_map: dict[str, Any]) -> None:
    """Confirm the field map declares the fixed record contract this tool emits.

    Checks ``record.length``, ``record.link_length_observed`` and
    ``sample_definition_contract.emitted_record_length`` against
    ``COMMAREA_RECORD_LENGTH``, the padding character and justification recorded for
    both item kinds, and the kind of every layout item flagged
    ``chain_required_numeric``. Raises ``FieldMapError`` naming the member that differs.
    """
    _record_length(field_map)
    record = _mapping_section(field_map, "record", "field map")
    observed = _positive_int(record, "link_length_observed", "field map record")
    if observed != COMMAREA_RECORD_LENGTH:
        raise FieldMapError(
            f"field map record: 'link_length_observed' must be "
            f"{COMMAREA_RECORD_LENGTH}, found {observed}"
        )
    where = "field map sample_definition_contract"
    emitted = _positive_int(
        field_map["sample_definition_contract"], "emitted_record_length", where
    )
    if emitted != COMMAREA_RECORD_LENGTH:
        raise FieldMapError(
            f"{where}: 'emitted_record_length' must be {COMMAREA_RECORD_LENGTH}, "
            f"found {emitted}"
        )
    _fill_rules(field_map)
    _check_chain_numeric_kinds(field_map)


class _FieldMapSource(NamedTuple):
    """One field map read once: its path, the exact bytes read and the document."""

    path: Path
    payload: bytes
    document: dict[str, Any]


def _read_field_map(path: str | os.PathLike[str] | None) -> _FieldMapSource:
    """Read one field map with a single bounded read and validate what it declares.

    The one read serves both the parse and any caller that also needs the exact bytes,
    which are returned beside the document, so the path is opened no second time and
    the bytes a caller works from are the bytes the parse saw. The path defaults to
    ``DEFAULT_FIELD_MAP``, is confined to the validated read roots, and the validation
    is the contract ``load_field_map`` states.
    """
    map_path = Path(path) if path is not None else DEFAULT_FIELD_MAP
    source = _read_limited_input(
        map_path,
        MAX_FIELD_MAP_BYTES,
        "field map",
        FieldMapError,
        _validated_read_roots(),
    )
    text = source.text

    try:
        document = yaml.load(text, Loader=_FieldMapLoader)
    except yaml.YAMLError as error:
        raise FieldMapError(
            f"field map {_display(str(map_path))} is not valid YAML: "
            f"{_display(' '.join(str(error).split()))}"
        ) from error
    except RecursionError as error:
        raise FieldMapError(
            f"field map {_display(str(map_path))} nests containers too deeply to "
            f"parse: {_reason(error)}"
        ) from error
    except ValueError as error:
        raise FieldMapError(
            f"field map {_display(str(map_path))} carries a scalar the YAML parser "
            f"cannot construct ({_type_name(error)}); the value is not echoed"
        ) from error

    if not isinstance(document, dict):
        raise FieldMapError(
            f"field map {_display(str(map_path))} must be a mapping, "
            f"found {_type_name(document)}"
        )

    where = f"field map {_display(str(map_path))}"
    depth = _document_depth(document, where, FieldMapError)
    if depth > MAX_DOCUMENT_DEPTH:
        raise FieldMapError(
            f"{where} nests {depth} containers, above the "
            f"{MAX_DOCUMENT_DEPTH} container limit this tool reads"
        )

    record = _mapping_section(document, "record", where)
    declared_length = _positive_int(record, "length", f"{where} record")
    if declared_length != COMMAREA_RECORD_LENGTH:
        raise FieldMapError(
            f"{where} record: 'length' is {declared_length}; this builder emits "
            f"records of exactly {COMMAREA_RECORD_LENGTH} characters"
        )

    layout = _mapping_section(document, "layout", where)
    if not layout:
        raise FieldMapError(f"{where}: section 'layout' declares no groups")
    _check_string_keys(layout, "group name", f"{where} layout")
    for group_name in layout:
        group = _mapping_section(layout, group_name, f"{where} layout")
        _sequence_section(
            group, "items", f"{where} layout group {_display(group_name)}"
        )

    routing = _mapping_section(document, "request_routing", where)
    routing_map = _mapping_section(routing, "map", f"{where} request_routing")
    _check_string_keys(routing_map, "request id", f"{where} request_routing.map")
    _sequence_section(document, "supported_request_ids", where)
    _sequence_section(document, "supported_samples", where)
    _sequence_section(document, "fields", where)
    contract = _mapping_section(document, "sample_definition_contract", where)
    emitted_length = _positive_int(
        contract, "emitted_record_length", f"{where} sample_definition_contract"
    )
    if emitted_length != COMMAREA_RECORD_LENGTH:
        raise FieldMapError(
            f"{where} sample_definition_contract: 'emitted_record_length' is "
            f"{emitted_length}; this builder emits records of exactly "
            f"{COMMAREA_RECORD_LENGTH} characters"
        )
    _check_string_sequence(
        contract, "required_keys", f"{where} sample_definition_contract"
    )
    _check_fixed_contract(document)
    return _FieldMapSource(path=map_path, payload=source.payload, document=document)


def load_field_map(path: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    """Load the field map and confirm the sections this builder reads are present.

    ``path`` defaults to ``copybook_field_map.yml`` in this script's directory and must
    sit inside the validated read roots, which are ``modernization/extraction`` and
    ``modernization/harness/build`` under the canonical repository directory holding
    this script. The file must be one regular file holding at most
    ``MAX_FIELD_MAP_BYTES`` bytes of
    UTF-8 YAML, must not repeat a mapping key, must nest at most
    ``MAX_DOCUMENT_DEPTH`` containers, must expand to at most ``MAX_DOCUMENT_NODES``
    values without a container appearing inside itself, and must declare
    ``COMMAREA_RECORD_LENGTH`` under both ``record.length`` and
    ``sample_definition_contract.emitted_record_length``. The returned document is the
    parsed YAML mapping.
    """
    return _read_field_map(path).document


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Build an object from JSON key/value pairs, rejecting a repeated key."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SampleError(f"sample definition repeats key {_display(key)}")
        result[key] = value
    return result


def load_sample(path: str | os.PathLike[str]) -> dict[str, str]:
    """Read one sample definition and confirm it is a flat object of string values.

    ``path`` must sit inside the validated read roots, which are
    ``modernization/extraction`` and ``modernization/harness/build`` under the canonical
    repository directory holding this script. The file must be one regular file holding
    at most ``MAX_SAMPLE_BYTES`` bytes of UTF-8 JSON, must nest at most
    ``MAX_DOCUMENT_DEPTH`` containers, must expand to at
    most ``MAX_DOCUMENT_NODES`` values without a container appearing inside itself, and
    must declare at most ``MAX_SAMPLE_KEYS`` keys, none of them repeated.
    """
    sample_path = Path(path)
    text = _read_limited_input(
        sample_path,
        MAX_SAMPLE_BYTES,
        "sample definition",
        SampleError,
        _validated_read_roots(),
    ).text

    try:
        document = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except json.JSONDecodeError as error:
        raise SampleError(
            f"sample definition {_display(str(sample_path))} is not valid JSON: "
            f"{_display(error.msg)} at line {error.lineno} column {error.colno}"
        ) from error
    except RecursionError as error:
        raise SampleError(
            f"sample definition {_display(str(sample_path))} nests containers too "
            f"deeply to parse: {_reason(error)}"
        ) from error

    if not isinstance(document, dict):
        raise SampleError(
            f"sample definition {_display(str(sample_path))} must be a JSON object, "
            f"found {_type_name(document)}"
        )

    depth = _document_depth(
        document, f"sample definition {_display(str(sample_path))}", SampleError
    )
    if depth > MAX_DOCUMENT_DEPTH:
        raise SampleError(
            f"sample definition {_display(str(sample_path))} nests {depth} containers, "
            f"above the {MAX_DOCUMENT_DEPTH} container limit this tool reads"
        )
    if len(document) > MAX_SAMPLE_KEYS:
        raise SampleError(
            f"sample definition {_display(str(sample_path))} declares "
            f"{len(document)} keys, above the {MAX_SAMPLE_KEYS} key limit this tool "
            f"reads"
        )

    for key, value in document.items():
        if not isinstance(value, str):
            raise SampleError(
                f"sample definition {_display(str(sample_path))}: value for key "
                f"{_display(key)} must be a string, found {_type_name(value)}"
            )
    return document


def _request_id_item(field_map: dict[str, Any]) -> str:
    """Return the COMMAREA item name that request routing evaluates."""
    item = field_map["request_routing"].get("evaluated_item")
    if not isinstance(item, str) or not item:
        raise FieldMapError(
            "field map request_routing: 'evaluated_item' must be a non-empty string, "
            f"found {_display(item)}"
        )
    return item


def _overlay_group_names(field_map: dict[str, Any]) -> set[str]:
    """Return every layout group name that request routing selects as an overlay."""
    names: set[str] = set()
    for request_id, entry in field_map["request_routing"]["map"].items():
        if not isinstance(entry, dict):
            raise FieldMapError(
                f"field map request_routing.map entry {_display(request_id)} must be a "
                f"mapping, found {_type_name(entry)}"
            )
        overlay = entry.get("overlay")
        if overlay is None:
            continue
        if not isinstance(overlay, str) or not overlay:
            raise FieldMapError(
                f"field map request_routing.map entry {_display(request_id)}: "
                f"'overlay' must be a non-empty string or null, "
                f"found {_display(overlay)}"
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
                f"a non-empty string, found {_display(request_id)}"
            )
        if request_id in entries:
            raise FieldMapError(
                f"field map supported_samples declares request id "
                f"{_display(request_id)} more than once"
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
            f"field map layout group {_display(name)}: 'order' must be an integer, "
            f"found {_display(order)}"
        )
    return (order, name)


def _item_semantics(item: dict[str, Any], where: str) -> str | None:
    """Return the ``value_semantics`` one layout item records, or None when it has none.

    A recorded semantics outside ``KNOWN_VALUE_SEMANTICS`` raises ``FieldMapError``.
    """
    semantics = item.get("value_semantics")
    if semantics is None:
        return None
    if semantics not in KNOWN_VALUE_SEMANTICS:
        raise FieldMapError(
            f"{where}: 'value_semantics' must be {_quote_all(KNOWN_VALUE_SEMANTICS)} "
            f"when recorded, found {_shown(semantics)}"
        )
    return semantics


def _item_host_declaration(
    item: dict[str, Any], where: str
) -> tuple[str | None, str | None, int | None]:
    """Return the host declaration one layout item records: name, PICTURE and maximum.

    An item that records ``moved_to`` must record both ``moved_to_pic`` and a positive
    ``moved_to_max_value``; a missing member raises ``FieldMapError``. An item without
    ``moved_to`` yields three None values.
    """
    moved_to = item.get("moved_to")
    if moved_to is None:
        return (None, None, None)
    if not isinstance(moved_to, str) or not moved_to:
        raise FieldMapError(
            f"{where}: 'moved_to' must be a non-empty string when recorded, "
            f"found {_shown(moved_to)}"
        )
    declared_pic = item.get("moved_to_pic")
    if not isinstance(declared_pic, str) or not declared_pic:
        raise FieldMapError(
            f"{where}: records 'moved_to' {_escaped(moved_to)} without a non-empty "
            f"'moved_to_pic' host declaration, found {_shown(declared_pic)}"
        )
    return (moved_to, declared_pic, _positive_int(item, "moved_to_max_value", where))


def _group_windows(layout: dict[str, Any], name: str) -> list[Window]:
    """Return the placeable windows of one layout group, in declaration order.

    An item carrying a non-empty ``redefined_by`` list is excluded; the items that
    redefine it are placed in its bytes instead. Each window carries the item's recorded
    value semantics and host declaration.
    """
    windows: list[Window] = []
    for position, item in enumerate(layout[name]["items"], start=1):
        if not isinstance(item, dict):
            raise FieldMapError(
                f"field map layout group {_display(name)} item {position} must be a "
                f"mapping, found {_type_name(item)}"
            )
        declared = item.get("item")
        if not isinstance(declared, str) or not declared:
            raise FieldMapError(
                f"field map layout group {_display(name)} item {position}: 'item' must "
                f"be a non-empty string, found {_display(declared)}"
            )
        if item.get("redefined_by"):
            continue
        kind = item.get("kind")
        if kind not in (KIND_NUMERIC, KIND_ALPHANUMERIC):
            raise FieldMapError(
                f"field map layout item {_display(declared)}: 'kind' must be "
                f"'{KIND_NUMERIC}' or '{KIND_ALPHANUMERIC}', found {_display(kind)}"
            )
        where = f"field map layout item {_display(declared)}"
        moved_to, declared_pic, maximum = _item_host_declaration(item, where)
        windows.append(
            Window(
                item=declared,
                group=name,
                offset=_positive_int(item, "offset", where),
                length=_positive_int(item, "length", where),
                kind=kind,
                semantics=_item_semantics(item, where),
                moved_to=moved_to,
                moved_to_pic=declared_pic,
                moved_to_max_value=maximum,
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
        raise FieldMapError(
            f"field map layout declares no group {_display(routing.overlay)}"
        )

    selected = [
        name for name in layout if name == routing.overlay or name not in overlays
    ]
    windows: list[Window] = []
    for name in sorted(selected, key=lambda group: _group_order(layout, group)):
        windows.extend(_group_windows(layout, name))
    if not windows:
        raise FieldMapError(
            f"field map layout selects no placeable item for request id "
            f"{_display(routing.request_id)}"
        )
    return windows


def _window_index(windows: Iterable[Window]) -> dict[str, Window]:
    """Return the windows keyed by upper-case item name for case-insensitive lookup."""
    index: dict[str, Window] = {}
    for window in windows:
        existing = index.get(window.item.upper())
        if existing is not None:
            raise FieldMapError(
                f"field map layout declares item {_display(window.item)} in both group "
                f"{_display(existing.group)} and group {_display(window.group)}"
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
        raise SampleError(
            f"sample definition does not supply required item {_display(item)}"
        )
    if len(matches) > 1:
        raise SampleError(
            f"keys {_quote_all(matches)} all name item {_display(item)}; "
            "supply it once"
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
            f"{_request_id_item(field_map)} {_display(request_id)} is not a generated "
            f"sample; the supported request ids are {_quote_all(supported)}"
        )

    entry = field_map["request_routing"]["map"].get(request_id)
    if not isinstance(entry, dict):
        raise FieldMapError(
            f"field map request_routing.map has no entry for request id "
            f"{_display(request_id)}"
        )

    overlay = entry.get("overlay")
    if not isinstance(overlay, str) or not overlay:
        raise FieldMapError(
            f"field map request_routing.map entry {_display(request_id)} selects no "
            f"overlay group, found {_display(overlay)}"
        )
    policy_type = entry.get("policy_type")
    if not isinstance(policy_type, str) or len(policy_type) != 1:
        raise FieldMapError(
            f"field map request_routing.map entry {_display(request_id)}: "
            f"'policy_type' must be a single character, found {_display(policy_type)}"
        )

    sample_entry = supported[request_id]
    for member, resolved in (("overlay", overlay), ("policy_type", policy_type)):
        stated = sample_entry.get(member)
        if stated is not None and stated != resolved:
            raise FieldMapError(
                f"field map supported_samples entry {_display(request_id)} states "
                f"{member} {_display(stated)} while request_routing.map resolves "
                f"{_display(resolved)}"
            )

    group = _mapping_section(field_map["layout"], overlay, "field map layout")
    if group.get("policy_type") != policy_type:
        raise FieldMapError(
            f"field map layout group {_display(overlay)} states policy_type "
            f"{_display(group.get('policy_type'))} while request_routing.map resolves "
            f"{_display(policy_type)}"
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


def _check_numeric_value(window: Window, key: str, value: str) -> None:
    """Confirm one non-empty numeric value holds digits and fits its host declaration.

    The diagnostic names the item, the offending position or the declared limit, and the
    length of the supplied value; the value itself is never part of it.
    """
    if not _ASCII_DIGITS.fullmatch(value):
        position, offender = next(
            (index, character)
            for index, character in enumerate(value, start=1)
            if character not in _DIGITS
        )
        raise SampleError(
            f"value supplied under key {_display(key)} for numeric item "
            f"{_display(window.item)} holds a character outside digits 0-9 at position "
            f"{position} (code point {ord(offender)})"
        )
    if window.moved_to_max_value is not None and int(value) > window.moved_to_max_value:
        raise SampleError(
            f"value supplied under key {_display(key)} for numeric item "
            f"{_display(window.item)} ({len(value)} characters) exceeds the largest "
            f"whole number {window.moved_to_max_value} that host declaration "
            f"{_display(window.host_declaration)} carries"
        )


def _check_alphanumeric_value(window: Window, key: str, value: str) -> None:
    """Confirm one non-empty alphanumeric value holds printable 7-bit ASCII only."""
    if _PRINTABLE_ASCII.fullmatch(value):
        return
    position, offender = next(
        (index, character)
        for index, character in enumerate(value, start=1)
        if not 0x20 <= ord(character) <= 0x7E
    )
    raise SampleError(
        f"value supplied under key {_display(key)} for alphanumeric item "
        f"{_display(window.item)} holds a character at position {position} (code point "
        f"{ord(offender)}), outside printable 7-bit ASCII"
    )


def _check_iso_date_value(window: Window, key: str, value: str) -> None:
    """Confirm one non-empty value is a real calendar date written as YYYY-MM-DD."""
    shape = _ISO_DATE_SHAPE.fullmatch(value)
    if shape is None:
        raise SampleError(
            f"value supplied under key {_display(key)} for item "
            f"{_display(window.item)} ({len(value)} characters) is not written as "
            "YYYY-MM-DD"
        )
    year, month, day = (int(part) for part in shape.groups())
    try:
        datetime.date(year, month, day)
    except ValueError as error:
        raise SampleError(
            f"value supplied under key {_display(key)} for item "
            f"{_display(window.item)} is written as YYYY-MM-DD but is not a real "
            "calendar date"
        ) from error


def _check_value(window: Window, key: str, value: str) -> None:
    """Confirm one supplied value fits its window and its recorded semantics.

    A supplied value carries at least one character: an item left at its zero-fill or
    space-fill default is omitted from the sample definition rather than supplied empty,
    and a required item supplied empty is rejected by the same rule. A non-empty value
    holds the character class its kind records, stays within ``moved_to_max_value`` where
    the layout records the host declaration the chain moves it into, and is a real
    calendar date where the layout records ``value_semantics: iso_date``. No diagnostic
    quotes the rejected value.
    """
    if not value:
        raise SampleError(
            f"value supplied under key {_display(key)} for item "
            f"{_display(window.item)} is empty; omit the key to leave the item at its "
            f"{'zero' if window.kind == KIND_NUMERIC else 'space'} fill"
        )
    if len(value) > window.length:
        raise SampleError(
            f"value supplied under key {_display(key)} for item "
            f"{_display(window.item)} is {len(value)} characters, longer than the "
            f"declared length {window.length}"
        )
    if window.kind == KIND_NUMERIC:
        _check_numeric_value(window, key, value)
    else:
        _check_alphanumeric_value(window, key, value)
    if window.semantics == SEMANTICS_ISO_DATE:
        _check_iso_date_value(window, key, value)


def validate_sample(
    field_map: dict[str, Any], sample: dict[str, str], routing: Routing
) -> dict[str, str]:
    """Validate one sample definition and return its accepted values.

    Keys are matched against the field map without regard to case and the result is
    keyed by the spelling the field map declares. A required item must be supplied with
    a non-empty value, and no supplied value may be empty: an item left at its zero-fill
    or space-fill default is omitted from the sample definition rather than supplied
    empty. A key naming an item of ``PROTECTED_FILL_ITEMS`` is rejected along with an
    unknown key, an unselected overlay's key, a chain-assigned key, a repeated key and a
    value that breaches ``_check_value``. Raises ``SampleError`` naming the offending key
    when the sample breaches the sample definition contract, and ``FieldMapError`` when
    the map itself is inconsistent.
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
            f"{_display(routing.policy_type)} but declares no layout window for it"
        )
    protected_required = sorted(set(required) & PROTECTED_FILL_ITEMS)
    if protected_required:
        raise FieldMapError(
            f"field map requires filler item(s) {_quote_all(protected_required)} from "
            "the sample definition; those windows stay at their fill character"
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
                    f"key {_display(key)} names item {_display(elsewhere[0])} of "
                    f"overlay {_display(elsewhere[1])}, which request id "
                    f"{_display(routing.request_id)} does not select; the selected "
                    f"overlay is {_display(routing.overlay)}"
                )
            raise SampleError(
                f"key {_display(key)} names no item declared for request id "
                f"{_display(routing.request_id)}"
            )
        if lookup in chain_items:
            raise SampleError(
                f"key {_display(key)} names item {_display(window.item)}, which the "
                "chain assigns; a sample definition must not supply it"
            )
        if lookup in PROTECTED_FILL_ITEMS:
            raise SampleError(
                f"key {_display(key)} names filler item {_display(window.item)}, whose "
                "window stays at its fill character; a sample definition must not "
                "supply it"
            )
        previous = supplied_under.get(lookup)
        if previous is not None:
            raise SampleError(
                f"keys {_display(previous)} and {_display(key)} both name item "
                f"{_display(window.item)}; supply it once"
            )
        _check_value(window, key, value)
        supplied_under[lookup] = key
        accepted[window.item] = value

    absent = [name for key, name in required.items() if key not in supplied_under]
    if absent:
        raise SampleError(
            f"sample definition for request id {_display(routing.request_id)} does not "
            f"supply required item(s) {_quote_all(absent)}"
        )
    return accepted


def _record_length(field_map: dict[str, Any]) -> int:
    """Return the record length the field map declares, which must be COMMAREA_RECORD_LENGTH."""
    declared = _positive_int(field_map["record"], "length", "field map record")
    if declared != COMMAREA_RECORD_LENGTH:
        raise FieldMapError(
            f"field map record: 'length' must be {COMMAREA_RECORD_LENGTH}, found {declared}"
        )
    return declared


def _fill_rules(field_map: dict[str, Any]) -> dict[str, tuple[str, str]]:
    """Return the padding character and justification recorded for each item kind.

    Each kind must record the padding character listed in ``FIXED_PADDING``, the
    justification listed in ``FIXED_JUSTIFICATION`` and the fill label listed in
    ``FILL_LABEL_BY_KIND``; any other value raises ``FieldMapError`` naming the member.
    """
    where = "field map sample_definition_contract"
    contract = field_map["sample_definition_contract"]
    padding = _mapping_section(contract, "value_padding", where)
    justification = _mapping_section(contract, "value_justification", where)
    fills = _mapping_section(contract, "fill_by_kind", where)

    rules: dict[str, tuple[str, str]] = {}
    for kind in (KIND_NUMERIC, KIND_ALPHANUMERIC):
        character = padding.get(kind)
        if character != FIXED_PADDING[kind]:
            raise FieldMapError(
                f"{where}.value_padding['{kind}'] must be "
                f"{_escaped(FIXED_PADDING[kind])}, found {_shown(character)}"
            )
        side = justification.get(kind)
        if side != FIXED_JUSTIFICATION[kind]:
            raise FieldMapError(
                f"{where}.value_justification['{kind}'] must be "
                f"'{FIXED_JUSTIFICATION[kind]}', found {_shown(side)}"
            )
        label = fills.get(kind)
        if label != FILL_LABEL_BY_KIND[kind]:
            raise FieldMapError(
                f"{where}.fill_by_kind['{kind}'] must be "
                f"'{FILL_LABEL_BY_KIND[kind]}', found {_shown(label)}"
            )
        rules[kind] = (character, side)
    return rules


def _item_domains(field_map: dict[str, Any]) -> dict[str, tuple[str, tuple[str, ...]]]:
    """Return the value domain every logical entry declares, keyed by COMMAREA item.

    Each result entry maps the upper-case item name to the name of the logical entry
    that declares the domain and the members it lists. Raises ``FieldMapError`` when a
    recorded ``domain`` is not a non-empty sequence of non-empty strings.
    """
    domains: dict[str, tuple[str, tuple[str, ...]]] = {}
    for entry in _logical_entries(field_map):
        declared = entry.get("domain")
        if declared is None:
            continue
        item = _commarea_item(entry)
        if item is None:
            continue
        name = str(entry.get("logical_entry"))
        if not isinstance(declared, list) or not declared:
            raise FieldMapError(
                f"field map fields entry {_display(name)}: 'domain' must be a "
                f"non-empty sequence when recorded, found {_shown(declared)}"
            )
        members: list[str] = []
        for member in declared:
            if not isinstance(member, str) or not member:
                raise FieldMapError(
                    f"field map fields entry {_display(name)}: 'domain' holds "
                    f"{_shown(member)}, and every member must be a non-empty string"
                )
            members.append(member)
        domains[item.upper()] = (name, tuple(members))
    return domains


def _chain_content_characters(
    entry: dict[str, Any], window: Window, domain: tuple[str, tuple[str, ...]] | None
) -> str:
    """Return the characters one ``chain_populated_items`` entry places in its window.

    The entry records exactly one of ``fill`` and ``seed``. ``fill`` yields the padding
    character of the window's kind across the whole window and must carry the label
    ``FILL_LABEL_BY_KIND`` lists for that kind. ``seed`` yields the literal itself,
    which must be as long as the window, must hold digits only for a numeric window,
    must hold printable 7-bit ASCII only for an alphanumeric window, and must stand
    outside ``domain`` where the item's logical entry declares one, so a seeded window
    cannot already hold a value the chain produces.
    """
    where = (
        f"field map sample_definition_contract.chain_populated_items entry "
        f"{_display(window.item)}"
    )
    fill = entry.get(CHAIN_CONTENT_FILL)
    seed = entry.get(CHAIN_CONTENT_SEED)
    if (fill is None) == (seed is None):
        raise FieldMapError(
            f"{where} must record exactly one of '{CHAIN_CONTENT_FILL}' and "
            f"'{CHAIN_CONTENT_SEED}', found {_shown(fill)} and {_shown(seed)}"
        )
    if seed is None:
        if fill != FILL_LABEL_BY_KIND[window.kind]:
            raise FieldMapError(
                f"{where} records '{CHAIN_CONTENT_FILL}' {_shown(fill)} while a "
                f"'{window.kind}' window is filled with "
                f"'{FILL_LABEL_BY_KIND[window.kind]}'"
            )
        return FIXED_PADDING[window.kind] * window.length

    if not isinstance(seed, str):
        raise FieldMapError(
            f"{where}: '{CHAIN_CONTENT_SEED}' must be a string, "
            f"found {_type_name(seed)}"
        )
    if len(seed) != window.length:
        raise FieldMapError(
            f"{where}: '{CHAIN_CONTENT_SEED}' holds {len(seed)} character(s) and the "
            f"declared length of the window is {window.length}"
        )
    if window.kind == KIND_NUMERIC:
        if not _ASCII_DIGITS.fullmatch(seed):
            position, offender = next(
                (index, character)
                for index, character in enumerate(seed, start=1)
                if character not in _DIGITS
            )
            raise FieldMapError(
                f"{where}: '{CHAIN_CONTENT_SEED}' holds a character outside digits "
                f"0-9 at position {position} (code point {ord(offender)}) and the "
                f"window is numeric"
            )
    elif not _PRINTABLE_ASCII.fullmatch(seed):
        position, offender = next(
            (index, character)
            for index, character in enumerate(seed, start=1)
            if not 0x20 <= ord(character) <= 0x7E
        )
        raise FieldMapError(
            f"{where}: '{CHAIN_CONTENT_SEED}' holds a character at position "
            f"{position} (code point {ord(offender)}), outside printable 7-bit ASCII"
        )
    if domain is not None and seed in domain[1]:
        raise FieldMapError(
            f"{where}: '{CHAIN_CONTENT_SEED}' {_escaped(seed)} is a member of the "
            f"domain logical entry {_display(domain[0])} declares "
            f"({_quote_all(domain[1])}); a seeded window holds no value the chain "
            f"produces"
        )
    return seed


def _chain_populated_content(
    field_map: dict[str, Any], routing: Routing, windows: Iterable[Window]
) -> dict[str, str]:
    """Return the characters every chain-populated window carries, keyed upper-case.

    ``sample_definition_contract.chain_populated_items`` is the authoritative statement
    of that content and is required to hold exactly one entry per logical entry
    recording ``populated_by: chain``: a missing, repeated or foreign entry raises
    ``FieldMapError``, as does an entry whose ``kind`` differs from the kind the layout
    declares for the item or whose recorded content breaches
    ``_chain_content_characters``. Every returned value is exactly as long as its
    window, so ``render_record`` places it without padding or justification.
    """
    where = "field map sample_definition_contract.chain_populated_items"
    contract = field_map["sample_definition_contract"]
    declared = contract.get(CHAIN_POPULATED_SECTION)
    if not isinstance(declared, list) or not declared:
        raise FieldMapError(
            f"{where} must be a non-empty sequence, found {_shown(declared)}"
        )

    chain_items = _items_populated_by(field_map, POPULATED_BY_CHAIN)
    if not chain_items:
        raise FieldMapError(
            "field map records no logical entry with "
            f"'populated_by: {POPULATED_BY_CHAIN}' while {where} holds "
            f"{len(declared)} entry/entries"
        )
    index = _window_index(windows)
    domains = _item_domains(field_map)

    content: dict[str, str] = {}
    for position, entry in enumerate(declared, start=1):
        if not isinstance(entry, dict):
            raise FieldMapError(
                f"{where} entry {position} must be a mapping, found {_type_name(entry)}"
            )
        item = entry.get("item")
        if not isinstance(item, str) or not item:
            raise FieldMapError(
                f"{where} entry {position}: 'item' must be a non-empty string, "
                f"found {_display(item)}"
            )
        key = item.upper()
        if key in content:
            raise FieldMapError(
                f"{where} entry {position} repeats item {_display(item)}"
            )
        if key not in chain_items:
            raise FieldMapError(
                f"{where} entry {position} names item {_display(item)}, which no "
                f"logical entry records as 'populated_by: {POPULATED_BY_CHAIN}'"
            )
        window = index.get(key)
        if window is None:
            raise FieldMapError(
                f"{where} entry {position} names item {_display(item)}, for which the "
                f"layout declares no window under request id "
                f"{_display(routing.request_id)}"
            )
        kind = entry.get("kind")
        if kind != window.kind:
            raise FieldMapError(
                f"{where} entry {position} records item {_display(item)} as "
                f"{_shown(kind)} while the layout declares it "
                f"'{window.kind}'"
            )
        content[key] = _chain_content_characters(entry, window, domains.get(key))

    absent = [name for key, name in chain_items.items() if key not in content]
    if absent:
        raise FieldMapError(
            f"{where} records no entry for chain-populated item(s) {_quote_all(absent)}"
        )
    return content


def _placed_characters(
    window: Window, value: str | None, rules: dict[str, tuple[str, str]]
) -> str:
    """Return the exact characters to write into one window.

    A supplied value carries at least one character and is justified and padded as
    ``sample_definition_contract`` records for the window's kind. ``None`` marks an
    item the sample definition omits and yields a window filled with that kind's
    padding character, which for a numeric window is the digit zero.
    """
    character, side = rules[window.kind]
    if value is None:
        text = ""
    else:
        text = value
        if not text:
            raise SampleError(
                f"value for item {_display(window.item)} is empty; omit the item to "
                f"leave its window at the fill character {_display(character)}"
            )
        if len(text) > window.length:
            raise SampleError(
                f"value for item {_display(window.item)} is {len(text)} characters, "
                f"longer than the declared length {window.length}"
            )
        if window.kind == KIND_NUMERIC and not _ASCII_DIGITS.fullmatch(text):
            position = next(
                index
                for index, character in enumerate(text, start=1)
                if character not in _DIGITS
            )
            raise SampleError(
                f"value for numeric item {_display(window.item)} ({len(text)} "
                f"characters) holds a character outside digits 0-9 at position "
                f"{position}"
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
    windows receive their value or the padding character, a window the chain assigns
    receives the content ``chain_populated_items`` states for it, and any byte no window
    claims stays a space. The buffer is allocated only after ``record.length`` is
    confirmed to be ``RECORD_LENGTH``, so the result always carries 32,500 characters.
    The result always carries ``COMMAREA_RECORD_LENGTH`` characters, every window of
    ``PROTECTED_FILL_ITEMS`` the layout selects holds spaces only, and every
    chain-populated window holds exactly the content that section states.

    Raises ``FieldMapError`` when two windows overlap, when a window falls outside the
    record, when a selected filler window did not stay spaces, when a chain-populated
    window did not receive its stated content, or when the assembled record does not
    match ``COMMAREA_RECORD_LENGTH``.
    """
    length = COMMAREA_RECORD_LENGTH
    rules = _fill_rules(field_map)
    windows = _layout_windows(field_map, routing)
    chain_content = _chain_populated_content(field_map, routing, windows)

    placeable = {window.item.upper() for window in windows}
    unplaceable = [item for item in values if item.upper() not in placeable]
    if unplaceable:
        raise SampleError(
            f"no layout window under request id {_display(routing.request_id)} for "
            f"value(s) {_quote_all(unplaceable)}"
        )

    supplied = {item.upper(): value for item, value in values.items()}
    buffer = [" "] * length
    furthest: Window | None = None
    for window in sorted(windows, key=lambda entry: (entry.offset, entry.item)):
        if window.end_byte > length:
            raise FieldMapError(
                f"field map layout item {_display(window.item)} spans bytes "
                f"{window.offset}-{window.end_byte}, outside the record length {length}"
            )
        if furthest is not None and window.offset <= furthest.end_byte:
            raise FieldMapError(
                f"field map layout items {_display(furthest.item)} (bytes "
                f"{furthest.offset}-{furthest.end_byte}) and {_display(window.item)} "
                f"(bytes {window.offset}-{window.end_byte}) claim the same bytes"
            )
        stated = chain_content.get(window.item.upper())
        if stated is None:
            text = _placed_characters(window, supplied.get(window.item.upper()), rules)
        else:
            text = stated
        buffer[window.offset - 1 : window.end_byte] = list(text)
        if furthest is None or window.end_byte > furthest.end_byte:
            furthest = window

    record = "".join(buffer)
    if len(record) != length:
        raise FieldMapError(
            f"rendered record is {len(record)} characters, expected {length}"
        )
    for window in windows:
        if window.item.upper() not in PROTECTED_FILL_ITEMS:
            continue
        placed = record[window.offset - 1 : window.end_byte]
        if placed.strip(" "):
            raise FieldMapError(
                f"field map layout item {_display(window.item)} filled bytes "
                f"{window.offset}-{window.end_byte} with characters other than "
                f"spaces; that window holds spaces only"
            )
    for window in windows:
        stated = chain_content.get(window.item.upper())
        if stated is None:
            continue
        placed = record[window.offset - 1 : window.end_byte]
        if placed != stated:
            raise FieldMapError(
                f"chain-populated item {_display(window.item)} holds "
                f"{_escaped(placed)} in bytes {window.offset}-{window.end_byte}, and "
                f"{CHAIN_POPULATED_SECTION} states {_escaped(stated)}"
            )
    return record


def _default_file_mode() -> int:
    """Return the mode a plainly created file receives under the current umask."""
    mask = os.umask(0)
    os.umask(mask)
    return 0o666 & ~mask


def _absolute_path(path: str | os.PathLike[str]) -> Path:
    """Return ``path`` made absolute, reporting a working directory it cannot read.

    Raises ``InputOutputError`` when the current working directory that completes a
    relative path cannot be read.
    """
    try:
        return Path(os.path.abspath(os.fspath(path)))
    except OSError as error:
        raise InputOutputError(
            f"cannot make the path {_path_shown(path)} absolute: "
            f"{error.strerror or error}"
        ) from error


def _canonical_path(path: str | os.PathLike[str]) -> Path:
    """Return the absolute, symbolic-link-free form of ``path``.

    The nearest ancestor that already exists is resolved with ``os.path.realpath`` and
    the components that do not exist yet are appended to that result unchanged, which
    canonicalises a path whose final components are absent. Raises ``InputOutputError``
    when resolution fails, which an entry removed while its link is being read causes.
    """
    missing: list[str] = []
    try:
        probe = _absolute_path(path)
        while not os.path.lexists(probe):
            parent = probe.parent
            if parent == probe:
                break
            missing.append(probe.name)
            probe = parent
        resolved = Path(os.path.realpath(os.fspath(probe)))
    except OSError as error:
        raise InputOutputError(
            f"cannot resolve the path {_path_shown(path)}: {error.strerror or error}"
        ) from error

    for name in reversed(missing):
        resolved = resolved / name
    return resolved


def _refuse_symbolic_component(
    path: Path, ancestor: Path, what: str, refusal: str = "refusing to write"
) -> None:
    """Refuse when a component from ``ancestor`` down to ``path`` is a symbolic link.

    ``ancestor`` must contain ``path``. Each component below it is examined in turn and
    the first symbolic link found raises ``InputOutputError`` naming it; a component
    that does not exist yet is not a symbolic link and is accepted. ``refusal`` closes
    the diagnostic, so a read and a write each name the operation being refused.
    """
    probe = ancestor
    for name in path.relative_to(ancestor).parts:
        probe = probe / name
        if os.path.islink(probe):
            raise InputOutputError(
                f"{what} {_path_shown(path)} passes through symbolic link "
                f"{_path_shown(probe)}; {refusal}"
            )


def _validated_build_root() -> Path:
    """Return the generated-output root after confirming it is the declared directory.

    The root must canonicalise to exactly ``modernization/harness/build`` under the
    canonical repository directory that holds this script, and no component from that
    repository directory down to it may be a symbolic link. Any other state raises
    ``InputOutputError`` naming the rule, before any directory or entry is created.
    """
    repository = _canonical_path(REPOSITORY_ROOT)
    declared = repository / "modernization" / "harness" / "build"
    canonical = _canonical_path(DEFAULT_OUTPUT_ROOT)
    if canonical != declared:
        raise InputOutputError(
            f"generated-output root {_path_shown(DEFAULT_OUTPUT_ROOT)} resolves to "
            f"{_path_shown(canonical)} and not to {_path_shown(declared)}; a generated "
            "record is written only inside modernization/harness/build under the "
            "canonical repository directory holding this script; refusing to write"
        )
    _refuse_symbolic_component(declared, repository, "generated-output root")
    return declared


def _opened_by_components(
    canonical: Path, what: str, refusal: str = "refusing to write"
) -> int:
    """Return a descriptor for ``canonical``, descending one component at a time.

    ``canonical`` must be absolute. The filesystem root is opened first and every
    component below it is opened as one single name relative to the descriptor above it
    without following a symbolic link, so no ancestor is ever resolved from a full
    path. Each descriptor is closed as the walk descends past it and the descriptor
    returned is the caller's to close. ``what`` names the directory in every diagnostic.
    A component that cannot be opened raises ``InputOutputError`` naming that component
    and the directory, reported for a canonical path that carried no symbolic-link
    component when it was resolved as the entry having changed while this run was in
    progress. ``refusal`` closes every diagnostic, so a read and a write each name the
    operation being refused.
    """
    if not canonical.is_absolute():
        raise InputOutputError(
            f"the {what} {_path_shown(canonical)} is not an absolute path; {refusal}"
        )

    try:
        dirfd = os.open(canonical.anchor, os.O_RDONLY | os.O_DIRECTORY)
    except OSError as error:
        raise InputOutputError(
            f"cannot open the filesystem root {_path_shown(canonical.anchor)} the "
            f"{what} {_path_shown(canonical)} descends from: {error.strerror or error}"
        ) from error

    for component in canonical.relative_to(canonical.anchor).parts:
        try:
            descended = os.open(
                component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=dirfd
            )
        except OSError as error:
            raise InputOutputError(
                f"cannot open component {_escaped(component)} of the {what} "
                f"{_path_shown(canonical)}: {error.strerror or error}; that path "
                "carried no symbolic-link component when it was resolved, so the entry "
                f"changed while this run was in progress; {refusal}"
            ) from error
        finally:
            with contextlib.suppress(OSError):
                os.close(dirfd)
        dirfd = descended
    return dirfd


def _confirm_same_directory(descriptor: int, canonical: Path, what: str) -> None:
    """Confirm ``descriptor`` still holds the directory ``canonical`` names.

    The device and inode numbers carried by the open descriptor are compared with those
    the canonical path carries, taken without following a final symbolic link. A failure
    to take either of them, and any difference between them, are both reported as the
    entry having changed while this run was in progress. ``what`` names the directory in
    every diagnostic.
    """
    try:
        opened = os.fstat(descriptor)
        named = os.stat(canonical, follow_symlinks=False)
    except OSError as error:
        raise InputOutputError(
            f"cannot confirm the {what} {_path_shown(canonical)} the write descends "
            f"from: {error.strerror or error}; refusing to write"
        ) from error
    if (opened.st_dev, opened.st_ino) != (named.st_dev, named.st_ino):
        raise InputOutputError(
            f"the {what} {_path_shown(canonical)} the write descends from is no longer "
            "the directory that path named when it was validated; the entry changed "
            "while this run was in progress; refusing to write"
        )


def _opened_output_root(
    root: Path, build_root: Path, build_fd: int, given: str | os.PathLike[str]
) -> int:
    """Return a descriptor for a named output root that stands below the build root.

    ``build_fd`` is the descriptor already held on ``build_root``; the walk starts
    from a duplicate of it, so the caller's descriptor stays the caller's to close, and
    every component leading down to ``root`` is opened as one single name relative to
    the descriptor above it with ``O_NOFOLLOW``. Containment is therefore established
    through held descriptors rather than by comparing pathnames: a symbolic link at any
    level, including one whose target spells a path inside the build root, is refused
    instead of followed. The root is never created: an absent component and a component
    that is not a directory are both reported as a root that is not an existing
    directory below the build root. ``given`` names the root as the command line spelled
    it. The descriptor returned is the caller's to close.
    """
    try:
        dirfd = os.dup(build_fd)
    except OSError as error:
        raise InputOutputError(
            f"cannot duplicate the descriptor of the generated-output root "
            f"{_path_shown(build_root)} the output root descends from: "
            f"{error.strerror or error}"
        ) from error

    for component in root.relative_to(build_root).parts:
        try:
            descended = os.open(
                component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=dirfd
            )
        except (FileNotFoundError, NotADirectoryError) as error:
            raise InputOutputError(
                f"output root {_path_shown(given)} is not an existing directory below "
                f"{_path_shown(build_root)}"
            ) from error
        except OSError as error:
            raise InputOutputError(
                f"cannot open component {_escaped(component)} of output root "
                f"{_path_shown(given)} below {_path_shown(build_root)}: "
                f"{error.strerror or error}; refusing to write"
            ) from error
        finally:
            with contextlib.suppress(OSError):
                os.close(dirfd)
        dirfd = descended
    return dirfd


class _OutputRoot(NamedTuple):
    """The directory a destination must resolve inside and the anchor of every write.

    ``path`` is the canonical root the destination must resolve inside. ``anchor`` is
    the canonical directory the write descends from: the repository directory that holds
    this script while the default generated-output root is in force, whose absent
    components below it this tool creates, and the named root itself otherwise.
    ``descriptor`` is open on ``anchor``, obtained by descending one component at a time
    from the filesystem root under the default root and from the descriptor held on the
    validated generated-output root for a named root, and is the caller's to close.
    """

    path: Path
    anchor: Path
    descriptor: int


def _allowed_output_root(output_root: str | os.PathLike[str] | None) -> _OutputRoot:
    """Return the canonical root a destination must resolve inside, with its anchor.

    ``None`` selects the validated generated-output root, which this tool creates when
    it is absent, and anchors the write at the canonical repository directory that holds
    this script. A named root must already exist as a directory, must carry no control
    character and no symbolic-link component, and must resolve inside that same
    validated generated-output root; every other root is refused, the system temporary
    directory and a directory whose trailing components merely spell
    ``modernization/harness/build`` included. A named root is reached by descending from
    a descriptor held on the validated generated-output root one single component at a
    time, so its containment is established through held descriptors and no symbolic
    link is followed at any level. The anchor is returned with that open descriptor, so
    the anchor is never resolved from a full path again; a root refused after a
    descriptor is open closes it before raising.
    """
    build_root = _validated_build_root()
    if output_root is None:
        repository = _canonical_path(REPOSITORY_ROOT)
        return _OutputRoot(
            path=build_root,
            anchor=repository,
            descriptor=_opened_by_components(repository, "repository directory"),
        )

    given = _absolute_path(output_root)
    _refuse_control_characters(given, "output root", "refusing to write")
    _refuse_symbolic_component(given, Path(given.anchor), "output root")
    root = _canonical_path(given)
    if root != build_root and not root.is_relative_to(build_root):
        raise InputOutputError(
            f"output root {_path_shown(output_root)} resolves to "
            f"{_path_shown(root)}, which is not inside the generated-output root "
            f"{_path_shown(build_root)}; a generated record is written only inside "
            "modernization/harness/build under the canonical repository directory "
            "holding this script; refusing to write"
        )

    build_fd = _opened_by_components(build_root, "generated-output root")
    try:
        _confirm_same_directory(build_fd, build_root, "generated-output root")
        descriptor = _opened_output_root(root, build_root, build_fd, output_root)
    finally:
        with contextlib.suppress(OSError):
            os.close(build_fd)
    return _OutputRoot(path=root, anchor=root, descriptor=descriptor)


class _Destination(NamedTuple):
    """One validated destination and the directory every write to it descends from.

    ``anchor`` is the canonical directory the write descends from: the repository
    directory that holds this script while the default generated-output root is in
    force, and the named output root, itself standing inside the validated
    generated-output root, otherwise. ``anchor_fd`` is open on that directory, opened
    during validation one single component at a time without following a symbolic link
    and confirmed to still hold the directory that path names; it is the only object the
    write descends from, the anchor is never resolved as a pathname again, and closing
    the descriptor is the caller's to do. ``path`` is
    the canonical destination, always inside ``anchor``.
    """

    anchor: Path
    anchor_fd: int
    path: Path


def _validated_destination(
    path: str | os.PathLike[str], output_root: str | os.PathLike[str] | None
) -> _Destination:
    """Return the canonical destination to write, refusing every unsafe one.

    The destination must not be a symbolic link, must not already exist as anything
    other than a regular file, and its canonical form must sit inside the allowed output
    root. A destination whose canonical form sits inside the repository directory that
    holds this script must sit inside the validated generated-output root whichever root
    is in force, and a destination whose canonical form sits inside that repository's
    ``base`` directory is refused outright. Every check runs before any directory is
    created and before any temporary entry is written. The accepted destination is
    returned with the directory the write descends from and an open descriptor on it:
    the repository directory under the default root, whose
    ``modernization/harness/build`` components this tool creates where they are absent,
    and the named output root, which must already exist inside those components, when
    one is given. That descriptor is obtained while this function validates the
    destination, by descending one component at a time without following a symbolic
    link, and is confirmed to still hold the directory the anchor names before it is
    returned; it is the caller's to close, and a rule refused after it is open closes it
    before raising.
    """
    _refuse_control_characters(path, "destination", "refusing to write")
    given = _absolute_path(path)
    if os.path.islink(given):
        raise InputOutputError(
            f"destination {_path_shown(path)} is a symbolic link; refusing to write"
        )

    destination = _canonical_path(given)
    if os.path.lexists(destination) and not os.path.isfile(destination):
        raise InputOutputError(
            f"destination {_path_shown(path)} exists and is not a regular file; "
            "refusing to write"
        )

    root = _allowed_output_root(output_root)
    try:
        if destination == root.path or not destination.is_relative_to(root.path):
            raise InputOutputError(
                f"destination {_path_shown(path)} resolves to "
                f"{_path_shown(destination)}, which is not a file inside the output "
                f"root {_path_shown(root.path)}; refusing to write"
            )

        repository = _canonical_path(REPOSITORY_ROOT)
        source_root = repository / "base"
        if destination.is_relative_to(source_root):
            raise InputOutputError(
                f"destination {_path_shown(path)} resolves to "
                f"{_path_shown(destination)} inside the read-only source directory "
                f"{_path_shown(source_root)}; refusing to write"
            )

        build_root = _validated_build_root()
        inside_repository = destination.is_relative_to(repository)
        if inside_repository and not destination.is_relative_to(build_root):
            raise InputOutputError(
                f"destination {_path_shown(path)} resolves to "
                f"{_path_shown(destination)} inside the repository, outside "
                f"{_path_shown(build_root)}; refusing to write"
            )
        _confirm_same_directory(root.descriptor, root.anchor, "directory")
    except BuildError:
        with contextlib.suppress(OSError):
            os.close(root.descriptor)
        raise
    return _Destination(anchor=root.anchor, anchor_fd=root.descriptor, path=destination)


def _temporary_entry(name: str, dirfd: int, mode: int) -> tuple[str, int]:
    """Create one exclusive temporary entry beside ``name`` and return its name and fd.

    The entry is created relative to ``dirfd`` with ``O_EXCL`` and ``O_NOFOLLOW``. An
    entry that already carries the candidate name, a symbolic link included, is never
    written through. Up to ``MAX_TEMPORARY_ATTEMPTS`` candidate names are tried before
    the write is refused.
    """
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    for _attempt in range(MAX_TEMPORARY_ATTEMPTS):
        candidate = f".{name}.{os.getpid()}.{os.urandom(6).hex()}.partial"
        try:
            return (candidate, os.open(candidate, flags, mode, dir_fd=dirfd))
        except FileExistsError:
            continue
    raise InputOutputError(
        f"cannot create a temporary entry beside {_escaped(name)}: "
        f"{MAX_TEMPORARY_ATTEMPTS} candidate names are all taken; refusing to write"
    )


def _write_through(handle: int, payload: bytes) -> None:
    """Write every byte of ``payload`` through ``handle`` and flush it to the device."""
    offset = 0
    while offset < len(payload):
        offset += os.write(handle, payload[offset:])
    os.fsync(handle)


def _read_back(name: str, dirfd: int, limit: int) -> bytes:
    """Return at most ``limit`` bytes of ``name``, read relative to ``dirfd``.

    The entry is opened with ``O_NOFOLLOW``. A symbolic link put in place of the
    written record is reported rather than followed.
    """
    handle = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=dirfd)
    try:
        chunks: list[bytes] = []
        remaining = limit
        while remaining > 0:
            chunk = os.read(handle, min(remaining, READ_BACK_CHUNK_BYTES))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        return b"".join(chunks)
    finally:
        os.close(handle)


def _relative_components(anchor: Path, destination: Path) -> tuple[str, ...]:
    """Return the components leading from ``anchor`` to ``destination``, name last.

    Both paths are already canonical, so every component is a plain entry name. A
    component the descriptor walk cannot take one name at a time, and a destination not
    below ``anchor``, are internal inconsistencies and each raises ``InputOutputError``.
    """
    try:
        relative = destination.relative_to(anchor)
    except ValueError as error:
        raise InputOutputError(
            f"destination {_path_shown(destination)} does not sit below "
            f"{_path_shown(anchor)}; refusing to write"
        ) from error

    components = relative.parts
    unwalkable = [
        name
        for name in components
        if name in ("", os.curdir, os.pardir) or os.sep in name or os.path.isabs(name)
    ]
    if not components or unwalkable:
        raise InputOutputError(
            f"destination {_path_shown(destination)} does not name plain entries below "
            f"{_path_shown(anchor)}; refusing to write"
        )
    return components


def _descended_directory(parent_fd: int, component: str, anchor: Path) -> int:
    """Return a descriptor for ``component`` in ``parent_fd``, creating it if absent.

    The single component is created and opened relative to ``parent_fd`` and never as
    part of a path that could be resolved again, so ``O_NOFOLLOW`` refuses a symbolic
    link standing in its place at this level as it does at every other. ``anchor`` names
    the directory the walk descends from in every diagnostic.
    """
    try:
        os.mkdir(component, DIRECTORY_MODE, dir_fd=parent_fd)
    except FileExistsError:
        pass
    except OSError as error:
        raise InputOutputError(
            f"cannot create directory {_escaped(component)} below "
            f"{_path_shown(anchor)}: {error.strerror or error}"
        ) from error

    try:
        return os.open(
            component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd
        )
    except OSError as error:
        raise InputOutputError(
            f"cannot open directory {_escaped(component)} below "
            f"{_path_shown(anchor)}: {error.strerror or error}"
        ) from error


def _parent_descriptor(
    anchor_fd: int, anchor: Path, components: tuple[str, ...]
) -> int:
    """Return a descriptor for the directory holding the destination entry.

    The walk starts from a duplicate of ``anchor_fd``, so the caller's descriptor stays
    open and remains the caller's to close, and each component below it is created where
    absent and opened relative to the descriptor above it, so a symbolic link is refused
    at every level and no component is resolved from a full path. Each descriptor the
    walk owns is closed as it descends past it; the descriptor returned is the caller's
    to close. ``anchor`` names the directory the walk descends from in every diagnostic.
    """
    try:
        dirfd = os.dup(anchor_fd)
    except OSError as error:
        raise InputOutputError(
            f"cannot duplicate the descriptor of the directory {_path_shown(anchor)} "
            f"the write descends from: {error.strerror or error}"
        ) from error
    for component in components:
        try:
            descended = _descended_directory(dirfd, component, anchor)
        finally:
            with contextlib.suppress(OSError):
                os.close(dirfd)
        dirfd = descended
    return dirfd


def _replaced_under_anchor(
    anchor: Path,
    anchor_fd: int,
    destination: Path,
    payload: bytes,
    mode: int,
    limit: int,
) -> bytes:
    """Write ``payload`` onto ``destination`` by descending from ``anchor_fd``.

    ``anchor_fd`` is the descriptor already open on ``anchor``; this function descends
    from a duplicate of it, never resolves ``anchor`` as a pathname and never closes the
    caller's descriptor, which stays the caller's to close. The directory holding the
    destination is reached by opening each component below the anchor one at a time,
    creating a component that is absent. The payload is written to a temporary entry
    created exclusively relative to that descriptor, flushed to the device, renamed onto
    the destination name and read back, all through the same descriptor. The temporary
    entry is removed through it when any step fails, every descriptor this function owns
    is closed, no failure of any of those steps leaves this function as anything other
    than a ``BuildError``, and at most ``limit`` bytes of the result are returned.
    """
    components = _relative_components(anchor, destination)
    name = components[-1]
    dirfd = _parent_descriptor(anchor_fd, anchor, components[:-1])

    temporary: str | None = None
    try:
        try:
            temporary, handle = _temporary_entry(name, dirfd, mode)
            try:
                _write_through(handle, payload)
            finally:
                os.close(handle)
            os.replace(temporary, name, src_dir_fd=dirfd, dst_dir_fd=dirfd)
            temporary = None
        except OSError as error:
            raise InputOutputError(
                f"cannot write record to {_path_shown(destination)}: "
                f"{error.strerror or error}"
            ) from error
        try:
            return _read_back(name, dirfd, limit)
        except OSError as error:
            raise InputOutputError(
                f"cannot read back {_path_shown(destination)}: "
                f"{error.strerror or error}"
            ) from error
    finally:
        if temporary is not None:
            with contextlib.suppress(OSError):
                os.unlink(temporary, dir_fd=dirfd)
        with contextlib.suppress(OSError):
            os.close(dirfd)


def write_record(
    path: str | os.PathLike[str],
    record: str,
    output_root: str | os.PathLike[str] | None = None,
) -> Path:
    """Write ``record`` to ``path`` as one line closed by a single newline.

    The record must already hold ``expected_length`` characters and only 7-bit ASCII.
    The destination is canonicalised and confined to ``output_root``, which must itself
    stand inside the validated generated-output root and defaults to that root, before
    anything is created, and that validation leaves one descriptor open on the directory
    the write descends from, obtained by descending one component at a time without
    following a symbolic link. The write then runs through
    descriptors only: every directory below that one is created where absent and opened
    by single component relative to the descriptor above it, and the characters are
    written to a temporary entry, flushed to the device, renamed onto the destination
    name and read back through the descriptor holding it, then compared byte for byte
    with the rendered characters before the canonical destination path is returned. The
    descriptor validation opened is closed before this function returns or raises.
    """
    if len(record) != COMMAREA_RECORD_LENGTH:
        raise FieldMapError(
            f"record is {len(record)} characters, expected {COMMAREA_RECORD_LENGTH}; "
            "refusing to write"
        )
    if not record.isascii():
        position, offender = next(
            (index, character)
            for index, character in enumerate(record, start=1)
            if not character.isascii()
        )
        raise SampleError(
            f"record holds a character outside 7-bit ASCII at position {position} "
            f"(code point {ord(offender)}); refusing to write"
        )

    destination = _validated_destination(path, output_root)
    try:
        payload = (record + "\n").encode("ascii")
        written = _replaced_under_anchor(
            destination.anchor,
            destination.anchor_fd,
            destination.path,
            payload,
            _default_file_mode(),
            len(payload) + 1,
        )
        if written != payload:
            if len(written) > len(payload):
                detail = f"holds more than the expected {len(payload)} bytes"
            elif len(written) != len(payload):
                detail = f"holds {len(written)} bytes, expected {len(payload)}"
            else:
                detail = "content differs from the rendered record"
            raise InputOutputError(
                f"{_path_shown(destination.path)} {detail} after writing"
            )
        return destination.path
    finally:
        with contextlib.suppress(OSError):
            os.close(destination.anchor_fd)


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


# Self-test support: the copybook layout oracle. It reads base/src/lgcmarea.cpy and
# computes every item's offset, length and kind without consulting the field map.

# Zero-based index of the fixed-format indicator column and the end of area B.
_INDICATOR_COLUMN = 6
_AREA_END_COLUMN = 72

# Repository-relative copybook path each exercised layout group cites.
_COPYBOOK_REPOSITORY_PATH = "base/src/lgcmarea.cpy"

_COPYBOOK_DATA_LINE = re.compile(r"^(\d{2})\s+([A-Za-z0-9][A-Za-z0-9-]*)(.*)$")
_COPYBOOK_PICTURE = re.compile(
    r"\bPIC(?:TURE)?\s+(?:IS\s+)?([A-Za-z0-9()]+)", re.IGNORECASE
)
_COPYBOOK_REDEFINES = re.compile(
    r"\bREDEFINES\s+([A-Za-z0-9][A-Za-z0-9-]*)", re.IGNORECASE
)
_PICTURE_TOKEN = re.compile(r"([X9])(?:\((\d+)\))?")
_LINE_RANGE = re.compile(r"^(\d+)-(\d+)$")


class CopybookItem(NamedTuple):
    """One item parsed from the COMMAREA copybook."""

    name: str
    level: int
    line: int
    offset: int
    length: int
    kind: str
    redefines: str | None

    @property
    def end_byte(self) -> int:
        """Return the 1-based position of the item's last character."""
        return self.offset + self.length - 1


class CopybookLayout(NamedTuple):
    """The parsed copybook: items keyed by upper-case name, plus the record length."""

    items: dict[str, CopybookItem]
    record_length: int


class _OpenGroup:
    """One group item whose children are still being read."""

    __slots__ = ("cursor", "level", "line", "name", "offset", "redefines")

    def __init__(
        self, level: int, name: str, line: int, offset: int, redefines: str | None
    ) -> None:
        self.level = level
        self.name = name
        self.line = line
        self.offset = offset
        self.cursor = offset
        self.redefines = redefines


def _picture_length_and_kind(picture: str, where: str) -> tuple[int, str]:
    """Return the character count and item kind of one PICTURE clause.

    ``X`` and ``9`` symbols are read, each optionally followed by a parenthesised
    repeat count, so ``X(6)``, ``9(10)``, ``99`` and ``X`` all resolve. An item using
    any other symbol raises ``SelfTestError`` naming the clause.
    """
    position = 0
    total = 0
    symbols: set[str] = set()
    while position < len(picture):
        token = _PICTURE_TOKEN.match(picture, position)
        if token is None:
            raise SelfTestError(
                f"{where}: PICTURE {_display(picture)} uses a symbol this parse does "
                f"not read"
            )
        total += int(token.group(2)) if token.group(2) else 1
        symbols.add(token.group(1).upper())
        position = token.end()
    if total < 1:
        raise SelfTestError(
            f"{where}: PICTURE {_display(picture)} describes no character"
        )
    return total, KIND_ALPHANUMERIC if "X" in symbols else KIND_NUMERIC


def _record_copybook_item(
    items: dict[str, CopybookItem], item: CopybookItem, where: str
) -> None:
    """Store one parsed item, rejecting a name the copybook already declared."""
    key = item.name.upper()
    existing = items.get(key)
    if existing is not None:
        raise SelfTestError(
            f"{where}: item {_display(item.name)} on line {item.line} repeats the "
            f"name declared on line {existing.line}"
        )
    items[key] = item


def _close_copybook_group(
    stack: list[_OpenGroup], items: dict[str, CopybookItem], where: str
) -> None:
    """Finish the innermost open group and advance its parent when it adds bytes."""
    group = stack.pop()
    length = group.cursor - group.offset
    if length < 1:
        raise SelfTestError(
            f"{where}: group {_display(group.name)} on line {group.line} declares no "
            f"item"
        )
    _record_copybook_item(
        items,
        CopybookItem(
            name=group.name,
            level=group.level,
            line=group.line,
            offset=group.offset,
            length=length,
            kind=KIND_GROUP,
            redefines=group.redefines,
        ),
        where,
    )
    if group.redefines is None:
        stack[-1].cursor = group.offset + length


def parse_copybook_layout(
    path: str | os.PathLike[str] | None = None,
) -> CopybookLayout:
    """Parse the COMMAREA copybook into offsets, lengths and kinds.

    ``path`` defaults to ``COMMAREA_COPYBOOK``. A line carrying ``*`` or ``/`` in the
    fixed-format indicator column is a comment; every other line declares one level
    number, one item name and either a PICTURE clause or a group. An item with a
    REDEFINES clause starts at the offset already recorded for the item it names and
    adds no bytes to its parent. Offsets are 1-based positions in the emitted record,
    and the returned record length is the total the level-01 group would occupy.

    Raises ``SelfTestError`` naming the file and line for any construct this parse does
    not read.
    """
    copybook = Path(path) if path is not None else COMMAREA_COPYBOOK
    where = f"copybook {_display(str(copybook))}"
    try:
        text = copybook.read_text(encoding="utf-8")
    except OSError as error:
        raise SelfTestError(f"cannot read {where}: {_reason(error)}") from error
    except UnicodeError as error:
        raise SelfTestError(
            f"{where} is not valid UTF-8 text: {_reason(error)}"
        ) from error

    items: dict[str, CopybookItem] = {}
    stack = [_OpenGroup(level=0, name="DFHCOMMAREA", line=0, offset=1, redefines=None)]
    for number, raw in enumerate(text.splitlines(), start=1):
        if len(raw) > _INDICATOR_COLUMN and raw[_INDICATOR_COLUMN] in "*/":
            continue
        body = raw[_INDICATOR_COLUMN + 1 : _AREA_END_COLUMN].strip()
        if not body:
            continue
        declaration = _COPYBOOK_DATA_LINE.match(body)
        if declaration is None:
            raise SelfTestError(
                f"{where} line {number}: cannot read a level number and item name "
                f"from {_display(body)}"
            )
        level = int(declaration.group(1))
        name = declaration.group(2)
        if not 1 <= level <= 49:
            raise SelfTestError(
                f"{where} line {number}: level {level} is not a data description this "
                f"parse reads"
            )
        clauses = declaration.group(3).strip()
        if not clauses.endswith("."):
            raise SelfTestError(
                f"{where} line {number}: declaration {_display(body)} does not end "
                f"with a period"
            )
        clauses = clauses[:-1].strip()

        redefines: str | None = None
        redefines_clause = _COPYBOOK_REDEFINES.search(clauses)
        if redefines_clause is not None:
            redefines = redefines_clause.group(1).upper()
            clauses = (
                clauses[: redefines_clause.start()] + clauses[redefines_clause.end() :]
            ).strip()
        picture: str | None = None
        picture_clause = _COPYBOOK_PICTURE.search(clauses)
        if picture_clause is not None:
            picture = picture_clause.group(1)
            clauses = (
                clauses[: picture_clause.start()] + clauses[picture_clause.end() :]
            ).strip()
        if clauses:
            raise SelfTestError(
                f"{where} line {number}: clause {_display(clauses)} is not a construct "
                f"this parse reads"
            )

        while stack[-1].level >= level:
            _close_copybook_group(stack, items, where)
        parent = stack[-1]
        if redefines is not None:
            target = items.get(redefines)
            if target is None:
                raise SelfTestError(
                    f"{where} line {number}: REDEFINES names {_display(redefines)}, "
                    f"which is not declared above it"
                )
            offset = target.offset
        else:
            offset = parent.cursor

        if picture is None:
            stack.append(
                _OpenGroup(
                    level=level,
                    name=name,
                    line=number,
                    offset=offset,
                    redefines=redefines,
                )
            )
            continue
        length, kind = _picture_length_and_kind(picture, f"{where} line {number}")
        _record_copybook_item(
            items,
            CopybookItem(
                name=name,
                level=level,
                line=number,
                offset=offset,
                length=length,
                kind=kind,
                redefines=redefines,
            ),
            where,
        )
        if redefines is None:
            parent.cursor = offset + length

    while len(stack) > 1:
        _close_copybook_group(stack, items, where)
    if not items:
        raise SelfTestError(f"{where} declares no item")
    return CopybookLayout(items=items, record_length=stack[0].cursor - 1)


# Self-test support: the expected content of every window each fixture produces. Item
# names index the copybook parse for the offset and length; the values are literals.


class _Fill(NamedTuple):
    """Expectation that a whole window holds one repeated character."""

    character: str


_FILL_SPACES = _Fill(" ")
_FILL_ZEROS = _Fill("0")

# The literal the field map seeds the CA-RETURN-CODE window with, held by this matrix
# independently of that document: the fixture cases compare the emitted record against
# this literal, and the self-test compares the seed the field map declares against it.
# It stands outside the return_codes domain the field map declares for that item, so a
# code inside that domain on an executed record is one the chain wrote. See
# modernization/docs/decision-log.md.
_CHAIN_RETURN_CODE_SEED = "55"

# Content every chain-populated window carries on the emitted record, before the chain
# runs. The three names are the items sample_definition_contract.chain_populated_items
# records: the seeded return-code window, the zero-filled identity window and the
# space-filled timestamp window.
_CHAIN_WINDOW_CONTENT: dict[str, str | _Fill] = {
    "CA-RETURN-CODE": _CHAIN_RETURN_CODE_SEED,
    "CA-POLICY-NUM": _FILL_ZEROS,
    "CA-LASTCHANGED": _FILL_SPACES,
}

# Seeds the adversarial chain-populated cases offer in place of the accepted one: the
# success code, a member of the domain the return_code logical entry declares; a
# two-character value whose second character is not a digit; and, for the foreign-entry
# case, one request-supplied numeric item the chain does not assign.
_RETURN_CODE_DOMAIN_MEMBER = "00"
_NON_DIGIT_SEED = "5X"
_FOREIGN_CHAIN_ITEM = "CA-PAYMENT"


class _FixtureKeys(NamedTuple):
    """The keys one fixture supplies and the items it leaves at their fill.

    ``supplied`` is the complete key set the fixture document declares. ``omitted``
    names every window of the selected layout the fixture must not supply: the items
    the chain assigns, the protected filler and every other window that holds its fill
    character on the emitted record.
    """

    supplied: frozenset[str]
    omitted: frozenset[str]


_MOTOR_EXPECTED_WINDOWS: dict[str, str | _Fill] = {
    "CA-REQUEST-ID": "01AMOT",
    "CA-RETURN-CODE": _CHAIN_WINDOW_CONTENT["CA-RETURN-CODE"],
    "CA-CUSTOMER-NUM": "0000001001",
    "CA-POLICY-NUM": _CHAIN_WINDOW_CONTENT["CA-POLICY-NUM"],
    "CA-ISSUE-DATE": "2026-08-19",
    "CA-EXPIRY-DATE": "2027-08-18",
    "CA-LASTCHANGED": _CHAIN_WINDOW_CONTENT["CA-LASTCHANGED"],
    "CA-BROKERID": "0000000042",
    "CA-BROKERSREF": "BRMOT001" + " " * 2,
    "CA-PAYMENT": "000500",
    "CA-M-MAKE": "FORD" + " " * 11,
    "CA-M-MODEL": "FIESTA" + " " * 9,
    "CA-M-VALUE": "012500",
    "CA-M-REGNUMBER": "AB12CDE",
    "CA-M-COLOUR": "BLUE" + " " * 4,
    "CA-M-CC": "1400",
    "CA-M-MANUFACTURED": "2019-03-15",
    "CA-M-PREMIUM": "000450",
    "CA-M-ACCIDENTS": "000001",
    "CA-M-FILLER": _FILL_SPACES,
}

_COMMERCIAL_EXPECTED_WINDOWS: dict[str, str | _Fill] = {
    "CA-REQUEST-ID": "01ACOM",
    "CA-RETURN-CODE": _CHAIN_WINDOW_CONTENT["CA-RETURN-CODE"],
    "CA-CUSTOMER-NUM": "0000002002",
    "CA-POLICY-NUM": _CHAIN_WINDOW_CONTENT["CA-POLICY-NUM"],
    "CA-ISSUE-DATE": "2026-08-19",
    "CA-EXPIRY-DATE": "2027-08-18",
    "CA-LASTCHANGED": _CHAIN_WINDOW_CONTENT["CA-LASTCHANGED"],
    "CA-BROKERID": "0000000084",
    "CA-BROKERSREF": "BRCOM001" + " " * 2,
    "CA-PAYMENT": "001750",
    "CA-B-Address": "1 EXAMPLE INDUSTRIAL ESTATE, EXAMPLE TOWN" + " " * 214,
    "CA-B-Postcode": "EX1 2AB" + " ",
    "CA-B-Latitude": "51.4779" + " " * 4,
    "CA-B-Longitude": "-0.0015" + " " * 4,
    "CA-B-Customer": "EXAMPLE MANUFACTURING LTD" + " " * 230,
    "CA-B-PropType": "WAREHOUSE" + " " * 246,
    "CA-B-FirePeril": "0011",
    "CA-B-FirePremium": "00013500",
    "CA-B-CrimePeril": "0022",
    "CA-B-CrimePremium": "00003400",
    "CA-B-FloodPeril": "0033",
    "CA-B-FloodPremium": "00007800",
    "CA-B-WeatherPeril": "0044",
    "CA-B-WeatherPremium": "00002600",
    "CA-B-Status": "0000",
    "CA-B-RejectReason": " " * 255,
    "CA-B-FILLER": _FILL_SPACES,
}

_MOTOR_FIXTURE_KEYS = _FixtureKeys(
    supplied=frozenset(
        {
            "CA-REQUEST-ID",
            "CA-CUSTOMER-NUM",
            "CA-ISSUE-DATE",
            "CA-EXPIRY-DATE",
            "CA-BROKERID",
            "CA-BROKERSREF",
            "CA-PAYMENT",
            "CA-M-MAKE",
            "CA-M-MODEL",
            "CA-M-VALUE",
            "CA-M-REGNUMBER",
            "CA-M-COLOUR",
            "CA-M-CC",
            "CA-M-MANUFACTURED",
            "CA-M-PREMIUM",
            "CA-M-ACCIDENTS",
        }
    ),
    omitted=frozenset(
        {
            "CA-RETURN-CODE",
            "CA-POLICY-NUM",
            "CA-LASTCHANGED",
            "CA-M-FILLER",
        }
    ),
)

_COMMERCIAL_FIXTURE_KEYS = _FixtureKeys(
    supplied=frozenset(
        {
            "CA-REQUEST-ID",
            "CA-CUSTOMER-NUM",
            "CA-ISSUE-DATE",
            "CA-EXPIRY-DATE",
            "CA-BROKERID",
            "CA-BROKERSREF",
            "CA-PAYMENT",
            "CA-B-Address",
            "CA-B-Postcode",
            "CA-B-Latitude",
            "CA-B-Longitude",
            "CA-B-Customer",
            "CA-B-PropType",
            "CA-B-FirePeril",
            "CA-B-FirePremium",
            "CA-B-CrimePeril",
            "CA-B-CrimePremium",
            "CA-B-FloodPeril",
            "CA-B-FloodPremium",
            "CA-B-WeatherPeril",
            "CA-B-WeatherPremium",
            "CA-B-Status",
        }
    ),
    omitted=frozenset(
        {
            "CA-RETURN-CODE",
            "CA-POLICY-NUM",
            "CA-LASTCHANGED",
            "CA-B-RejectReason",
            "CA-B-FILLER",
        }
    ),
)

# Commercial status value the companion case supplies in place of the fixture's zeros.
_NON_ZERO_COMMERCIAL_STATUS = "0407"

# Repeated text the adversarial commercial case fills CA-B-Address with.
_WIDE_ADDRESS_PATTERN = "EXAMPLE COMMERCIAL PREMISES BLOCK "

# Values narrower than their windows that the short-value case supplies in place of the
# motor fixture's full-width payment and colour, and the windows they must produce: the
# numeric value right-justified over zeros, the alphanumeric value left-justified over
# spaces.
_SHORT_NUMERIC_VALUE = "500"
_SHORT_ALPHANUMERIC_VALUE = "RED"
_SHORT_VALUE_EXPECTED_WINDOWS: dict[str, str | _Fill] = {
    **_MOTOR_EXPECTED_WINDOWS,
    "CA-PAYMENT": "000500",
    "CA-M-COLOUR": "RED" + " " * 5,
}

# The one window the short-value record moves when a field map justifies numeric values
# to the left instead: the same three digits padded on their right. The alphanumeric
# windows and every full-width numeric window hold the content above either way, so a
# left-justifying field map must produce this table and nothing else.
_LEFT_JUSTIFIED_NUMERIC_ITEM = "CA-PAYMENT"
_LEFT_JUSTIFIED_NUMERIC_WINDOW = "500000"
_LEFT_NUMERIC_EXPECTED_WINDOWS: dict[str, str | _Fill] = {
    **_SHORT_VALUE_EXPECTED_WINDOWS,
    _LEFT_JUSTIFIED_NUMERIC_ITEM: _LEFT_JUSTIFIED_NUMERIC_WINDOW,
}

# The four commercial premium items and the value the motor case offers for the first of
# them. Their windows fall inside CA-M-FILLER on a motor record.
_COMMERCIAL_PREMIUM_ITEMS = (
    "CA-B-FirePremium",
    "CA-B-CrimePremium",
    "CA-B-FloodPremium",
    "CA-B-WeatherPremium",
)
_COMMERCIAL_PREMIUM_PROBE = "00013500"

# The one 7-bit ASCII character the length case appends to a rendered record, so
# write_record is offered one character more than it writes.
_EXTRA_RECORD_CHARACTER = "0"

# The field map's product premium nullability claim, held here as literals: the builder
# cases it may name for the record bytes, the statements it withholds, the dbt test that
# carries the transformed column-level assertion and the cases it requires of that test.
# That test stands in the tree at this milestone and no case in this matrix runs it; the
# literals below compare the claim's metadata and read no warehouse column.
_NULLABILITY_CLAIMED_CASES = frozenset(
    {"commercial_inactive_overlay_filled", "motor_inactive_overlay_spaces"}
)
_NULLABILITY_WITHHELD = (
    "any raw, staging, intermediate or canonical column value",
    "motor_premium_amount IS NULL while the four commercial premiums carry values",
    "the four commercial premiums IS NULL while motor_premium_amount carries a value",
)
_NULLABILITY_TRANSFORMED_TEST = (
    "modernization/dbt/genapp_rqi/tests/assert_product_premium_nullability.sql"
)
_NULLABILITY_INACTIVE_BYTES = "non_blank"
_NULLABILITY_REQUIRED_CASES: dict[str, dict[str, Any]] = {
    "M": {
        "policy_type": "M",
        "raw_inactive_overlay_bytes": _NULLABILITY_INACTIVE_BYTES,
        "populated": ["motor_premium_amount"],
        "null_fields": [
            "fire_premium_amount",
            "crime_premium_amount",
            "flood_premium_amount",
            "weather_premium_amount",
        ],
    },
    "C": {
        "policy_type": "C",
        "raw_inactive_overlay_bytes": _NULLABILITY_INACTIVE_BYTES,
        "populated": [
            "fire_premium_amount",
            "crime_premium_amount",
            "flood_premium_amount",
            "weather_premium_amount",
        ],
        "null_fields": ["motor_premium_amount"],
    },
}

# Anchored sequences the alias case expands to _ALIAS_DAG_FANOUT ** _ALIAS_DAG_LEVELS
# leaf values, and the self-referential mapping the cyclic case declares.
_ALIAS_DAG_KEY = "alias_dag_probe"
_ALIAS_DAG_LEVELS = 6
_ALIAS_DAG_FANOUT = 10
_CYCLIC_ALIAS_TEXT = "cycle_probe: &cycle_probe\n  child: *cycle_probe\n"

# Mapping key a loader cannot compare against the keys already seen.
_UNHASHABLE_KEY_TEXT = "unhashable_probe:\n  ? [1, 2]\n  : compared by no loader\n"

# Container nesting the parser case uses; it stays inside MAX_SAMPLE_BYTES and exceeds
# the nesting the JSON parser reads before it raises.
_PARSER_NESTING_PROBE = 25000


class _SelfTestFailure(Exception):
    """One self-test case did not hold; the message states what was observed."""


class _CaseResult(NamedTuple):
    """The outcome of one self-test case."""

    name: str
    passed: bool
    detail: str


class _CliResult(NamedTuple):
    """The status and captured streams of one command line run in this process."""

    status: int
    stdout: str
    stderr: str


def _designated_output_root(tree: _HeldTree, argv: list[str]) -> list[str]:
    """Return ``argv`` with the held run directory named as the output root.

    Every self-test case writes inside the private run directory this self-test holds
    under ``modernization/harness/build/builder-selftest``, so that directory is named
    to the tool as the root the ``--output`` argument must resolve inside, which
    exercises ``--output-root`` on every case that builds or is refused a record. It is
    named by its canonical path, the form the tool accepts for a root, and it stands
    inside the validated generated-output root, so it is accepted for the same reason
    any other directory below that root is. An ``argv`` that already names a root, or
    that names no destination, is returned unchanged.

    The destination it designates that root for must name an entry below the held run
    directory, spelled either below the pathname of the descriptor held on it or below
    its canonical path. A destination spelled any other way would receive a root it does
    not stand inside, so it is refused here as an inconsistency of this matrix rather
    than handed to a run under test.
    """
    if "--output" not in argv or "--output-root" in argv:
        return argv
    destination = argv[argv.index("--output") + 1]
    accepted = (f"{tree.handoff()}{os.sep}", f"{tree.path}{os.sep}")
    if not destination.startswith(accepted):
        raise _SelfTestFailure(
            f"destination {_display(destination)} names no entry below the private run "
            f"directory {_path_shown(tree.path)} this matrix writes inside"
        )
    return [*argv, "--output-root", str(tree.path)]


def _run_cli(tree: _HeldTree, argv: list[str]) -> _CliResult:
    """Run one command line in this process and capture its status and streams.

    Every scratch document a case names sits inside the private run directory below
    ``modernization/harness/build``, which is one of the validated read roots, so no
    command line this runner assembles needs an authority a caller could not obtain.
    The command line is one pathname handoff: the held run directory is confirmed to
    still be named by the entry it was created under immediately before the run starts
    and immediately after it returns, so a visible name replaced around the run is
    reported instead of being handed to it.
    """

    def _run() -> _CliResult:
        out = io.StringIO()
        err = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                status = main(_designated_output_root(tree, argv))
            except SystemExit as request:
                status = request.code if isinstance(request.code, int) else 1
        return _CliResult(status=status, stdout=out.getvalue(), stderr=err.getvalue())

    return _handed_off(tree, "self-test run directory", _run)


def _assert_diagnostic(stderr: str) -> None:
    """Confirm a failure wrote one printable 7-bit ASCII line naming this tool."""
    if not stderr:
        raise _SelfTestFailure("wrote no diagnostic to stderr")
    if not stderr.endswith("\n") or stderr.count("\n") != 1:
        raise _SelfTestFailure(
            f"diagnostic holds {stderr.count(chr(10))} newline(s), expected 1"
        )
    line = stderr[:-1]
    if not line.startswith(f"{_PROGRAM}: "):
        raise _SelfTestFailure(f"diagnostic does not name this tool: {_display(line)}")
    outside = [
        character for character in line if not 0x20 <= ord(character) <= 0x7E
    ]
    if outside:
        raise _SelfTestFailure(
            f"diagnostic holds {_display(outside[0])} outside printable ASCII"
        )


def _first_difference(left: str, right: str) -> int:
    """Return the 0-based index of the first character at which two strings differ."""
    for position in range(max(len(left), len(right))):
        if left[position : position + 1] != right[position : position + 1]:
            return position
    return -1


def _expectation_text(expectation: str | _Fill, item: CopybookItem) -> str:
    """Return the expected characters of one window at its copybook length."""
    if isinstance(expectation, _Fill):
        return expectation.character * item.length
    return expectation


def _expected_record(
    expectations: dict[str, str | _Fill], layout: CopybookLayout
) -> str:
    """Assemble the whole expected record from the literal window contents.

    Each expectation is placed at the offset the copybook parse reports for its item,
    every byte no expectation claims stays a space, and any expectation whose width
    differs from the copybook length raises ``_SelfTestFailure``.
    """
    buffer = [" "] * layout.record_length
    for name, expectation in expectations.items():
        item = layout.items.get(name.upper())
        if item is None:
            raise _SelfTestFailure(
                f"copybook declares no item {_display(name)} for the expected content"
            )
        text = _expectation_text(expectation, item)
        if len(text) != item.length:
            raise _SelfTestFailure(
                f"expected content for {_display(name)} is {len(text)} characters, "
                f"copybook declares {item.length}"
            )
        buffer[item.offset - 1 : item.end_byte] = list(text)
    return "".join(buffer)


def _assert_windows(
    record: str,
    expectations: dict[str, str | _Fill],
    layout: CopybookLayout,
    what: str,
) -> None:
    """Compare every expected window content against the produced record."""
    for name in sorted(expectations):
        item = layout.items.get(name.upper())
        if item is None:
            raise _SelfTestFailure(
                f"copybook declares no item {_display(name)} for the expected content"
            )
        text = _expectation_text(expectations[name], item)
        placed = record[item.offset - 1 : item.end_byte]
        if placed == text:
            continue
        position = _first_difference(placed, text)
        raise _SelfTestFailure(
            f"{what} item {_display(name)} differs at byte {item.offset + position}: "
            f"holds {_display(placed[position : position + 12])}, expected "
            f"{_display(text[position : position + 12])}"
        )


def _assert_fixture_keys(
    sample: dict[str, str], keys: _FixtureKeys, what: str
) -> None:
    """Confirm one fixture supplies exactly ``keys.supplied`` and nothing else.

    Keys are compared without regard to case. The message names the missing and the
    unexpected keys, so a key removed from or added to a fixture document fails here
    before the record is rendered. ``keys.omitted`` must share no key with the
    document.
    """
    supplied = {key.upper() for key in sample}
    expected = {name.upper() for name in keys.supplied}
    if len(supplied) != len(sample):
        raise _SelfTestFailure(
            f"{what} declares {len(sample)} key(s) that differ only by case"
        )
    missing = expected - supplied
    unexpected = supplied - expected
    if missing or unexpected:
        raise _SelfTestFailure(
            f"{what} supplies {len(supplied)} key(s) where {len(expected)} are "
            f"expected; missing {_quote_all(missing) or 'nothing'}, unexpected "
            f"{_quote_all(unexpected) or 'nothing'}"
        )
    also_omitted = {name.upper() for name in keys.omitted} & supplied
    if also_omitted:
        raise _SelfTestFailure(
            f"{what} supplies {_quote_all(also_omitted)}, which it must leave at the "
            f"fill character"
        )


def _assert_fill_windows(
    record: str, omitted: Iterable[str], layout: CopybookLayout, what: str
) -> None:
    """Confirm every window the fixture omits holds the content declared for it.

    A window named by ``_CHAIN_WINDOW_CONTENT`` is a window the chain assigns and holds
    the pre-execution content that table records for it, which is what the chain
    overwrites; the comparison therefore states what the record carried before the run
    rather than what a fill character would have put there. Every other omitted window
    holds the fill its kind declares: the digit zero across a numeric window, spaces
    across an alphanumeric one. The expected characters come from the copybook parse and
    from that table, not from the field map or the expected-window table.
    """
    for name in sorted(omitted):
        item = layout.items.get(name.upper())
        if item is None:
            raise _SelfTestFailure(
                f"copybook declares no item {_display(name)} for the omitted window"
            )
        stated = _CHAIN_WINDOW_CONTENT.get(name.upper())
        if stated is not None:
            expected = _expectation_text(stated, item)
            if len(expected) != item.length:
                raise _SelfTestFailure(
                    f"the declared content of chain-populated item {_display(name)} is "
                    f"{len(expected)} characters, copybook declares {item.length}"
                )
            wanted = f"the declared content {_display(expected)}"
        else:
            if item.kind == KIND_NUMERIC:
                fill = "0"
            elif item.kind == KIND_ALPHANUMERIC:
                fill = " "
            else:
                raise _SelfTestFailure(
                    f"copybook declares {_display(name)} as {item.kind}, which no fill "
                    f"character covers"
                )
            expected = fill * item.length
            wanted = f"the {_display(fill)} fill"
        placed = record[item.offset - 1 : item.end_byte]
        if placed == expected:
            continue
        position = _first_difference(placed, expected)
        raise _SelfTestFailure(
            f"{what} omitted item {_display(name)} holds "
            f"{_display(placed[position : position + 12])} at byte "
            f"{item.offset + position}, expected {wanted}"
        )


def _read_record(tree: _HeldTree, name: str, what: str) -> str:
    """Return the record at ``name`` after checking its byte count and newline.

    The entry is read through the descriptor held on the run directory, so the record
    compared is the one the run under test wrote below that directory and no pathname is
    resolved to reach it. A read of more than the emitted record and its newline is
    reported as an oversized record rather than truncated silently.
    """
    try:
        payload = tree.read(name)
    except BuildError as error:
        raise _SelfTestFailure(f"{what} cannot be read: {error}") from error
    expected_bytes = COMMAREA_RECORD_LENGTH + 1
    if len(payload) != expected_bytes:
        raise _SelfTestFailure(
            f"{what} holds {len(payload)} bytes, expected {expected_bytes}"
        )
    if not payload.endswith(b"\n") or payload.count(b"\n") != 1:
        raise _SelfTestFailure(f"{what} does not end with exactly one newline")
    try:
        return payload[:-1].decode("ascii")
    except UnicodeError as error:
        raise _SelfTestFailure(
            f"{what} holds bytes outside 7-bit ASCII: {_reason(error)}"
        ) from error


def _line_range(group_name: str, group: dict[str, Any]) -> tuple[int, int]:
    """Return the copybook line range one layout group declares."""
    declared = group.get("line_range")
    match = _LINE_RANGE.match(declared) if isinstance(declared, str) else None
    if match is None:
        raise _SelfTestFailure(
            f"layout group {_display(group_name)} declares line_range "
            f"{_display(declared)}"
        )
    first, last = int(match.group(1)), int(match.group(2))
    if first > last:
        raise _SelfTestFailure(
            f"layout group {_display(group_name)} declares line_range "
            f"{_display(declared)}, which ends before it starts"
        )
    return first, last


def _compare_declaration(
    where: str,
    declared: dict[str, Any],
    members: Iterable[tuple[str, Any]],
) -> list[str]:
    """Return one message per member of ``declared`` that the copybook contradicts."""
    problems: list[str] = []
    for member, observed in members:
        stated = declared.get(member)
        if member == "level" and isinstance(stated, str) and stated.isdigit():
            stated = int(stated)
        if member == "redefines" and isinstance(stated, str):
            stated = stated.upper()
        if stated != observed:
            problems.append(
                f"{where} declares {member} {_display(stated)}, copybook shows "
                f"{_display(observed)}"
            )
    return problems


def _layout_disagreements(
    field_map: dict[str, Any], layout: CopybookLayout
) -> list[str]:
    """Return every disagreement between the field map layout and the copybook parse.

    Each exercised group is compared in both directions: every declared item and group
    declaration must match the copybook's offset, length, kind, line, level and
    REDEFINES target, and every copybook item inside the group's declared line range
    must appear in that group.
    """
    problems: list[str] = []
    if layout.record_length != COMMAREA_RECORD_LENGTH:
        problems.append(
            f"copybook items total {layout.record_length} characters, expected "
            f"{COMMAREA_RECORD_LENGTH}"
        )
    for group_name, group in sorted(
        field_map["layout"].items(), key=lambda pair: pair[0]
    ):
        cited = group.get("copybook")
        if cited != _COPYBOOK_REPOSITORY_PATH:
            problems.append(
                f"layout group {_display(group_name)} cites copybook "
                f"{_display(cited)}, expected {_display(_COPYBOOK_REPOSITORY_PATH)}"
            )
            continue
        first, last = _line_range(group_name, group)
        declared_items: set[str] = set()
        for entry in group["items"]:
            name = str(entry.get("item"))
            declared_items.add(name.upper())
            parsed = layout.items.get(name.upper())
            if parsed is None:
                problems.append(
                    f"layout group {_display(group_name)} declares item "
                    f"{_display(name)}, which the copybook does not"
                )
                continue
            problems.extend(
                _compare_declaration(
                    f"layout item {_display(name)}",
                    entry,
                    (
                        ("offset", parsed.offset),
                        ("length", parsed.length),
                        ("kind", parsed.kind),
                        ("line", parsed.line),
                    ),
                )
            )
        declared_groups: set[str] = set()
        for entry in group.get("group_declarations") or []:
            name = str(entry.get("item"))
            declared_groups.add(name.upper())
            parsed = layout.items.get(name.upper())
            if parsed is None:
                problems.append(
                    f"layout group {_display(group_name)} declares group item "
                    f"{_display(name)}, which the copybook does not"
                )
                continue
            problems.extend(
                _compare_declaration(
                    f"layout group declaration {_display(name)}",
                    entry,
                    (
                        ("offset", parsed.offset),
                        ("length", parsed.length),
                        ("line", parsed.line),
                        ("level", parsed.level),
                        ("redefines", parsed.redefines),
                    ),
                )
            )
        for parsed in layout.items.values():
            if not first <= parsed.line <= last:
                continue
            known = declared_groups if parsed.kind == KIND_GROUP else declared_items
            if parsed.name.upper() not in known:
                problems.append(
                    f"copybook line {parsed.line} declares {_display(parsed.name)}, "
                    f"which layout group {_display(group_name)} does not"
                )
    return problems


# Self-test support: the private scratch tree every case reads and writes inside.

# Directory below the validated generated-output root that holds one directory per
# self-test run, and the components leading to it from the repository directory.
_SELF_TEST_SCRATCH_NAME = "builder-selftest"
_SELF_TEST_SCRATCH_COMPONENTS = (
    "modernization",
    "harness",
    "build",
    _SELF_TEST_SCRATCH_NAME,
)

# Attempts made to create and open the shared scratch directory before the run is
# refused, which a concurrent run removing the same emptied directory can cost.
_SCRATCH_ACQUIRE_ATTEMPTS = 8

# Directory of the running process the pathname handoff of a held descriptor is taken
# from: ``<_HANDOFF_DIRECTORY>/<descriptor>/<entry>`` names the entry below the
# directory the descriptor holds, whichever name that directory currently carries.
_HANDOFF_DIRECTORY = "/proc/self/fd"

# Bytes one fixture read takes from an entry below a held descriptor before the read is
# reported as oversized: the emitted record, its newline and one byte more.
_MAX_FIXTURE_READ_BYTES = COMMAREA_RECORD_LENGTH + 2

# Names the adversarial name-swap case creates below the private run directory: the
# probe subtree, the run directory inside it whose visible name is replaced, the name
# that replacement moves it to, and the canary directory the replaced name points at,
# which stands outside the held run directory and must gain no entry.
_SWAP_PROBE_NAME = "name_swap_probe"
_SWAP_HELD_NAME = "held_run"
_SWAP_MOVED_NAME = "held_run.moved"
_SWAP_CANARY_NAME = "outside_canary"

# Bytes the name-swap case writes through the held descriptor before and after the
# visible name is replaced, and the record a run under test is asked to write below that
# descriptor's own pathname while the replacement stands.
_SWAP_BEFORE_BYTES = b"HELD BEFORE THE NAME SWAP\n"
_SWAP_AFTER_BYTES = b"HELD AFTER THE NAME SWAP\n"
_SWAP_RECORD_NAME = "name_swap_record.rec"

# Bytes a destination offered to a refused run holds before and after that run, which
# is how a refusal that wrote nothing is told from one that wrote first.
_SENTINEL_DESTINATION_BYTES = b"SENTINEL RECORD NOT REPLACED\n"

# Value returned by a held-tree operation, carried through the pathname handoff guard.
_HandedOff = TypeVar("_HandedOff")


class _HeldTree:
    """One directory this self-test holds open, and every operation rooted in it.

    ``path`` is the canonical directory the descriptor held when it was opened, carried
    in diagnostics and in the pathname arguments a run under test must be given.
    ``name`` is the single component the directory carries below ``parent_fd``, and
    ``device`` and ``inode`` are the identity ``descriptor`` reported when this object
    took it.

    Every fixture entry is created, read, listed, renamed and removed relative to
    ``descriptor`` with ``O_NOFOLLOW``, and a subdirectory is held as one more
    ``_HeldTree`` opened relative to it the same way, so no operation this object
    performs resolves the directory as a pathname a second time and an entry replaced
    while a case runs cannot direct one outside the tree the descriptor holds.

    A pathname a run under test must be handed comes from one of two members.
    ``handoff`` names the entry below ``/proc/self/fd/<descriptor>``, which the run
    under test canonicalises to the directory the descriptor holds whatever name that
    directory currently carries, and is what every destination argument uses.
    ``named`` names the entry below the canonical path, which is the form the run under
    test accepts for an argument it refuses to reach through a symbolic-link component,
    and is what every input and output-root argument uses. ``confirm`` states that the
    descriptor still reports the recorded identity and that the visible name still names
    it, and is run immediately before and immediately after every handoff.
    """

    def __init__(
        self,
        path: Path,
        name: str,
        descriptor: int,
        parent_fd: int,
        device: int,
        inode: int,
    ) -> None:
        self.path = path
        self.name = name
        self.descriptor = descriptor
        self.parent_fd = parent_fd
        self.device = device
        self.inode = inode

    # Identity of the held directory, and of the entry that names it.

    def identity(self, what: str) -> None:
        """Confirm the descriptor still reports the identity this object recorded.

        Raises ``InputOutputError`` when the descriptor cannot be examined or reports
        another device and inode, which no operation of this object can cause and which
        a descriptor closed or replaced elsewhere in this process would.
        """
        try:
            held = os.fstat(self.descriptor)
        except OSError as error:
            raise InputOutputError(
                f"cannot confirm the {what} {_path_shown(self.path)} held for this "
                f"self-test: {error.strerror or error}"
            ) from error
        if (held.st_dev, held.st_ino) != (self.device, self.inode):
            raise InputOutputError(
                f"the descriptor held on the {what} {_path_shown(self.path)} now "
                f"reports device {held.st_dev} inode {held.st_ino} and not the "
                f"device {self.device} inode {self.inode} it reported when this "
                f"self-test took it; refusing to hand a pathname to a run under test"
            )

    def confirm(self, what: str) -> None:
        """Confirm the visible name still names the directory the descriptor holds.

        The descriptor's identity is confirmed first, then the single component below
        ``parent_fd`` is examined without following a final symbolic link and must
        report the same device and inode. A replaced, removed or relinked name raises
        ``InputOutputError`` naming what changed, so a pathname handoff is refused
        rather than made against a name that no longer names the held directory.
        """
        self.identity(what)
        try:
            named = os.stat(self.name, dir_fd=self.parent_fd, follow_symlinks=False)
        except FileNotFoundError as error:
            raise InputOutputError(
                f"the {what} {_path_shown(self.path)} is no longer named by "
                f"{_escaped(self.name)} below {_path_shown(self.path.parent)}; the "
                f"entry was removed while this self-test was in progress; refusing to "
                f"hand a pathname to a run under test"
            ) from error
        except OSError as error:
            raise InputOutputError(
                f"cannot examine {_escaped(self.name)} below "
                f"{_path_shown(self.path.parent)}, which names the {what}: "
                f"{error.strerror or error}"
            ) from error
        if (named.st_dev, named.st_ino) != (self.device, self.inode):
            raise InputOutputError(
                f"{_escaped(self.name)} below {_path_shown(self.path.parent)} no "
                f"longer names the {what} this self-test holds open: it names device "
                f"{named.st_dev} inode {named.st_ino} and not device {self.device} "
                f"inode {self.inode}; the entry was replaced while this self-test was "
                f"in progress; refusing to hand a pathname to a run under test"
            )

    def visible_name(self, what: str) -> str:
        """Return the single component that currently names the held directory.

        The descriptor's own pathname is read from ``/proc/self/fd`` and its last
        component is confirmed, below ``parent_fd`` and without following a final
        symbolic link, to name the device and inode the descriptor reports, so the name
        returned is the entry the held directory stands at and not the name it stood at
        when it was created. Raises ``InputOutputError`` when the descriptor's pathname
        cannot be read, when it reports a directory that has been unlinked, or when no
        entry of that name below ``parent_fd`` names the held directory.
        """
        self.identity(what)
        handoff = f"{_HANDOFF_DIRECTORY}/{self.descriptor}"
        try:
            current = os.readlink(handoff)
        except OSError as error:
            raise InputOutputError(
                f"cannot read the pathname of the descriptor held on the {what} "
                f"{_path_shown(self.path)}: {error.strerror or error}"
            ) from error
        if current.endswith(" (deleted)"):
            raise InputOutputError(
                f"the {what} {_path_shown(self.path)} stands at no name below "
                f"{_path_shown(self.path.parent)}: the descriptor reports "
                f"{_path_shown(current)}; nothing of it can be removed by name"
            )
        candidate = os.path.basename(current)
        try:
            named = os.stat(candidate, dir_fd=self.parent_fd, follow_symlinks=False)
        except OSError as error:
            raise InputOutputError(
                f"cannot examine {_escaped(candidate)}, the name the descriptor held "
                f"on the {what} {_path_shown(self.path)} reports, below "
                f"{_path_shown(self.path.parent)}: {error.strerror or error}"
            ) from error
        if (named.st_dev, named.st_ino) != (self.device, self.inode):
            raise InputOutputError(
                f"{_escaped(candidate)} below {_path_shown(self.path.parent)} does not "
                f"name the {what} this self-test holds open; the entry changed while "
                f"this self-test was in progress"
            )
        return candidate

    # Pathnames handed to a run under test.

    def confirm_handoff(self, what: str) -> None:
        """Confirm the pathname handoff of this descriptor names the held directory.

        The ``/proc/self/fd`` entry of the descriptor is followed and must report the
        device and inode the descriptor itself reports, which is what makes a
        destination named below it reach this directory. Raises ``InputOutputError``
        when that entry cannot be examined, as a process filesystem that is not mounted
        makes it, or when it names another directory, so the matrix stops with one
        diagnostic instead of failing every case that hands over a destination.
        """
        self.identity(what)
        handoff = self.handoff()
        try:
            named = os.stat(handoff)
        except OSError as error:
            raise InputOutputError(
                f"cannot examine {_path_shown(handoff)}, the pathname the {what} "
                f"{_path_shown(self.path)} is handed over as: "
                f"{error.strerror or error}; refusing to run the self-test"
            ) from error
        if (named.st_dev, named.st_ino) != (self.device, self.inode):
            raise InputOutputError(
                f"{_path_shown(handoff)} names device {named.st_dev} inode "
                f"{named.st_ino} and not the device {self.device} inode {self.inode} "
                f"of the {what} {_path_shown(self.path)}; refusing to run the "
                f"self-test"
            )

    def handoff(self, *names: str) -> Path:
        """Return the ``/proc/self/fd`` pathname of ``names`` below this directory."""
        return Path(f"{_HANDOFF_DIRECTORY}/{self.descriptor}", *names)

    def named(self, *names: str) -> Path:
        """Return the canonical pathname of ``names`` below this directory."""
        return self.path.joinpath(*names)

    # Fixture entries, each created, read and removed relative to the descriptor.

    def create(self, name: str, payload: bytes) -> str:
        """Create ``name`` below this directory holding exactly ``payload``.

        The entry is created with ``O_EXCL`` and ``O_NOFOLLOW``, so an entry already
        carrying the name, a symbolic link included, is reported rather than written
        through, and every byte of ``payload`` is written before the descriptor closes.
        Returns the name, which is what a case names in a pathname handoff.
        """
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
        try:
            handle = os.open(name, flags, _default_file_mode(), dir_fd=self.descriptor)
        except OSError as error:
            raise InputOutputError(
                f"cannot create the self-test entry {_escaped(name)} below "
                f"{_path_shown(self.path)}: {error.strerror or error}"
            ) from error
        try:
            offset = 0
            while offset < len(payload):
                offset += os.write(handle, payload[offset:])
        except OSError as error:
            raise InputOutputError(
                f"cannot write the {len(payload)} byte(s) of the self-test entry "
                f"{_escaped(name)} below {_path_shown(self.path)}: "
                f"{error.strerror or error}"
            ) from error
        finally:
            with contextlib.suppress(OSError):
                os.close(handle)
        return name

    def read(self, name: str, limit: int = _MAX_FIXTURE_READ_BYTES) -> bytes:
        """Return at most ``limit`` bytes of ``name`` below this directory.

        The entry is opened relative to the descriptor with ``O_NOFOLLOW`` and without
        blocking, so a symbolic link or a FIFO standing at the name is reported rather
        than followed or waited on.
        """
        try:
            handle = os.open(
                name, _NON_BLOCKING_READ | os.O_NOFOLLOW, dir_fd=self.descriptor
            )
        except OSError as error:
            raise InputOutputError(
                f"cannot read the self-test entry {_escaped(name)} below "
                f"{_path_shown(self.path)}: {error.strerror or error}"
            ) from error
        try:
            chunks: list[bytes] = []
            pending = limit
            while pending > 0:
                chunk = os.read(handle, min(pending, READ_BACK_CHUNK_BYTES))
                if not chunk:
                    break
                chunks.append(chunk)
                pending -= len(chunk)
            return b"".join(chunks)
        except OSError as error:
            raise InputOutputError(
                f"cannot read the self-test entry {_escaped(name)} below "
                f"{_path_shown(self.path)}: {error.strerror or error}"
            ) from error
        finally:
            with contextlib.suppress(OSError):
                os.close(handle)

    def fifo(self, name: str) -> str:
        """Create one FIFO at ``name`` below this directory and return the name."""
        try:
            os.mkfifo(name, dir_fd=self.descriptor)
        except OSError as error:
            raise InputOutputError(
                f"cannot create the self-test FIFO {_escaped(name)} below "
                f"{_path_shown(self.path)}: {error.strerror or error}"
            ) from error
        return name

    def link(self, target: str | os.PathLike[str], name: str) -> str:
        """Create one symbolic link at ``name`` naming ``target`` and return the name.

        The link is created relative to the descriptor, so the link itself stands inside
        the held directory whatever its target names, and nothing is followed while it
        is created.
        """
        try:
            os.symlink(target, name, dir_fd=self.descriptor)
        except OSError as error:
            raise InputOutputError(
                f"cannot create the self-test symbolic link {_escaped(name)} below "
                f"{_path_shown(self.path)}: {error.strerror or error}"
            ) from error
        return name

    def directory(self, name: str) -> _HeldTree:
        """Create ``name`` below this directory and return it as one more held tree.

        The single component is created and opened relative to this descriptor with
        ``O_NOFOLLOW``, so a symbolic link standing in its place is refused rather than
        followed, and the returned tree records the identity that descriptor reports.
        The caller closes it through ``close``.
        """
        try:
            os.mkdir(name, DIRECTORY_MODE, dir_fd=self.descriptor)
        except OSError as error:
            raise InputOutputError(
                f"cannot create the self-test directory {_escaped(name)} below "
                f"{_path_shown(self.path)}: {error.strerror or error}"
            ) from error
        try:
            descriptor = os.open(
                name,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=self.descriptor,
            )
        except OSError as error:
            with contextlib.suppress(OSError):
                os.rmdir(name, dir_fd=self.descriptor)
            raise InputOutputError(
                f"cannot open the self-test directory {_escaped(name)} below "
                f"{_path_shown(self.path)}: {error.strerror or error}"
            ) from error
        return _held_tree(self.path / name, name, descriptor, self.descriptor)

    def status(self, name: str) -> os.stat_result | None:
        """Return the status of ``name`` below this directory, or ``None`` if absent.

        The entry is examined without following a final symbolic link, so a link is
        reported as the link it is.
        """
        try:
            return os.stat(name, dir_fd=self.descriptor, follow_symlinks=False)
        except FileNotFoundError:
            return None
        except OSError as error:
            raise InputOutputError(
                f"cannot examine the self-test entry {_escaped(name)} below "
                f"{_path_shown(self.path)}: {error.strerror or error}"
            ) from error

    def holds(self, name: str) -> bool:
        """State whether any entry, a symbolic link included, stands at ``name``."""
        return self.status(name) is not None

    def entries(self) -> list[str]:
        """Return every entry name this directory holds, taken from the descriptor."""
        try:
            return sorted(os.listdir(self.descriptor))
        except OSError as error:
            raise InputOutputError(
                f"cannot list the self-test directory {_path_shown(self.path)}: "
                f"{error.strerror or error}"
            ) from error

    def rename(self, name: str, replacement: str) -> None:
        """Move ``name`` onto ``replacement``, both relative to this descriptor."""
        try:
            os.rename(
                name,
                replacement,
                src_dir_fd=self.descriptor,
                dst_dir_fd=self.descriptor,
            )
        except OSError as error:
            raise InputOutputError(
                f"cannot rename the self-test entry {_escaped(name)} to "
                f"{_escaped(replacement)} below {_path_shown(self.path)}: "
                f"{error.strerror or error}"
            ) from error

    def remove(self, name: str) -> None:
        """Unlink ``name`` below this directory by its single name."""
        try:
            os.unlink(name, dir_fd=self.descriptor)
        except FileNotFoundError:
            return
        except OSError as error:
            raise InputOutputError(
                f"cannot remove the self-test entry {_escaped(name)} below "
                f"{_path_shown(self.path)}: {error.strerror or error}"
            ) from error

    def remove_directory(self, name: str) -> None:
        """Remove the empty directory ``name`` below this directory."""
        try:
            os.rmdir(name, dir_fd=self.descriptor)
        except FileNotFoundError:
            return
        except OSError as error:
            raise InputOutputError(
                f"cannot remove the self-test directory {_escaped(name)} below "
                f"{_path_shown(self.path)}: {error.strerror or error}"
            ) from error

    def empty(self) -> None:
        """Remove every entry below this directory through the held descriptor."""
        _emptied_directory(self.descriptor)

    def close(self) -> None:
        """Close the descriptor this tree holds, whatever state the tree is in."""
        with contextlib.suppress(OSError):
            os.close(self.descriptor)


def _held_tree(path: Path, name: str, descriptor: int, parent_fd: int) -> _HeldTree:
    """Return one held tree for ``descriptor``, recording the identity it reports.

    Raises ``InputOutputError`` when the descriptor cannot be examined, so no tree is
    ever built without the identity every later confirmation compares against.
    """
    try:
        status = os.fstat(descriptor)
    except OSError as error:
        with contextlib.suppress(OSError):
            os.close(descriptor)
        raise InputOutputError(
            f"cannot examine the descriptor opened on {_path_shown(path)}: "
            f"{error.strerror or error}"
        ) from error
    return _HeldTree(
        path=path,
        name=name,
        descriptor=descriptor,
        parent_fd=parent_fd,
        device=status.st_dev,
        inode=status.st_ino,
    )


def _handed_off(
    tree: _HeldTree, what: str, action: Callable[[], _HandedOff]
) -> _HandedOff:
    """Run ``action`` between two confirmations that ``tree`` is still held.

    ``action`` is the one step of a case that hands a pathname to a run under test, so
    the held directory is confirmed immediately before the pathname is used and
    immediately after the step returns. A confirmation that fails raises
    ``InputOutputError`` and the step is not run, or its result is not accepted; a
    failure raised by ``action`` itself reaches the caller unchanged.
    """
    tree.confirm(what)
    result = action()
    tree.confirm(what)
    return result


def _removed_held_directory(tree: _HeldTree, what: str) -> str:
    """Empty and remove the directory ``tree`` holds, reporting a changed visible name.

    The directory is emptied through the held descriptor, so every entry is reached by
    one single name. The entry that names the held directory below ``parent_fd`` is then
    removed: the visible name when it still names the held device and inode, and the
    name the descriptor's own pathname reports otherwise, which is confirmed to name
    that same device and inode immediately before the removal and to hold nothing
    immediately after it. A visible name that changed is reported as
    ``InputOutputError`` once the originally held directory has been removed, so a run
    whose private directory was renamed or relinked while it worked fails rather than
    passing quietly. The descriptor is closed either way.
    """
    changed: InputOutputError | None = None
    try:
        tree.empty()
        try:
            tree.confirm(what)
            removable = tree.name
        except InputOutputError as error:
            changed = error
            removable = tree.visible_name(what)
        try:
            os.rmdir(removable, dir_fd=tree.parent_fd)
        except FileNotFoundError:
            pass
        except OSError as error:
            raise InputOutputError(
                f"cannot remove the {what} {_escaped(removable)} below "
                f"{_path_shown(tree.path.parent)}: {error.strerror or error}"
            ) from error
        try:
            standing = os.stat(
                removable, dir_fd=tree.parent_fd, follow_symlinks=False
            )
        except FileNotFoundError:
            standing = None
        except OSError as error:
            raise InputOutputError(
                f"cannot confirm the {what} {_escaped(removable)} below "
                f"{_path_shown(tree.path.parent)} was removed: "
                f"{error.strerror or error}"
            ) from error
        if standing is not None and (standing.st_dev, standing.st_ino) == (
            tree.device,
            tree.inode,
        ):
            raise InputOutputError(
                f"the {what} {_escaped(removable)} below "
                f"{_path_shown(tree.path.parent)} still names the directory this "
                f"self-test held open after it was removed"
            )
    finally:
        tree.close()

    if changed is not None:
        raise InputOutputError(
            f"the {what} {_path_shown(tree.path)} was removed under the name "
            f"{_escaped(removable)} the held descriptor reported, and the name it was "
            f"created under no longer named it: {changed}"
        )
    return f"removed {_path_shown(tree.path)} through the descriptor held on it"


class _Scratch(NamedTuple):
    """The private directory one self-test run works in, and its held descriptors.

    ``tree`` holds the run directory every case creates its fixtures below, together
    with the descriptor open on it and the descriptor open on the shared
    ``builder-selftest`` directory above it. ``build_fd`` is open on the validated
    generated-output root above that, so the run directory is created, emptied and
    removed relative to a held descriptor and never through a resolved pathname.
    """

    tree: _HeldTree
    build_fd: int


def _opened_scratch_parent(build_fd: int, build_root: Path) -> int:
    """Return a descriptor for the shared scratch directory below the build root.

    The single component is created where absent and opened relative to ``build_fd``
    with ``O_NOFOLLOW``, so a symbolic link standing in its place is refused rather than
    followed. A concurrent run that removes the directory after emptying it can make the
    open fail although the creation succeeded; that case retries up to
    ``_SCRATCH_ACQUIRE_ATTEMPTS`` times and is reported only if every attempt loses the
    same race. The descriptor returned is the caller's to close.
    """
    for _attempt in range(_SCRATCH_ACQUIRE_ATTEMPTS):
        try:
            os.mkdir(_SELF_TEST_SCRATCH_NAME, DIRECTORY_MODE, dir_fd=build_fd)
        except FileExistsError:
            pass
        except OSError as error:
            raise InputOutputError(
                f"cannot create the self-test directory "
                f"{_escaped(_SELF_TEST_SCRATCH_NAME)} below "
                f"{_path_shown(build_root)}: {error.strerror or error}"
            ) from error
        try:
            return os.open(
                _SELF_TEST_SCRATCH_NAME,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=build_fd,
            )
        except FileNotFoundError:
            continue
        except OSError as error:
            raise InputOutputError(
                f"cannot open the self-test directory "
                f"{_escaped(_SELF_TEST_SCRATCH_NAME)} below "
                f"{_path_shown(build_root)}: {error.strerror or error}"
            ) from error
    raise InputOutputError(
        f"cannot hold the self-test directory {_escaped(_SELF_TEST_SCRATCH_NAME)} "
        f"below {_path_shown(build_root)}: {_SCRATCH_ACQUIRE_ATTEMPTS} attempts each "
        "found it removed again; refusing to run the self-test"
    )


def _created_scratch_run(parent_fd: int, parent: Path) -> tuple[str, int]:
    """Create one exclusive run directory below ``parent_fd`` and return name and fd.

    The name carries this process identifier and six random bytes, and is created with
    ``os.mkdir``, which fails rather than reusing an entry that already carries it, so
    the run starts in a directory holding nothing. It is opened relative to the same
    descriptor with ``O_NOFOLLOW``. ``parent`` names the shared scratch directory in
    every diagnostic. The descriptor returned is the caller's to close.
    """
    for _attempt in range(MAX_TEMPORARY_ATTEMPTS):
        candidate = f"{os.getpid()}.{os.urandom(6).hex()}"
        try:
            os.mkdir(candidate, DIRECTORY_MODE, dir_fd=parent_fd)
        except FileExistsError:
            continue
        except OSError as error:
            raise InputOutputError(
                f"cannot create the self-test run directory {_escaped(candidate)} "
                f"below {_path_shown(parent)}: {error.strerror or error}"
            ) from error
        try:
            return (
                candidate,
                os.open(
                    candidate,
                    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                    dir_fd=parent_fd,
                ),
            )
        except OSError as error:
            with contextlib.suppress(OSError):
                os.rmdir(candidate, dir_fd=parent_fd)
            raise InputOutputError(
                f"cannot open the self-test run directory {_escaped(candidate)} below "
                f"{_path_shown(parent)}: {error.strerror or error}"
            ) from error
    raise InputOutputError(
        f"cannot create a self-test run directory below {_path_shown(parent)}: "
        f"{MAX_TEMPORARY_ATTEMPTS} candidate names are all taken; refusing to run the "
        "self-test"
    )


def _emptied_directory(descriptor: int) -> None:
    """Remove every entry below ``descriptor`` through descriptors alone.

    Each name held by the open directory is examined without following a final symbolic
    link. A subdirectory is opened relative to the same descriptor with ``O_NOFOLLOW``,
    emptied by this function and then removed; every other entry, a symbolic link and a
    FIFO included, is unlinked by its single name. Nothing is resolved as a pathname, so
    an entry replaced while the removal runs cannot direct it outside the tree it holds.
    Raises ``InputOutputError`` naming the directory that could not be listed or the
    entry that could not be removed, so no failure of this removal reaches the caller as
    a bare operating-system error.
    """
    try:
        held = os.listdir(descriptor)
    except OSError as error:
        raise InputOutputError(
            f"cannot list the self-test directory held open for removal: "
            f"{error.strerror or error}"
        ) from error
    for name in held:
        try:
            status = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
        except FileNotFoundError:
            continue
        except OSError as error:
            raise InputOutputError(
                f"cannot examine self-test entry {_escaped(name)} for removal: "
                f"{error.strerror or error}"
            ) from error
        if stat.S_ISDIR(status.st_mode):
            try:
                child = os.open(
                    name,
                    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                    dir_fd=descriptor,
                )
            except FileNotFoundError:
                continue
            except OSError as error:
                raise InputOutputError(
                    f"cannot open self-test directory {_escaped(name)} for removal: "
                    f"{error.strerror or error}"
                ) from error
            try:
                _emptied_directory(child)
            finally:
                with contextlib.suppress(OSError):
                    os.close(child)
            try:
                os.rmdir(name, dir_fd=descriptor)
            except FileNotFoundError:
                continue
            except OSError as error:
                raise InputOutputError(
                    f"cannot remove self-test directory {_escaped(name)}: "
                    f"{error.strerror or error}"
                ) from error
            continue
        try:
            os.unlink(name, dir_fd=descriptor)
        except FileNotFoundError:
            continue
        except OSError as error:
            raise InputOutputError(
                f"cannot remove self-test entry {_escaped(name)}: "
                f"{error.strerror or error}"
            ) from error


def _held_scratch() -> _Scratch:
    """Return one private run directory for the self-test, with its held descriptors.

    The validated generated-output root is created where absent by descending the
    canonical repository directory one component at a time, exactly as a record write
    does, and the descriptor reached is confirmed to still hold that root. The shared
    ``builder-selftest`` directory and one run directory below it are then created and
    opened relative to the descriptor above each, so no component is followed through a
    symbolic link and no pathname is resolved a second time. Every case reads and writes
    inside the returned directory, which therefore stands inside the validated read
    roots and inside the generated-output root, and no scratch document reaches the
    system temporary directory or any other tree.

    The caller owns the three descriptors returned and releases them through
    ``_released_scratch``, which is the only step that removes what the run created. A
    failure to acquire any level closes every descriptor already open and raises
    ``InputOutputError`` naming the level, so nothing is left held. The run directory is
    returned as a ``_HeldTree``, so every fixture below it is created, read and removed
    relative to the descriptor held on it and every pathname a run under test is handed
    is confirmed against the identity that descriptor reported here.
    """
    repository = _canonical_path(REPOSITORY_ROOT)
    build_root = _validated_build_root()
    anchor_fd = _opened_by_components(repository, "repository directory")
    try:
        _confirm_same_directory(anchor_fd, repository, "repository directory")
        build_fd = _parent_descriptor(
            anchor_fd, repository, _SELF_TEST_SCRATCH_COMPONENTS[:-1]
        )
    finally:
        with contextlib.suppress(OSError):
            os.close(anchor_fd)

    try:
        _confirm_same_directory(build_fd, build_root, "generated-output root")
        parent = build_root / _SELF_TEST_SCRATCH_NAME
        parent_fd = _opened_scratch_parent(build_fd, build_root)
        try:
            name, run_fd = _created_scratch_run(parent_fd, parent)
        except BuildError:
            with contextlib.suppress(OSError):
                os.close(parent_fd)
            raise
    except BuildError:
        with contextlib.suppress(OSError):
            os.close(build_fd)
        raise

    tree = _held_tree(parent / name, name, run_fd, parent_fd)
    try:
        tree.confirm_handoff("self-test run directory")
        tree.confirm("self-test run directory")
    except BuildError:
        # The run directory holds nothing yet, so the refusal removes it and the shared
        # directory it stands in, which a concurrent run's own directory keeps in place.
        tree.close()
        with contextlib.suppress(OSError):
            os.rmdir(name, dir_fd=parent_fd)
        with contextlib.suppress(OSError):
            os.close(parent_fd)
        with contextlib.suppress(OSError):
            os.rmdir(_SELF_TEST_SCRATCH_NAME, dir_fd=build_fd)
        with contextlib.suppress(OSError):
            os.close(build_fd)
        raise
    return _Scratch(tree=tree, build_fd=build_fd)


def _released_scratch(scratch: _Scratch) -> str:
    """Remove everything ``scratch`` holds and return what the removal observed.

    The run directory is emptied and removed by ``_removed_held_directory`` through the
    descriptors held on it and on its parent, so every entry is reached by one single
    name, no pathname is resolved again, and a visible run name replaced after the
    directory was acquired is reported as a failure once the originally held directory
    has been removed. The shared ``builder-selftest`` directory is then removed relative
    to the descriptor held on the generated-output root while it holds nothing, which
    leaves a directory belonging to a concurrent run in place; whether it went is read
    from that same descriptor without following a final symbolic link, so no pathname is
    resolved by this removal either. Every descriptor is closed whether the removal
    completes or not. A removal that cannot complete raises ``InputOutputError`` naming
    the entry, and the returned text states the run directory that was removed and
    whether the shared directory went with it.
    """
    parent = scratch.tree.path.parent
    failure: BuildError | None = None
    try:
        _removed_held_directory(scratch.tree, "self-test run directory")
    except BuildError as error:
        failure = error
    with contextlib.suppress(OSError):
        os.close(scratch.tree.parent_fd)

    shared_removed = False
    if failure is None:
        try:
            os.rmdir(_SELF_TEST_SCRATCH_NAME, dir_fd=scratch.build_fd)
            shared_removed = True
        except OSError:
            # The shared directory holds a concurrent run's directory, or another run
            # removed it first; either way this run has nothing left to remove.
            try:
                os.stat(
                    _SELF_TEST_SCRATCH_NAME,
                    dir_fd=scratch.build_fd,
                    follow_symlinks=False,
                )
            except FileNotFoundError:
                shared_removed = True
            except OSError as error:
                failure = InputOutputError(
                    f"cannot examine the shared self-test directory "
                    f"{_path_shown(parent)} after the run directory was removed: "
                    f"{error.strerror or error}"
                )
    with contextlib.suppress(OSError):
        os.close(scratch.build_fd)

    if failure is not None:
        raise failure
    return (
        f"removed {_path_shown(scratch.tree.path)}; the shared directory "
        f"{_path_shown(parent)} {'went with it' if shared_removed else 'remains'}"
    )


def _discarded_scratch(scratch: _Scratch) -> None:
    """Release ``scratch`` while another failure is already being reported.

    The removal runs exactly as ``_released_scratch`` performs it, and a removal failure
    is suppressed so the failure the caller is already reporting reaches the caller
    unchanged. Every descriptor is closed either way.
    """
    with contextlib.suppress(BuildError, OSError):
        _released_scratch(scratch)


# Self-test support: scratch documents, case bodies and the case runner.


def _write_sample(tree: _HeldTree, name: str, document: dict[str, Any]) -> str:
    """Create one sample definition JSON document below the held run directory.

    The entry is created relative to the held descriptor and the name it carries is
    returned, which is what a case names in the pathname it hands to a run under test.
    """
    return tree.create(
        f"{name}.json",
        (json.dumps(document, indent=2, ensure_ascii=True) + "\n").encode("utf-8"),
    )


def _write_payload(tree: _HeldTree, name: str, payload: bytes) -> str:
    """Create one entry holding exactly ``payload`` below the held run directory."""
    return tree.create(name, payload)


def _make_fifo(tree: _HeldTree, name: str) -> str:
    """Create one FIFO below the held run directory and return its name."""
    return tree.fifo(name)


def _short_value_sample(motor: dict[str, str]) -> dict[str, str]:
    """Return the motor fixture with a short numeric and a short alphanumeric value."""
    sample = dict(motor)
    sample["CA-PAYMENT"] = _SHORT_NUMERIC_VALUE
    sample["CA-M-COLOUR"] = _SHORT_ALPHANUMERIC_VALUE
    return sample


def _duplicated_key_payload(text: str, anchor: str, inserted: str) -> bytes:
    """Return ``text`` as bytes with ``inserted`` placed after the line ``anchor``.

    ``anchor`` must equal exactly one whole line of ``text``. ``inserted`` is written
    directly beneath it, at the indentation it carries, so it repeats a key of the
    mapping that line opens.
    """
    lines = text.splitlines(keepends=True)
    found = [
        position
        for position, line in enumerate(lines)
        if line.rstrip("\n") == anchor
    ]
    if len(found) != 1:
        raise SelfTestError(
            f"field map holds {len(found)} line(s) equal to {_display(anchor)}, "
            f"expected exactly 1"
        )
    lines.insert(found[0] + 1, f"{inserted}\n")
    return "".join(lines).encode("utf-8")


def _duplicate_key_stated(key: str) -> str:
    """Return the fragment a rejected duplicate mapping key writes to a diagnostic.

    The loader's message names the key in quotes and the diagnostic escapes it to one
    printable line, so the quotes reach stderr in their escaped form.
    """
    return f"found duplicate key \\'{key}\\'"


def _alias_dag_text(levels: int, fanout: int) -> str:
    """Return YAML text whose anchors expand to ``fanout ** levels`` leaf values.

    Each level is one anchored sequence holding ``fanout`` references to the level
    below it, so the text stays short while the document it describes does not.
    """
    members = ", ".join(["leaf"] * fanout)
    lines = [f"{_ALIAS_DAG_KEY}:", f"  level0: &level0 [{members}]"]
    for level in range(1, levels + 1):
        aliases = ", ".join([f"*level{level - 1}"] * fanout)
        lines.append(f"  level{level}: &level{level} [{aliases}]")
    return "\n".join(lines) + "\n"


def _write_field_map(tree: _HeldTree, name: str, document: dict[str, Any]) -> str:
    """Create one field map document below the held run directory."""
    return tree.create(
        f"{name}.yml",
        yaml.safe_dump(
            document, default_flow_style=False, sort_keys=True, allow_unicode=False
        ).encode("utf-8"),
    )


def _mutated_field_map(
    tree: _HeldTree,
    name: str,
    document: dict[str, Any],
    mutate: Callable[[dict[str, Any]], None],
) -> str:
    """Create a copy of the field map with ``mutate`` applied to it."""
    altered = copy.deepcopy(document)
    mutate(altered)
    return _write_field_map(tree, name, altered)


def _swap_offsets(left: dict[str, Any], right: dict[str, Any]) -> None:
    """Exchange the ``offset`` members of two layout item entries."""
    left["offset"], right["offset"] = right["offset"], left["offset"]


def _layout_entry(
    document: dict[str, Any], group: str, item: str
) -> dict[str, Any]:
    """Return one layout item entry of a field map document."""
    for entry in document["layout"][group]["items"]:
        if isinstance(entry, dict) and str(entry.get("item", "")).upper() == item:
            return entry
    raise SelfTestError(
        f"field map layout group {_display(group)} declares no item {_display(item)}"
    )


def _protected_fill_entry(document: dict[str, Any], item: str) -> dict[str, Any]:
    """Return one protected_fill_items entry of a field map document."""
    contract = document["sample_definition_contract"]
    for entry in contract["protected_fill_items"]:
        if isinstance(entry, dict) and str(entry.get("item", "")).upper() == item:
            return entry
    raise SelfTestError(
        f"field map sample_definition_contract declares no protected filler "
        f"{_display(item)}"
    )


def _chain_populated_entry(document: dict[str, Any], item: str) -> dict[str, Any]:
    """Return one chain_populated_items entry of a field map document."""
    contract = document["sample_definition_contract"]
    for entry in contract[CHAIN_POPULATED_SECTION]:
        if isinstance(entry, dict) and str(entry.get("item", "")).upper() == item:
            return entry
    raise SelfTestError(
        f"field map sample_definition_contract.{CHAIN_POPULATED_SECTION} declares no "
        f"item {_display(item)}"
    )


def _seeded_destination(tree: _HeldTree, name: str) -> str:
    """Create a destination holding sentinel bytes and return its entry name."""
    return tree.create(f"{name}.out", _SENTINEL_DESTINATION_BYTES)


def _nested(depth: int) -> Any:
    """Return a value wrapped in ``depth`` nested single-element lists."""
    value: Any = "nested value"
    for _ in range(depth):
        value = [value]
    return value


def _assert_rejected(
    tree: _HeldTree,
    argv: list[str],
    expected_status: int,
    destination: str,
    fragment: str,
) -> str:
    """Run one failing invocation and confirm status, diagnostic and destination.

    ``fragment`` is the text the diagnostic must contain; a matching status alone does
    not pass the case. ``destination`` is the entry the run was offered below the held
    run directory, read through the descriptor held on it before and after the run, so
    the comparison reaches the entry the run was offered and no pathname is resolved.
    """
    before = tree.read(destination)
    result = _run_cli(tree, argv)
    if result.status != expected_status:
        raise _SelfTestFailure(
            f"exit {result.status}, expected {expected_status}; stderr "
            f"{_display(result.stderr.strip())}"
        )
    _assert_diagnostic(result.stderr)
    if fragment not in result.stderr:
        raise _SelfTestFailure(
            f"diagnostic {_display(result.stderr.strip())} does not state "
            f"{_display(fragment)}"
        )
    if result.stdout:
        raise _SelfTestFailure(
            f"wrote {len(result.stdout)} characters to stdout on failure"
        )
    if tree.read(destination) != before:
        raise _SelfTestFailure("destination changed while the run failed")
    return (
        f"exit={expected_status} diagnostic states {_display(fragment)} "
        f"destination={len(before)} bytes unchanged"
    )


def _assert_write_refused(tree: _HeldTree, destination: str, record: str) -> str:
    """Offer one record of the wrong width to ``write_record`` and confirm the refusal.

    ``write_record`` must raise ``FieldMapError`` stating the character count it was
    offered and the count this builder writes, and ``destination``, the entry offered
    below the held run directory, must still hold the bytes it held before the call. The
    destination is handed over as the entry below the held descriptor's own pathname,
    so a replaced visible run name cannot direct the call at another directory, and
    the held directory is confirmed immediately before and after it.
    """
    before = tree.read(destination)
    refusal: FieldMapError | None = None
    try:
        _handed_off(
            tree,
            "self-test run directory",
            lambda: write_record(tree.handoff(destination), record),
        )
    except FieldMapError as error:
        refusal = error
    if refusal is None:
        raise _SelfTestFailure(f"write_record accepted {len(record)} characters")
    stated = f"record is {len(record)} characters, expected {COMMAREA_RECORD_LENGTH}"
    if stated not in str(refusal):
        raise _SelfTestFailure(
            f"the refusal states {_display(str(refusal))}, expected "
            f"{_display(stated)}"
        )
    after = tree.read(destination)
    if after != before:
        raise _SelfTestFailure(
            f"destination changed while the {len(record)} character write was refused"
        )
    return (
        f"refused {len(record)} characters with {_display(stated)}, "
        f"destination={len(after)} bytes unchanged"
    )


def _loaded_scratch_field_map(tree: _HeldTree, name: str) -> dict[str, Any]:
    """Return the field map ``name`` below the held run directory, loaded once.

    ``load_field_map`` reads one pathname and refuses a symbolic-link component of it,
    so the entry is named by its canonical path below the held run directory, and that
    directory is confirmed immediately before and after the load.
    """
    return _handed_off(
        tree,
        "self-test run directory",
        lambda: load_field_map(tree.named(name)),
    )


def _case_copybook_record_length(layout: CopybookLayout) -> str:
    """Confirm the copybook items total the emitted record length."""
    if layout.record_length != COMMAREA_RECORD_LENGTH:
        raise _SelfTestFailure(
            f"copybook items total {layout.record_length} characters, expected "
            f"{COMMAREA_RECORD_LENGTH}"
        )
    return (
        f"{len(layout.items)} parsed item(s) total {COMMAREA_RECORD_LENGTH} characters"
    )


def _case_layout_cross_check(
    field_map: dict[str, Any], layout: CopybookLayout
) -> str:
    """Confirm the field map layout and the copybook parse agree in both directions."""
    problems = _layout_disagreements(field_map, layout)
    if problems:
        raise _SelfTestFailure(
            f"{len(problems)} disagreement(s); first: {problems[0]}"
        )
    exercised = sum(
        len(group["items"]) + len(group.get("group_declarations") or [])
        for group in field_map["layout"].values()
    )
    return f"{exercised} layout entry/entries agree with the copybook"


def _case_fixture_record(
    layout: CopybookLayout,
    map_path: Path,
    sample_path: Path,
    sample: dict[str, str],
    keys: _FixtureKeys,
    expectations: dict[str, str | _Fill],
    tree: _HeldTree,
    name: str,
) -> str:
    """Build one fixture and compare its keys and every window with the literals.

    The fixture's key set is compared with ``keys.supplied`` before the record is
    rendered, the expected-window table must cover exactly the supplied and the omitted
    items, every window is compared with its literal expectation, and every omitted
    window must hold the fill character its copybook kind declares.
    """
    _assert_fixture_keys(sample, keys, name)
    covered = {item.upper() for item in keys.supplied} | {
        item.upper() for item in keys.omitted
    }
    tabulated = {window.upper() for window in expectations}
    if covered != tabulated:
        raise _SelfTestFailure(
            f"{name} expects {len(tabulated)} window(s) while its key sets name "
            f"{len(covered)}; only in the table "
            f"{_quote_all(tabulated - covered) or 'nothing'}, only in the key sets "
            f"{_quote_all(covered - tabulated) or 'nothing'}"
        )
    output = f"{name}.rec"
    result = _run_cli(
        tree,
        [
            "--field-map",
            str(map_path),
            "--sample",
            str(sample_path),
            "--output",
            str(tree.handoff(output)),
        ],
    )
    if result.status != EXIT_OK:
        raise _SelfTestFailure(
            f"exit {result.status}: {_display(result.stderr.strip())}"
        )
    if result.stdout.count("\n") != 1:
        raise _SelfTestFailure(
            f"summary holds {result.stdout.count(chr(10))} line(s), expected 1"
        )
    if f"characters={COMMAREA_RECORD_LENGTH}" not in result.stdout:
        raise _SelfTestFailure("summary does not state the character count")
    if f"bytes={COMMAREA_RECORD_LENGTH + 1}" not in result.stdout:
        raise _SelfTestFailure("summary does not state the byte count")
    record = _read_record(tree, output, name)
    _assert_windows(record, expectations, layout, name)
    _assert_fill_windows(record, keys.omitted, layout, name)
    expected = _expected_record(expectations, layout)
    if record != expected:
        position = _first_difference(record, expected)
        raise _SelfTestFailure(
            f"record differs from the assembled expectation at byte {position + 1}: "
            f"holds {_display(record[position : position + 12])}, expected "
            f"{_display(expected[position : position + 12])}"
        )
    return (
        f"{len(keys.supplied)} supplied key(s) and {len(keys.omitted)} omitted "
        f"window(s) accounted for, {len(expectations)} window(s) match, "
        f"{COMMAREA_RECORD_LENGTH + 1} bytes on disk closed by one newline"
    )


def _case_protected_fill_items(
    field_map: dict[str, Any], layout: CopybookLayout
) -> str:
    """Confirm the protected filler names, fills, the contract and the copybook agree.

    ``sample_definition_contract.protected_fill_items`` must hold one entry per name in
    ``PROTECTED_FILL_ITEMS`` and no repeated entry, each entry must record
    ``FILL_LABEL_SPACES`` as its fill, and each named item must be an alphanumeric item
    the copybook declares on the stated line.
    """
    declared = field_map["sample_definition_contract"].get("protected_fill_items")
    if not isinstance(declared, list) or not declared:
        raise _SelfTestFailure(
            "sample_definition_contract declares no protected_fill_items sequence"
        )
    if len(declared) != len(PROTECTED_FILL_ITEMS):
        raise _SelfTestFailure(
            f"protected_fill_items holds {len(declared)} entry/entries while this tool "
            f"protects {len(PROTECTED_FILL_ITEMS)} item(s)"
        )
    names: list[str] = []
    for position, entry in enumerate(declared, start=1):
        if not isinstance(entry, dict):
            raise _SelfTestFailure(
                f"protected_fill_items entry {_display(entry)} is not a mapping"
            )
        name = str(entry.get("item"))
        if name.upper() in names:
            raise _SelfTestFailure(
                f"protected_fill_items entry {position} repeats item {_display(name)}"
            )
        names.append(name.upper())
        fill = entry.get("fill")
        if fill != FILL_LABEL_SPACES:
            raise _SelfTestFailure(
                f"protected_fill_items states fill {_display(fill)} for "
                f"{_display(name)}, expected {_display(FILL_LABEL_SPACES)}"
            )
        parsed = layout.items.get(name.upper())
        if parsed is None:
            raise _SelfTestFailure(
                f"copybook declares no item {_display(name)}"
            )
        if parsed.line != entry.get("line"):
            raise _SelfTestFailure(
                f"protected_fill_items states line {_display(entry.get('line'))} for "
                f"{_display(name)}, copybook shows {parsed.line}"
            )
        if parsed.kind != KIND_ALPHANUMERIC:
            raise _SelfTestFailure(
                f"copybook declares {_display(name)} as {parsed.kind}, expected "
                f"{KIND_ALPHANUMERIC}"
            )
    if set(names) != set(PROTECTED_FILL_ITEMS):
        raise _SelfTestFailure(
            f"protected_fill_items names {_quote_all(names)} while this tool protects "
            f"{_quote_all(PROTECTED_FILL_ITEMS)}"
        )
    return (
        f"{len(names)} protected filler item(s) agree with the contract, the "
        f"{_display(FILL_LABEL_SPACES)} fill and the copybook"
    )


def _case_chain_populated_items(
    field_map: dict[str, Any], layout: CopybookLayout
) -> str:
    """Confirm the chain-populated block, the logical entries, the copybook and the
    literals of this matrix all state the same pre-execution content.

    ``sample_definition_contract.chain_populated_items`` must hold one entry per logical
    entry recording ``populated_by: chain`` and no repeated entry; each entry's ``kind``
    must be the kind the copybook parse reports for the item; a ``fill`` entry must
    record the label ``FILL_LABEL_BY_KIND`` lists for that kind; a ``seed`` entry must
    be as long as the copybook window, must hold digits only for a numeric window and
    must stand outside the domain the item's logical entry declares. The resolved
    content is then compared with ``_CHAIN_WINDOW_CONTENT``, so a seed changed in the
    document under test cannot silently change what the fixture cases assert.
    """
    declared = field_map["sample_definition_contract"].get(CHAIN_POPULATED_SECTION)
    if not isinstance(declared, list) or not declared:
        raise _SelfTestFailure(
            f"sample_definition_contract declares no {CHAIN_POPULATED_SECTION} sequence"
        )
    chain_items = _items_populated_by(field_map, POPULATED_BY_CHAIN)
    domains = _item_domains(field_map)
    seeded = 0
    resolved: dict[str, str] = {}
    for position, entry in enumerate(declared, start=1):
        if not isinstance(entry, dict):
            raise _SelfTestFailure(
                f"{CHAIN_POPULATED_SECTION} entry {_display(entry)} is not a mapping"
            )
        name = str(entry.get("item"))
        key = name.upper()
        if key in resolved:
            raise _SelfTestFailure(
                f"{CHAIN_POPULATED_SECTION} entry {position} repeats item "
                f"{_display(name)}"
            )
        if key not in chain_items:
            raise _SelfTestFailure(
                f"{CHAIN_POPULATED_SECTION} entry {position} names {_display(name)}, "
                f"which no logical entry records as populated_by "
                f"{_display(POPULATED_BY_CHAIN)}"
            )
        parsed = layout.items.get(key)
        if parsed is None:
            raise _SelfTestFailure(f"copybook declares no item {_display(name)}")
        if parsed.kind not in FILL_LABEL_BY_KIND:
            raise _SelfTestFailure(
                f"copybook declares {_display(name)} as {_display(parsed.kind)}, "
                f"which no chain-populated content covers"
            )
        if entry.get("kind") != parsed.kind:
            raise _SelfTestFailure(
                f"{CHAIN_POPULATED_SECTION} states kind {_display(entry.get('kind'))} "
                f"for {_display(name)}, copybook shows {_display(parsed.kind)}"
            )
        window = Window(
            item=parsed.name,
            group=CHAIN_POPULATED_SECTION,
            offset=parsed.offset,
            length=parsed.length,
            kind=parsed.kind,
        )
        try:
            content = _chain_content_characters(entry, window, domains.get(key))
        except FieldMapError as error:
            raise _SelfTestFailure(
                f"{CHAIN_POPULATED_SECTION} entry {position} for {_display(name)} is "
                f"not placeable: {error}"
            ) from error
        if entry.get(CHAIN_CONTENT_SEED) is not None:
            seeded += 1
        resolved[key] = content

    absent = [item for key, item in chain_items.items() if key not in resolved]
    if absent:
        raise _SelfTestFailure(
            f"{CHAIN_POPULATED_SECTION} records no entry for chain-populated item(s) "
            f"{_quote_all(absent)}"
        )
    tabulated = {name.upper() for name in _CHAIN_WINDOW_CONTENT}
    if tabulated != set(resolved):
        raise _SelfTestFailure(
            f"this matrix tabulates {_quote_all(tabulated)} while the contract records "
            f"{_quote_all(resolved)}"
        )
    for key, content in sorted(resolved.items()):
        parsed = layout.items[key]
        expected = _expectation_text(_CHAIN_WINDOW_CONTENT[key], parsed)
        if content != expected:
            raise _SelfTestFailure(
                f"{CHAIN_POPULATED_SECTION} states {_display(content)} for "
                f"{_display(key)} while this matrix expects {_display(expected)}"
            )
    return (
        f"{len(resolved)} chain-populated window(s) agree with the logical entries, "
        f"the copybook and this matrix, {seeded} of them seeded outside a declared "
        f"domain"
    )


def _case_length_from_constant(
    field_map: dict[str, Any], motor: dict[str, str], tree: _HeldTree
) -> str:
    """Confirm the emitted length is the module constant, not a field map member.

    ``render_record`` is called with a field map whose ``record.length`` is short, and
    ``write_record`` is offered a record one character short of the constant.
    """
    altered = copy.deepcopy(field_map)
    short_length = COMMAREA_RECORD_LENGTH - 100
    altered["record"]["length"] = short_length
    routing = resolve_overlay(altered, _sample_request_id(altered, motor))
    values = validate_sample(altered, motor, routing)
    record = render_record(altered, routing, values)
    if len(record) != COMMAREA_RECORD_LENGTH:
        raise _SelfTestFailure(
            f"render_record returned {len(record)} characters for a field map "
            f"declaring {short_length}"
        )
    destination = _seeded_destination(tree, "length_from_constant")
    refusal = _assert_write_refused(tree, destination, record[:-1])
    return (
        f"render_record emitted {COMMAREA_RECORD_LENGTH} characters from a field map "
        f"declaring {short_length}; write_record {refusal}"
    )


def _case_long_record_refused(
    field_map: dict[str, Any], motor: dict[str, str], tree: _HeldTree
) -> str:
    """Confirm ``write_record`` refuses one character more than the constant.

    The motor fixture is rendered from the shipped field map and one 7-bit ASCII
    character is appended, so ``write_record`` is offered ``COMMAREA_RECORD_LENGTH + 1``
    characters and must refuse them and leave the seeded destination alone.
    """
    routing = resolve_overlay(field_map, _sample_request_id(field_map, motor))
    values = validate_sample(field_map, motor, routing)
    record = render_record(field_map, routing, values)
    if len(record) != COMMAREA_RECORD_LENGTH:
        raise _SelfTestFailure(
            f"render_record returned {len(record)} characters, expected "
            f"{COMMAREA_RECORD_LENGTH}"
        )
    destination = _seeded_destination(tree, "long_record_refused")
    return _assert_write_refused(tree, destination, record + _EXTRA_RECORD_CHARACTER)


def _case_rerun_identical(
    map_path: Path, sample_path: Path, tree: _HeldTree, name: str
) -> str:
    """Confirm two builds of the same fixture produce identical bytes."""
    output = f"{name}.rec"
    argv = [
        "--field-map",
        str(map_path),
        "--sample",
        str(sample_path),
        "--output",
        str(tree.handoff(output)),
        "--quiet",
    ]
    first = _run_cli(tree, argv)
    if first.status != EXIT_OK:
        raise _SelfTestFailure(f"first build exit {first.status}")
    if first.stdout:
        raise _SelfTestFailure("--quiet still wrote a summary")
    before = tree.read(output)
    second = _run_cli(tree, argv)
    if second.status != EXIT_OK:
        raise _SelfTestFailure(f"second build exit {second.status}")
    after = tree.read(output)
    if after != before:
        raise _SelfTestFailure("the second build differs from the first")
    return f"two builds produced the same {len(after)} bytes"


def _case_commercial_status_placed(
    layout: CopybookLayout,
    map_path: Path,
    commercial: dict[str, str],
    tree: _HeldTree,
) -> str:
    """Confirm a non-zero commercial status lands in its own window and nowhere else."""
    item = layout.items["CA-B-STATUS"]
    sample = dict(commercial)
    sample["CA-B-Status"] = _NON_ZERO_COMMERCIAL_STATUS
    sample_name = _write_sample(tree, "commercial_status", sample)
    output = "commercial_status.rec"
    result = _run_cli(
        tree,
        [
            "--field-map",
            str(map_path),
            "--sample",
            str(tree.named(sample_name)),
            "--output",
            str(tree.handoff(output)),
            "--quiet",
        ],
    )
    if result.status != EXIT_OK:
        raise _SelfTestFailure(
            f"exit {result.status}: {_display(result.stderr.strip())}"
        )
    record = _read_record(tree, output, "commercial_status")
    placed = record[item.offset - 1 : item.end_byte]
    if placed != _NON_ZERO_COMMERCIAL_STATUS:
        raise _SelfTestFailure(
            f"bytes {item.offset}-{item.end_byte} hold {_display(placed)}, expected "
            f"{_display(_NON_ZERO_COMMERCIAL_STATUS)}"
        )
    canonical = _expected_record(_COMMERCIAL_EXPECTED_WINDOWS, layout)
    if record == canonical:
        raise _SelfTestFailure(
            "the record matches the fixture's record, so the status is "
            "indistinguishable"
        )
    restored = (
        record[: item.offset - 1]
        + _expectation_text(_COMMERCIAL_EXPECTED_WINDOWS["CA-B-Status"], item)
        + record[item.end_byte :]
    )
    if restored != canonical:
        position = _first_difference(restored, canonical)
        raise _SelfTestFailure(
            f"the record also differs outside its status window, first at byte "
            f"{position + 1}"
        )
    return (
        f"bytes {item.offset}-{item.end_byte} hold "
        f"{_NON_ZERO_COMMERCIAL_STATUS} and the record differs from the fixture's "
        f"record only there"
    )


def _case_commercial_inactive_overlay(
    layout: CopybookLayout,
    field_map: dict[str, Any],
    map_path: Path,
    commercial: dict[str, str],
    tree: _HeldTree,
) -> str:
    """Confirm a full-width commercial address leaves the motor premium bytes filled.

    The commercial address covers the bytes the motor overlay reads as
    ``CA-M-PREMIUM``. With the address filled to its declared width those bytes are not
    blank, the request id still resolves policy type ``C``, and a motor premium key is
    still rejected for that request id.
    """
    address_item = layout.items["CA-B-ADDRESS"]
    premium_item = layout.items["CA-M-PREMIUM"]
    repeats = address_item.length // len(_WIDE_ADDRESS_PATTERN) + 1
    address = (_WIDE_ADDRESS_PATTERN * repeats)[: address_item.length]
    sample = dict(commercial)
    sample["CA-B-Address"] = address
    sample_name = _write_sample(tree, "commercial_wide_address", sample)
    output = "commercial_wide_address.rec"
    result = _run_cli(
        tree,
        [
            "--field-map",
            str(map_path),
            "--sample",
            str(tree.named(sample_name)),
            "--output",
            str(tree.handoff(output)),
            "--quiet",
        ],
    )
    if result.status != EXIT_OK:
        raise _SelfTestFailure(
            f"exit {result.status}: {_display(result.stderr.strip())}"
        )
    record = _read_record(tree, output, "commercial_wide_address")
    placed = record[premium_item.offset - 1 : premium_item.end_byte]
    if not placed.strip(" "):
        raise _SelfTestFailure(
            f"bytes {premium_item.offset}-{premium_item.end_byte} are blank"
        )
    expected_slice = address[
        premium_item.offset - address_item.offset : premium_item.end_byte
        - address_item.offset
        + 1
    ]
    if placed != expected_slice:
        raise _SelfTestFailure(
            f"bytes {premium_item.offset}-{premium_item.end_byte} hold "
            f"{_display(placed)}, expected {_display(expected_slice)}"
        )

    routing = resolve_overlay(field_map, commercial["CA-REQUEST-ID"])
    if routing.policy_type != "C":
        raise _SelfTestFailure(
            f"request id {_display(commercial['CA-REQUEST-ID'])} resolves policy type "
            f"{_display(routing.policy_type)}, expected 'C'"
        )
    rejected = dict(sample)
    rejected["CA-M-PREMIUM"] = "000450"
    rejected_name = _write_sample(
        tree, "commercial_wide_address_motor_premium", rejected
    )
    destination = _seeded_destination(tree, "commercial_wide_address_rejected")
    _assert_rejected(
        tree,
        [
            "--field-map",
            str(map_path),
            "--sample",
            str(tree.named(rejected_name)),
            "--output",
            str(tree.handoff(destination)),
        ],
        EXIT_SAMPLE_REJECTED,
        destination,
        "of overlay 'motor_overlay'",
    )
    return (
        f"bytes {premium_item.offset}-{premium_item.end_byte} carry address content, "
        f"policy_type={routing.policy_type} from the request id, motor premium key "
        f"rejected"
    )


def _case_motor_inactive_overlay(
    layout: CopybookLayout,
    field_map: dict[str, Any],
    map_path: Path,
    motor: dict[str, str],
    tree: _HeldTree,
) -> str:
    """Confirm the motor record holds spaces where the commercial premiums sit.

    The four commercial premium windows fall inside ``CA-M-FILLER``, which a sample
    definition may not supply, so a motor record holds the filler's spaces across all
    four windows. The request id resolves policy type ``M`` and a commercial premium key
    is rejected for that request id.
    """
    filler = layout.items["CA-M-FILLER"]
    output = "motor_inactive_overlay.rec"
    result = _run_cli(
        tree,
        [
            "--field-map",
            str(map_path),
            "--sample",
            str(MOTOR_SAMPLE_DEFINITION),
            "--output",
            str(tree.handoff(output)),
            "--quiet",
        ],
    )
    if result.status != EXIT_OK:
        raise _SelfTestFailure(
            f"exit {result.status}: {_display(result.stderr.strip())}"
        )
    record = _read_record(tree, output, "motor_inactive_overlay")
    for name in _COMMERCIAL_PREMIUM_ITEMS:
        item = layout.items[name.upper()]
        if not filler.offset <= item.offset <= item.end_byte <= filler.end_byte:
            raise _SelfTestFailure(
                f"item {_display(name)} spans bytes {item.offset}-{item.end_byte}, "
                f"outside the {_display(filler.name)} window "
                f"{filler.offset}-{filler.end_byte}"
            )
        placed = record[item.offset - 1 : item.end_byte]
        if placed != " " * item.length:
            position = _first_difference(placed, " " * item.length)
            raise _SelfTestFailure(
                f"bytes {item.offset}-{item.end_byte} hold "
                f"{_display(placed[position : position + 12])}, expected spaces"
            )

    routing = resolve_overlay(field_map, motor["CA-REQUEST-ID"])
    if routing.policy_type != "M":
        raise _SelfTestFailure(
            f"request id {_display(motor['CA-REQUEST-ID'])} resolves policy type "
            f"{_display(routing.policy_type)}, expected 'M'"
        )
    rejected = dict(motor)
    rejected["CA-B-FirePremium"] = _COMMERCIAL_PREMIUM_PROBE
    rejected_name = _write_sample(tree, "motor_commercial_premium", rejected)
    destination = _seeded_destination(tree, "motor_commercial_premium_rejected")
    _assert_rejected(
        tree,
        [
            "--field-map",
            str(map_path),
            "--sample",
            str(tree.named(rejected_name)),
            "--output",
            str(tree.handoff(destination)),
        ],
        EXIT_SAMPLE_REJECTED,
        destination,
        "of overlay 'commercial_overlay'",
    )
    return (
        f"{len(_COMMERCIAL_PREMIUM_ITEMS)} commercial premium window(s) inside "
        f"{_display(filler.name)} hold spaces, policy_type={routing.policy_type} from "
        f"the request id, commercial premium key rejected"
    )


def _case_short_values(
    layout: CopybookLayout, map_path: Path, motor: dict[str, str], tree: _HeldTree
) -> str:
    """Confirm a value narrower than its window is justified and padded by kind.

    The supplied payment is three digits and lands right-justified over zeros; the
    supplied colour is three characters and lands left-justified over spaces. Every
    other window holds the motor fixture's expected content.
    """
    name = "short_values"
    sample_name = _write_sample(tree, name, _short_value_sample(motor))
    output = f"{name}.rec"
    result = _run_cli(
        tree,
        [
            "--field-map",
            str(map_path),
            "--sample",
            str(tree.named(sample_name)),
            "--output",
            str(tree.handoff(output)),
            "--quiet",
        ],
    )
    if result.status != EXIT_OK:
        raise _SelfTestFailure(
            f"exit {result.status}: {_display(result.stderr.strip())}"
        )
    record = _read_record(tree, output, name)
    _assert_windows(record, _SHORT_VALUE_EXPECTED_WINDOWS, layout, name)
    expected = _expected_record(_SHORT_VALUE_EXPECTED_WINDOWS, layout)
    if record != expected:
        position = _first_difference(record, expected)
        raise _SelfTestFailure(
            f"record differs from the assembled expectation at byte {position + 1}: "
            f"holds {_display(record[position : position + 12])}, expected "
            f"{_display(expected[position : position + 12])}"
        )
    payment = layout.items["CA-PAYMENT"]
    colour = layout.items["CA-M-COLOUR"]
    return (
        f"{_display(_SHORT_NUMERIC_VALUE)} landed as "
        f"{_display(record[payment.offset - 1 : payment.end_byte])} at bytes "
        f"{payment.offset}-{payment.end_byte}, "
        f"{_display(_SHORT_ALPHANUMERIC_VALUE)} landed as "
        f"{_display(record[colour.offset - 1 : colour.end_byte])} at bytes "
        f"{colour.offset}-{colour.end_byte}"
    )


def _case_justification_mutation(
    tree: _HeldTree, mutated_map: str, layout: CopybookLayout, sample_name: str
) -> str:
    """Confirm a flipped numeric justification is refused before any record is built.

    The mutated field map justifies numeric values to the left. Loading requires each
    item kind to declare the justification this builder emits, so the build must stop
    with ``EXIT_FIELD_MAP_INVALID``, name the member that differs, and write nothing.
    The case first confirms the mutation would otherwise be observable: the window the
    two justifications expect for the short numeric value must differ, so a build that
    accepted the mutated map could not have produced the shipped record. The
    destination the run is offered must hold nothing afterwards, which is read through
    the descriptor held on the run directory.
    """
    name = "map_left_numeric"
    shipped = _SHORT_VALUE_EXPECTED_WINDOWS[_LEFT_JUSTIFIED_NUMERIC_ITEM]
    if shipped == _LEFT_JUSTIFIED_NUMERIC_WINDOW:
        raise _SelfTestFailure(
            f"the two justifications expect the same window "
            f"{_display(_LEFT_JUSTIFIED_NUMERIC_WINDOW)}, so the mutation is "
            f"unobservable"
        )
    item = layout.items[_LEFT_JUSTIFIED_NUMERIC_ITEM.upper()]
    output = f"{name}.rec"
    stated = (
        f"value_justification['{KIND_NUMERIC}'] must be "
        f"'{FIXED_JUSTIFICATION[KIND_NUMERIC]}', found '{JUSTIFY_LEFT}'"
    )
    result = _run_cli(
        tree,
        [
            "--field-map",
            str(tree.named(mutated_map)),
            "--sample",
            str(tree.named(sample_name)),
            "--output",
            str(tree.handoff(output)),
            "--quiet",
        ],
    )
    if result.status != EXIT_FIELD_MAP_INVALID:
        raise _SelfTestFailure(
            f"exit {result.status}, expected {EXIT_FIELD_MAP_INVALID}; stderr "
            f"{_display(result.stderr.strip())}"
        )
    _assert_diagnostic(result.stderr)
    if stated not in result.stderr:
        raise _SelfTestFailure(
            f"diagnostic {_display(result.stderr.strip())} does not state "
            f"{_display(stated)}"
        )
    if tree.holds(output):
        raise _SelfTestFailure(
            f"{_display(output)} was written below {_path_shown(tree.path)} while the "
            f"mutated map was refused"
        )
    return (
        f"exit={EXIT_FIELD_MAP_INVALID} diagnostic states {_display(stated)}; the "
        f"mutation is observable because bytes {item.offset}-{item.end_byte} would "
        f"hold {_display(_LEFT_JUSTIFIED_NUMERIC_WINDOW)} instead of "
        f"{_display(shipped)}; nothing written"
    )


def _case_nullability_claim(field_map: dict[str, Any], names: Iterable[str]) -> str:
    """Confirm the nullability claim matches the literals this module holds.

    ``product_premium_nullability.record_bytes_demonstrated_by`` must name exactly the
    builder cases of ``_NULLABILITY_CLAIMED_CASES``, each of them run by this matrix,
    and must withhold exactly the statements of ``_NULLABILITY_WITHHELD``.
    ``transformed_assertion_carried_by`` must name the test
    ``_NULLABILITY_TRANSFORMED_TEST`` and the same test as ``enforcement``,
    and must
    require exactly the ``_NULLABILITY_REQUIRED_CASES`` objects: one for every policy
    type whose allocation populates a product premium, each carrying its literal
    ``raw_inactive_overlay_bytes`` value and repeating the ``by_policy_type``
    allocation exactly.
    """
    contract = field_map["product_premium_nullability"]
    demonstrated = contract.get("record_bytes_demonstrated_by")
    if not isinstance(demonstrated, dict):
        raise _SelfTestFailure(
            "product_premium_nullability records no record_bytes_demonstrated_by "
            "mapping"
        )
    cases = demonstrated.get("cases")
    if not isinstance(cases, list) or not cases:
        raise _SelfTestFailure("record_bytes_demonstrated_by names no case")
    claimed = {
        str(entry.get("case")) for entry in cases if isinstance(entry, dict)
    }
    if claimed != set(_NULLABILITY_CLAIMED_CASES):
        raise _SelfTestFailure(
            f"record_bytes_demonstrated_by names {_quote_all(claimed)}, expected "
            f"{_quote_all(_NULLABILITY_CLAIMED_CASES)}"
        )
    unrun = claimed - set(names)
    if unrun:
        raise _SelfTestFailure(
            f"record_bytes_demonstrated_by names {_quote_all(unrun)}, which this "
            f"matrix does not run"
        )
    withheld = demonstrated.get("does_not_establish")
    if not isinstance(withheld, list):
        raise _SelfTestFailure(
            f"record_bytes_demonstrated_by withholds {_display(withheld)}, expected a "
            f"sequence of {len(_NULLABILITY_WITHHELD)} statement(s)"
        )
    if tuple(withheld) != _NULLABILITY_WITHHELD:
        raise _SelfTestFailure(
            f"record_bytes_demonstrated_by withholds {_display(withheld)}, expected "
            f"{_display(list(_NULLABILITY_WITHHELD))}"
        )
    carried = contract.get("transformed_assertion_carried_by")
    if not isinstance(carried, dict):
        raise _SelfTestFailure(
            "product_premium_nullability records no transformed_assertion_carried_by "
            "mapping"
        )
    if carried.get("test") != _NULLABILITY_TRANSFORMED_TEST:
        raise _SelfTestFailure(
            f"transformed_assertion_carried_by names test "
            f"{_display(carried.get('test'))}, expected "
            f"{_display(_NULLABILITY_TRANSFORMED_TEST)}"
        )
    if carried.get("test") != contract.get("enforcement"):
        raise _SelfTestFailure(
            f"transformed_assertion_carried_by names test "
            f"{_display(carried.get('test'))} while enforcement names "
            f"{_display(contract.get('enforcement'))}"
        )
    required = carried.get("required_cases")
    if not isinstance(required, list) or not required:
        raise _SelfTestFailure(
            "transformed_assertion_carried_by names no required case"
        )
    allocations = contract["by_policy_type"]
    stated = {
        str(entry.get("policy_type")) for entry in required if isinstance(entry, dict)
    }
    populating = {
        policy_type
        for policy_type, allocation in allocations.items()
        if allocation.get("populated")
    }
    if stated != populating:
        raise _SelfTestFailure(
            f"transformed_assertion_carried_by requires cases for "
            f"{_quote_all(stated)} while a product premium is populated for "
            f"{_quote_all(populating)}"
        )
    if len(required) != len(_NULLABILITY_REQUIRED_CASES) or stated != set(
        _NULLABILITY_REQUIRED_CASES
    ):
        raise _SelfTestFailure(
            f"transformed_assertion_carried_by requires {len(required)} case(s) for "
            f"{_quote_all(stated)}, expected "
            f"{len(_NULLABILITY_REQUIRED_CASES)} for "
            f"{_quote_all(_NULLABILITY_REQUIRED_CASES)}"
        )
    for entry in required:
        policy_type = str(entry.get("policy_type"))
        expected = _NULLABILITY_REQUIRED_CASES[policy_type]
        if entry != expected:
            raise _SelfTestFailure(
                f"required case {_display(policy_type)} states {_display(entry)}, "
                f"expected {_display(expected)}"
            )
        allocation = allocations[policy_type]
        for member in ("populated", "null_fields"):
            if entry.get(member) != allocation.get(member):
                raise _SelfTestFailure(
                    f"required case {_display(policy_type)} states {member} "
                    f"{_display(entry.get(member))} while by_policy_type records "
                    f"{_display(allocation.get(member))}"
                )
    return (
        f"{len(claimed)} named builder case(s) ran, {len(withheld)} withheld "
        f"statement(s) match, {len(required)} required transformed case(s) carry "
        f"{_display(_NULLABILITY_INACTIVE_BYTES)} inactive overlay bytes, repeat "
        f"by_policy_type and name {_display(carried.get('test'))}"
    )


def _case_protected_fill_mutation(
    tree: _HeldTree, mutated_map: str, layout: CopybookLayout, item: str
) -> str:
    """Confirm the protected filler check reports a fill other than spaces.

    The mutated field map records the zeros fill for one protected filler entry, and
    the contract-agreement check must report that disagreement. The mutated map is
    loaded by its canonical name below the held run directory, with that directory
    confirmed immediately before and after the load.
    """
    field_map = _loaded_scratch_field_map(tree, mutated_map)
    try:
        detail = _case_protected_fill_items(field_map, layout)
    except _SelfTestFailure as failure:
        return f"the contract check reported {_display(str(failure))}"
    raise _SelfTestFailure(
        f"the contract check accepted the {FILL_LABEL_ZEROS} fill recorded for "
        f"{_display(item)}: {detail}"
    )


def _case_mutation_detected(
    tree: _HeldTree,
    mutated_map: str,
    layout: CopybookLayout,
    sample_path: Path,
    expectations: dict[str, str | _Fill],
    name: str,
    expect_record_differs: bool,
) -> str:
    """Confirm the copybook cross-check reports a mutated field map."""
    field_map = _loaded_scratch_field_map(tree, mutated_map)
    problems = _layout_disagreements(field_map, layout)
    if not problems:
        raise _SelfTestFailure("the copybook cross-check reported no disagreement")
    output = f"{name}.rec"
    result = _run_cli(
        tree,
        [
            "--field-map",
            str(tree.named(mutated_map)),
            "--sample",
            str(sample_path),
            "--output",
            str(tree.handoff(output)),
            "--quiet",
        ],
    )
    if result.status != EXIT_OK:
        return (
            f"{len(problems)} disagreement(s) reported; the build stopped with exit "
            f"{result.status}"
        )
    record = _read_record(tree, output, name)
    differs = record != _expected_record(expectations, layout)
    if expect_record_differs and not differs:
        raise _SelfTestFailure(
            "the built record still matches the expectation, so the mutation is "
            "invisible in both the bytes and the cross-check"
        )
    return (
        f"{len(problems)} disagreement(s) reported; built record "
        f"{'differs from' if differs else 'equals'} the expectation"
    )


# Self-test support: the confinement of every root and destination a run may name.


def _entry_outside(directory: Path, name: str) -> os.stat_result | None:
    """Return the status of ``name`` below ``directory``, or ``None`` if absent.

    ``directory`` stands outside the private run directory, so no descriptor this
    self-test holds reaches it: the canary directories a refused run must not write into
    are the repository's ``base`` directory, the validated generated-output root, the
    shared self-test directory the run directory stands in and the temporary directory
    of the filesystem the repository sits on. The directory is therefore opened the way
    this tool opens a directory it writes through, by descending the absolute path one
    single component at a time and following no symbolic link at any level, and the
    entry is examined relative to that descriptor without following a final symbolic
    link. A directory that is absent, or that stands at a name no longer holding a
    directory, holds no entry either, and both are reported as nothing standing; a
    directory that exists and cannot be opened is raised rather than reported as empty,
    so no unreadable directory passes a check it was never examined for. Raises
    ``InputOutputError`` when the directory or the entry cannot be examined.
    """
    try:
        dirfd = _opened_by_components(
            directory, "directory a refused run must not write into", "refusing to read"
        )
    except InputOutputError as error:
        if isinstance(error.__cause__, (FileNotFoundError, NotADirectoryError)):
            return None
        raise
    try:
        return os.stat(name, dir_fd=dirfd, follow_symlinks=False)
    except (FileNotFoundError, NotADirectoryError):
        return None
    except OSError as error:
        raise InputOutputError(
            f"cannot examine {_escaped(name)} below {_path_shown(directory)}, which a "
            f"refused run must not have written into: {error.strerror or error}"
        ) from error
    finally:
        with contextlib.suppress(OSError):
            os.close(dirfd)


def _confirm_nothing_outside(paths: Iterable[Path], refused: str) -> int:
    """Confirm every path in ``paths`` holds nothing and return how many were examined.

    Each path is split into the directory holding it and the single entry name below it,
    and is examined by ``_entry_outside``, so a symbolic-link component cannot make an
    entry a refused run created look absent. ``refused`` states what was refused in the
    failure this raises. Raises ``_SelfTestFailure`` naming the first path that holds
    anything.
    """
    examined = 0
    for path in paths:
        examined += 1
        if _entry_outside(path.parent, path.name) is not None:
            raise _SelfTestFailure(
                f"an entry stands at {_path_shown(path)} although {refused}"
            )
    return examined


def _escape_probe_name(tree: _HeldTree) -> str:
    """Return the entry name a refused probe would create outside its output root.

    The name carries this tool's name and the private run directory's own name, so two
    runs never examine the same entry in a directory they share.
    """
    return f"{_PROGRAM}.escape-probe.{tree.name}.rec"


def _refused_output_roots() -> tuple[Path, ...]:
    """Return existing directories that may not serve as an output root.

    Each one stands outside the validated generated-output root: the repository
    directory itself, the extraction directory a read is authorised from, the directory
    immediately above the generated-output root, and the temporary directory of the
    filesystem the repository sits on.
    """
    repository = _canonical_path(REPOSITORY_ROOT)
    return (
        repository,
        repository / "modernization" / "extraction",
        repository / "modernization" / "harness",
        Path(repository.anchor) / "tmp",
    )


def _assert_nothing_created(
    tree: _HeldTree,
    argv: list[str],
    expected_status: int,
    fragment: str,
    absent: Iterable[Path],
) -> str:
    """Run one failing invocation and confirm no entry stands at the named paths.

    The status, the single control-free diagnostic naming this tool, the stated fragment
    and the silent stdout are checked exactly as ``_assert_rejected`` checks them. Every
    path in ``absent`` stands outside the held run directory and must still hold
    nothing, examined relative to a descriptor opened on the directory holding it one
    component at a time and without following a final symbolic link, which is how a
    destination refused for leaving the output root is distinguished from one written
    before the refusal.
    """
    named = tuple(absent)
    result = _run_cli(tree, argv)
    if result.status != expected_status:
        raise _SelfTestFailure(
            f"exit {result.status}, expected {expected_status}; stderr "
            f"{_display(result.stderr.strip())}"
        )
    _assert_diagnostic(result.stderr)
    if fragment not in result.stderr:
        raise _SelfTestFailure(
            f"diagnostic {_display(result.stderr.strip())} does not state "
            f"{_display(fragment)}"
        )
    if result.stdout:
        raise _SelfTestFailure(
            f"wrote {len(result.stdout)} characters to stdout on failure"
        )
    examined = _confirm_nothing_outside(named, "the run was refused")
    return (
        f"exit={expected_status} diagnostic states {_display(fragment)}, "
        f"{examined} named path(s) hold nothing"
    )


def _case_output_root_outside(map_path: Path, tree: _HeldTree) -> str:
    """Confirm every output root outside the generated-output root is refused.

    Each probe names one root with a seeded destination inside the private run
    directory. A root resolving outside the validated generated-output root is refused
    for standing outside it, whether or not it exists, and a root that would stand
    inside it but is absent is refused for not existing, because a named root is never
    created. Every probe must leave its sentinel destination unchanged.
    """
    build_root = _validated_build_root()
    probes = [
        (root, "is not inside the generated-output root")
        for root in _refused_output_roots()
    ]
    probes.append((tree.named("absent_root"), "is not an existing directory below"))
    for index, (root, fragment) in enumerate(probes, start=1):
        destination = _seeded_destination(tree, f"output_root_refused_{index}")
        _assert_rejected(
            tree,
            [
                "--field-map",
                str(map_path),
                "--sample",
                str(MOTOR_SAMPLE_DEFINITION),
                "--output",
                str(tree.handoff(destination)),
                "--output-root",
                str(root),
            ],
            EXIT_IO_ERROR,
            destination,
            fragment,
        )
    return (
        f"{len(probes)} output root(s) refused with exit {EXIT_IO_ERROR} against "
        f"{_path_shown(build_root)}, every sentinel unchanged"
    )


def _case_output_root_symlink(map_path: Path, tree: _HeldTree) -> str:
    """Confirm an output root reached through a symbolic link is refused unfollowed.

    The link is created relative to the descriptor held on the private run directory and
    names the validated generated-output root itself, so its target would authorise a
    write while the link may not: the refusal must name the link as a symbolic-link
    component, the sentinel destination must still hold its bytes, the link must still
    stand as a link, examined through the held descriptor, and the link's target
    directory must not have gained an entry, examined relative to a descriptor opened on
    that directory one component at a time.
    """
    build_root = _validated_build_root()
    link = tree.link(build_root, "output_root_link")
    destination = _seeded_destination(tree, "output_root_symlink")
    detail = _assert_rejected(
        tree,
        [
            "--field-map",
            str(map_path),
            "--sample",
            str(MOTOR_SAMPLE_DEFINITION),
            "--output",
            str(tree.handoff(destination)),
            "--output-root",
            str(tree.named(link)),
        ],
        EXIT_IO_ERROR,
        destination,
        "passes through symbolic link",
    )
    standing = tree.status(link)
    if standing is None or not stat.S_ISLNK(standing.st_mode):
        raise _SelfTestFailure(
            f"{_display(link)} no longer stands as a symbolic link below "
            f"{_path_shown(tree.path)} after the refusal"
        )
    _confirm_nothing_outside((build_root / destination,), "the root was refused")
    return f"{detail}; the link still names {_path_shown(build_root)}"


def _case_output_escapes_root(map_path: Path, tree: _HeldTree) -> str:
    """Confirm a destination whose canonical form leaves the output root is refused.

    The destination is named below a symbolic link created relative to the descriptor
    held on the private run directory that points at the temporary directory of the
    filesystem the repository sits on, with the run directory itself named as the output
    root. The destination is handed over below the held descriptor's own pathname, so
    the link the run resolves is the one inside the held directory. Canonicalisation
    therefore places the destination outside that root, which must be refused before
    anything is created at the link's target.
    """
    target = Path(_canonical_path(REPOSITORY_ROOT).anchor) / "tmp"
    probe = _escape_probe_name(tree)
    link = tree.link(target, "output_escape_link")
    detail = _assert_nothing_created(
        tree,
        [
            "--field-map",
            str(map_path),
            "--sample",
            str(MOTOR_SAMPLE_DEFINITION),
            "--output",
            str(tree.handoff(link, probe)),
            "--output-root",
            str(tree.path),
        ],
        EXIT_IO_ERROR,
        "is not a file inside the output root",
        (target / probe,),
    )
    return f"{detail}; {_path_shown(target)} gained no record"


def _case_output_into_base_refused(tree: _HeldTree) -> str:
    """Confirm a destination canonicalising into the read-only source tree is refused.

    A symbolic link created relative to the descriptor held on the private run directory
    names the repository's ``base`` directory, and one full-width record is offered to
    ``write_record`` below that held descriptor's own pathname under the default
    generated-output root. The refusal must name the canonical destination the link
    leads to and the write it refuses, and no entry may stand at that destination
    afterwards, examined relative to a descriptor opened on the read-only source
    directory one component at a time.
    """
    source_root = _canonical_path(REPOSITORY_ROOT) / "base"
    probe = _escape_probe_name(tree)
    link = tree.link(source_root, "source_root_link")
    planted = source_root / probe
    refusal: InputOutputError | None = None
    try:
        _handed_off(
            tree,
            "self-test run directory",
            lambda: write_record(
                tree.handoff(link, probe), "0" * COMMAREA_RECORD_LENGTH
            ),
        )
    except InputOutputError as error:
        refusal = error
    if refusal is None:
        raise _SelfTestFailure(
            f"write_record accepted a destination inside {_path_shown(source_root)}"
        )
    for stated in (_path_shown(planted), "refusing to write"):
        if stated not in str(refusal):
            raise _SelfTestFailure(
                f"the refusal states {_display(str(refusal))}, expected "
                f"{_display(stated)}"
            )
    _confirm_nothing_outside((planted,), "the write was refused")
    return f"refused a record for {_path_shown(planted)}; that path holds nothing"


def _case_scratch_subtree_removed(tree: _HeldTree) -> str:
    """Confirm a scratch subtree is removed through descriptors without following links.

    The probe subtree is created relative to the descriptor held on the private run
    directory and carries a nested directory, a regular file, a FIFO and a symbolic link
    naming a sentinel file beside it. Emptying it through the descriptor held on it must
    remove every entry it holds, leave the sentinel's bytes in place, which is what
    proves the link was unlinked rather than followed, and leave nothing at the
    subtree's own name once it is removed relative to the descriptor above it.
    """
    sentinel_bytes = b"SENTINEL KEPT BY THE REMOVAL\n"
    sentinel = _write_payload(tree, "removal_sentinel", sentinel_bytes)
    probe = tree.directory("removal_probe")
    try:
        nested = probe.directory("nested")
        try:
            deeper = nested.directory("deeper")
            try:
                deeper.create("leaf.rec", b"LEAF RECORD\n")
            finally:
                deeper.close()
        finally:
            nested.close()
        probe.fifo("removal_pipe")
        probe.link(tree.named(sentinel), "sentinel_link")
        entries = len(probe.entries())

        probe.empty()
        remaining = probe.entries()
        if remaining:
            raise _SelfTestFailure(
                f"{len(remaining)} entry(s) remain below {_path_shown(probe.path)}, "
                f"first {_escaped(remaining[0])}"
            )
    finally:
        probe.close()

    tree.remove_directory(probe.name)
    if tree.holds(probe.name):
        raise _SelfTestFailure(
            f"{_path_shown(probe.path)} still stands after it was removed"
        )
    if tree.read(sentinel) != sentinel_bytes:
        raise _SelfTestFailure(
            f"the sentinel {_display(sentinel)} changed while the subtree holding a "
            f"link to it was removed"
        )
    return (
        f"{entries} held entry(s) removed through descriptors, "
        f"{_path_shown(probe.path)} gone, sentinel={len(sentinel_bytes)} bytes "
        f"unchanged"
    )


def _case_name_swap_not_redirected(tree: _HeldTree, map_path: Path) -> str:
    """Confirm a replaced visible directory name redirects nothing and leaves nothing.

    The probe stands below the private run directory and carries a held run directory of
    its own and a canary directory outside that held directory. The held directory's
    visible name is then replaced the way a concurrent run holding no descriptor on it
    would replace it: the directory is renamed aside and a symbolic link naming the
    canary is created at the name it stood at, both relative to the descriptor above
    them.

    With that replacement standing, the case confirms five things. A pathname handoff is
    refused, naming the entry that no longer names the held directory, so no visible
    pathname of it is handed to a run under test. A write made relative to the held
    descriptor still lands in the held directory, read back through that descriptor and
    found at the name the directory was renamed to. The pathname the held descriptor
    itself reports still names the held directory rather than the replacement. One
    whole record a run under test writes below that descriptor's own pathname lands in
    the held directory too, at the emitted length and read back through the held
    descriptor, which is what proves the replaced name redirected no write the tool
    itself made. And the removal that closes a run empties and removes the originally
    held directory, found through the descriptor's own pathname, while reporting the
    changed visible name as a failure.

    The canary must hold nothing throughout, which is what proves nothing was written
    outside the held directory, and every entry the probe created is removed through
    held descriptors, so nothing of it survives the case.
    """
    probe = tree.directory(_SWAP_PROBE_NAME)
    try:
        canary = probe.directory(_SWAP_CANARY_NAME)
        try:
            held = probe.directory(_SWAP_HELD_NAME)
            closed = False
            try:
                held.create("before_swap.rec", _SWAP_BEFORE_BYTES)
                probe.rename(_SWAP_HELD_NAME, _SWAP_MOVED_NAME)
                probe.link(_SWAP_CANARY_NAME, _SWAP_HELD_NAME)

                refusal: InputOutputError | None = None
                try:
                    _handed_off(held, "probe run directory", lambda: None)
                except InputOutputError as error:
                    refusal = error
                if refusal is None:
                    raise _SelfTestFailure(
                        "the pathname handoff accepted a run directory whose visible "
                        "name had been replaced"
                    )
                for stated in (_SWAP_HELD_NAME, "no longer names"):
                    if stated not in str(refusal):
                        raise _SelfTestFailure(
                            f"the refusal states {_display(str(refusal))}, expected "
                            f"{_display(stated)}"
                        )

                held.create("after_swap.rec", _SWAP_AFTER_BYTES)
                if held.read("after_swap.rec") != _SWAP_AFTER_BYTES:
                    raise _SelfTestFailure(
                        "the entry written through the held descriptor does not hold "
                        "the bytes it was given"
                    )
                if held.visible_name("probe run directory") != _SWAP_MOVED_NAME:
                    raise _SelfTestFailure(
                        f"the held descriptor reports a name other than "
                        f"{_display(_SWAP_MOVED_NAME)} after the replacement"
                    )
                moved = probe.status(_SWAP_MOVED_NAME)
                if moved is None or (moved.st_dev, moved.st_ino) != (
                    held.device,
                    held.inode,
                ):
                    raise _SelfTestFailure(
                        f"{_display(_SWAP_MOVED_NAME)} does not name the directory the "
                        f"probe holds open"
                    )
                written = sorted(canary.entries())
                if written:
                    raise _SelfTestFailure(
                        f"the canary {_path_shown(canary.path)} holds {len(written)} "
                        f"entry(s), first {_escaped(written[0])}, so a write followed "
                        f"the replaced name"
                    )

                # One whole record written by a run under test, named below the held
                # descriptor's own pathname while the replacement stands: the run
                # resolves that pathname to the directory the descriptor holds, so the
                # record must land there and the canary must stay empty. The output root
                # is named here, so the run is given the run directory this matrix works
                # inside and not the probe the destination stands below.
                build = _run_cli(
                    tree,
                    [
                        "--field-map",
                        str(map_path),
                        "--sample",
                        str(MOTOR_SAMPLE_DEFINITION),
                        "--output",
                        str(held.handoff(_SWAP_RECORD_NAME)),
                        "--output-root",
                        str(tree.path),
                        "--quiet",
                    ],
                )
                if build.status != EXIT_OK:
                    raise _SelfTestFailure(
                        f"the record offered below the held descriptor exited "
                        f"{build.status}: {_display(build.stderr.strip())}"
                    )
                if build.stdout:
                    raise _SelfTestFailure("--quiet still wrote a summary")
                record = _read_record(
                    held, _SWAP_RECORD_NAME, "the record written through the descriptor"
                )
                if len(record) != COMMAREA_RECORD_LENGTH:
                    raise _SelfTestFailure(
                        f"the record written through the held descriptor holds "
                        f"{len(record)} characters, expected {COMMAREA_RECORD_LENGTH}"
                    )
                redirected = sorted(canary.entries())
                if redirected:
                    raise _SelfTestFailure(
                        f"the canary {_path_shown(canary.path)} holds "
                        f"{len(redirected)} entry(s) after the record was written, "
                        f"first {_escaped(redirected[0])}, so the run followed the "
                        f"replaced name"
                    )
                replacement = probe.status(_SWAP_HELD_NAME)
                if replacement is None or not stat.S_ISLNK(replacement.st_mode):
                    raise _SelfTestFailure(
                        f"{_display(_SWAP_HELD_NAME)} no longer stands as the symbolic "
                        f"link the replacement put in place"
                    )

                removal: InputOutputError | None = None
                closed = True
                try:
                    _removed_held_directory(held, "probe run directory")
                except InputOutputError as error:
                    removal = error
                if removal is None:
                    raise _SelfTestFailure(
                        "the removal reported no failure although the visible name had "
                        "been replaced"
                    )
                for stated in (_SWAP_MOVED_NAME, "no longer named it"):
                    if stated not in str(removal):
                        raise _SelfTestFailure(
                            f"the removal states {_display(str(removal))}, expected "
                            f"{_display(stated)}"
                        )
                if probe.holds(_SWAP_MOVED_NAME):
                    raise _SelfTestFailure(
                        f"{_display(_SWAP_MOVED_NAME)} still stands after the removal, "
                        f"so the originally held directory was not removed"
                    )
                left = sorted(canary.entries())
                if left:
                    raise _SelfTestFailure(
                        f"the canary {_path_shown(canary.path)} holds {len(left)} "
                        f"entry(s) after the removal, first {_escaped(left[0])}"
                    )
            finally:
                if not closed:
                    held.close()
            probe.remove(_SWAP_HELD_NAME)
        finally:
            canary.close()
        probe.remove_directory(_SWAP_CANARY_NAME)
        remaining = probe.entries()
        if remaining:
            raise _SelfTestFailure(
                f"{len(remaining)} entry(s) remain below {_path_shown(probe.path)}, "
                f"first {_escaped(remaining[0])}"
            )
    finally:
        probe.close()

    tree.remove_directory(_SWAP_PROBE_NAME)
    if tree.holds(_SWAP_PROBE_NAME):
        raise _SelfTestFailure(
            f"{_display(_SWAP_PROBE_NAME)} still stands below {_path_shown(tree.path)} "
            f"after the case removed it"
        )
    return (
        f"the handoff was refused for {_display(_SWAP_HELD_NAME)}, the write through "
        f"the held descriptor stayed in {_display(_SWAP_MOVED_NAME)}, the "
        f"{COMMAREA_RECORD_LENGTH} character record a run wrote below that descriptor "
        f"landed there too, the removal reported the replaced name and removed the "
        f"held directory, and the canary {_display(_SWAP_CANARY_NAME)} held nothing "
        f"and left nothing"
    )


def _case_scratch_removed(scratch: _Scratch) -> str:
    """Release the private run directory and confirm nothing of it remains.

    The removal runs through the descriptors this run has held on the run directory and
    its parents, so it reaches nothing the run did not create, and it confirms through
    those descriptors that the entry it removed holds nothing. Every descriptor is
    closed by the time it returns, so this case confirms the same for the run
    directory's own name by opening the shared directory holding it one component at a
    time and examining that name without following a final symbolic link; a shared
    directory that went with the run holds nothing either.
    """
    path = scratch.tree.path
    detail = _released_scratch(scratch)
    _confirm_nothing_outside((path,), "the removal returned")
    return detail


def _run_case(
    results: list[_CaseResult],
    stream: Any,
    quiet: bool,
    name: str,
    body: Callable[[], str],
) -> None:
    """Run one case, record its outcome and print its line.

    A case that raises records a failure and the run continues with the next case.
    ``_SelfTestFailure`` carries the observation the case made; a ``BuildError`` or any
    of the listed defect classes is reported by type and message.
    """
    try:
        detail = body()
    except _SelfTestFailure as failure:
        result = _CaseResult(name=name, passed=False, detail=str(failure))
    except BuildError as error:
        result = _CaseResult(
            name=name, passed=False, detail=f"{_type_name(error)}: {error}"
        )
    except (
        ArithmeticError,
        AssertionError,
        AttributeError,
        LookupError,
        NameError,
        OSError,
        RuntimeError,
        StopIteration,
        TypeError,
        ValueError,
        yaml.YAMLError,
    ) as error:
        result = _CaseResult(
            name=name,
            passed=False,
            detail=f"unexpected {_type_name(error)}: {_display(error)}",
        )
    else:
        result = _CaseResult(name=name, passed=True, detail=detail)
    results.append(result)
    if result.passed and quiet:
        return
    verdict = "PASS" if result.passed else "FAIL"
    print(f"self-test {verdict} {result.name} -- {result.detail}", file=stream)


def run_self_test(
    field_map_path: str | os.PathLike[str] | None = None,
    *,
    quiet: bool = False,
    stream: Any = None,
) -> int:
    """Run every self-test case and return ``EXIT_OK`` or ``EXIT_SELF_TEST_FAILED``.

    The copybook parse, the field map and both sample definitions are read first, so a
    field map or copybook that cannot be read raises its own ``BuildError`` before any
    case runs. One bounded read of the field map supplies both the document the cases
    read and the bytes the mutated field maps are seeded from, so the mutants carry the
    content that parse saw. Each case then prints one line to ``stream``, which defaults
    to stdout, followed by one summary line. ``quiet`` limits the case lines to the
    failing ones. Every scratch document and every destination a case offers sits inside
    one private run directory below ``modernization/harness/build/builder-selftest``,
    held through descriptors on its parents and removed by the final case, so a run
    reaches no directory outside the generated-output root and leaves nothing behind.
    Each of those entries is created, read and removed relative to the descriptor held
    on that run directory, and every pathname a case hands to a run under test is
    confirmed against the identity that descriptor reported immediately before and
    after it is used, so a visible run name replaced while the matrix runs is reported
    rather than followed.
    """
    out = sys.stdout if stream is None else stream
    layout = parse_copybook_layout()
    selected_map = _read_field_map(field_map_path)
    map_path = selected_map.path
    field_map = selected_map.document
    map_text = selected_map.payload
    motor = load_sample(MOTOR_SAMPLE_DEFINITION)
    commercial = load_sample(COMMERCIAL_SAMPLE_DEFINITION)
    results: list[_CaseResult] = []

    scratch = _held_scratch()
    try:
        tree = scratch.tree

        _run_case(
            results,
            out,
            quiet,
            "copybook_record_length",
            lambda: _case_copybook_record_length(layout),
        )
        _run_case(
            results,
            out,
            quiet,
            "layout_matches_copybook",
            lambda: _case_layout_cross_check(field_map, layout),
        )
        _run_case(
            results,
            out,
            quiet,
            "motor_record_bytes",
            lambda: _case_fixture_record(
                layout,
                map_path,
                MOTOR_SAMPLE_DEFINITION,
                motor,
                _MOTOR_FIXTURE_KEYS,
                _MOTOR_EXPECTED_WINDOWS,
                tree,
                "motor",
            ),
        )
        _run_case(
            results,
            out,
            quiet,
            "commercial_record_bytes",
            lambda: _case_fixture_record(
                layout,
                map_path,
                COMMERCIAL_SAMPLE_DEFINITION,
                commercial,
                _COMMERCIAL_FIXTURE_KEYS,
                _COMMERCIAL_EXPECTED_WINDOWS,
                tree,
                "commercial",
            ),
        )
        _run_case(
            results,
            out,
            quiet,
            "protected_fill_items_agree",
            lambda: _case_protected_fill_items(field_map, layout),
        )
        _run_case(
            results,
            out,
            quiet,
            "chain_populated_items_agree",
            lambda: _case_chain_populated_items(field_map, layout),
        )
        _run_case(
            results,
            out,
            quiet,
            "emitted_length_from_constant",
            lambda: _case_length_from_constant(field_map, motor, tree),
        )
        _run_case(
            results,
            out,
            quiet,
            "long_record_refused",
            lambda: _case_long_record_refused(field_map, motor, tree),
        )
        _run_case(
            results,
            out,
            quiet,
            "motor_rerun_identical",
            lambda: _case_rerun_identical(
                map_path, MOTOR_SAMPLE_DEFINITION, tree, "motor_rerun"
            ),
        )
        _run_case(
            results,
            out,
            quiet,
            "commercial_status_placed",
            lambda: _case_commercial_status_placed(
                layout, map_path, commercial, tree
            ),
        )
        _run_case(
            results,
            out,
            quiet,
            "commercial_inactive_overlay_filled",
            lambda: _case_commercial_inactive_overlay(
                layout, field_map, map_path, commercial, tree
            ),
        )
        _run_case(
            results,
            out,
            quiet,
            "motor_inactive_overlay_spaces",
            lambda: _case_motor_inactive_overlay(
                layout, field_map, map_path, motor, tree
            ),
        )
        _run_case(
            results,
            out,
            quiet,
            "short_values_justified",
            lambda: _case_short_values(layout, map_path, motor, tree),
        )

        left_numeric = _mutated_field_map(
            tree,
            "map_left_numeric",
            field_map,
            lambda document: document["sample_definition_contract"][
                "value_justification"
            ].__setitem__(KIND_NUMERIC, JUSTIFY_LEFT),
        )
        short_values_sample = _write_sample(
            tree, "short_values_mutation", _short_value_sample(motor)
        )
        _run_case(
            results,
            out,
            quiet,
            "map_left_numeric_justification_detected",
            lambda: _case_justification_mutation(
                tree, left_numeric, layout, short_values_sample
            ),
        )
        zero_filler = _mutated_field_map(
            tree,
            "map_zero_filled_protected_item",
            field_map,
            lambda document: _protected_fill_entry(
                document, "CA-M-FILLER"
            ).__setitem__("fill", FILL_LABEL_ZEROS),
        )
        _run_case(
            results,
            out,
            quiet,
            "map_protected_fill_label_detected",
            lambda: _case_protected_fill_mutation(
                tree, zero_filler, layout, "CA-M-FILLER"
            ),
        )

        swapped = _mutated_field_map(
            tree,
            "map_swapped_offsets",
            field_map,
            lambda document: _swap_offsets(
                _layout_entry(document, "policy_common", "CA-ISSUE-DATE"),
                _layout_entry(document, "policy_common", "CA-EXPIRY-DATE"),
            ),
        )
        _run_case(
            results,
            out,
            quiet,
            "map_swapped_offsets_detected",
            lambda: _case_mutation_detected(
                tree,
                swapped,
                layout,
                MOTOR_SAMPLE_DEFINITION,
                _MOTOR_EXPECTED_WINDOWS,
                "map_swapped_offsets",
                expect_record_differs=True,
            ),
        )
        shortened = _mutated_field_map(
            tree,
            "map_shortened_item",
            field_map,
            lambda document: _layout_entry(
                document, "policy_common", "CA-BROKERSREF"
            ).__setitem__("length", 9),
        )
        _run_case(
            results,
            out,
            quiet,
            "map_shortened_item_detected",
            lambda: _case_mutation_detected(
                tree,
                shortened,
                layout,
                MOTOR_SAMPLE_DEFINITION,
                _MOTOR_EXPECTED_WINDOWS,
                "map_shortened_item",
                expect_record_differs=False,
            ),
        )

        dropped_item = _mutated_field_map(
            tree,
            "map_dropped_item",
            field_map,
            lambda document: document["layout"]["motor_overlay"]["items"].remove(
                _layout_entry(document, "motor_overlay", "CA-M-COLOUR")
            ),
        )
        numeric_filler = _mutated_field_map(
            tree,
            "map_numeric_filler",
            field_map,
            lambda document: _layout_entry(
                document, "motor_overlay", "CA-M-FILLER"
            ).__setitem__("kind", KIND_NUMERIC),
        )
        seed_in_domain = _mutated_field_map(
            tree,
            "map_chain_seed_in_domain",
            field_map,
            lambda document: _chain_populated_entry(
                document, "CA-RETURN-CODE"
            ).__setitem__(CHAIN_CONTENT_SEED, _RETURN_CODE_DOMAIN_MEMBER),
        )
        seed_wrong_length = _mutated_field_map(
            tree,
            "map_chain_seed_short",
            field_map,
            lambda document: _chain_populated_entry(
                document, "CA-RETURN-CODE"
            ).__setitem__(CHAIN_CONTENT_SEED, _CHAIN_RETURN_CODE_SEED[:1]),
        )
        seed_not_numeric = _mutated_field_map(
            tree,
            "map_chain_seed_not_numeric",
            field_map,
            lambda document: _chain_populated_entry(
                document, "CA-RETURN-CODE"
            ).__setitem__(CHAIN_CONTENT_SEED, _NON_DIGIT_SEED),
        )
        chain_item_missing = _mutated_field_map(
            tree,
            "map_chain_item_missing",
            field_map,
            lambda document: document["sample_definition_contract"][
                CHAIN_POPULATED_SECTION
            ].remove(_chain_populated_entry(document, "CA-LASTCHANGED")),
        )
        chain_item_foreign = _mutated_field_map(
            tree,
            "map_chain_item_foreign",
            field_map,
            lambda document: document["sample_definition_contract"][
                CHAIN_POPULATED_SECTION
            ].append(
                {
                    "item": _FOREIGN_CHAIN_ITEM,
                    "kind": KIND_NUMERIC,
                    CHAIN_CONTENT_FILL: FILL_LABEL_ZEROS,
                }
            ),
        )
        short_record = _mutated_field_map(
            tree,
            "map_record_length_short",
            field_map,
            lambda document: document["record"].__setitem__(
                "length", COMMAREA_RECORD_LENGTH - 1
            ),
        )
        long_record = _mutated_field_map(
            tree,
            "map_record_length_long",
            field_map,
            lambda document: document["record"].__setitem__(
                "length", COMMAREA_RECORD_LENGTH + 1
            ),
        )
        wrong_emitted = _mutated_field_map(
            tree,
            "map_emitted_length",
            field_map,
            lambda document: document["sample_definition_contract"].__setitem__(
                "emitted_record_length", 999
            ),
        )
        deep_map = _mutated_field_map(
            tree,
            "map_deeply_nested",
            field_map,
            lambda document: document.__setitem__(
                "depth_probe", _nested(MAX_DOCUMENT_DEPTH + 2)
            ),
        )
        duplicate_map = _write_payload(
            tree,
            "map_duplicate_key.yml",
            map_text + b"\nrecord:\n  length: 100\n",
        )
        map_source = map_text.decode("utf-8")
        duplicate_offset = _write_payload(
            tree,
            "map_duplicate_offset.yml",
            _duplicated_key_payload(
                map_source, "      - item: CA-PAYMENT", "        offset: 999"
            ),
        )
        duplicate_length = _write_payload(
            tree,
            "map_duplicate_length.yml",
            _duplicated_key_payload(
                map_source, "      - item: CA-M-PREMIUM", "        length: 7"
            ),
        )
        duplicate_kind = _write_payload(
            tree,
            "map_duplicate_kind.yml",
            _duplicated_key_payload(
                map_source,
                "      - item: CA-B-FirePremium",
                f"        kind: {KIND_ALPHANUMERIC}",
            ),
        )
        duplicate_emitted = _write_payload(
            tree,
            "map_duplicate_emitted_length.yml",
            _duplicated_key_payload(
                map_source,
                "sample_definition_contract:",
                "  emitted_record_length: 999",
            ),
        )
        unhashable_map = _write_payload(
            tree,
            "map_unhashable_key.yml",
            map_text + b"\n" + _UNHASHABLE_KEY_TEXT.encode("utf-8"),
        )
        cyclic_map = _write_payload(
            tree,
            "map_self_referential.yml",
            map_text + b"\n" + _CYCLIC_ALIAS_TEXT.encode("utf-8"),
        )
        alias_dag_map = _write_payload(
            tree,
            "map_alias_dag.yml",
            map_text
            + b"\n"
            + _alias_dag_text(_ALIAS_DAG_LEVELS, _ALIAS_DAG_FANOUT).encode("utf-8"),
        )
        undecodable_map = _write_payload(
            tree, "map_bad_utf8.yml", map_text + b"\n# \xff\n"
        )
        oversized_map = _write_payload(
            tree,
            "map_oversized.yml",
            map_text + b"\n# " + b"p" * MAX_FIELD_MAP_BYTES + b"\n",
        )
        absent_map = "map_absent.yml"
        fifo_map = _make_fifo(tree, "map_fifo.yml")

        for case_name, mutated, expected_status, fragment in (
            (
                "map_dropped_item_rejects_key",
                dropped_item,
                EXIT_SAMPLE_REJECTED,
                "names no item declared for request id",
            ),
            (
                "map_numeric_filler_rejected",
                numeric_filler,
                EXIT_FIELD_MAP_INVALID,
                "that window holds spaces only",
            ),
            (
                "map_chain_seed_in_domain_rejected",
                seed_in_domain,
                EXIT_FIELD_MAP_INVALID,
                (
                    f"'{CHAIN_CONTENT_SEED}' '{_RETURN_CODE_DOMAIN_MEMBER}' is a "
                    "member of the domain logical entry 'return_code' declares"
                ),
            ),
            (
                "map_chain_seed_short_rejected",
                seed_wrong_length,
                EXIT_FIELD_MAP_INVALID,
                (
                    f"'{CHAIN_CONTENT_SEED}' holds 1 character(s) and the declared "
                    "length of the window is 2"
                ),
            ),
            (
                "map_chain_seed_not_numeric_rejected",
                seed_not_numeric,
                EXIT_FIELD_MAP_INVALID,
                (
                    f"'{CHAIN_CONTENT_SEED}' holds a character outside digits 0-9 at "
                    "position 2"
                ),
            ),
            (
                "map_chain_item_missing_rejected",
                chain_item_missing,
                EXIT_FIELD_MAP_INVALID,
                "records no entry for chain-populated item(s) 'CA-LASTCHANGED'",
            ),
            (
                "map_chain_item_foreign_rejected",
                chain_item_foreign,
                EXIT_FIELD_MAP_INVALID,
                (
                    f"names item '{_FOREIGN_CHAIN_ITEM}', which no logical entry "
                    f"records as 'populated_by: {POPULATED_BY_CHAIN}'"
                ),
            ),
            (
                "map_record_length_short",
                short_record,
                EXIT_FIELD_MAP_INVALID,
                f"'length' is {COMMAREA_RECORD_LENGTH - 1}",
            ),
            (
                "map_record_length_long",
                long_record,
                EXIT_FIELD_MAP_INVALID,
                f"'length' is {COMMAREA_RECORD_LENGTH + 1}",
            ),
            (
                "map_emitted_length_mismatch",
                wrong_emitted,
                EXIT_FIELD_MAP_INVALID,
                "'emitted_record_length' is 999",
            ),
            (
                "map_duplicate_key",
                duplicate_map,
                EXIT_FIELD_MAP_INVALID,
                _duplicate_key_stated("record"),
            ),
            (
                "map_duplicate_offset",
                duplicate_offset,
                EXIT_FIELD_MAP_INVALID,
                _duplicate_key_stated("offset"),
            ),
            (
                "map_duplicate_length",
                duplicate_length,
                EXIT_FIELD_MAP_INVALID,
                _duplicate_key_stated("length"),
            ),
            (
                "map_duplicate_kind",
                duplicate_kind,
                EXIT_FIELD_MAP_INVALID,
                _duplicate_key_stated("kind"),
            ),
            (
                "map_duplicate_emitted_length",
                duplicate_emitted,
                EXIT_FIELD_MAP_INVALID,
                _duplicate_key_stated("emitted_record_length"),
            ),
            (
                "map_unhashable_key",
                unhashable_map,
                EXIT_FIELD_MAP_INVALID,
                "found unhashable key of type list",
            ),
            (
                "map_self_referential",
                cyclic_map,
                EXIT_FIELD_MAP_INVALID,
                "an alias is not accepted",
            ),
            (
                "map_alias_dag",
                alias_dag_map,
                EXIT_FIELD_MAP_INVALID,
                "an alias is not accepted",
            ),
            (
                "map_not_regular_file",
                fifo_map,
                EXIT_FIELD_MAP_INVALID,
                "is not a regular file",
            ),
            (
                "map_deeply_nested",
                deep_map,
                EXIT_FIELD_MAP_INVALID,
                f"nests deeper than the accepted {MAX_DOCUMENT_DEPTH} levels",
            ),
            (
                "map_undecodable_bytes",
                undecodable_map,
                EXIT_FIELD_MAP_INVALID,
                "is not valid UTF-8 text",
            ),
            (
                "map_oversized",
                oversized_map,
                EXIT_FIELD_MAP_INVALID,
                f"above the {MAX_FIELD_MAP_BYTES} byte limit",
            ),
            ("map_absent", absent_map, EXIT_IO_ERROR, "cannot read field map"),
        ):
            destination = _seeded_destination(tree, case_name)
            _run_case(
                results,
                out,
                quiet,
                case_name,
                lambda mutated=mutated,
                expected_status=expected_status,
                fragment=fragment,
                destination=destination: _assert_rejected(
                    tree,
                    [
                        "--field-map",
                        str(tree.named(mutated)),
                        "--sample",
                        str(MOTOR_SAMPLE_DEFINITION),
                        "--output",
                        str(tree.handoff(destination)),
                    ],
                    expected_status,
                    destination,
                    fragment,
                ),
            )

        rejected_samples: list[tuple[str, dict[str, Any], str]] = [
            (
                "sample_unknown_key",
                {**motor, "CA-NOT-AN-ITEM": "X"},
                "key 'CA-NOT-AN-ITEM' names no item declared for request id",
            ),
            (
                "sample_wrong_overlay_motor",
                {**motor, "CA-B-FirePremium": "00013500"},
                "of overlay 'commercial_overlay'",
            ),
            (
                "sample_wrong_overlay_commercial",
                {**commercial, "CA-M-PREMIUM": "000450"},
                "of overlay 'motor_overlay'",
            ),
            (
                "sample_unsupported_request_id",
                {**motor, "CA-REQUEST-ID": "01AEND"},
                "'01AEND' is not a generated sample",
            ),
            (
                "sample_duplicate_request_id_spelling",
                {**motor, "ca-request-id": motor["CA-REQUEST-ID"]},
                (
                    "keys 'CA-REQUEST-ID', 'ca-request-id' all name item "
                    "'CA-REQUEST-ID'; supply it once"
                ),
            ),
            (
                "sample_duplicate_key_spelling",
                {**motor, "ca-payment": "000600"},
                (
                    "keys 'CA-PAYMENT' and 'ca-payment' both name item "
                    "'CA-PAYMENT'; supply it once"
                ),
            ),
            (
                "sample_chain_return_code",
                {**motor, "CA-RETURN-CODE": "00"},
                "names item 'CA-RETURN-CODE', which the chain assigns",
            ),
            (
                "sample_chain_policy_number",
                {**motor, "CA-POLICY-NUM": "0000000001"},
                "names item 'CA-POLICY-NUM', which the chain assigns",
            ),
            (
                "sample_chain_last_changed",
                {**motor, "CA-LASTCHANGED": "2026-08-19-12.00.00.000000"},
                "names item 'CA-LASTCHANGED', which the chain assigns",
            ),
            (
                "sample_protected_filler_key",
                {**motor, "CA-M-FILLER": "INJECTED"},
                "names filler item 'CA-M-FILLER'",
            ),
            (
                "sample_non_string_value",
                {**motor, "CA-PAYMENT": 500},
                "value for key 'CA-PAYMENT' must be a string, found int",
            ),
            (
                "sample_over_length_value",
                {**motor, "CA-M-COLOUR": "MIDNIGHTBLUE"},
                "is 12 characters, longer than the declared length 8",
            ),
            (
                "sample_non_digit_numeric",
                {**motor, "CA-PAYMENT": "0005O0"},
                "holds a character outside digits 0-9 at position 5",
            ),
            (
                "sample_non_ascii_value",
                {**motor, "CA-M-MAKE": "FORD\u00c9"},
                "outside printable 7-bit ASCII",
            ),
            (
                "sample_control_character_key",
                {**motor, "BAD\nKEY\x1b[31m": "X"},
                "'BAD\\nKEY\\x1b[31m'",
            ),
            (
                "sample_empty_common_value",
                {**motor, "CA-PAYMENT": ""},
                "for item 'CA-PAYMENT' is empty; omit the key",
            ),
            (
                "sample_empty_premium_value",
                {**motor, "CA-M-PREMIUM": ""},
                "for item 'CA-M-PREMIUM' is empty; omit the key",
            ),
            (
                "sample_empty_alphanumeric_value",
                {**motor, "CA-M-MAKE": ""},
                "for item 'CA-M-MAKE' is empty; omit the key",
            ),
            (
                "sample_missing_request_id",
                {key: value for key, value in motor.items() if key != "CA-REQUEST-ID"},
                "does not supply required item 'CA-REQUEST-ID'",
            ),
            (
                "sample_missing_required_payment",
                {key: value for key, value in motor.items() if key != "CA-PAYMENT"},
                "does not supply required item(s) 'CA-PAYMENT'",
            ),
            (
                "sample_too_many_keys",
                {
                    **motor,
                    **{
                        f"CA-M-MAKE-{index}": "X"
                        for index in range(MAX_SAMPLE_KEYS + 1 - len(motor))
                    },
                },
                f"keys, above the {MAX_SAMPLE_KEYS} key limit",
            ),
            (
                "sample_deeply_nested",
                {"CA-REQUEST-ID": _nested(MAX_DOCUMENT_DEPTH)},
                f"above the {MAX_DOCUMENT_DEPTH} container limit",
            ),
        ]
        for case_name, document, fragment in rejected_samples:
            sample_name = _write_sample(tree, case_name, document)
            destination = _seeded_destination(tree, case_name)
            _run_case(
                results,
                out,
                quiet,
                case_name,
                lambda sample_name=sample_name,
                destination=destination,
                fragment=fragment: (
                    _assert_rejected(
                        tree,
                        [
                            "--field-map",
                            str(map_path),
                            "--sample",
                            str(tree.named(sample_name)),
                            "--output",
                            str(tree.handoff(destination)),
                        ],
                        EXIT_SAMPLE_REJECTED,
                        destination,
                        fragment,
                    )
                ),
            )

        rejected_payloads: list[tuple[str, bytes, str]] = [
            (
                "sample_duplicate_key",
                (
                    b'{"CA-REQUEST-ID": "01AMOT", "CA-PAYMENT": "000500", '
                    b'"CA-PAYMENT": "000600"}\n'
                ),
                "repeats key 'CA-PAYMENT'",
            ),
            (
                "sample_undecodable_bytes",
                b'{"CA-REQUEST-ID": "01AMOT", "CA-M-MAKE": "FOR\xffD"}\n',
                "is not valid UTF-8 text",
            ),
            (
                "sample_oversized",
                b'{"CA-REQUEST-ID": "01AMOT", "CA-M-MAKE": "'
                + b"A" * (MAX_SAMPLE_BYTES + 64)
                + b'"}\n',
                f"above the {MAX_SAMPLE_BYTES} byte limit",
            ),
            (
                "sample_nested_past_parser",
                b'{"CA-REQUEST-ID": '
                + b"[" * _PARSER_NESTING_PROBE
                + b"]" * _PARSER_NESTING_PROBE
                + b"}\n",
                "nests containers too deeply to parse",
            ),
        ]
        for case_name, payload, fragment in rejected_payloads:
            sample_name = _write_payload(tree, f"{case_name}.json", payload)
            destination = _seeded_destination(tree, case_name)
            _run_case(
                results,
                out,
                quiet,
                case_name,
                lambda sample_name=sample_name,
                destination=destination,
                fragment=fragment: (
                    _assert_rejected(
                        tree,
                        [
                            "--field-map",
                            str(map_path),
                            "--sample",
                            str(tree.named(sample_name)),
                            "--output",
                            str(tree.handoff(destination)),
                        ],
                        EXIT_SAMPLE_REJECTED,
                        destination,
                        fragment,
                    )
                ),
            )

        fifo_sample = _make_fifo(tree, "sample_fifo.json")
        fifo_destination = _seeded_destination(tree, "sample_not_regular_file")
        _run_case(
            results,
            out,
            quiet,
            "sample_not_regular_file",
            lambda: _assert_rejected(
                tree,
                [
                    "--field-map",
                    str(map_path),
                    "--sample",
                    str(tree.named(fifo_sample)),
                    "--output",
                    str(tree.handoff(fifo_destination)),
                ],
                EXIT_SAMPLE_REJECTED,
                fifo_destination,
                "is not a regular file",
            ),
        )

        blocked = _write_payload(tree, "blocked_output", b"NOT A DIRECTORY\n")
        _run_case(
            results,
            out,
            quiet,
            "output_directory_unusable",
            lambda: _assert_rejected(
                tree,
                [
                    "--field-map",
                    str(map_path),
                    "--sample",
                    str(MOTOR_SAMPLE_DEFINITION),
                    "--output",
                    str(tree.handoff(blocked, "record.rec")),
                ],
                EXIT_IO_ERROR,
                blocked,
                "cannot open directory 'blocked_output'",
            ),
        )
        _run_case(
            results,
            out,
            quiet,
            "output_root_outside_build_refused",
            lambda: _case_output_root_outside(map_path, tree),
        )
        _run_case(
            results,
            out,
            quiet,
            "output_root_symlink_refused",
            lambda: _case_output_root_symlink(map_path, tree),
        )
        _run_case(
            results,
            out,
            quiet,
            "output_escapes_root_refused",
            lambda: _case_output_escapes_root(map_path, tree),
        )
        _run_case(
            results,
            out,
            quiet,
            "output_into_base_refused",
            lambda: _case_output_into_base_refused(tree),
        )
        _run_case(
            results,
            out,
            quiet,
            "scratch_subtree_removed",
            lambda: _case_scratch_subtree_removed(tree),
        )
        _run_case(
            results,
            out,
            quiet,
            "run_directory_name_swap_refused",
            lambda: _case_name_swap_not_redirected(tree, map_path),
        )

        ran = [result.name for result in results]
        _run_case(
            results,
            out,
            quiet,
            "nullability_claim_matches_matrix",
            lambda: _case_nullability_claim(field_map, ran),
        )
    except BaseException:
        _discarded_scratch(scratch)
        raise

    _run_case(
        results,
        out,
        quiet,
        "self_test_scratch_removed",
        lambda: _case_scratch_removed(scratch),
    )

    passed = sum(1 for result in results if result.passed)
    failed = len(results) - passed
    print(
        f"self-test summary cases={len(results)} passed={passed} failed={failed}",
        file=out,
    )
    return EXIT_OK if failed == 0 else EXIT_SELF_TEST_FAILED


def build_arg_parser() -> argparse.ArgumentParser:
    """Return the non-interactive command line parser for this tool."""
    parser = _CommandLineParser(
        prog=_PROGRAM,
        description=(
            "Validate one GenApp Policy-Issue sample definition and write the\n"
            f"corresponding COMMAREA record of exactly {COMMAREA_RECORD_LENGTH} "
            "characters followed by one\n"
            "newline, or run the built-in case matrix with --self-test.\n"
            "\n"
            "Exit status: 0 success, 2 sample definition rejected, 3 field map\n"
            "invalid, 4 input failure, output refused or command line rejected,\n"
            "5 self-test case failure."
        ),
        epilog=(
            "The destination must resolve inside modernization/harness/build under the "
            "canonical repository directory holding this script, or inside "
            "--output-root; that root must itself already exist inside "
            "modernization/harness/build, so no path this tool writes leaves "
            "modernization, and the system temporary directory, an arbitrary temporary "
            "root and a directory whose trailing components merely spell "
            "modernization/harness/build are all refused. A destination resolving "
            "inside that repository must stay under "
            "modernization/harness/build under either root, and a destination "
            "resolving inside the repository's base directory is always refused. A "
            "symbolic link, a symbolic-link component of a root, an existing "
            "non-regular file and a canonical form outside the allowed root are "
            "refused before any directory is created. Validation itself opens the "
            "directory the write descends from, by descending one single component at "
            "a time and following no "
            "symbolic link at any level: from the filesystem root under the default "
            "root, and from the descriptor held on modernization/harness/build for a "
            "named root, so containment is established through held descriptors. The "
            "write descends from that descriptor "
            "alone, creating and opening each directory below it by single component, "
            "so a symbolic link is refused at every level and the directory is never "
            "resolved as a pathname again.\n"
            "A path this tool reads must sit inside modernization/extraction or "
            "modernization/harness/build under that same repository directory. Every "
            "path argument is text free of control characters, no symbolic-link "
            "component of one is followed, and each input is read from one descriptor "
            "opened with the leaf refused when it is a symbolic link, which must "
            "report a regular file reached by exactly one name on the device of the "
            "directory that authorised it.\n"
            "Every failure writes one control-free line to stderr and returns 2 for a "
            "rejected sample definition, 3 for an inconsistent field map, or 4 for an "
            "unreadable input, a refused output or a usage error.\n"
            "Decision rationale: modernization/docs/decision-log.md"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--sample",
        default=None,
        type=Path,
        metavar="PATH",
        help=(
            "sample definition JSON document to build the record from, holding at most "
            f"{MAX_SAMPLE_BYTES} bytes of UTF-8 text; it must sit inside an authorised "
            "read root"
        ),
    )
    parser.add_argument(
        "--field-map",
        default=None,
        type=Path,
        metavar="PATH",
        help=(
            "field map supplying every offset, length and kind, holding at most "
            f"{MAX_FIELD_MAP_BYTES} bytes of UTF-8 text; it must sit inside an "
            "authorised read root "
            "(default: copybook_field_map.yml beside this script)"
        ),
    )
    parser.add_argument(
        "--output",
        default=None,
        type=Path,
        metavar="PATH",
        help=(
            "destination path for the generated record; it must resolve inside the "
            "allowed output root, and its parent directories are created only after "
            "that check passes"
        ),
    )
    parser.add_argument(
        "--output-root",
        default=None,
        type=Path,
        metavar="PATH",
        help=(
            "existing directory the destination must resolve inside, replacing the "
            "default modernization/harness/build root; it must already exist inside "
            "that default root and carry no symbolic-link component, and no directory "
            "outside it is accepted"
        ),
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help=(
            "run the built-in case matrix against the field map, both sample "
            "definitions and the read-only copybook, then exit; accepts neither "
            "--sample nor --output, and works inside one private run directory below "
            "modernization/harness/build/builder-selftest that it creates, reads, "
            "writes and removes through the descriptor it holds on that directory, "
            "confirming that descriptor before and after every pathname it hands to a "
            "run under test, and removes before it returns"
        ),
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help=(
            "suppress the summary line written to stdout on success; with "
            "--self-test, print only the failing case lines and the summary"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Build one COMMAREA record, or run the self-test, and return the exit status.

    Every diagnostic reaches stderr as one line free of control characters, and the
    success summary reaches stdout the same way. A rejected command line is reported
    through the same single line, without a usage block, and returns the status a
    refused input or output returns, while ``--help`` prints the full help and exits
    with status 0. Every path this invocation reads is confined to the validated read
    roots and every path it writes to the validated generated-output root, whichever
    arguments it carries.
    """
    parser = build_arg_parser()
    try:
        args = parser.parse_args(argv)
        if args.self_test:
            if args.sample is not None or args.output is not None:
                parser.error("--self-test accepts neither --sample nor --output")
            return run_self_test(args.field_map, quiet=args.quiet)
        if args.sample is None or args.output is None:
            parser.error("--sample and --output are required unless --self-test is given")
        field_map = load_field_map(args.field_map)
        sample = load_sample(args.sample)
        routing = resolve_overlay(field_map, _sample_request_id(field_map, sample))
        values = validate_sample(field_map, sample, routing)
        record = render_record(field_map, routing, values)
        written = write_record(args.output, record, args.output_root)
    except BuildError as error:
        print(f"{_PROGRAM}: {_one_line(str(error))}", file=sys.stderr)
        return error.exit_status

    if not args.quiet:
        print(
            _one_line(
                f"built {written} request_id={routing.request_id} "
                f"overlay={routing.overlay} characters={len(record)} "
                f"bytes={len(record) + 1}"
            )
        )
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
