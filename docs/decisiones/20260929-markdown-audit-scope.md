# Decision: whole-repository Markdown audit

## Objective and scope

Replace the partial Markdown link scan with a reproducible inventory over all
maintained Markdown in the checkout. Check inline and reference links, local
paths, fragments, redirects, coverage and explicitly reported exclusions.

## Alternatives considered

- Extend the existing regular expression checks in each audit script. Rejected
  because it would leave multiple, divergent scopes and still miss fragments.
- Add a Markdown parser dependency. Rejected for this limited syntax audit to
  avoid a new runtime dependency; the standard-library scanner has regression
  tests for the syntax it supports.

## Impact, dependencies and compatibility

The new validator is Python 3.13 standard-library code. It does not change skill
invocation, Oracle/APEX routes, credentials, or application runtime. It makes CI
and pre-commit fail on local broken links, incomplete coverage, confirmed
external 404/410 responses, or external links that cannot be verified. That
network requirement may expose temporary connectivity restrictions as an
incomplete audit.

The audited scope includes all versioned Markdown plus non-ignored maintained
Markdown found in the checkout. It excludes Git metadata, Python environments,
caches, local `.upstreams` checkouts, and binary upstream snapshots under
`vendor/upstreams`; upstream validation remains governed by the upstream
registry and synchronization workflow.

## Validation and rollback

The test module covers root and non-`docs`/`skills` paths, local/root-relative
resolution, percent-encoding and query strings, inline/reference syntax, HTML
and heading anchors, code fences, broken fragments and incomplete coverage.
The shared CI runner and pre-commit hook call the same validator. Rollback is
to remove `scripts/audit_markdown_links.py` and its tests, remove its runner and
hook entries, and restore the former local-link check in `audit_quality_score.py`;
do not modify credentials or upstream snapshots during rollback.

## Current verification limits

This decision covers only Markdown-scope and link validation. It does not
approve the full skill inventory, dependency graph, routing, hierarchy,
installation compatibility, or functional regression audit; those remain
separate acceptance criteria for this work.

The frontmatter inventory currently shows a duplicate `order: 3.5` on
`apex-delivery-lifecycle-zaimella` and `apex-external-context-learn`. No
in-repository executable consumer was found in the first search; external skill
discovery/UI behavior is unverified, so the values are preserved pending that
compatibility check. In-repository installation searches copies/links every
directory containing `SKILL.md`; `.claude/settings.json` specifies alphabetical
organization, and no in-repository executable reader of `order` was found.
Tests and authoring guides do consume/assert selected order values. Values stay
unchanged because an external consumer may sort on them and no UI contract was
verified. The role count used in navigation is 1 entry coordinator,
7 workflow orchestrators (4 broad lifecycle/application flows and 3 focused
sub-workflows), and 23 specialist skills. `apex-api-client-safe` is marked
retired and remains present under its existing name and `.claude` command.
Direct edges in the dependent skills and the integration/dependency maps were
corrected: deployment uses the configured native route separately, data ETL no
longer depends on API sync, and test setup uses an existing configured target.
The legacy historical text inside the retired skill and broader cycle analysis
remain outside this correction and must not be treated as active capability.

The external link `https://claude.ai/code` is explicitly listed by the
[Anthropic Help Center as a universal link to the Claude Code new-session
composer](https://support.claude.com/en/articles/14898120-open-the-claude-mobile-app-with-a-link).
The direct route returned HTTP 200 in the final Markdown audit. The linked Help
Center article is independently visible in the web reader, while this audit
host's TLS certificate validation failed; that article URL is reported as
documented N/A, never as verified by the local checker.

GitHub API checks on 2026-09-30 confirmed the public repository
`diegodelacruz/apex.skills`, default branch `main`, and empty tag/release lists.
The `v1.0.0` compare/release examples in `docs/GITHUB-SETUP.md` therefore did
not identify an existing release. They were changed to explicit placeholders;
no release was created.
