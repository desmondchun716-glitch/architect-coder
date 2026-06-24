from __future__ import annotations

import fnmatch
import hashlib
import json
import re
import shlex
import shutil
import sys
import ctypes
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


DEFAULT_FORBIDDEN = [
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "id_rsa",
    "id_ed25519",
    "secrets.*",
    "*credential*",
]

SHELL_COMPOUND_CONTROL = re.compile(r"(?:&&|\|\||\r|\n)")
SHELL_OPERATOR_TOKENS = {"&", "|", ";", "<", ">", "2>", "1>", ">>", "2>>", "2>&1"}


def load_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path).expanduser().resolve()
    try:
        data = json.loads(config_path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise ValueError(f"Configuration not found: {config_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {config_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Configuration root must be a JSON object")
    return data


def ensure_within(base: Path, candidate: Path) -> Path:
    base = base.expanduser().resolve()
    candidate = candidate.expanduser().resolve()
    try:
        candidate.relative_to(base)
    except ValueError as exc:
        raise ValueError(f"Path escapes allowed root: {candidate}") from exc
    return candidate


def forbidden_patterns(config: dict[str, Any] | None = None) -> list[str]:
    configured = ((config or {}).get("security") or {}).get("forbidden_paths", [])
    return [*DEFAULT_FORBIDDEN, *(str(item) for item in configured)]


def is_forbidden(path: Path, patterns: list[str]) -> bool:
    candidates = [path.name, path.as_posix()]
    return any(
        fnmatch.fnmatch(candidate.casefold(), pattern.casefold())
        for pattern in patterns
        for candidate in candidates
    )


def obsidian_roots(config: dict[str, Any]) -> tuple[dict[str, Any], Path, Path]:
    obsidian = config.get("obsidian")
    if not isinstance(obsidian, dict):
        raise ValueError("Missing 'obsidian' configuration object")
    if obsidian.get("enabled") is False:
        raise ValueError("Obsidian integration is disabled")

    raw_vault = obsidian.get("vault_path")
    raw_allowed = obsidian.get("allowed_root")
    if not raw_vault or not raw_allowed:
        raise ValueError("Obsidian requires vault_path and allowed_root")

    vault = Path(str(raw_vault)).expanduser().resolve()
    if not vault.is_dir():
        raise ValueError(f"Obsidian vault does not exist: {vault}")

    allowed_value = Path(str(raw_allowed)).expanduser()
    allowed = (
        allowed_value.resolve()
        if allowed_value.is_absolute()
        else (vault / allowed_value).resolve()
    )
    ensure_within(vault, allowed)
    if not allowed.is_dir():
        raise ValueError(f"Obsidian allowed_root does not exist: {allowed}")
    return obsidian, vault, allowed


def configured_note_dir(
    config: dict[str, Any], note_type: str, *, create: bool = False
) -> tuple[Path, Path]:
    obsidian, vault, allowed = obsidian_roots(config)
    key_and_default = {
        "worklog": ("worklog_dir", "worklogs"),
        "adr": ("adr_dir", "adr"),
        "acceptance": ("acceptance_dir", "acceptance"),
        "note": ("project_note_dir", "."),
    }
    if note_type not in key_and_default:
        raise ValueError(f"Unsupported note type: {note_type}")
    key, default = key_and_default[note_type]
    raw_dir = obsidian.get(key)
    if raw_dir:
        configured = Path(str(raw_dir)).expanduser()
        target_dir = (
            configured.resolve()
            if configured.is_absolute()
            else (vault / configured).resolve()
        )
    else:
        target_dir = (allowed / default).resolve()
    ensure_within(allowed, target_dir)
    if create:
        target_dir.mkdir(parents=True, exist_ok=True)
    return allowed, target_dir


def configured_obsidian_asset_path(
    config: dict[str, Any],
    *,
    config_key: str,
    default_relative_path: str,
    allowed_suffixes: set[str],
    create_parent: bool = False,
) -> tuple[Path, Path]:
    obsidian, vault, allowed = obsidian_roots(config)
    raw_path = obsidian.get(config_key, default_relative_path)
    candidate_value = Path(str(raw_path)).expanduser()
    target = (
        candidate_value.resolve()
        if candidate_value.is_absolute()
        else (allowed / candidate_value).resolve()
    )
    ensure_within(allowed, target)
    suffixes = {suffix.casefold() for suffix in allowed_suffixes}
    if target.suffix.casefold() not in suffixes:
        expected = ", ".join(sorted(allowed_suffixes))
        raise ValueError(f"{config_key} must end with one of: {expected}")
    if create_parent:
        target.parent.mkdir(parents=True, exist_ok=True)
    return allowed, target


def slugify(value: str) -> str:
    value = value.strip().casefold()
    value = re.sub(r"[^\w\u4e00-\u9fff]+", "-", value, flags=re.UNICODE)
    value = re.sub(r"-{2,}", "-", value).strip("-_")
    if not value or value in {".", ".."}:
        raise ValueError("Title does not produce a safe filename")
    return value[:96]


def target_note_path(
    config: dict[str, Any],
    note_type: str,
    title: str,
    *,
    create_dir: bool = False,
    unique: bool = False,
) -> tuple[Path, Path]:
    allowed, directory = configured_note_dir(config, note_type, create=create_dir)
    prefix = f"{datetime.now().date().isoformat()}-" if note_type in {
        "worklog",
        "acceptance",
    } else ""
    stem = f"{prefix}{slugify(title)}"
    candidate = ensure_within(allowed, directory / f"{stem}.md")
    if unique:
        number = 2
        while candidate.exists():
            candidate = ensure_within(allowed, directory / f"{stem}-{number}.md")
            number += 1
    return allowed, candidate


def read_input(
    path: str | Path,
    *,
    config: dict[str, Any] | None = None,
    reject_forbidden: bool = True,
) -> str:
    input_path = Path(path).expanduser().resolve()
    if reject_forbidden and is_forbidden(input_path, forbidden_patterns(config)):
        raise ValueError(f"Refusing to read forbidden input path: {input_path}")
    try:
        return input_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValueError(f"Input file not found: {input_path}") from exc


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_preview_contract(
    *,
    allowed: Path,
    target: Path,
    content: str,
    expected_relative_path: str,
    expected_sha256: str,
) -> str:
    relative_path = target.relative_to(allowed).as_posix()
    if relative_path != expected_relative_path:
        raise ValueError(
            "Preview target mismatch: "
            f"expected {expected_relative_path}, got {relative_path}"
        )
    actual_sha256 = sha256_text(content)
    if actual_sha256 != expected_sha256:
        raise ValueError(
            "Preview content hash mismatch: generated content changed since preview"
        )
    return actual_sha256


def prepare_command(command: str, *, allow_shell: bool = False) -> tuple[str | list[str], bool]:
    command = str(command).strip()
    if not command:
        raise ValueError("Command is empty")
    if allow_shell:
        return command, True
    if SHELL_COMPOUND_CONTROL.search(command):
        raise ValueError(
            "Command contains shell control characters; pass --allow-shell or set "
            "quality.allow_shell=true only after reviewing the command."
        )
    argv = split_command(command)
    if not argv:
        raise ValueError("Command is empty")
    if any(token in SHELL_OPERATOR_TOKENS for token in argv):
        raise ValueError(
            "Command contains shell control characters; pass --allow-shell or set "
            "quality.allow_shell=true only after reviewing the command."
        )
    resolved = shutil.which(argv[0])
    if resolved:
        argv[0] = resolved
    return argv, False


def split_command(command: str) -> list[str]:
    if sys.platform != "win32":
        return shlex.split(command)
    argc = ctypes.c_int()
    command_line_to_argv = ctypes.windll.shell32.CommandLineToArgvW
    command_line_to_argv.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_int)]
    command_line_to_argv.restype = ctypes.POINTER(ctypes.c_wchar_p)
    local_free = ctypes.windll.kernel32.LocalFree
    local_free.argtypes = [ctypes.c_void_p]
    local_free.restype = ctypes.c_void_p
    argv = command_line_to_argv(ctypes.c_wchar_p(command), ctypes.byref(argc))
    if not argv:
        raise ValueError("Unable to parse command line")
    try:
        return [argv[index] for index in range(argc.value)]
    finally:
        local_free(argv)


