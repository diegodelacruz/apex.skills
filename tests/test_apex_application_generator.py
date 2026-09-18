"""Unit tests for apex_application_generator module."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from apex_application_generator import ApplicationGenerationOrchestrator, PipelinePhase  # noqa: E402


class TestPipelinePhase:
    """Test PipelinePhase enum."""

    @pytest.mark.unit
    def test_phase_values(self):
        """Test pipeline phase enum values."""
        assert PipelinePhase.INITIALIZATION.value == "initialization"
        assert PipelinePhase.CODE_GENERATION.value == "code_generation"
        assert PipelinePhase.DEPLOYMENT.value == "deployment"
        assert PipelinePhase.TESTING.value == "testing"
        assert PipelinePhase.COMPLETED.value == "completed"


class TestApplicationGenerationOrchestrator:
    """Test ApplicationGenerationOrchestrator class."""

    @pytest.mark.unit
    def test_create_orchestrator(self):
        """Create application generation orchestrator."""
        orchestrator = ApplicationGenerationOrchestrator(
            "TEST_PROJECT", "https://apex.example.com", "SOURCE_SCHEMA", "TARGET_SCHEMA"
        )
        assert orchestrator.project_name == "TEST_PROJECT"
        assert orchestrator.apex_instance == "https://apex.example.com"
        assert orchestrator.source_schema == "SOURCE_SCHEMA"
        assert orchestrator.target_schema == "TARGET_SCHEMA"

    @pytest.mark.unit
    def test_init_trims_trailing_slash(self):
        """Initialize trims trailing slash from APEX URL."""
        orchestrator = ApplicationGenerationOrchestrator(
            "TEST_PROJECT", "https://apex.example.com/", "SOURCE", "TARGET"
        )
        assert orchestrator.apex_instance == "https://apex.example.com"

    @pytest.mark.unit
    def test_initial_phase(self):
        """Orchestrator starts in initialization phase."""
        orchestrator = ApplicationGenerationOrchestrator("TEST_PROJECT", "https://apex.example.com", "SOURCE", "TARGET")
        assert orchestrator.current_phase == PipelinePhase.INITIALIZATION

    @pytest.mark.unit
    def test_verification_requires_started_pipeline(self):
        """Verification fails before mutating an unstarted pipeline."""
        orchestrator = ApplicationGenerationOrchestrator("TEST_PROJECT", "https://apex.example.com", "SOURCE", "TARGET")

        with pytest.raises(RuntimeError, match="Pipeline execution has not started"):
            orchestrator._execute_verification({})

        assert orchestrator.current_phase == PipelinePhase.INITIALIZATION
        assert orchestrator.pipeline_log == []

    @pytest.mark.unit
    def test_execute_full_generation(self):
        """Execute complete generation pipeline."""
        orchestrator = ApplicationGenerationOrchestrator("TEST_PROJECT", "https://apex.example.com", "SOURCE", "TARGET")
        config = {"forms": ["EMPLOYEES"], "reports": ["SUMMARY"], "target_env": "test"}

        result = orchestrator.execute_full_generation(config)

        assert result["status"] == "success"
        assert "total_duration" in result
        assert "phase_timings" in result

    @pytest.mark.unit
    def test_pipeline_phases_executed(self):
        """All pipeline phases are executed."""
        orchestrator = ApplicationGenerationOrchestrator("TEST_PROJECT", "https://apex.example.com", "SOURCE", "TARGET")
        config = {"forms": ["EMP"], "reports": ["REP"], "target_env": "test"}

        orchestrator.execute_full_generation(config)

        assert orchestrator.current_phase == PipelinePhase.COMPLETED
        assert orchestrator.phase_progress == 100

    @pytest.mark.unit
    def test_code_generation_phase(self):
        """Code generation phase generates artifacts."""
        orchestrator = ApplicationGenerationOrchestrator("TEST_PROJECT", "https://apex.example.com", "SOURCE", "TARGET")
        config = {
            "forms": ["EMPLOYEES", "DEPARTMENTS"],
            "reports": ["SUMMARY"],
            "target_env": "test",
        }

        orchestrator.execute_full_generation(config)

        assert len(orchestrator.generated_artifacts["forms"]) == 2
        assert len(orchestrator.generated_artifacts["reports"]) == 1
        assert "validations" in orchestrator.generated_artifacts

    @pytest.mark.unit
    def test_data_migration_phase(self):
        """Data migration phase creates mappings and validations."""
        orchestrator = ApplicationGenerationOrchestrator("TEST_PROJECT", "https://apex.example.com", "SOURCE", "TARGET")
        config = {
            "forms": ["EMP"],
            "reports": [],
            "mappings": {"OLD_TABLE": "NEW_TABLE"},
            "validation_rules": {"EMP": ["NOT NULL: ID"]},
            "target_env": "test",
        }

        orchestrator.execute_full_generation(config)

        assert "schema_mappings" in orchestrator.generated_artifacts
        assert "validation_rules" in orchestrator.generated_artifacts

    @pytest.mark.unit
    def test_deployment_phase(self):
        """Deployment phase creates rollback point."""
        orchestrator = ApplicationGenerationOrchestrator("TEST_PROJECT", "https://apex.example.com", "SOURCE", "TARGET")
        config = {"forms": ["EMP"], "reports": [], "target_env": "production"}

        orchestrator.execute_full_generation(config)

        assert "rollback_point" in orchestrator.generated_artifacts
        assert "deployment" in orchestrator.generated_artifacts
        assert orchestrator.generated_artifacts["deployment"]["environment"] == "production"

    @pytest.mark.unit
    def test_testing_phase(self):
        """Testing phase generates and runs tests."""
        orchestrator = ApplicationGenerationOrchestrator("TEST_PROJECT", "https://apex.example.com", "SOURCE", "TARGET")
        config = {
            "forms": ["EMP"],
            "reports": [],
            "test_types": ["ui", "performance"],
            "target_env": "test",
        }

        orchestrator.execute_full_generation(config)

        assert "test_results" in orchestrator.generated_artifacts
        assert "ui" in orchestrator.generated_artifacts["test_results"]
        assert "performance" in orchestrator.generated_artifacts["test_results"]

    @pytest.mark.unit
    def test_verification_phase(self):
        """Verification phase generates completion report."""
        orchestrator = ApplicationGenerationOrchestrator("TEST_PROJECT", "https://apex.example.com", "SOURCE", "TARGET")
        config = {"forms": ["EMP"], "reports": [], "target_env": "test"}

        orchestrator.execute_full_generation(config)

        assert "completion_report" in orchestrator.generated_artifacts
        assert orchestrator.generated_artifacts["completion_report"]["status"] == "success"

    @pytest.mark.unit
    def test_get_pipeline_status(self):
        """Get current pipeline status."""
        orchestrator = ApplicationGenerationOrchestrator("TEST_PROJECT", "https://apex.example.com", "SOURCE", "TARGET")
        config = {"forms": ["EMP"], "reports": [], "target_env": "test"}

        orchestrator.execute_full_generation(config)
        status = orchestrator.get_pipeline_status()

        assert "phase" in status
        assert status["phase"] == "completed"
        assert status["progress"] == 100

    @pytest.mark.unit
    def test_generate_completion_report(self):
        """Generate completion report."""
        orchestrator = ApplicationGenerationOrchestrator("TEST_PROJECT", "https://apex.example.com", "SOURCE", "TARGET")
        config = {"forms": ["EMP"], "reports": [], "target_env": "test"}

        orchestrator.execute_full_generation(config)
        report = orchestrator.generate_completion_report()

        assert report["status"] == "completed"
        assert "phase_timings" in report
        assert "total_duration" in report

    @pytest.mark.unit
    def test_phase_timings_recorded(self):
        """Phase execution timings are recorded."""
        orchestrator = ApplicationGenerationOrchestrator("TEST_PROJECT", "https://apex.example.com", "SOURCE", "TARGET")
        config = {"forms": ["EMP"], "reports": [], "target_env": "test"}

        orchestrator.execute_full_generation(config)

        assert "code_generation" in orchestrator.phase_timings
        assert "data_migration" in orchestrator.phase_timings
        assert "deployment" in orchestrator.phase_timings
        assert "testing" in orchestrator.phase_timings
        assert "verification" in orchestrator.phase_timings

    @pytest.mark.unit
    def test_get_pipeline_log(self):
        """Get pipeline execution log."""
        orchestrator = ApplicationGenerationOrchestrator("TEST_PROJECT", "https://apex.example.com", "SOURCE", "TARGET")
        config = {"forms": ["EMP"], "reports": [], "target_env": "test"}

        orchestrator.execute_full_generation(config)
        log = orchestrator.get_pipeline_log()

        assert len(log) > 0
        assert all("timestamp" in entry for entry in log)
        assert all("operation" in entry for entry in log)

    @pytest.mark.unit
    def test_to_json(self):
        """Export orchestrator state as JSON."""
        orchestrator = ApplicationGenerationOrchestrator("TEST_PROJECT", "https://apex.example.com", "SOURCE", "TARGET")
        config = {"forms": ["EMP"], "reports": [], "target_env": "test"}

        orchestrator.execute_full_generation(config)
        json_str = orchestrator.to_json()

        data = json.loads(json_str)
        assert data["project"] == "TEST_PROJECT"
        assert data["phase"] == "completed"

    @pytest.mark.unit
    def test_multiple_forms_and_reports(self):
        """Handle multiple forms and reports."""
        orchestrator = ApplicationGenerationOrchestrator(
            "LARGE_PROJECT", "https://apex.example.com", "SOURCE", "TARGET"
        )
        config = {
            "forms": ["USERS", "ROLES", "PERMISSIONS"],
            "reports": ["USER_SUMMARY", "ROLE_REPORT"],
            "target_env": "test",
        }

        result = orchestrator.execute_full_generation(config)

        assert result["status"] == "success"
        assert len(orchestrator.generated_artifacts["forms"]) == 3
        assert len(orchestrator.generated_artifacts["reports"]) == 2

    @pytest.mark.unit
    def test_regression_tests_included(self):
        """Regression tests included in testing phase."""
        orchestrator = ApplicationGenerationOrchestrator("TEST_PROJECT", "https://apex.example.com", "SOURCE", "TARGET")
        config = {
            "forms": ["EMP"],
            "reports": [],
            "test_types": ["ui", "performance", "regression"],
            "target_env": "test",
        }

        orchestrator.execute_full_generation(config)

        assert "regression" in orchestrator.generated_artifacts["test_results"]
        assert orchestrator.generated_artifacts["test_results"]["regression"]["baseline_match"]

    @pytest.mark.unit
    def test_development_environment_deployment(self):
        """Deploy to development environment."""
        orchestrator = ApplicationGenerationOrchestrator("TEST_PROJECT", "https://apex.example.com", "SOURCE", "TARGET")
        config = {"forms": ["EMP"], "reports": [], "target_env": "development"}

        orchestrator.execute_full_generation(config)

        assert orchestrator.generated_artifacts["deployment"]["environment"] == "development"

    @pytest.mark.unit
    def test_production_environment_deployment(self):
        """Deploy to production environment."""
        orchestrator = ApplicationGenerationOrchestrator("TEST_PROJECT", "https://apex.example.com", "SOURCE", "TARGET")
        config = {"forms": ["EMP"], "reports": [], "target_env": "production"}

        orchestrator.execute_full_generation(config)

        assert orchestrator.generated_artifacts["deployment"]["environment"] == "production"


class TestIntegration:
    """Integration tests for application generator."""

    @pytest.mark.unit
    def test_full_enterprise_application(self):
        """Test full enterprise application generation."""
        orchestrator = ApplicationGenerationOrchestrator(
            "ENTERPRISE_APP",
            "https://apex.example.com",
            "LEGACY_SYSTEM",
            "MODERN_SYSTEM",
        )
        config = {
            "forms": ["USERS", "PRODUCTS", "ORDERS", "INVOICES"],
            "reports": ["SALES_SUMMARY", "USER_ACTIVITY", "INVENTORY"],
            "mappings": {
                "OLD_USERS": "USERS",
                "OLD_PRODUCTS": "PRODUCTS",
                "OLD_ORDERS": "ORDERS",
            },
            "validation_rules": {
                "USERS": ["NOT NULL: USER_ID"],
                "PRODUCTS": ["NOT NULL: PRODUCT_ID"],
                "ORDERS": ["NOT NULL: ORDER_ID"],
            },
            "test_types": ["ui", "performance", "regression"],
            "target_env": "production",
        }

        result = orchestrator.execute_full_generation(config)

        assert result["status"] == "success"
        assert len(orchestrator.generated_artifacts["forms"]) == 4
        assert len(orchestrator.generated_artifacts["reports"]) == 3
        assert orchestrator.current_phase == PipelinePhase.COMPLETED

    @pytest.mark.unit
    def test_minimal_application(self):
        """Test minimal application generation."""
        orchestrator = ApplicationGenerationOrchestrator("MINIMAL_APP", "https://apex.example.com", "SOURCE", "TARGET")
        config = {"forms": ["ITEMS"], "reports": [], "target_env": "test"}

        result = orchestrator.execute_full_generation(config)

        assert result["status"] == "success"
        assert len(orchestrator.generated_artifacts["forms"]) == 1
        assert len(orchestrator.generated_artifacts["reports"]) == 0

    @pytest.mark.unit
    def test_pipeline_with_no_tests(self):
        """Execute pipeline without testing phase."""
        orchestrator = ApplicationGenerationOrchestrator("NO_TEST_APP", "https://apex.example.com", "SOURCE", "TARGET")
        config = {"forms": ["EMP"], "reports": [], "test_types": [], "target_env": "test"}

        result = orchestrator.execute_full_generation(config)

        assert result["status"] == "success"
        assert len(orchestrator.generated_artifacts["test_results"]) == 0
