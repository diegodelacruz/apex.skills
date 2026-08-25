# GitHub Configuration & Release Management

**Setup Date:** 2026-08-21
**Branch Protection:** Pending activation in GitHub repository settings
**Release Strategy:** Semantic Versioning

---

## 1. BRANCH PROTECTION SETUP

### Main Branch Rules

Required GitHub CLI configuration:

```bash
# Enable branch protection on main
gh repo rule create \
  --branch main \
  --require-status-checks \
  --require-code-review \
  --dismiss-stale-reviews \
  --require-merge-queue

# Require pull request reviews before merge
gh repo rule create \
  --branch main \
  --require-pull-request-reviews \
  --required-approving-review-count 1 \
  --require-review-from-code-owners

# Require branches to be up-to-date before merging
gh repo rule create \
  --branch main \
  --require-status-checks-to-pass
```

**Protection Rules:**
- ✅ Require PR reviews before merge (1 approval minimum)
- ✅ Require status checks passing (all tests, linting)
- ✅ Dismiss stale reviews when new commits pushed
- ✅ Require branches up-to-date before merge
- ✅ Require PR to target main (no direct commits)
- ✅ Include administrators (no bypasses)

### Feature Branch Rules

- ✅ Branch naming: `feature/*`, `fix/*`, `docs/*`, `refactor/*`
- ✅ Commit messages: Conventional commits format
- ✅ All commits signed with GPG (future requirement)

---

## 2. RELEASE MANAGEMENT

### Semantic Versioning

**Format:** `MAJOR.MINOR.PATCH`

- **MAJOR:** Breaking changes
- **MINOR:** New features (backward compatible)
- **PATCH:** Bug fixes (backward compatible)

**Examples:**
- `1.0.0` - Initial release
- `1.1.0` - New features added
- `1.1.1` - Bug fix
- `2.0.0` - Breaking changes

### Release Process

**Step 1: Prepare Release**
```bash
# Create release branch
git checkout -b release/v1.1.0 main

# Update version numbers (if applicable)
# Update CHANGELOG.md
git add CHANGELOG.md
git commit -m "chore: Prepare v1.1.0 release"
git push origin release/v1.1.0
```

**Step 2: Create Pull Request**
```bash
# Create PR for release
gh pr create \
  --title "chore: Release v1.1.0" \
  --body "Release notes: " \
  --draft
```

**Step 3: Verify**
- ✅ All tests passing
- ✅ All checks green
- ✅ Code review approved

**Step 4: Merge & Tag**
```bash
# Merge to main (via GitHub UI or gh pr merge)
gh pr merge --merge

# Create and push tag
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0
```

**Step 5: Create Release**
```bash
# Create GitHub release with notes
gh release create v1.1.0 \
  --title "v1.1.0 - New Features" \
  --notes-file CHANGELOG.md
```

### Release Notes Template

```markdown
## v1.1.0 - 2026-08-21

### Added
- New feature X
- Enhancement Y

### Fixed
- Bug fix Z

### Security
- Security patch A

### Breaking Changes
(if any)

### Contributors
- @contributor1
- @contributor2
```

---

## 3. COMMIT SIGNING (Optional policy decision)

### Setup GPG Key

```bash
# Generate GPG key (if not exists)
gpg --full-generate-key

# Add public key to GitHub
gh gpg-key add ~/.gnupg/public-key.asc

# Configure git to sign commits
git config --global user.signingKey [KEY_ID]
git config --global commit.gpgSign true
```

### Signed Commit

All commits will be signed with GPG (future requirement).

---

## 4. CI/CD PIPELINE (Versioned and active)

### GitHub Actions Workflow

```yaml
name: CI/CD

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
      - run: python scripts/security-audit.sh
      - run: bash scripts/validate-oracle-documentation.py
```

### Checks Required

- ✅ Tests passing (46/46)
- ✅ Security audit passing
- ✅ Type checking (mypy)
- ✅ Linting (pylint, flake8)
- ✅ Documentation present

---

## 5. CHANGELOG MANAGEMENT

### CHANGELOG.md Structure

```markdown
# Changelog

All notable changes documented here.
Format based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]
### Added
### Changed
### Fixed
### Security

## [1.0.0] - 2026-08-21
### Added
- Initial release

[Unreleased]: https://github.com/diegodelacruz/apex.skills/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/diegodelacruz/apex.skills/releases/tag/v1.0.0
```

---

## 6. QUICK SETUP SCRIPT

Run this script to enable all protections:

```bash
#!/bin/bash
# scripts/setup-github-protection.sh

REPO_OWNER="diegodelacruz"
REPO_NAME="apex.skills"

echo "Setting up GitHub branch protection..."

# Require pull request reviews
gh api repos/$REPO_OWNER/$REPO_NAME/branches/main/protection \
  --method PUT \
  -f required_pull_request_reviews='{
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "required_approving_review_count": 1
  }' \
  -f enforce_admins=true

echo "✅ Branch protection enabled"
echo "✅ PR reviews required (1 approval)"
echo "✅ Stale reviews dismissed"
```

---

## CURRENT GOVERNANCE STATUS

Versioned in this repository:
- CODEOWNERS defines repository ownership and review routing.
- Dependabot monitors Python and GitHub Actions dependencies.
- GitHub Actions CI bootstraps managed upstreams, runs tests, audit, formatting, type, security, secret, and whitespace checks.
- Pull requests use the repository template.

Still requires a repository administrator in GitHub:
- Protect main and require one CODEOWNER approval.
- Require the CI status checks before merge.
- Dismiss stale approvals and require branches to be up to date.
- Decide whether administrators are subject to the same rules.
- Decide and configure signed-commit enforcement.
- Create the first release tag and GitHub release.

## IMPLEMENTATION CHECKLIST

- [ ] Enable branch protection on main
- [ ] Require PR reviews (1 minimum)
- [ ] Require status checks passing
- [ ] Require branches up-to-date
- [ ] Create first release tag (v1.0.0)
- [ ] Setup CHANGELOG.md tracking
- [ ] Configure GitHub Actions (future)
- [ ] Enable commit signing (future)

---

**Next Steps:** Run setup script, then proceed to SPRINT 2 (Testing)