def note_project_name(config: dict[str, Any], note_type: str, target: Path) -> str:
    configured = config.get("project_name")
    if configured:
        return str(configured)
    if note_type in {"worklog", "adr", "acceptance"} and target.parent.parent != target.parent:
        return target.parent.parent.name
    return target.parent.name


def build_obsidian_note_content(
    *,
    config: dict[str, Any],
    note_type: str,
    title: str,
    body: str,
    target: Path,
    append_existing: bool = False,
    update_timestamp: str | None = None,
    source_repo: str = "",
    related_files: list[str] | None = None,
) -> tuple[str, str]:
    if note_type == "worklog" and append_existing:
        timestamp = update_timestamp or now_iso()
        return f"\n\n---\n\n## Update {timestamp}\n\n{body}\n", "append"
    if note_type == "note":
        return f"# {title}\n\n{body}\n", "create_unique"
    status = "Proposed" if note_type == "adr" else "draft"
    header = frontmatter(
        note_type=note_type,
        project=note_project_name(config, note_type, target),
        status=status,
        source_repo=source_repo,
        related_files=related_files,
    )
    return f"{header}\n\n# {title}\n\n{body}\n", "create_unique"


def build_architecture_index_base(*, config: dict[str, Any], allowed: Path) -> str:
    project = str(config.get("project_name") or allowed.name)
    _, vault, _ = obsidian_roots(config)
    allowed_folder = allowed.relative_to(vault).as_posix()
    md_filter = 'file.ext == "md"'
    architect_tag_filter = 'file.hasTag("architect-coder")'
    folder_filter = f"file.inFolder({json.dumps(allowed_folder, ensure_ascii=False)})"
    project_filter = f"project == {json.dumps(project, ensure_ascii=False)}"
    adr_filter = 'type == "adr"'
    acceptance_filter = 'type == "acceptance"'
    worklog_filter = 'type == "worklog"'
    lines = [
        "# Generated by architect-coder. Update through preview/write scripts.",
        "filters:",
        "  and:",
        f"    - {yaml_quote(md_filter)}",
        f"    - {yaml_quote(architect_tag_filter)}",
        f"    - {yaml_quote(folder_filter)}",
        "formulas:",
        "  days_since_update: 'if(updated, (today() - date(updated)).days, \"\")'",
        "  record_link: 'file.asLink(file.basename)'",
        "properties:",
        "  formula.record_link:",
        '    displayName: "Record"',
        "  type:",
        '    displayName: "Type"',
        "  status:",
        '    displayName: "Status"',
        "  project:",
        '    displayName: "Project"',
        "  updated:",
        '    displayName: "Updated"',
        "  source_repo:",
        '    displayName: "Source Repo"',
        "  related_files:",
        '    displayName: "Related Files"',
        "  decision_id:",
        '    displayName: "Decision ID"',
        "  decision_scope:",
        '    displayName: "Decision Scope"',
        "  reversibility:",
        '    displayName: "Reversibility"',
        "  risk_level:",
        '    displayName: "Risk Level"',
        "  governed_files:",
        '    displayName: "Governed Files"',
        "  verification_status:",
        '    displayName: "Verification Status"',
        "  supersedes:",
        '    displayName: "Supersedes"',
        "  superseded_by:",
        '    displayName: "Superseded By"',
        "  formula.days_since_update:",
        '    displayName: "Days Since Update"',
        "views:",
        "  - type: table",
        '    name: "Architecture Records"',
        "    order:",
        "      - formula.record_link",
        "      - type",
        "      - status",
        "      - project",
        "      - updated",
        "      - formula.days_since_update",
        "      - source_repo",
        "    groupBy:",
        "      property: type",
        "      direction: ASC",
        "  - type: table",
        '    name: "ADRs"',
        "    filters:",
        "      and:",
        f"        - {yaml_quote(project_filter)}",
        f"        - {yaml_quote(adr_filter)}",
        "    order:",
        "      - formula.record_link",
        "      - decision_id",
        "      - status",
        "      - decision_scope",
        "      - risk_level",
        "      - reversibility",
        "      - verification_status",
        "      - governed_files",
        "      - updated",
        "      - related_files",
        "  - type: table",
        '    name: "Acceptance"',
        "    filters:",
        "      and:",
        f"        - {yaml_quote(project_filter)}",
        f"        - {yaml_quote(acceptance_filter)}",
        "    order:",
        "      - formula.record_link",
        "      - status",
        "      - updated",
        "      - related_files",
        "  - type: table",
        '    name: "Worklogs"',
        "    filters:",
        "      and:",
        f"        - {yaml_quote(project_filter)}",
        f"        - {yaml_quote(worklog_filter)}",
        "    order:",
        "      - formula.record_link",
        "      - updated",
        "      - related_files",
    ]
    return "\n".join(lines) + "\n"


