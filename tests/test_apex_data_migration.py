"""Unit tests for apex_data_migration module."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from apex_data_migration import (
    ChangeTracker,
    DataMigrationFactory,
    DataValidator,
    ETLPipeline,
    RollbackManager,
    SchemaMappingGenerator,
)


class TestSchemaMappingGenerator:
    """Test SchemaMappingGenerator class."""

    @pytest.mark.unit
    def test_create_schema_mapper(self):
        """Create schema mapping generator."""
        mapper = SchemaMappingGenerator("OLD_SCHEMA", "NEW_SCHEMA")
        assert mapper.source_schema == "OLD_SCHEMA"
        assert mapper.target_schema == "NEW_SCHEMA"
        assert isinstance(mapper.mappings, list)

    @pytest.mark.unit
    def test_map_column(self):
        """Map source column to target."""
        mapper = SchemaMappingGenerator("OLD_SCHEMA", "NEW_SCHEMA")
        mapper.map_column("USER_ID", "USER_ID", "NUMBER")

        assert len(mapper.mappings) == 1
        assert mapper.mappings[0]["source"] == "USER_ID"

    @pytest.mark.unit
    def test_map_column_with_length(self):
        """Map column with length specification."""
        mapper = SchemaMappingGenerator("OLD_SCHEMA", "NEW_SCHEMA")
        mapper.map_column("USERNAME", "USER_NAME", "VARCHAR2", length=100)

        assert mapper.mappings[0]["length"] == 100

    @pytest.mark.unit
    def test_add_transformation(self):
        """Add transformation rule."""
        mapper = SchemaMappingGenerator("OLD_SCHEMA", "NEW_SCHEMA")
        mapper.add_transformation("STATUS", lambda v: "ACTIVE" if v == 1 else "INACTIVE")

        assert "STATUS" in mapper.transformations

    @pytest.mark.unit
    def test_add_column_mapping(self):
        """Add complex column mapping."""
        mapper = SchemaMappingGenerator("OLD_SCHEMA", "NEW_SCHEMA")
        mapper.add_column_mapping({"source": "COL1", "target": "COL2", "transform": "UPPER"})

        assert len(mapper.mappings) == 1

    @pytest.mark.unit
    def test_set_not_nullable(self):
        """Mark column as NOT NULL."""
        mapper = SchemaMappingGenerator("OLD_SCHEMA", "NEW_SCHEMA")
        mapper.map_column("ID", "ID", "NUMBER")
        mapper.set_not_nullable("ID")

        assert mapper.mappings[0]["nullable"] is False

    @pytest.mark.unit
    def test_to_json(self):
        """Export mapping as JSON."""
        mapper = SchemaMappingGenerator("OLD_SCHEMA", "NEW_SCHEMA")
        mapper.map_column("ID", "ID", "NUMBER")
        json_str = mapper.to_json()

        data = json.loads(json_str)
        assert "source_schema" in data
        assert "column_mappings" in data

    @pytest.mark.unit
    def test_to_dict(self):
        """Export mapping as dictionary."""
        mapper = SchemaMappingGenerator("OLD_SCHEMA", "NEW_SCHEMA")
        mapper.map_column("ID", "ID", "NUMBER")
        result = mapper.to_dict()

        assert isinstance(result, dict)
        assert result["source_schema"] == "OLD_SCHEMA"

    @pytest.mark.unit
    def test_method_chaining(self):
        """Test method chaining."""
        mapper = SchemaMappingGenerator("OLD_SCHEMA", "NEW_SCHEMA")
        mapper.map_column("ID", "ID", "NUMBER").set_not_nullable("ID").add_transformation("STATUS", lambda v: v)

        assert len(mapper.mappings) == 1


class TestDataValidator:
    """Test DataValidator class."""

    @pytest.mark.unit
    def test_create_validator(self):
        """Create data validator."""
        validator = DataValidator()
        assert isinstance(validator.validation_rules, list)

    @pytest.mark.unit
    def test_add_not_null_rule(self):
        """Add NOT NULL validation rule."""
        validator = DataValidator()
        validator.add_not_null_rule("USER_ID")

        assert len(validator.validation_rules) == 1
        assert validator.validation_rules[0]["type"] == "not_null"

    @pytest.mark.unit
    def test_add_length_rule(self):
        """Add length validation rule."""
        validator = DataValidator()
        validator.add_length_rule("USERNAME", min=3, max=50)

        assert len(validator.validation_rules) == 1
        assert validator.validation_rules[0]["type"] == "length"

    @pytest.mark.unit
    def test_add_format_rule(self):
        """Add format validation rule."""
        validator = DataValidator()
        validator.add_format_rule("EMAIL", r"^[\w\.-]+@[\w\.-]+\.\w+$")

        assert len(validator.validation_rules) == 1

    @pytest.mark.unit
    def test_add_range_rule(self):
        """Add range validation rule."""
        validator = DataValidator()
        validator.add_range_rule("AGE", min=0, max=150)

        assert len(validator.validation_rules) == 1

    @pytest.mark.unit
    def test_add_uniqueness_rule(self):
        """Add uniqueness validation rule."""
        validator = DataValidator()
        validator.add_uniqueness_rule("USER_ID")

        assert len(validator.validation_rules) == 1

    @pytest.mark.unit
    def test_validate_valid_data(self):
        """Validate valid data."""
        validator = DataValidator()
        validator.add_not_null_rule("id")

        data = [{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}]
        result = validator.validate(data)

        assert result["valid_rows"] == 2
        assert result["invalid_rows"] == 0

    @pytest.mark.unit
    def test_validate_invalid_data(self):
        """Validate data with violations."""
        validator = DataValidator()
        validator.add_not_null_rule("id")

        data = [{"id": 1, "name": "John"}, {"id": None, "name": "Jane"}]
        result = validator.validate(data)

        assert result["invalid_rows"] == 1
        assert len(result["violations"]) > 0

    @pytest.mark.unit
    def test_flag_violations(self):
        """Flag violations from validation result."""
        validator = DataValidator()
        validator.add_not_null_rule("id")

        data = [{"id": None}]
        result = validator.validate(data)
        violations = validator.flag_violations(result)

        assert len(violations) > 0

    @pytest.mark.unit
    def test_to_json(self):
        """Export validator rules as JSON."""
        validator = DataValidator()
        validator.add_not_null_rule("id")
        json_str = validator.to_json()

        data = json.loads(json_str)
        assert "validation_rules" in data


class TestETLPipeline:
    """Test ETLPipeline class."""

    @pytest.mark.unit
    def test_create_pipeline(self):
        """Create ETL pipeline."""
        pipeline = ETLPipeline("source_db", "target_db")
        assert pipeline.source_conn == "source_db"
        assert pipeline.target_conn == "target_db"

    @pytest.mark.unit
    def test_extract(self):
        """Extract data from source."""
        pipeline = ETLPipeline("source_db", "target_db")
        data = pipeline.extract("USERS", batch_size=1000)

        assert isinstance(data, list)
        assert len(data) == 1000

    @pytest.mark.unit
    def test_transform(self):
        """Transform extracted data."""
        pipeline = ETLPipeline("source_db", "target_db")
        data = [{"id": 1, "name": "John"}]
        mapping = {"target_schema": "NEW_SCHEMA"}

        transformed = pipeline.transform(data, mapping)

        assert isinstance(transformed, list)

    @pytest.mark.unit
    def test_validate(self):
        """Validate transformed data."""
        pipeline = ETLPipeline("source_db", "target_db")
        data = [{"id": 1, "name": "John"}]

        result = pipeline.validate(data)

        assert "valid_rows" in result
        assert "invalid_rows" in result

    @pytest.mark.unit
    def test_load(self):
        """Load data into target."""
        pipeline = ETLPipeline("source_db", "target_db")
        data = [{"id": 1, "name": "John"}]

        result = pipeline.load(data, "NEW_USERS")

        assert result is True

    @pytest.mark.unit
    def test_load_with_rollback(self):
        """Load data with rollback point."""
        pipeline = ETLPipeline("source_db", "target_db")
        data = [{"id": 1, "name": "John"}]

        result = pipeline.load(data, "NEW_USERS", create_rollback=True)

        assert result is True

    @pytest.mark.unit
    def test_verify(self):
        """Verify data integrity."""
        pipeline = ETLPipeline("source_db", "target_db")

        result = pipeline.verify(1000, 1000)

        assert result is True

    @pytest.mark.unit
    def test_verify_mismatch(self):
        """Verify with count mismatch."""
        pipeline = ETLPipeline("source_db", "target_db")

        result = pipeline.verify(1000, 999)

        assert result is False

    @pytest.mark.unit
    def test_get_operation_log(self):
        """Get operation audit log."""
        pipeline = ETLPipeline("source_db", "target_db")
        pipeline.extract("USERS")

        log = pipeline.get_operation_log()

        assert len(log) > 0


class TestRollbackManager:
    """Test RollbackManager class."""

    @pytest.mark.unit
    def test_create_rollback_manager(self):
        """Create rollback manager."""
        manager = RollbackManager()
        assert isinstance(manager.rollback_points, list)

    @pytest.mark.unit
    def test_create_rollback_point(self):
        """Create rollback point."""
        manager = RollbackManager()
        point = manager.create_rollback_point("NEW_SCHEMA", ["USERS", "ACCOUNTS"])

        assert "id" in point
        assert point["schema"] == "NEW_SCHEMA"

    @pytest.mark.unit
    def test_rollback_to_point(self):
        """Rollback to specific point."""
        manager = RollbackManager()
        point = manager.create_rollback_point("NEW_SCHEMA", ["USERS"])

        result = manager.rollback_to_point(point)

        assert result is True
        assert point["status"] == "rolled_back"

    @pytest.mark.unit
    def test_rollback_to_invalid_point(self):
        """Rollback to non-existent point."""
        manager = RollbackManager()

        result = manager.rollback_to_point({"id": "invalid_id"})

        assert result is False

    @pytest.mark.unit
    def test_get_rollback_points(self):
        """Get all rollback points."""
        manager = RollbackManager()
        manager.create_rollback_point("NEW_SCHEMA", ["USERS"])
        manager.create_rollback_point("NEW_SCHEMA", ["ACCOUNTS"])

        points = manager.get_rollback_points()

        assert len(points) == 2

    @pytest.mark.unit
    def test_clear_rollback_points(self):
        """Clear all rollback points."""
        manager = RollbackManager()
        manager.create_rollback_point("NEW_SCHEMA", ["USERS"])
        manager.clear_rollback_points()

        points = manager.get_rollback_points()

        assert len(points) == 0


class TestChangeTracker:
    """Test ChangeTracker class."""

    @pytest.mark.unit
    def test_create_tracker(self):
        """Create change tracker."""
        tracker = ChangeTracker()
        assert isinstance(tracker.audit_log, list)

    @pytest.mark.unit
    def test_record_change(self):
        """Record data change."""
        tracker = ChangeTracker()
        tracker.record_change("INSERT", "USERS", 1000)

        assert len(tracker.audit_log) == 1

    @pytest.mark.unit
    def test_record_multiple_changes(self):
        """Record multiple changes."""
        tracker = ChangeTracker()
        tracker.record_change("INSERT", "USERS", 1000).record_change("INSERT", "ACCOUNTS", 500)

        assert len(tracker.audit_log) == 2

    @pytest.mark.unit
    def test_record_change_with_hash(self):
        """Record change with data hash."""
        tracker = ChangeTracker()
        tracker.record_change("INSERT", "USERS", 1000, data_hash="abc123")

        assert tracker.audit_log[0]["hash"] == "abc123"

    @pytest.mark.unit
    def test_get_audit_log(self):
        """Get audit log copy."""
        tracker = ChangeTracker()
        tracker.record_change("INSERT", "USERS", 1000)

        log = tracker.get_audit_log()

        assert len(log) == 1

    @pytest.mark.unit
    def test_audit_log_immutability(self):
        """Audit log returned as copy."""
        tracker = ChangeTracker()
        tracker.record_change("INSERT", "USERS", 1000)

        log1 = tracker.get_audit_log()
        log2 = tracker.get_audit_log()

        assert log1 == log2
        assert log1 is not log2

    @pytest.mark.unit
    def test_clear_audit_log(self):
        """Clear audit log."""
        tracker = ChangeTracker()
        tracker.record_change("INSERT", "USERS", 1000)
        tracker.clear_audit_log()

        log = tracker.get_audit_log()

        assert len(log) == 0

    @pytest.mark.unit
    def test_to_json(self):
        """Export audit log as JSON."""
        tracker = ChangeTracker()
        tracker.record_change("INSERT", "USERS", 1000)
        json_str = tracker.to_json()

        data = json.loads(json_str)
        assert isinstance(data, list)


class TestDataMigrationFactory:
    """Test DataMigrationFactory class."""

    @pytest.mark.unit
    def test_factory_create_schema_mapper(self):
        """Factory creates schema mapper."""
        component = DataMigrationFactory.create_component("schema_mapper", source_schema="OLD", target_schema="NEW")
        assert isinstance(component, SchemaMappingGenerator)

    @pytest.mark.unit
    def test_factory_create_validator(self):
        """Factory creates validator."""
        component = DataMigrationFactory.create_component("validator")
        assert isinstance(component, DataValidator)

    @pytest.mark.unit
    def test_factory_create_etl(self):
        """Factory creates ETL pipeline."""
        component = DataMigrationFactory.create_component("etl", source_conn="source", target_conn="target")
        assert isinstance(component, ETLPipeline)

    @pytest.mark.unit
    def test_factory_create_rollback(self):
        """Factory creates rollback manager."""
        component = DataMigrationFactory.create_component("rollback")
        assert isinstance(component, RollbackManager)

    @pytest.mark.unit
    def test_factory_create_tracker(self):
        """Factory creates change tracker."""
        component = DataMigrationFactory.create_component("tracker")
        assert isinstance(component, ChangeTracker)

    @pytest.mark.unit
    def test_factory_invalid_type(self):
        """Factory raises error for invalid type."""
        with pytest.raises(ValueError, match="Unknown component type"):
            DataMigrationFactory.create_component("invalid")


class TestIntegration:
    """Integration tests for data migration."""

    @pytest.mark.unit
    def test_full_migration_workflow(self):
        """Test full data migration workflow."""
        # Create mapper
        mapper = SchemaMappingGenerator("OLD_SCHEMA", "NEW_SCHEMA")
        mapper.map_column("USER_ID", "USER_ID", "NUMBER")
        mapper.map_column("USERNAME", "USER_NAME", "VARCHAR2", length=100)

        # Create validator
        validator = DataValidator()
        validator.add_not_null_rule("USER_ID")
        validator.add_length_rule("USER_NAME", min=3, max=100)

        # Create pipeline
        pipeline = ETLPipeline("source", "target")

        # Execute pipeline
        data = pipeline.extract("USERS", batch_size=100)
        transformed = pipeline.transform(data, mapper.to_dict())
        validation_result = pipeline.validate(transformed)
        pipeline.load(transformed, "NEW_USERS", create_rollback=True)

        assert len(data) == 100
        assert validation_result["valid_rows"] == 100

    @pytest.mark.unit
    def test_migration_with_rollback(self):
        """Test migration with rollback capability."""
        manager = RollbackManager()
        tracker = ChangeTracker()

        # Create rollback point
        point = manager.create_rollback_point("NEW_SCHEMA", ["USERS"])

        # Record changes
        tracker.record_change("INSERT", "USERS", 1000)

        # Simulate failure and rollback
        manager.rollback_to_point(point)

        assert point["status"] == "rolled_back"
        assert len(tracker.get_audit_log()) == 1

    @pytest.mark.unit
    def test_factory_full_workflow(self):
        """Test full workflow using factory."""
        mapper = DataMigrationFactory.create_component("schema_mapper", source_schema="OLD", target_schema="NEW")
        validator = DataMigrationFactory.create_component("validator")
        pipeline = DataMigrationFactory.create_component("etl", source_conn="source", target_conn="target")
        manager = DataMigrationFactory.create_component("rollback")

        assert isinstance(mapper, SchemaMappingGenerator)
        assert isinstance(validator, DataValidator)
        assert isinstance(pipeline, ETLPipeline)
        assert isinstance(manager, RollbackManager)
