---
name: apex-qa-orchestrator-safe
description: Orchestrate complete QA workflow - static validation, automated testing, environment alignment
category: Apex Testing & QA
order: 6.5
tags:
  - orchestration
  - qa
  - testing
  - automation
  - validation
  - quality-assurance
access_level: read-write
cost: medium
created: 2026-09-17
status: development
---

# apex-qa-orchestrator-safe

**Sub-Coordinator Orchestrator:** Coordinate static QA → automated testing → environment validation.

Execute comprehensive QA workflows from static code validation through automated testing to environment readiness verification, with approval gates at each phase.

## Overview

Execute full QA pipeline safely:
- **Static QA** - Validate APEX export structure and integrity
- **Automated Testing** - UI, performance, and regression tests
- **Environment Validation** - Verify TEST/PROD alignment
- **Approval Gates** - Sign-off required at each phase
- **Ready for Release** - Comprehensive quality assurance

## Architecture

```
┌─────────────────────────────────────────────────┐
│ apex-qa-orchestrator-safe (Sub-Coordinator)    │
│                                                  │
│ ┌───────────────────────────────────────────┐  │
│ │ Phase 1: Static QA                        │  │
│ │ Delegate to: apex-export-qa-safe          │  │
│ │ - Validate ZIP structure                  │  │
│ │ - Check component integrity               │  │
│ │ - Detect syntax errors                    │  │
│ │ - Generate QA report                      │  │
│ └───────────────────────────────────────────┘  │
│         GATE: Static QA must pass ✓            │
│                      ↓                          │
│ ┌───────────────────────────────────────────┐  │
│ │ Phase 2: Automated Testing                │  │
│ │ Delegate to: apex-automated-testing-safe  │  │
│ │ - Generate UI tests (Selenium)            │  │
│ │ - Execute performance tests               │  │
│ │ - Run regression tests                    │  │
│ │ - Generate test results report            │  │
│ └───────────────────────────────────────────┘  │
│      GATE: All automated tests pass ✓          │
│                      ↓                          │
│ ┌───────────────────────────────────────────┐  │
│ │ Phase 3: Environment Validation           │  │
│ │ Delegate to: apex-environment-alignment-..│  │
│ │ - Verify TEST/PROD alignment              │  │
│ │ - Validate connectivity                   │  │
│ │ - Check credentials                       │  │
│ │ - Verify resource availability            │  │
│ └───────────────────────────────────────────┘  │
│        GATE: Environment ready ✓               │
│                      ↓                          │
│ ┌───────────────────────────────────────────┐  │
│ │ Outputs:                                   │  │
│ │ - QA report (static + automated)          │  │
│ │ - Test results (all passing)              │  │
│ │ - Environment validation (passed)         │  │
│ │ - RELEASE APPROVED ✓                      │  │
│ └───────────────────────────────────────────┘  │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Capabilities

### Comprehensive Quality Assurance

```python
# Initialize orchestrator
qa_orchestrator = QAOrchestrator(
    project_name='EMPLOYEE_APP',
    export_path='exports/app-2026-09-17.zip'
)

# Phase 1: Static QA
static_result = qa_orchestrator.execute_static_qa(
    export_file='exports/app-2026-09-17.zip',
    checks=['structure', 'integrity', 'syntax']
)
# Result: {'status': 'passed', 'issues': 0, 'report': '...'}

# GATE: Require static QA pass before proceeding
if not static_result['passed']:
    raise Exception("Static QA failed - see report")

# Phase 2: Automated Testing
test_result = qa_orchestrator.execute_automated_testing(
    test_types=['ui', 'performance', 'regression'],
    test_config={
        'ui': {'tests': 25, 'timeout': '10m'},
        'performance': {'throughput': '400 req/s'},
        'regression': {'baseline': 'v1.0'}
    }
)
# Result: {'status': 'passed', 'ui': {...}, 'performance': {...}}

# GATE: Require all tests pass
if not test_result['all_passed']:
    raise Exception("Automated tests failed - see results")

