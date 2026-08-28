#!/bin/bash
# ============================================================================
# security-audit.sh - Comprehensive Security Audit Script
# ============================================================================
# PURPOSE: Run all security checks and produce audit report
#
# USAGE:
#   bash scripts/security-audit.sh
#   bash scripts/security-audit.sh --verbose
#   bash scripts/security-audit.sh --report audit_report.txt
#
# CHECKS:
#   1. Secret scanning (detect-secrets)
#   2. Hardcoded credentials (grep patterns)
#   3. Bare exception blocks (Python files)
#   4. Security linting (Bandit)
#   5. Type checking (mypy)
#   6. Dependency audit (pip)
#   7. Git commit signing status
#   8. File permissions (for sensitive files)
#
# EXIT CODES:
#   0 = All checks passed
#   1 = One or more checks failed
# ============================================================================

set -o pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT" || exit 1
PATH="$REPO_ROOT/.venv/Scripts:$REPO_ROOT/.venv/bin:$PATH"
resolve_tool() {
	local tool="$1"
	if command -v "$tool" >/dev/null 2>&1; then
		command -v "$tool"
		return 0
	fi
	for candidate in ".venv/bin/$tool" ".venv/bin/$tool.exe" ".venv/Scripts/$tool" ".venv/Scripts/$tool.exe"; do
		if [ -x "$candidate" ]; then
			printf '%s\n' "$candidate"
			return 0
		fi
	done
	return 1
}

# Configuration
VERBOSE=${VERBOSE:-0}
REPORT_FILE=""
FAILED_CHECKS=0
TOTAL_CHECKS=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Helper Functions
# ============================================================================

log_info() {
	echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
	echo -e "${GREEN}[PASS]${NC} $1"
	((TOTAL_CHECKS++))
}

log_fail() {
	echo -e "${RED}[FAIL]${NC} $1"
	((TOTAL_CHECKS++))
	((FAILED_CHECKS++))
}

log_warn() {
	echo -e "${YELLOW}[WARN]${NC} $1"
}

check_command_exists() {
	if ! command -v "$1" &> /dev/null; then
		log_warn "$1 not found - skipping check"
		return 1
	fi
	return 0
}

# ============================================================================
# Security Checks
# ============================================================================

check_secrets() {
	log_info "Checking for hardcoded secrets..."

	local scanner
	if ! scanner="$(resolve_tool detect-secrets)"; then
		log_fail "detect-secrets is not installed"
		return
	fi

	if ! "$scanner" scan --baseline .secrets.baseline --all-files --force-use-all-plugins --exclude-files '(^|[\\/])(\.env|\.mypy_cache|\.pytest_cache|\.venv|\.upstreams|\.upstream-backups|upstreams\.lock\.json|htmlcov|\.secrets\.baseline)([\\/]|$)' >/dev/null 2>&1; then
		log_fail "detect-secrets scan failed"
		return
	fi

	if python -c 'import json; from pathlib import Path; raise SystemExit(0 if not json.loads(Path(".secrets.baseline").read_text(encoding="utf-8")).get("results") else 1)'; then
		log_success "No unapproved secrets detected"
	else
		log_fail "Possible secrets detected; review .secrets.baseline"
	fi
}

check_hardcoded_credentials() {
	log_info "Checking for common credential patterns..."

	local found=0 pattern
	local patterns=("password\\s*=\\s*['\"]" "api_key\\s*=\\s*['\"]" "secret\\s*=\\s*['\"]" "token\\s*=\\s*['\"]" "AWS_SECRET" "PRIVATE_KEY")
	for pattern in "${patterns[@]}"; do
		if git grep -I -n -i -E "$pattern" -- "*.py" "*.sql" "*.sh" ":!docs/**" ":!.upstreams/**" ":!.venv/**" ":!*.example" ":!.secrets.baseline" ":!scripts/security-audit.sh" >/dev/null 2>&1; then
			found=1
		fi
	done

	if [ "$found" -eq 0 ]; then log_success "No hardcoded credential patterns found"; else log_fail "Possible hardcoded credentials found"; fi
}
check_bare_exceptions() {
	log_info "Checking for bare exception blocks..."

	# Find bare except blocks in Python files
	if git grep -I -n -E "^[[:space:]]*except[[:space:]]*:" -- "*.py" ":!docs/**" ":!.upstreams/**" ":!.venv/**" >/dev/null 2>&1; then
		log_fail "Bare exception blocks found (should use specific exceptions)"
	else
		log_success "No bare exception blocks found"
	fi
}

check_security_linting() {
	log_info "Running Bandit security linting..."

	if ! check_command_exists "bandit"; then
		return
	fi

	if bandit -c .bandit.yaml -r scripts tests -q 2>/dev/null; then
		log_success "Bandit security scanning passed"
	else
		log_fail "Bandit found security issues"
	fi
}

check_type_checking() {
	log_info "Running mypy type checking..."

	if ! check_command_exists "mypy"; then
		log_warn "mypy not installed - install with 'pip install mypy'"
		return
	fi

	if mypy scripts/ --ignore-missing-imports 2>/dev/null | grep -q "error:"; then
		log_fail "Type checking failed (run 'mypy scripts/')"
	else
		log_success "Type checking passed"
	fi
}

