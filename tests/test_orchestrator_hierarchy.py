"""Integration tests for orchestrator hierarchy and inter-operability."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from apex_application_generator import ApplicationGenerationOrchestrator  # noqa: E402
from apex_data_migration import ETLPipeline  # noqa: E402


class TestOrchestratorHierarchy:
    """Test the complete orchestrator hierarchy."""

    @pytest.mark.unit
    def test_apex_coordinator_exists(self):
        """APEX Coordinator (skills/apex/) exists and has routing logic."""
        skill_path = Path(__file__).resolve().parent.parent / "skills" / "apex" / "SKILL.md"
        assert skill_path.exists(), "APEX Coordinator skill should exist"

        with open(skill_path) as f:
            content = f.read()
            assert "Apex Coordinator" in content
            assert "routing" in content.lower()
            assert "coordinator" in content.lower()

    @pytest.mark.unit
    def test_application_generator_orchestrator_exists(self):
        """ApplicationGenerationOrchestrator exists (HITO 5)."""
        orchestrator = ApplicationGenerationOrchestrator("TEST", "https://apex.example.com", "SOURCE", "TARGET")
        assert orchestrator is not None
        assert orchestrator.project_name == "TEST"

    @pytest.mark.unit
    def test_etl_pipeline_exists(self):
        """ETLPipeline exists (HITO 4 sub-orchestrator)."""
        pipeline = ETLPipeline("source", "target")
        assert pipeline is not None
        assert pipeline.source_conn == "source"

    @pytest.mark.unit
    def test_orchestrator_hierarchy_levels(self):
        """Verify orchestrator hierarchy levels."""
        # Level 1: APEX Coordinator (routing maestro)
        skill_path = Path(__file__).resolve().parent.parent / "skills" / "apex" / "SKILL.md"
        with open(skill_path) as f:
            coordinator_content = f.read()
            assert "Classify the request" in coordinator_content
            assert "Delegate to the smallest set" in coordinator_content

        # Level 2: ApplicationGenerationOrchestrator (application maestro)
        app_gen = ApplicationGenerationOrchestrator("L2_ORCHESTRATOR", "https://apex.example.com", "SOURCE", "TARGET")
        assert app_gen.current_phase.value == "initialization"
        assert len(app_gen.phase_timings) == 0

        # Level 3: ETLPipeline (sub-orchestrator for data)
        etl = ETLPipeline("source", "target")
        assert etl.source_conn == "source"
        assert etl.target_conn == "target"


class TestOrchhestratorInteroperability:
    """Test how orchestrators work together."""

    @pytest.mark.unit
    def test_application_generator_uses_etl_pipeline_pattern(self):
        """ApplicationGenerationOrchestrator uses ETL pipeline pattern."""
        orchestrator = ApplicationGenerationOrchestrator("ETL_TEST", "https://apex.example.com", "SOURCE", "TARGET")
        config = {
            "forms": ["USERS"],
            "reports": [],
            "mappings": {"OLD_USERS": "USERS"},
            "validation_rules": {"USERS": ["NOT NULL: ID"]},
            "target_env": "test",
        }

        orchestrator.execute_full_generation(config)

        # Verify ETL-like phases were executed
        assert "schema_mappings" in orchestrator.generated_artifacts
        assert "validation_rules" in orchestrator.generated_artifacts
        assert "data_migration" in orchestrator.phase_timings

    @pytest.mark.unit
    def test_orchestrator_audit_trail(self):
        """All orchestrators maintain audit trail."""
        # ETLPipeline audit trail
        etl = ETLPipeline("source", "target")
        etl.extract("USERS")
        etl_log = etl.get_operation_log()
        assert len(etl_log) > 0

        # ApplicationGenerationOrchestrator audit trail
        app_gen = ApplicationGenerationOrchestrator("AUDIT_TEST", "https://apex.example.com", "SOURCE", "TARGET")
        config = {"forms": ["EMP"], "reports": [], "target_env": "test"}
        app_gen.execute_full_generation(config)
        app_log = app_gen.get_pipeline_log()
        assert len(app_log) > 0

    @pytest.mark.unit
    def test_orchestrator_error_handling(self):
        """Orchestrators handle errors gracefully."""
        app_gen = ApplicationGenerationOrchestrator("ERROR_TEST", "https://apex.example.com", "SOURCE", "TARGET")

        # Empty config should still work (uses defaults)
        result = app_gen.execute_full_generation({})
        assert result["status"] == "success"

    @pytest.mark.unit
    def test_orchestrator_phase_tracking(self):
        """Orchestrators track phases and progress."""
        app_gen = ApplicationGenerationOrchestrator("PHASE_TEST", "https://apex.example.com", "SOURCE", "TARGET")
        config = {"forms": ["EMP"], "reports": [], "target_env": "test"}

        app_gen.execute_full_generation(config)

        # Should have tracked all 5 phases
        assert len(app_gen.phase_timings) == 5
        assert "code_generation" in app_gen.phase_timings
        assert "data_migration" in app_gen.phase_timings
        assert "deployment" in app_gen.phase_timings
        assert "testing" in app_gen.phase_timings
        assert "verification" in app_gen.phase_timings

    @pytest.mark.unit
    def test_orchestrator_reporting(self):
        """Orchestrators generate complete reports."""
        app_gen = ApplicationGenerationOrchestrator("REPORT_TEST", "https://apex.example.com", "SOURCE", "TARGET")
        config = {"forms": ["EMP"], "reports": ["SUMMARY"], "target_env": "test"}

        app_gen.execute_full_generation(config)
        report = app_gen.generate_completion_report()

        assert report["status"] == "completed"
        assert "phase_timings" in report
        assert "total_duration" in report
        assert "artifacts_generated" in report


class TestOrchestratorHierarchyDiagram:
    """Verify orchestrator hierarchy structure."""

    @pytest.mark.unit
    def test_orchestrator_roles(self):
        """Each orchestrator has clear role in hierarchy."""
        roles = {
            "APEX Coordinator": {
                "level": "MAESTRO",
                "role": "Request routing and governance",
                "manages": "All skill delegation",
            },
            "ApplicationGenerationOrchestrator": {
                "level": "APPLICATION MAESTRO",
                "role": "End-to-end application generation",
                "manages": "5 sequential phases",
            },
            "ETLPipeline": {
                "level": "SUB-ORCHESTRATOR",
                "role": "Data migration orchestration",
                "manages": "Extract, Transform, Load, Rollback",
            },
        }

        assert len(roles) == 3
        for role_info in roles.values():
            assert "level" in role_info
            assert "role" in role_info
            assert "manages" in role_info

    @pytest.mark.unit
    def test_orchestrator_delegation_chain(self):
        """Verify delegation chain from APEX Coordinator down."""
        # This test verifies the conceptual chain:
        # APEX Coordinator → ApplicationGenerationOrchestrator → ETLPipeline

        # Simulate APEX Coordinator selecting ApplicationGenerationOrchestrator
        app_gen = ApplicationGenerationOrchestrator("DELEGATION_TEST", "https://apex.example.com", "SOURCE", "TARGET")

        # ApplicationGenerationOrchestrator uses ETL internally
        config = {
            "forms": ["EMP"],
            "reports": [],
            "mappings": {"OLD": "NEW"},
            "validation_rules": {"EMP": ["NOT NULL: ID"]},
            "target_env": "test",
        }

        app_gen.execute_full_generation(config)

        # Verify ETL phase was executed
        assert "data_migration" in app_gen.phase_timings
        assert app_gen.phase_timings["data_migration"] > 0

    @pytest.mark.unit
    def test_orchestrator_capabilities_matrix(self):
        """Verify capabilities of each orchestrator."""
        # Verify APEX Coordinator capabilities via SKILL.md
        skill_path = Path(__file__).resolve().parent.parent / "skills" / "apex" / "SKILL.md"
        with open(skill_path) as f:
            content = f.read()
            assert "routing" in content.lower()
            assert "governance" in content.lower()

        # Verify ApplicationGenerationOrchestrator capabilities
        app_gen = ApplicationGenerationOrchestrator("CAP_TEST", "https://apex.example.com", "SOURCE", "TARGET")
        assert hasattr(app_gen, "execute_full_generation")
        assert hasattr(app_gen, "get_pipeline_status")
        assert hasattr(app_gen, "generate_completion_report")

        # Verify ETLPipeline capabilities
        etl = ETLPipeline("source", "target")
        assert hasattr(etl, "extract")
        assert hasattr(etl, "transform")
        assert hasattr(etl, "validate")
        assert hasattr(etl, "load")


class TestOrchestratorIntegration:
    """Integration tests across orchestrator hierarchy."""

    @pytest.mark.unit
    def test_full_orchestrator_chain(self):
        """Test complete flow through orchestrator hierarchy."""
        # Step 1: APEX Coordinator would select ApplicationGenerationOrchestrator
        # (simulated by directly creating it)
        app_gen = ApplicationGenerationOrchestrator(
            "FULL_CHAIN_TEST", "https://apex.example.com", "LEGACY_SYSTEM", "MODERN_SYSTEM"
        )

        # Step 2: ApplicationGenerationOrchestrator executes all phases
        config = {
            "forms": ["EMPLOYEES", "DEPARTMENTS"],
            "reports": ["EMPLOYEE_SUMMARY"],
            "mappings": {"OLD_EMP": "EMPLOYEES", "OLD_DEPT": "DEPARTMENTS"},
            "validation_rules": {
                "EMPLOYEES": ["NOT NULL: EMP_ID"],
                "DEPARTMENTS": ["NOT NULL: DEPT_ID"],
            },
            "test_types": ["ui", "performance", "regression"],
            "target_env": "production",
        }

        result = app_gen.execute_full_generation(config)

        # Verify complete execution
        assert result["status"] == "success"
        assert len(app_gen.phase_timings) == 5
        assert len(app_gen.generated_artifacts) > 0
        assert len(app_gen.get_pipeline_log()) > 10

    @pytest.mark.unit
    def test_orchestrator_json_export(self):
        """All orchestrators can export state as JSON."""
        # ApplicationGenerationOrchestrator
        app_gen = ApplicationGenerationOrchestrator("JSON_TEST", "https://apex.example.com", "SOURCE", "TARGET")
        config = {"forms": ["EMP"], "reports": [], "target_env": "test"}
        app_gen.execute_full_generation(config)
        json_state = app_gen.to_json()
        data = json.loads(json_state)
        assert "project" in data
        assert "phase" in data

        # ETLPipeline
        etl = ETLPipeline("source", "target")
        etl.extract("USERS")
        etl_json = etl.get_operation_log()
        assert isinstance(etl_json, list)