# Phase 3: Environment Validation
env_result = qa_orchestrator.validate_environments(
    environments=['test', 'production'],
    checks=['connectivity', 'credentials', 'alignment']
)
# Result: {'status': 'passed', 'test': {...}, 'prod': {...}}

# GATE: Require environment validation
if not env_result['ready_for_release']:
    raise Exception("Environment validation failed")

# Get comprehensive QA report
report = qa_orchestrator.generate_qa_report()
print(f"Release Status: {report['release_approved']}")  # True
```

## Workflow

### Phase 1: Static QA

Delegate to `apex-export-qa-safe`:

```
1. Validate APEX export:
   - ZIP file structure valid
   - All required files present
   - No corrupted components

2. Check component integrity:
   - Page definitions intact
   - SQL valid
   - PL/SQL compilable
   - No circular references

3. Detect syntax errors:
   - SQL syntax validation
   - PL/SQL compilation check
   - Component dependency check

4. Generate QA report:
   - Issues found: list with severity
   - Component summary
   - Pass/fail status
   - Recommendations
```

**Gate:** Static QA must show 0 critical issues before proceeding.

### Phase 2: Automated Testing

Delegate to `apex-automated-testing-safe`:

```
1. UI Testing (Selenium):
   - Generate test suite from components
   - Login flow validation
   - Navigation tests
   - Form submission tests
   - Report rendering tests
   - Result: X tests executed, Y passed, Z failed

2. Performance Testing:
   - Page load time benchmarks
   - Query execution analysis
   - Resource utilization
   - Throughput validation
   - Result: Avg response < 2s, Throughput > 400 req/s

3. Regression Testing:
   - Compare to baseline (previous version)
   - Detect behavioral changes
   - Validate against regression suite
   - Result: Baseline match: Yes, Deviations: 0

4. Generate test results:
   - Test summary report
   - Failed test details
   - Performance metrics
   - Coverage analysis
```

**Gate:** All tests must pass (UI 100%, Performance acceptable, Regression zero deviations) before proceeding.

### Phase 3: Environment Validation

Delegate to `apex-environment-alignment-complete`:

```
1. Verify TEST/PROD alignment:
   - Database versions match
   - Plugin versions match
   - Configuration alignment
   - Feature availability

2. Validate connectivity:
   - TEST environment: OK
   - PROD environment: OK
   - Network latency acceptable
   - No connection errors

3. Check credentials:
   - APEX user exists and active
   - Database user exists and active
   - API tokens valid
   - No expired credentials

4. Verify resource availability:
   - Storage space sufficient
   - Memory available
   - CPU resources adequate
   - No resource constraints

5. Generate environment report:
   - Alignment status: PASSED
   - Connectivity: OK
   - Credentials: Valid
   - Resources: Available
   - Release ready: YES
```

**Gate:** All environment checks must pass before release approval.

## Integration Points

| Phase | Orchestrates | Purpose |
|-------|--------------|---------|
| **Phase 1** | `apex-export-qa-safe` | Static validation |
| **Phase 2** | `apex-automated-testing-safe` | Automated testing |
| **Phase 3** | `apex-environment-alignment-complete` | Environment readiness |
| **Audit** | Git (.bitacora.json) | Complete QA trail |

## Features

### Safety

- **Approval gates** - Explicit sign-off at each phase
- **Comprehensive validation** - Static + automated + environment
- **Detailed reporting** - Issue tracking and traceability
- **No regressions** - Baseline comparison

### Automation

- **End-to-end orchestration** - All 3 phases coordinated
- **Test generation** - Automated test suite creation
- **Batch reporting** - Aggregated results
- **Error categorization** - Issues by severity

### Observability

- **Phase tracking** - Progress at each step
- **Detailed test results** - Pass/fail details
- **Performance metrics** - Timing and resource usage
- **Audit trail** - Complete QA history

## Configuration

Example QA workflow:

```yaml
orchestration:
  project_name: EMPLOYEE_APP
  export_file: exports/app-2026-09-17.zip

