#!/bin/bash
# ============================================================================
# run-pylint.sh - Pylint Code Quality Checker
# ============================================================================
# PURPOSE: Run pylint on scripts and generate quality report
#
# USAGE:
#   bash scripts/run-pylint.sh
#   bash scripts/run-pylint.sh --verbose
#   bash scripts/run-pylint.sh --report quality_report.txt
#
# SCORING:
#   10.0 = Perfect (no issues)
#   9.0+ = Excellent
#   8.0+ = Good
#   7.0+ = Acceptable
#   <7.0 = Needs improvement
#
# EXIT CODES:
#   0 = Score >= 9.0 (PASS)
#   1 = Score < 9.0 (FAIL)
# ============================================================================

set -o pipefail

# Configuration
VERBOSE=${VERBOSE:-0}
REPORT_FILE=""
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
	echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
	echo -e "${GREEN}[PASS]${NC} $1"
}

log_fail() {
	echo -e "${RED}[FAIL]${NC} $1"
}

log_warn() {
	echo -e "${YELLOW}[WARN]${NC} $1"
}

check_pylint_installed() {
	if ! command -v pylint &> /dev/null; then
		log_warn "pylint not installed - installing..."
		pip install pylint -q
	fi
}

run_pylint_check() {
	local filepath="$1"
	local filename=$(basename "$filepath")

	if [ "$VERBOSE" -eq 1 ]; then
		log_info "Checking $filename..."
	fi

	# Run pylint with JSON output for parsing
	pylint_output=$(pylint "$filepath" --disable=all --enable=E,F,W --fail-under=9 2>&1)
	local exit_code=$?

	if [ $exit_code -eq 0 ]; then
		log_success "$filename"
		return 0
	else
		log_fail "$filename"
		if [ "$VERBOSE" -eq 1 ]; then
			echo "$pylint_output" | grep -E "^.*:[0-9]+:" | head -5
		fi
		return 1
	fi
}

main() {
	echo "╔════════════════════════════════════════════════════════════════╗"
	echo "║                  PYLINT CODE QUALITY CHECKER                   ║"
	echo "╚════════════════════════════════════════════════════════════════╝"
	echo ""
	echo "Python Version: $PYTHON_VERSION"
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

	# Check if pylint is installed
	check_pylint_installed

	log_info "Running pylint checks on scripts..."
	echo ""

	# Track results
	passed=0
	failed=0

	# Check all Python scripts (excluding tests)
	for script in scripts/*.py; do
		if [ -f "$script" ] && [[ ! "$script" == *"test_"* ]]; then
			if run_pylint_check "$script"; then
				((passed++))
			else
				((failed++))
			fi
		fi
	done

	echo ""
	echo "╔════════════════════════════════════════════════════════════════╗"
	echo "║                    PYLINT SUMMARY                              ║"
	echo "╚════════════════════════════════════════════════════════════════╝"
	echo ""
	echo -e "Passed: ${GREEN}$passed${NC}"
	echo -e "Failed: ${RED}$failed${NC}"
	echo ""

	# Calculate overall score
	total=$((passed + failed))
	if [ $total -gt 0 ]; then
		score=$(echo "scale=2; ($passed / $total) * 10" | bc)
	else
		score=0
	fi

	echo "Overall Quality Score: $score / 10.0"
	echo ""

	if (( $(echo "$score >= 9.0" | bc -l) )); then
		log_success "Code quality EXCELLENT"
		exit_code=0
	elif (( $(echo "$score >= 8.0" | bc -l) )); then
		log_success "Code quality GOOD"
		exit_code=0
	else
		log_fail "Code quality needs improvement"
		exit_code=1
	fi

	# Write report if requested
	if [ -n "$REPORT_FILE" ]; then
		{
			echo "Pylint Code Quality Report"
			echo "=========================="
			echo "Date: $(date)"
			echo "Python: $PYTHON_VERSION"
			echo ""
			echo "Results:"
			echo "  Passed: $passed"
			echo "  Failed: $failed"
			echo "  Total:  $total"
			echo ""
			echo "Score: $score / 10.0"
			echo "Status: $([ $exit_code -eq 0 ] && echo 'PASS' || echo 'FAIL')"
		} > "$REPORT_FILE"
		log_info "Report written to: $REPORT_FILE"
	fi

	echo ""
	return $exit_code
}

# Run main function
main "$@"
exit $?
