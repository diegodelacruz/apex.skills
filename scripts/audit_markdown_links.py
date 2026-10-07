#!/usr/bin/env python3
"""Audit Markdown coverage, local destinations, and fragments across the repository."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from os import walk
from pathlib import Path
from typing import TypedDict
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
EXCLUDED_DIRS = {".git", ".venv", ".upstreams", ".mypy_cache", ".pytest_cache", "htmlcov", "__pycache__"}
EXCLUDED_FILES = {
    "vendor/upstreams",  # Stored upstream archives are binary snapshots, not maintained Markdown.
    ".claude/worktrees",  # Nested managed checkouts are separate repositories, not this repo's maintained docs.
}
# This exact URL is a Claude Code universal link documented by Anthropic Help:
# https://support.claude.com/en/articles/14898120-open-the-claude-mobile-app-with-a-link
# The reviewed Help Center article is the source supporting that disposition.
# The current CI network returns HTTP 403 or a TLS inspection error for these
# endpoints. They are N/A for direct anonymous HTTP verification; a confirmed
# 404/410 still fails.
DOCUMENTED_EXTERNAL_NA = {
    "https://claude.ai/code": (
        "Anthropic documents this URL as a Claude Code universal link; "
        "anonymous CI HTTP access is blocked (403/TLS)."
    ),
    "https://support.claude.com/en/articles/14898120-open-the-claude-mobile-app-with-a-link": (
        "Official Anthropic Help Center article reviewed as source evidence; "
        "direct CI TLS validation fails with an expired certificate."
    ),
}
FENCE_START = re.compile(r"^ {0,3}(`{3,}|~{3,})")
INLINE = re.compile(r"!?\[[^\]]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)")
REFERENCE = re.compile(r"(?m)^\s{0,3}\[([^\]]+)\]:\s*<?([^\s>]+)>?")
REF_USE = re.compile(r"!?\[[^\]]*\]\[([^\]]*)\]")
SHORTCUT_REF = re.compile(r"(?<!!)(?<!\])\[([^\]]+)\](?![\[(:])")
AUTOLINK = re.compile(r"<(https?://[^ >]+)>", re.I)
HTML_ID = re.compile(r"\b(?:id|name)=[\"']([^\"']+)[\"']", re.I)
HEADING = re.compile(r"(?m)^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
SETEXT = re.compile(r"(?m)^(.+?)\n {0,3}(=+|-+)\s*$")


@dataclass(frozen=True)
class Link:
    source: Path
    line: int
    target: str


class AuditResult(TypedDict):
    expected: int
    tracked: int
    tracked_excluded: int
    covered: int
    untracked_included: int
    excluded_markdown: int
    excluded: list[str]
    links: int
    local_valid: int
    external_links: list[str]
    external_valid: list[str]
    external_broken: list[str]
    external_unverifiable: list[str]
    external_na: list[str]
    broken: list[str]
    coverage_gaps: list[str]
    passed: bool


def markdown_inventory() -> tuple[set[Path], set[Path]]:
    """Return expected filesystem Markdown and documented exclusions."""
    submodules = tracked_submodules()
    if submodules:
        roots = ", ".join(path.as_posix() for path in sorted(submodules))
        raise RuntimeError(
            "registered submodules need a nested Markdown audit from each submodule root "
            "before the parent audit can pass: " + roots
        )
    expected: set[Path] = set()
    excluded: set[Path] = set()
    for base, directories, files in walk(ROOT):
        current = Path(base)
        rel_dir = current.relative_to(ROOT)
        kept: list[str] = []
        for directory in directories:
            candidate = rel_dir / directory
            candidate_text = candidate.as_posix()
            if directory in EXCLUDED_DIRS or any(
                candidate_text == prefix or candidate_text.startswith(prefix + "/") for prefix in EXCLUDED_FILES
            ):
                excluded.add(candidate)
            else:
                kept.append(directory)
        directories[:] = kept
        for filename in files:
            path = current / filename
            if path.suffix.lower() in {".md", ".markdown"}:
                expected.add(path.relative_to(ROOT))
    tracked = {item for item in tracked_markdown() if not is_excluded(item)}
    missing = {ROOT / item for item in tracked if not (ROOT / item).is_file()}
    if missing:
        raise RuntimeError("tracked Markdown missing from checkout: " + ", ".join(map(str, sorted(missing))))
    # Filesystem scan includes untracked Markdown; versioned paths are independently reconciled above.
    return expected, excluded


def is_excluded(path: Path) -> bool:
    normalized = path.as_posix()
    return any(part in EXCLUDED_DIRS for part in path.parts) or any(
        normalized == prefix or normalized.startswith(prefix + "/") for prefix in EXCLUDED_FILES
    )


def tracked_markdown() -> set[Path]:
    git = shutil.which("git")
    if not git:
        raise RuntimeError("Git executable is required to reconcile versioned Markdown coverage")
    result = subprocess.run(
        [git, "ls-files", "-z", "--", "*.md", "*.markdown"], cwd=ROOT, check=True, capture_output=True
    )
    return {Path(item.decode("utf-8", errors="surrogateescape")) for item in result.stdout.split(b"\0") if item}


def tracked_submodules() -> list[Path]:
    """List registered submodule roots; nested repos require their own audit root."""
    if not (ROOT / ".git").exists():
        return []
    git = shutil.which("git")
    if not git:
        raise RuntimeError("Git executable is required to inspect submodule boundaries")
    result = subprocess.run([git, "ls-files", "--stage", "-z"], cwd=ROOT, check=True, capture_output=True)
    roots = []
    for entry in result.stdout.split(b"\0"):
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        if metadata.split(maxsplit=1)[0] == b"160000":
            roots.append(Path(raw_path.decode("utf-8", errors="surrogateescape")))
    return roots


def slug(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    text = re.sub(r"[^\w -]", "", text).strip().replace(" ", "-")
    return re.sub(r"-+", "-", text)


def extract_links(path: Path) -> list[Link]:
    text = path.read_text(encoding="utf-8", errors="replace")
    clean = strip_inline_code(strip_frontmatter(strip_fences(text)))
    refs = {key.casefold(): target for key, target in REFERENCE.findall(clean)}
    found: list[Link] = []
    for match in INLINE.finditer(clean):
        target = match.group(1).strip("<>")
        found.append(Link(path, clean.count("\n", 0, match.start()) + 1, target))
    for match in REF_USE.finditer(clean):
        key = (match.group(1) or "").strip().casefold()
        if not key:
            continue
        if key in refs:
            found.append(Link(path, clean.count("\n", 0, match.start()) + 1, refs[key]))
    for match in SHORTCUT_REF.finditer(clean):
        key = match.group(1).strip().casefold()
        if key in refs:
            found.append(Link(path, clean.count("\n", 0, match.start()) + 1, refs[key]))
    for match in AUTOLINK.finditer(clean):
        found.append(Link(path, clean.count("\n", 0, match.start()) + 1, match.group(1)))
    return sorted(found, key=lambda link: link.line)


def anchors(path: Path) -> set[str]:
    text = strip_fences(path.read_text(encoding="utf-8", errors="replace"))
    result = set(HTML_ID.findall(text))
    used: dict[str, int] = {}
    heading_matches = [(match.start(), match.group(2)) for match in HEADING.finditer(text)]
    heading_matches += [(match.start(), match.group(1)) for match in SETEXT.finditer(text)]
    for _, raw_heading in sorted(heading_matches):
        raw_heading = re.sub(r"!?\[([^\]]+)\]\([^)]*\)", r"\1", raw_heading)
        raw_heading = re.sub(r"`([^`]+)`", r"\1", raw_heading)
        base = slug(raw_heading)
        count = used.get(base, 0)
        result.add(base if count == 0 else f"{base}-{count}")
        used[base] = count + 1
    return result


def strip_fences(text: str) -> str:
    """Blank fenced code while preserving lines and links outside the fences."""
    output: list[str] = []
    active_char: str | None = None
    active_length = 0
    for line in text.splitlines(keepends=True):
        match = FENCE_START.match(line)
        if active_char is None:
            if match:
                fence = match.group(1)
                active_char, active_length = fence[0], len(fence)
                output.append("\n" if line.endswith(("\n", "\r")) else "")
            else:
                output.append(line)
            continue
        output.append("\n" if line.endswith(("\n", "\r")) else "")
        if match and match.group(1)[0] == active_char and len(match.group(1)) >= active_length:
            active_char = None
            active_length = 0
    return "".join(output)


def strip_frontmatter(text: str) -> str:
    """Remove YAML frontmatter from Markdown documents when present."""
    if not text.startswith("---\n"):
        return text
    closing = re.search(r"(?m)^---\s*$", text[4:])
    if not closing:
        return text
    end = 4 + closing.end()
    return "\n" * text[:end].count("\n") + text[end:]


def strip_inline_code(text: str) -> str:
    """Blank inline code spans so Markdown examples are not audited as links."""
    return re.sub(r"(?<!`)`+[^`\n]*`+(?!`)", lambda match: " " * len(match.group(0)), text)


def resolve(link: Link) -> tuple[str, str | None]:
    target = link.target.strip()
    parts = urlsplit(target)
    if parts.scheme or parts.netloc:
        return "external", None
    if target.startswith("mailto:"):
        return "external", None
    decoded = unquote(parts.path)
    if not decoded:
        destination = link.source
    elif decoded.startswith("/"):
        destination = ROOT / decoded.lstrip("/")
    else:
        destination = link.source.parent / decoded
    try:
        destination = destination.resolve(strict=True)
        destination.relative_to(ROOT.resolve())
    except (OSError, ValueError):
        return "broken", f"{link.source.relative_to(ROOT)}:{link.line} -> {target}"
    anchor_target = destination
    if destination.is_dir():
        anchor_target = next(
            (item for item in (destination / "README.md", destination / "index.md") if item.is_file()), destination
        )
    if (
        parts.fragment
        and anchor_target.is_file()
        and anchor_target.suffix.lower() in {".md", ".markdown", ".html", ".htm"}
    ):
        if unquote(parts.fragment) not in anchors(anchor_target):
            source = f"{link.source.relative_to(ROOT)}:{link.line}"
            fragment = unquote(parts.fragment)
            destination = anchor_target.relative_to(ROOT)
            return (
                "broken",
                f"{source} -> missing anchor #{fragment} in {destination}",
            )
    return "local", None


def verify_url(url: str) -> tuple[str, str]:
    """Check an external URL, following redirects and falling back from HEAD to GET."""
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        return "broken", "only HTTP and HTTPS links are supported"
    for method in ("HEAD", "GET"):
        request = Request(url, method=method, headers={"User-Agent": "apex-skills-markdown-audit/1.0"})
        try:
            with urlopen(request, timeout=12) as response:  # nosec B310: urlsplit above limits this to HTTP(S).
                detail = f"HTTP {response.status} -> {response.geturl()}"
                return ("valid", detail) if 200 <= response.status < 400 else ("broken", detail)
        except HTTPError as error:
            if method == "HEAD" and error.code in {405, 501}:
                continue
            if error.code in {403, 429} or error.code >= 500:
                return "unverifiable", f"HTTP {error.code}"
            return "broken", f"HTTP {error.code}"
        except (TimeoutError, URLError, OSError) as error:
            return "unverifiable", str(error)
    return "unverifiable", "HEAD and GET unsupported"


def audit(check_external: bool = True) -> AuditResult:
    expected, excluded = markdown_inventory()
    links = [link for relative in sorted(expected) for link in extract_links(ROOT / relative)]
    broken: list[str] = []
    external: list[str] = []
    local = 0
    external_results: dict[str, tuple[str, str]] = {}
    for link in links:
        kind, error = resolve(link)
        if kind == "broken" and error:
            broken.append(error)
        elif kind == "external":
            external.append(f"{link.source.relative_to(ROOT)}:{link.line} -> {link.target}")
            if check_external and link.target not in external_results:
                external_results[link.target] = verify_url(link.target)
        else:
            local += 1
    all_tracked = tracked_markdown()
    tracked = {item for item in all_tracked if not is_excluded(item)}
    on_disk = expected & tracked
    uncovered = tracked - on_disk
    excluded_markdown_count = sum(
        1
        for directory in excluded
        if directory.is_dir()
        for file in directory.rglob("*")
        if file.is_file() and file.suffix.lower() in {".md", ".markdown"}
    )
    broken_external = [f"{url}: {detail}" for url, (status, detail) in external_results.items() if status == "broken"]
    unverifiable = [
        f"{url}: {detail}" for url, (status, detail) in external_results.items() if status == "unverifiable"
    ]
    valid_external = [f"{url} -> {detail}" for url, (status, detail) in external_results.items() if status == "valid"]
    documented_na = [
        f"{url}: {DOCUMENTED_EXTERNAL_NA[url]} Observed: {detail}"
        for url, (status, detail) in external_results.items()
        if status == "unverifiable" and url in DOCUMENTED_EXTERNAL_NA
    ]
    unresolved_external = [
        item for item in unverifiable if not any(item.startswith(f"{url}:") for url in DOCUMENTED_EXTERNAL_NA)
    ]
    excluded_tracked = {item for item in all_tracked if is_excluded(item)}
    result: AuditResult = {
        "expected": len(expected),
        "tracked": len(tracked),
        "tracked_excluded": len(excluded_tracked),
        "covered": len(on_disk) + len(expected - tracked),
        "excluded_markdown": excluded_markdown_count,
        "untracked_included": len(expected - tracked),
        "excluded": sorted(map(str, excluded)),
        "links": len(links),
        "local_valid": local,
        "external_links": external,
        "external_valid": valid_external,
        "external_broken": broken_external,
        "external_unverifiable": unverifiable,
        "external_na": documented_na,
        "broken": broken,
        "coverage_gaps": sorted(map(str, uncovered)),
        "passed": not broken and not uncovered and not broken_external and not unresolved_external,
    }
    return result


def main() -> int:
    try:
        result = audit()
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"AUDIT_INCOMPLETE: {error}", file=sys.stderr)
        return 2
    incomplete = any(
        not any(item.startswith(f"{url}:") for url in DOCUMENTED_EXTERNAL_NA)
        for item in result["external_unverifiable"]
    )
    failed = bool(result["broken"] or result["external_broken"] or result["coverage_gaps"])
    status = "FAIL" if failed else "INCOMPLETE" if incomplete else "PASS_WITH_NA" if result["external_na"] else "PASS"
    summary_fields = (
        f"{key}={value}"
        for key, value in (
            ("expected", result["expected"]),
            ("covered", result["covered"]),
            ("tracked", result["tracked"]),
            ("tracked_excluded", result["tracked_excluded"]),
            ("untracked_included", result["untracked_included"]),
            ("excluded_markdown", result["excluded_markdown"]),
            ("excluded_roots", len(result["excluded"])),
            ("links", result["links"]),
            ("local_valid", result["local_valid"]),
            ("external", len(result["external_links"])),
            ("external_broken", len(result["external_broken"])),
            ("external_unverifiable", len(result["external_unverifiable"])),
            ("external_na", len(result["external_na"])),
            ("broken", len(result["broken"])),
            ("coverage_gaps", len(result["coverage_gaps"])),
        )
    )
    print(f"MARKDOWN_AUDIT_{status}: " + " ".join(summary_fields))
    for label in (
        "broken",
        "coverage_gaps",
        "external_valid",
        "external_broken",
        "external_unverifiable",
        "external_na",
        "excluded",
    ):
        for item in result[label]:
            print(f"{label}: {item}")
    return 0 if result["passed"] else 2 if incomplete and not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