phase_1_static_qa:
  checks:
    - structure
    - integrity
    - syntax
    - dependencies

  critical_issues_allowed: 0
  warnings_allowed: 5

phase_2_automated_testing:
  ui_tests:
    enabled: true
    timeout: 10m
    expected_pass_rate: 100%

  performance_tests:
    enabled: true
    expected_response_time: "< 2s"
    expected_throughput: "> 400 req/s"

  regression_tests:
    enabled: true
    baseline: v1.0
    allowed_deviations: 0

phase_3_environment_validation:
  environments:
    - test
    - production

  checks:
    - connectivity
    - credentials
    - alignment
    - resources

  required_pass: true
```

## Error Handling

- **Phase 1 (Static QA) issues** → Report violations, require fixes, retry
- **Phase 2 (Testing) failures** → Report failed tests, investigate, retry
- **Phase 3 (Environment) issues** → Report misalignment, escalate to ops, retry

**Rollback:** If any gate fails, stop and escalate - do not proceed to release.

## Logging

Complete QA trail:

```
2026-09-17 10:00:00 - QA_ORCHESTRATOR_START - EMPLOYEE_APP
2026-09-17 10:05:00 - PHASE_1_START - Static QA

2026-09-17 10:10:00 - ZIP_VALIDATION - PASSED
2026-09-17 10:15:00 - STRUCTURE_CHECK - PASSED
2026-09-17 10:20:00 - SYNTAX_CHECK - PASSED
2026-09-17 10:25:00 - DEPENDENCY_CHECK - PASSED
2026-09-17 10:30:00 - PHASE_1_COMPLETE - Static QA: PASSED

2026-09-17 10:35:00 - GATE_1_CHECK - Static QA passed ✓
2026-09-17 10:40:00 - PHASE_2_START - Automated Testing

2026-09-17 10:45:00 - UI_TEST_GENERATION - 25 tests generated
2026-09-17 11:00:00 - UI_TESTS_EXECUTION - 25/25 passed
2026-09-17 11:05:00 - PERF_TEST_EXECUTION - Avg: 450ms, Throughput: 420 req/s
2026-09-17 11:10:00 - REGRESSION_TEST_EXECUTION - Baseline match: YES
2026-09-17 11:15:00 - PHASE_2_COMPLETE - Automated Testing: PASSED

2026-09-17 11:20:00 - GATE_2_CHECK - All tests passed ✓
2026-09-17 11:25:00 - PHASE_3_START - Environment Validation

2026-09-17 11:30:00 - TEST_ENV_CHECK - PASSED
2026-09-17 11:35:00 - PROD_ENV_CHECK - PASSED
2026-09-17 11:40:00 - CONNECTIVITY_CHECK - PASSED
2026-09-17 11:45:00 - CREDENTIALS_CHECK - PASSED
2026-09-17 11:50:00 - RESOURCES_CHECK - PASSED
2026-09-17 11:55:00 - PHASE_3_COMPLETE - Environment Validation: PASSED

2026-09-17 12:00:00 - GATE_3_CHECK - Environment ready ✓
2026-09-17 12:05:00 - QA_ORCHESTRATOR_COMPLETE - RELEASE APPROVED ✓
```

## Performance

Typical QA cycle timing:

| Phase | Duration (medium app) | Activity |
|-------|----------------------|----------|
| Static QA | 5-10 min | Export analysis |
| Automated Testing | 15-30 min | Test execution |
| Environment Validation | 5-10 min | Connectivity checks |
| **Total** | **25-50 min** | Full QA cycle |

## Status

🚧 **Development** - QA orchestration coordinator (20% complete)

---

**Last Updated:** 2026-09-17
**Version:** 0.1.0-dev
**Upstream Skills:**
- `apex-export-qa-safe` (static validation)
- `apex-automated-testing-safe` (automated testing)
- `apex-environment-alignment-complete` (environment validation)