def yaml_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def frontmatter(
    *,
    note_type: str,
    project: str,
    status: str,
    source_repo: str = "",
    related_files: list[str] | None = None,
) -> str:
    today = datetime.now().date().isoformat()
    related = json.dumps(related_files or [], ensure_ascii=False)
    lines = [
        "---",
        f"type: {yaml_quote(note_type)}",
        f"project: {yaml_quote(project)}",
        f"status: {yaml_quote(status)}",
        f"created: {yaml_quote(today)}",
        f"updated: {yaml_quote(today)}",
        f"tags: [architect-coder, {note_type}]",
        f"source_repo: {yaml_quote(source_repo)}",
        f"related_files: {related}",
    ]
    if note_type == "adr":
        lines.extend(
            [
                f"decision_id: {yaml_quote('')}",
                f"decision_scope: {yaml_quote('')}",
                f"reversibility: {yaml_quote('')}",
                f"risk_level: {yaml_quote('')}",
                f"governed_files: {related}",
                "supersedes: []",
                f"superseded_by: {yaml_quote('')}",
                f"verification_status: {yaml_quote('unverified')}",
            ]
        )
    lines.append("---")
    return "\n".join(lines)


def run_cli(main: Callable[[], int]) -> int:
    try:
        return main()
    except (ValueError, OSError) as exc:
        print(
            json.dumps({"status": "failed", "error": str(exc)}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 2