check_dependencies() {
	log_info "Checking for outdated/vulnerable dependencies..."

	if ! check_command_exists "pip"; then
		return
	fi

	# Check for outdated packages
	outdated=$(pip list --outdated 2>/dev/null | wc -l)
	if [ "$outdated" -le 1 ]; then
		log_success "All dependencies are up-to-date"
	else
		log_warn "Found $((outdated - 1)) outdated packages (run 'pip list --outdated')"
	fi
}

check_git_status() {
	log_info "Checking git repository status..."

	if ! command -v "git" &> /dev/null; then
		log_warn "git not found"
		return
	fi

	# Check for uncommitted changes
	if [ -z "$(git status --porcelain)" ]; then
		log_success "Working tree is clean"
	else
		log_warn "Uncommitted changes present"
	fi

	# Check if on main branch (risky to develop on main)
	if [ "$(git rev-parse --abbrev-ref HEAD)" == "main" ]; then
		log_success "Current branch: $(git rev-parse --abbrev-ref HEAD)"
	fi
}

check_file_permissions() {
	log_info "Checking file permissions..."

	# Check if .env files have restrictive permissions
	if [ -f ".env" ] && [[ "$(uname -s)" != MINGW* && "$(uname -s)" != MSYS* && "$(uname -s)" != CYGWIN* ]]; then
		perms=$(stat -c %a .env 2>/dev/null)
		if [ "$perms" == "600" ]; then
			log_success ".env has secure permissions (600)"
		else
			log_fail ".env has insecure permissions ($perms) - should be 600"
		fi
	fi

	# Check if private keys have restrictive permissions
	if [ -f "$HOME/.ssh/id_rsa" ] && [[ "$(uname -s)" != MINGW* && "$(uname -s)" != MSYS* && "$(uname -s)" != CYGWIN* ]]; then
		perms=$(stat -c %a "$HOME/.ssh/id_rsa" 2>/dev/null)
		if [ "$perms" == "600" ]; then
			log_success "SSH key has secure permissions (600)"
		else
			log_fail "SSH key has insecure permissions ($perms) - should be 600"
		fi
	fi
}

check_documentation() {
	log_info "Checking documentation compliance..."

	if [ -f "docs/ORACLE-APEX-DOCUMENTATION-POLICY.md" ]; then
		log_success "Oracle/APEX documentation policy exists"
	else
		log_fail "Oracle/APEX documentation policy missing"
	fi

	if [ -f "docs/SECURITY-THREATS.md" ]; then
		log_success "Threat model documentation exists"
	else
		log_fail "Threat model documentation missing"
	fi
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
	echo "╔════════════════════════════════════════════════════════════════╗"
	echo "║          SECURITY AUDIT - apex.skills Repository              ║"
	echo "╚════════════════════════════════════════════════════════════════╝"
	echo ""

	# Parse arguments
	while [[ $# -gt 0 ]]; do
		case $1 in
			--verbose)
				VERBOSE=1
				shift
				;;
			--report)
				REPORT_FILE="$2"
				shift 2
				;;
			*)
				echo "Unknown option: $1"
				exit 1
				;;
		esac
	done

	# Run all checks
	echo "🔐 Running Security Audit Checks..."
	echo ""

	check_secrets
	check_hardcoded_credentials
	check_bare_exceptions
	check_security_linting
	check_type_checking
	check_dependencies
	check_git_status
	check_file_permissions
	check_documentation

	# Summary
	echo ""
	echo "╔════════════════════════════════════════════════════════════════╗"
	echo "║                      AUDIT SUMMARY                             ║"
	echo "╚════════════════════════════════════════════════════════════════╝"
	echo ""
	echo "Total Checks: $TOTAL_CHECKS"
	echo -e "Passed: ${GREEN}$((TOTAL_CHECKS - FAILED_CHECKS))${NC}"
	echo -e "Failed: ${RED}$FAILED_CHECKS${NC}"
	echo ""

	# Write report if requested
	if [ -n "$REPORT_FILE" ]; then
		{
			echo "Security Audit Report"
			echo "====================="
			echo "Date: $(date)"
			echo "Repository: $(pwd)"
			echo ""
			echo "Total Checks: $TOTAL_CHECKS"
			echo "Passed: $((TOTAL_CHECKS - FAILED_CHECKS))"
			echo "Failed: $FAILED_CHECKS"
			echo ""
			echo "Status: $([ $FAILED_CHECKS -eq 0 ] && echo 'PASSED' || echo 'FAILED')"
		} > "$REPORT_FILE"
		echo "Report written to: $REPORT_FILE"
	fi

	# Exit with appropriate code
	if [ $FAILED_CHECKS -eq 0 ]; then
		echo -e "${GREEN}✓ Security audit PASSED${NC}"
		return 0
	else
		echo -e "${RED}✗ Security audit FAILED${NC}"
		return 1
	fi
}

# Run main function
main "$@"
exit $?
