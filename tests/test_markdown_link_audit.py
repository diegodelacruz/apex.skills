"""Regression coverage for whole-repository Markdown link auditing."""

from pathlib import Path

import pytest

import scripts.audit_markdown_links as audit


def test_inline_reference_html_anchor_and_fences(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    target = tmp_path / "target file.md"
    target.write_text('# Heading\n<span id="html-anchor"></span>\n', encoding="utf-8")
    source.write_text(
        "[relative](target%20file.md#heading)\n"
        "[root](/target%20file.md#html-anchor)\n"
        "[reference][ref]\n[ref]: target%20file.md#heading\n"
        "[short-ref]\n[short-ref]: target%20file.md#heading\n"
        "```md\n[ignored](missing.md#bad)\n```\n"
        "[after fence](target%20file.md#heading)\n"
        "<https://example.com/path>\n",
        encoding="utf-8",
    )
    links = audit.extract_links(source)
    assert [item.target for item in links] == [
        "target%20file.md#heading",
        "/target%20file.md#html-anchor",
        "target%20file.md#heading",
        "target%20file.md#heading",
        "target%20file.md#heading",
        "https://example.com/path",
    ]
    assert "heading" in audit.anchors(target)
    assert "html-anchor" in audit.anchors(target)


def test_local_fragment_failure_is_reported(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    (tmp_path / "source.md").write_text("[bad](target.md#missing)\n", encoding="utf-8")
    (tmp_path / "target.md").write_text("# Existing\n", encoding="utf-8")
    result = audit.resolve(audit.Link(tmp_path / "source.md", 1, "target.md#missing"))
    assert result[0] == "broken"
    assert "missing anchor" in (result[1] or "")


def test_setext_heading_anchor_and_directory_readme_anchor(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    source = tmp_path / "source.md"
    source.write_text("# Source\n", encoding="utf-8")
    folder = tmp_path / "folder"
    folder.mkdir()
    (folder / "README.md").write_text("Underlined title\n===============\n", encoding="utf-8")
    result = audit.resolve(audit.Link(source, 1, "folder/#underlined-title"))
    assert result[0] == "local"


def test_missing_reference_text_frontmatter_and_task_lists_are_not_links(tmp_path: Path) -> None:
    source = tmp_path / "source.md"
    source.write_text(
        '---\ntags: ["tag-one", "tag-two"]\n---\n'
        "[ ] Task item\n[x] Completed task\n[missing][undefined]\n"
        "Inline example: `[fake](missing.md)`\n",
        encoding="utf-8",
    )
    assert audit.extract_links(source) == []


def test_root_relative_and_query_paths_resolve(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    (tmp_path / "source.md").write_text("", encoding="utf-8")
    (tmp_path / "target file.md").write_text("# Target\n", encoding="utf-8")
    assert audit.resolve(audit.Link(tmp_path / "source.md", 1, "/target%20file.md?view=1#target"))[0] == "local"


def test_coverage_gap_prevents_pass(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    monkeypatch.setattr(audit, "tracked_markdown", lambda: {Path("missing.md")})
    (tmp_path / "visible.md").write_text("# Visible\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="tracked Markdown missing"):
        audit.markdown_inventory()


def test_registered_submodule_requires_nested_audit(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    monkeypatch.setattr(audit, "tracked_submodules", lambda: [Path("vendor/example")])
    with pytest.raises(RuntimeError, match="nested Markdown audit"):
        audit.markdown_inventory()


def test_inventory_covers_root_and_paths_outside_docs_and_skills(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    files = {Path("README.md"), Path("control-proyecto/guide.md"), Path(".github/guide.md")}
    monkeypatch.setattr(audit, "tracked_markdown", lambda: files)
    for relative in files:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Maintained\n", encoding="utf-8")
    (tmp_path / ".venv" / "vendor.md").parent.mkdir()
    (tmp_path / ".venv" / "vendor.md").write_text("# Excluded\n", encoding="utf-8")
    expected, excluded = audit.markdown_inventory()
    assert expected == files
    assert Path(".venv") in excluded


def test_nested_managed_worktrees_are_excluded_from_markdown_scope() -> None:
    assert audit.is_excluded(Path(".claude/worktrees/feature/docs/README.md"))


def test_audit_returns_coverage_and_link_counts(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    source = Path("control-proyecto/guide.md")
    target = Path("README.md")
    (tmp_path / source).parent.mkdir(parents=True)
    (tmp_path / source).write_text("[home](/README.md)\n", encoding="utf-8")
    (tmp_path / target).write_text("# Home\n", encoding="utf-8")
    monkeypatch.setattr(audit, "tracked_markdown", lambda: {source, target})
    result = audit.audit(check_external=False)
    assert result["passed"] is True
    assert result["expected"] == result["covered"] == 2
    assert result["links"] == result["local_valid"] == 1


@pytest.mark.parametrize("source", [Path("README.md"), Path("control-proyecto/guide.md"), Path(".github/guide.md")])
def test_audit_fails_broken_links_in_root_and_outside_docs_skills(tmp_path: Path, monkeypatch, source: Path) -> None:
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    file_path = tmp_path / source
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("[broken](missing.md)\n", encoding="utf-8")
    monkeypatch.setattr(audit, "tracked_markdown", lambda: {source})
    result = audit.audit(check_external=False)
    assert result["passed"] is False
    assert len(result["broken"]) == 1


def test_unverifiable_external_url_is_incomplete(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    source = tmp_path / "README.md"
    source.write_text("[external](https://example.invalid)\n", encoding="utf-8")
    monkeypatch.setattr(audit, "tracked_markdown", lambda: {Path("README.md")})
    monkeypatch.setattr(audit, "verify_url", lambda _url: ("unverifiable", "HTTP 403"))
    result = audit.audit()
    assert result["passed"] is False
    assert result["external_unverifiable"] == ["https://example.invalid: HTTP 403"]


def test_documented_claude_code_link_is_na_not_valid(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    source = tmp_path / "README.md"
    source.write_text("[Claude Code](https://claude.ai/code)\n", encoding="utf-8")
    monkeypatch.setattr(audit, "tracked_markdown", lambda: {Path("README.md")})
    monkeypatch.setattr(audit, "verify_url", lambda _url: ("unverifiable", "HTTP 403"))
    result = audit.audit()
    assert result["passed"] is True
    assert result["external_valid"] == []
    assert result["external_unverifiable"] == ["https://claude.ai/code: HTTP 403"]
    assert len(result["external_na"]) == 1


def test_documented_external_na_does_not_hide_confirmed_404(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(audit, "ROOT", tmp_path)
    source = tmp_path / "README.md"
    source.write_text("[Claude Code](https://claude.ai/code)\n", encoding="utf-8")
    monkeypatch.setattr(audit, "tracked_markdown", lambda: {Path("README.md")})
    monkeypatch.setattr(audit, "verify_url", lambda _url: ("broken", "HTTP 404"))
    result = audit.audit()
    assert result["passed"] is False
    assert result["external_broken"] == ["https://claude.ai/code: HTTP 404"]
    assert result["external_na"] == []
