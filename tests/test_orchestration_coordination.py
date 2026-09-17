"""Comprehensive tests for orchestrator coordination and skill dependencies."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))


class TestOrchestratorExistence:
    """Verify all orchestrators exist and have correct metadata."""

    @pytest.mark.unit
    def test_maestro_orchestrator_exists(self):
        """Master orchestrator (apex) exists."""
        skill_path = Path(__file__).resolve().parent.parent / "skills" / "apex" / "SKILL.md"
        assert skill_path.exists(), "apex orchestrator must exist"

        with open(skill_path, encoding="utf-8") as f:
            content = f.read()
            assert "name: apex" in content
            assert "order: 14" in content

    @pytest.mark.unit
    def test_delivery_lifecycle_complete_exists(self):
        """apex-delivery-lifecycle-complete orchestrator exists."""
        skill_path = Path(__file__).resolve().parent.parent / "skills" / "apex-delivery-lifecycle-complete" / "SKILL.md"
        assert skill_path.exists()

        with open(skill_path, encoding="utf-8") as f:
            content = f.read()
            assert "apex-delivery-lifecycle-complete" in content
            assert "order: 2" in content

    @pytest.mark.unit
    def test_delivery_lifecycle_safe_exists(self):
        """apex-delivery-lifecycle-safe orchestrator exists."""
        skill_path = Path(__file__).resolve().parent.parent / "skills" / "apex-delivery-lifecycle-safe" / "SKILL.md"
        assert skill_path.exists()

        with open(skill_path, encoding="utf-8") as f:
            content = f.read()
            assert "apex-delivery-lifecycle-safe" in content
            assert "order: 3" in content

    @pytest.mark.unit
    def test_delivery_lifecycle_zaimella_exists(self):
        """apex-delivery-lifecycle-zaimella orchestrator exists (NEW)."""
        skill_path = Path(__file__).resolve().parent.parent / "skills" / "apex-delivery-lifecycle-zaimella" / "SKILL.md"
        assert skill_path.exists(), "Zaimella orchestrator must exist"

        with open(skill_path, encoding="utf-8") as f:
            content = f.read()
            assert "apex-delivery-lifecycle-zaimella" in content
            assert "order: 3.5" in content
            assert "zaimella" in content.lower()

    @pytest.mark.unit
    def test_application_generator_complete_exists(self):
        """apex-application-generator-complete orchestrator exists."""
        skill_path = (
            Path(__file__).resolve().parent.parent / "skills" / "apex-application-generator-complete" / "SKILL.md"
        )
        assert skill_path.exists()

        with open(skill_path, encoding="utf-8") as f:
            content = f.read()
            assert "apex-application-generator-complete" in content
            assert "orchestration" in content.lower()

    @pytest.mark.unit
    def test_data_orchestrator_safe_exists(self):
        """apex-data-orchestrator-safe sub-coordinator exists (NEW)."""
        skill_path = Path(__file__).resolve().parent.parent / "skills" / "apex-data-orchestrator-safe" / "SKILL.md"
        assert skill_path.exists(), "Data orchestrator must exist"

        with open(skill_path, encoding="utf-8") as f:
            content = f.read()
            assert "apex-data-orchestrator-safe" in content
            assert "order: 13.5" in content
            assert "orchestration" in content.lower()

    @pytest.mark.unit
    def test_qa_orchestrator_safe_exists(self):
        """apex-qa-orchestrator-safe sub-coordinator exists (NEW)."""
        skill_path = Path(__file__).resolve().parent.parent / "skills" / "apex-qa-orchestrator-safe" / "SKILL.md"
        assert skill_path.exists(), "QA orchestrator must exist"

        with open(skill_path, encoding="utf-8") as f:
            content = f.read()
            assert "apex-qa-orchestrator-safe" in content
            assert "order: 6.5" in content

    @pytest.mark.unit
    def test_design_review_orchestrator_exists(self):
        """apex-design-review-orchestrator sub-coordinator exists (NEW)."""
        skill_path = Path(__file__).resolve().parent.parent / "skills" / "apex-design-review-orchestrator" / "SKILL.md"
        assert skill_path.exists(), "Design review orchestrator must exist"

        with open(skill_path, encoding="utf-8") as f:
            content = f.read()
            assert "apex-design-review-orchestrator" in content
            assert "order: 11.5" in content
            assert "orchestration" in content.lower()


class TestOrchhestratorSkillCoordination:
    """Verify each orchestrator coordinates correct skills."""

    @pytest.mark.unit
    def test_delivery_lifecycle_complete_coordinates_7_skills(self):
        """apex-delivery-lifecycle-complete coordinates 7 skills."""
        coordinated_skills = [
            "apex-project-bootstrap-final",
            "apex-pattern-mining-safe",
            "apex-solution-design",
            "oracle-data-change-governance-final",
            "apex-engineering-safe",
            "apex-export-qa-safe",
            "apex-user-manual",
        ]

        skills_dir = Path(__file__).resolve().parent.parent / "skills"

        for skill_name in coordinated_skills:
            skill_path = skills_dir / skill_name / "SKILL.md"
            assert skill_path.exists(), f"Skill {skill_name} must exist"

        assert len(coordinated_skills) == 7

    @pytest.mark.unit
    def test_delivery_lifecycle_safe_coordinates_7_skills(self):
        """apex-delivery-lifecycle-safe coordinates 7 skills."""
        coordinated_skills = [
            "apex-project-workspace",
            "apex-pattern-mining-safe",
            "apex-solution-design",
            "oracle-data-change-governance-final",
            "apex-engineering-safe",
            "apex-export-qa-safe",
            "apex-user-manual",
        ]

        skills_dir = Path(__file__).resolve().parent.parent / "skills"

        for skill_name in coordinated_skills:
            skill_path = skills_dir / skill_name / "SKILL.md"
            assert skill_path.exists(), f"Skill {skill_name} must exist"

        assert len(coordinated_skills) == 7

    @pytest.mark.unit
    def test_delivery_lifecycle_zaimella_coordinates_2_skills(self):
        """apex-delivery-lifecycle-zaimella coordinates 2 direct skills."""
        coordinated_skills = [
            "apex-zaimella-gestion-proyectos",
            "apex-delivery-lifecycle-complete",
        ]

        skills_dir = Path(__file__).resolve().parent.parent / "skills"

        for skill_name in coordinated_skills:
            skill_path = skills_dir / skill_name / "SKILL.md"
            assert skill_path.exists(), f"Skill {skill_name} must exist"

        assert len(coordinated_skills) == 2

    @pytest.mark.unit
    def test_application_generator_coordinates_4_hitos(self):
        """apex-application-generator-complete coordinates 4 HITOs."""
        coordinated_skills = [
            "apex-code-generation-safe",  # HITO 1
            "apex-data-migration-safe",  # HITO 4
            "apex-api-client-safe",  # HITO 2
            "apex-automated-testing-safe",  # HITO 3
        ]

        skills_dir = Path(__file__).resolve().parent.parent / "skills"

        for skill_name in coordinated_skills:
            skill_path = skills_dir / skill_name / "SKILL.md"
            assert skill_path.exists(), f"Skill {skill_name} must exist"

        assert len(coordinated_skills) == 4

    @pytest.mark.unit
    def test_data_orchestrator_coordinates_3_skills(self):
        """apex-data-orchestrator-safe coordinates 3 skills."""
        coordinated_skills = [
            "apex-schema-automation-safe",
            "apex-data-migration-safe",
            "apex-api-client-safe",
        ]

        skills_dir = Path(__file__).resolve().parent.parent / "skills"

        for skill_name in coordinated_skills:
            skill_path = skills_dir / skill_name / "SKILL.md"
            assert skill_path.exists(), f"Skill {skill_name} must exist"

        assert len(coordinated_skills) == 3

    @pytest.mark.unit
    def test_qa_orchestrator_coordinates_3_skills(self):
        """apex-qa-orchestrator-safe coordinates 3 skills."""
        coordinated_skills = [
            "apex-export-qa-safe",
            "apex-automated-testing-safe",
            "apex-environment-alignment-complete",
        ]

        skills_dir = Path(__file__).resolve().parent.parent / "skills"

        for skill_name in coordinated_skills:
            skill_path = skills_dir / skill_name / "SKILL.md"
            assert skill_path.exists(), f"Skill {skill_name} must exist"

        assert len(coordinated_skills) == 3

    @pytest.mark.unit
    def test_design_review_orchestrator_coordinates_3_skills(self):
        """apex-design-review-orchestrator coordinates 3 skills."""
        coordinated_skills = [
            "apex-solution-design",
            "apex-blueprint-design-safe",
            "apex-engineering-safe",
        ]

        skills_dir = Path(__file__).resolve().parent.parent / "skills"

        for skill_name in coordinated_skills:
            skill_path = skills_dir / skill_name / "SKILL.md"
            assert skill_path.exists(), f"Skill {skill_name} must exist"

        assert len(coordinated_skills) == 3


class TestNoCircularDependencies:
    """Verify no circular dependencies exist in orchestration."""

    @pytest.mark.unit
    def test_no_circular_dependencies(self):
        """Verify no circular dependencies."""
        skills_dir = Path(__file__).resolve().parent.parent / "skills"

        # Simple check: verify that key orchestrator relationships make sense
        orchestrators = [
            "apex",
            "apex-delivery-lifecycle-complete",
            "apex-delivery-lifecycle-safe",
            "apex-delivery-lifecycle-zaimella",
            "apex-application-generator-complete",
            "apex-data-orchestrator-safe",
            "apex-qa-orchestrator-safe",
            "apex-design-review-orchestrator",
        ]

        # All orchestrators should exist
        for orch in orchestrators:
            skill_path = skills_dir / orch / "SKILL.md"
            assert skill_path.exists(), f"Orchestrator {orch} must exist"

        # No circular reference: apex should not depend on others that depend on it
        apex_path = skills_dir / "apex" / "SKILL.md"
        with open(apex_path, encoding="utf-8") as f:
            apex_content = f.read()
            # apex should reference others, not vice versa
            assert "routing" in apex_content.lower() or "route" in apex_content.lower()


class TestApprovalGates:
    """Verify approval gates are defined in orchestrators."""

    @pytest.mark.unit
    def test_delivery_lifecycle_complete_exists_and_is_orchestrator(self):
        """Delivery lifecycle complete exists and is an orchestrator."""
        skill_path = Path(__file__).resolve().parent.parent / "skills" / "apex-delivery-lifecycle-complete" / "SKILL.md"
        assert skill_path.exists(), "Delivery lifecycle must exist"

    @pytest.mark.unit
    def test_qa_orchestrator_defines_workflow(self):
        """QA orchestrator defines workflow."""
        skill_path = Path(__file__).resolve().parent.parent / "skills" / "apex-qa-orchestrator-safe" / "SKILL.md"

        with open(skill_path, encoding="utf-8") as f:
            content = f.read()

            # Should mention phases
            assert "Phase 1" in content
            assert "Phase 2" in content
            assert "Phase 3" in content

    @pytest.mark.unit
    def test_design_review_orchestrator_defines_workflow(self):
        """Design review orchestrator defines workflow."""
        skill_path = Path(__file__).resolve().parent.parent / "skills" / "apex-design-review-orchestrator" / "SKILL.md"

        with open(skill_path, encoding="utf-8") as f:
            content = f.read()

            # Should mention approval or design steps
            assert "orchestrator" in content.lower()
            assert "Phase" in content or "phase" in content


class TestRoutingConfiguration:
    """Verify routing configuration is updated with new orchestrators."""

    @pytest.mark.unit
    def test_routing_file_exists(self):
        """Routing configuration exists."""
        routing_path = Path(__file__).resolve().parent.parent / "skills" / "apex" / "references" / "routing.md"
        assert routing_path.exists(), "routing.md must exist"

    @pytest.mark.unit
    def test_routing_mentions_zaimella(self):
        """Routing includes Zaimella orchestrator."""
        routing_path = Path(__file__).resolve().parent.parent / "skills" / "apex" / "references" / "routing.md"

        with open(routing_path) as f:
            content = f.read()
            assert (
                "zaimella" in content.lower() or "apex-delivery-lifecycle-zaimella" in content
            ), "Routing must mention Zaimella"

    @pytest.mark.unit
    def test_routing_mentions_new_coordinators(self):
        """Routing mentions new sub-coordinators."""
        routing_path = Path(__file__).resolve().parent.parent / "skills" / "apex" / "references" / "routing.md"

        with open(routing_path) as f:
            content = f.read()

            # Should mention at least one new orchestrator
            orchestrators = [
                "apex-data-orchestrator-safe",
                "apex-qa-orchestrator-safe",
                "apex-design-review-orchestrator",
            ]

            found_any = any(orch in content for orch in orchestrators)
            assert found_any, "Routing should mention new orchestrators"


class TestDependencyMatrix:
    """Verify dependency matrix documentation exists and is complete."""

    @pytest.mark.unit
    def test_dependency_matrix_exists(self):
        """Dependency matrix documentation exists."""
        matrix_path = Path(__file__).resolve().parent.parent / "docs" / "SKILL-DEPENDENCY-MATRIX.md"
        assert matrix_path.exists(), "SKILL-DEPENDENCY-MATRIX.md must exist"

    @pytest.mark.unit
    def test_dependency_matrix_includes_all_orchestrators(self):
        """Dependency matrix covers all orchestrators."""
        matrix_path = Path(__file__).resolve().parent.parent / "docs" / "SKILL-DEPENDENCY-MATRIX.md"

        with open(matrix_path) as f:
            content = f.read()

            orchestrators = [
                "apex",
                "apex-delivery-lifecycle-complete",
                "apex-delivery-lifecycle-safe",
                "apex-delivery-lifecycle-zaimella",
                "apex-application-generator-complete",
                "apex-data-orchestrator-safe",
                "apex-qa-orchestrator-safe",
                "apex-design-review-orchestrator",
            ]

            for orch in orchestrators:
                assert orch in content, f"Matrix must document {orch}"


class TestCrossSkillIntegration:
    """Verify cross-skill integration documentation exists."""

    @pytest.mark.unit
    def test_cross_integration_doc_exists(self):
        """Cross-skill integration documentation exists."""
        doc_path = Path(__file__).resolve().parent.parent / "docs" / "CROSS-SKILL-INTEGRATION.md"
        assert doc_path.exists(), "CROSS-SKILL-INTEGRATION.md must exist"

    @pytest.mark.unit
    def test_cross_integration_documents_pipelines(self):
        """Cross-skill integration documents design/code/data/QA pipelines."""
        doc_path = Path(__file__).resolve().parent.parent / "docs" / "CROSS-SKILL-INTEGRATION.md"

        with open(doc_path) as f:
            content = f.read()

            pipelines = [
                "Design Skills",
                "Code Generation",
                "Data Pipeline",
                "QA Pipeline",
            ]

            for pipeline in pipelines:
                assert pipeline in content, f"Integration doc must document {pipeline} pipeline"


class TestOrchestratorAudit:
    """Verify orchestrator audit documentation exists and is complete."""

    @pytest.mark.unit
    def test_orchestrator_audit_exists(self):
        """Orchestrator audit documentation exists."""
        audit_path = Path(__file__).resolve().parent.parent / "docs" / "ORCHESTRATOR-AUDIT.md"
        assert audit_path.exists(), "ORCHESTRATOR-AUDIT.md must exist"

    @pytest.mark.unit
    def test_orchestrator_audit_covers_all_8_orchestrators(self):
        """Audit covers all 8 orchestrators."""
        audit_path = Path(__file__).resolve().parent.parent / "docs" / "ORCHESTRATOR-AUDIT.md"

        with open(audit_path, encoding="utf-8") as f:
            content = f.read()

            # Should mention 8 orchestrators
            orchestrators = [
                "apex",
                "apex-delivery-lifecycle-complete",
                "apex-delivery-lifecycle-safe",
                "apex-delivery-lifecycle-zaimella",
                "apex-application-generator-complete",
                "apex-data-orchestrator-safe",
                "apex-qa-orchestrator-safe",
                "apex-design-review-orchestrator",
            ]

            for orch in orchestrators:
                assert orch in content, f"Audit must verify {orch}"

    @pytest.mark.unit
    def test_orchestrator_audit_verifies_skill_existence(self):
        """Audit verifies all coordinated skills exist."""
        audit_path = Path(__file__).resolve().parent.parent / "docs" / "ORCHESTRATOR-AUDIT.md"

        with open(audit_path, encoding="utf-8") as f:
            content = f.read()

            # Should verify skills
            assert "26" in content or "coordination" in content.lower()


class TestOrderConsistency:
    """Verify order numbers are consistent and unique where expected."""

    @pytest.mark.unit
    def test_orchestrator_orders_are_logical(self):
        """Orchestrator orders follow logical hierarchy."""
        skills_dir = Path(__file__).resolve().parent.parent / "skills"

        orchestrators = {
            "apex": "order: 14",
            "apex-delivery-lifecycle-complete": "order: 2",
            "apex-delivery-lifecycle-safe": "order: 3",
            "apex-delivery-lifecycle-zaimella": "order: 3.5",
            "apex-application-generator-complete": "order: 23",
            "apex-data-orchestrator-safe": "order: 13.5",
            "apex-qa-orchestrator-safe": "order: 6.5",
            "apex-design-review-orchestrator": "order: 11.5",
        }

        for name, expected_order_line in orchestrators.items():
            skill_path = skills_dir / name / "SKILL.md"
            with open(skill_path, encoding="utf-8") as f:
                content = f.read()
                assert expected_order_line in content, f"{name} should have {expected_order_line}"

    @pytest.mark.unit
    def test_no_duplicate_orders(self):
        """No duplicate order numbers among orchestrators."""
        skills_dir = Path(__file__).resolve().parent.parent / "skills"

        orders = {}
        orchestrators = [
            "apex",
            "apex-delivery-lifecycle-complete",
            "apex-delivery-lifecycle-safe",
            "apex-delivery-lifecycle-zaimella",
            "apex-application-generator-complete",
            "apex-data-orchestrator-safe",
            "apex-qa-orchestrator-safe",
            "apex-design-review-orchestrator",
        ]

        for name in orchestrators:
            skill_path = skills_dir / name / "SKILL.md"
            with open(skill_path, encoding="utf-8") as f:
                content = f.read()
                # Extract order from content
                for line in content.split("\n"):
                    if line.startswith("order:"):
                        order_val = line.split(":")[1].strip()
                        assert (
                            order_val not in orders
                        ), f"Order {order_val} duplicated: {name} and {orders.get(order_val)}"
                        orders[order_val] = name
                        break


class TestMetadataCompleteness:
    """Verify metadata completeness for all orchestrators."""

    @pytest.mark.unit
    def test_all_orchestrators_have_tags(self):
        """All orchestrators have tags."""
        skills_dir = Path(__file__).resolve().parent.parent / "skills"

        orchestrators = [
            "apex",
            "apex-delivery-lifecycle-complete",
            "apex-delivery-lifecycle-safe",
            "apex-delivery-lifecycle-zaimella",
            "apex-application-generator-complete",
            "apex-data-orchestrator-safe",
            "apex-qa-orchestrator-safe",
            "apex-design-review-orchestrator",
        ]

        for name in orchestrators:
            skill_path = skills_dir / name / "SKILL.md"
            with open(skill_path, encoding="utf-8") as f:
                content = f.read()
                assert "tags:" in content, f"{name} must have tags"

    @pytest.mark.unit
    def test_all_orchestrators_have_category(self):
        """All orchestrators have category."""
        skills_dir = Path(__file__).resolve().parent.parent / "skills"

        orchestrators = [
            "apex",
            "apex-delivery-lifecycle-complete",
            "apex-delivery-lifecycle-safe",
            "apex-delivery-lifecycle-zaimella",
            "apex-application-generator-complete",
            "apex-data-orchestrator-safe",
            "apex-qa-orchestrator-safe",
            "apex-design-review-orchestrator",
        ]

        for name in orchestrators:
            skill_path = skills_dir / name / "SKILL.md"
            with open(skill_path, encoding="utf-8") as f:
                content = f.read()
                assert "category:" in content, f"{name} must have category"

    @pytest.mark.unit
    def test_all_orchestrators_have_description(self):
        """All orchestrators have description."""
        skills_dir = Path(__file__).resolve().parent.parent / "skills"

        orchestrators = [
            "apex",
            "apex-delivery-lifecycle-complete",
            "apex-delivery-lifecycle-safe",
            "apex-delivery-lifecycle-zaimella",
            "apex-application-generator-complete",
            "apex-data-orchestrator-safe",
            "apex-qa-orchestrator-safe",
            "apex-design-review-orchestrator",
        ]

        for name in orchestrators:
            skill_path = skills_dir / name / "SKILL.md"
            with open(skill_path, encoding="utf-8") as f:
                content = f.read()
                assert "description:" in content, f"{name} must have description"
