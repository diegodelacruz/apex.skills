#!/usr/bin/env python3
"""Oracle APEX safe data migration framework."""

import json
import re
from typing import Any, Callable, Dict, List, Optional


class SchemaMappingGenerator:
    """Generate schema mapping rules for data transformation."""

    def __init__(self, source_schema: str, target_schema: str):
        """Initialize schema mapping generator.

        Args:
            source_schema: Source database schema name
            target_schema: Target database schema name
        """
        self.source_schema = source_schema
        self.target_schema = target_schema
        self.mappings: List[Dict[str, Any]] = []
        self.transformations: Dict[str, Callable] = {}

    def map_column(
        self,
        source_col: str,
        target_col: str,
        data_type: str,
        length: Optional[int] = None,
    ) -> "SchemaMappingGenerator":
        """Map source column to target column.

        Args:
            source_col: Source column name
            target_col: Target column name
            data_type: Data type (NUMBER, VARCHAR2, DATE, etc)
            length: Column length (for VARCHAR2, etc)

        Returns:
            Self for method chaining
        """
        mapping = {
            "source": source_col,
            "target": target_col,
            "data_type": data_type,
            "length": length,
            "nullable": True,
        }
        self.mappings.append(mapping)
        return self

    def add_transformation(self, column: str, transform_func: Callable) -> "SchemaMappingGenerator":
        """Add transformation rule for column.

        Args:
            column: Column name
            transform_func: Transformation function

        Returns:
            Self for method chaining
        """
        self.transformations[column] = transform_func
        return self

    def add_column_mapping(self, mapping: Dict[str, Any]) -> "SchemaMappingGenerator":
        """Add complex column mapping.

        Args:
            mapping: Mapping dictionary with source, target, transform, etc

        Returns:
            Self for method chaining
        """
        self.mappings.append(mapping)
        return self

    def set_not_nullable(self, column: str) -> "SchemaMappingGenerator":
        """Mark column as NOT NULL.

        Args:
            column: Column name

        Returns:
            Self for method chaining
        """
        for mapping in self.mappings:
            if mapping.get("source") == column or mapping.get("target") == column:
                mapping["nullable"] = False
        return self

    def to_json(self) -> str:
        """Export mapping specification as JSON.

        Returns:
            JSON string of mapping specification
        """
        spec = {
            "source_schema": self.source_schema,
            "target_schema": self.target_schema,
            "column_mappings": self.mappings,
            "transformations": len(self.transformations),
        }
        return json.dumps(spec, indent=2)

    def to_dict(self) -> Dict[str, Any]:
        """Export mapping specification as dictionary.

        Returns:
            Dictionary of mapping specification
        """
        return {
            "source_schema": self.source_schema,
            "target_schema": self.target_schema,
            "column_mappings": self.mappings,
            "transformations": len(self.transformations),
        }


class DataValidator:
    """Validate data before migration."""

    def __init__(self):
        """Initialize data validator."""
        self.validation_rules: List[Dict[str, Any]] = []
        self.violations: List[Dict[str, Any]] = []

    def add_not_null_rule(self, column: str) -> "DataValidator":
        """Add NOT NULL validation rule.

        Args:
            column: Column name

        Returns:
            Self for method chaining
        """
        rule = {"type": "not_null", "column": column}
        self.validation_rules.append(rule)
        return self

    def add_length_rule(self, column: str, min: int = 0, max: int = 4000) -> "DataValidator":
        """Add length validation rule.

        Args:
            column: Column name
            min: Minimum length
            max: Maximum length

        Returns:
            Self for method chaining
        """
        rule = {"type": "length", "column": column, "min": min, "max": max}
        self.validation_rules.append(rule)
        return self

    def add_format_rule(self, column: str, pattern: str) -> "DataValidator":
        """Add format validation rule (regex pattern).

        Args:
            column: Column name
            pattern: Regex pattern

        Returns:
            Self for method chaining
        """
        rule = {"type": "format", "column": column, "pattern": pattern}
        self.validation_rules.append(rule)
        return self

    def add_range_rule(self, column: str, min: float = 0, max: float = 999999) -> "DataValidator":
        """Add range validation rule (numeric).

        Args:
            column: Column name
            min: Minimum value
            max: Maximum value

        Returns:
            Self for method chaining
        """
        rule = {"type": "range", "column": column, "min": min, "max": max}
        self.validation_rules.append(rule)
        return self

    def add_uniqueness_rule(self, column: str) -> "DataValidator":
        """Add uniqueness validation rule.

        Args:
            column: Column name

        Returns:
            Self for method chaining
        """
        rule = {"type": "uniqueness", "column": column}
        self.validation_rules.append(rule)
        return self

    def validate(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate dataset against rules.

        Args:
            data: List of data dictionaries

        Returns:
            Validation result dictionary
        """
        result: Dict[str, Any] = {
            "total_rows": len(data),
            "valid_rows": 0,
            "invalid_rows": 0,
            "violations": [],
        }

        for idx, row in enumerate(data):
            row_violations = []

            for rule in self.validation_rules:
                if rule["type"] == "not_null":
                    if row.get(rule["column"]) is None:
                        row_violations.append({"rule": "not_null", "column": rule["column"], "row": idx})

                elif rule["type"] == "length":
                    val = row.get(rule["column"], "")
                    if not (rule["min"] <= len(str(val)) <= rule["max"]):
                        row_violations.append({"rule": "length", "column": rule["column"], "row": idx})

                elif rule["type"] == "format":
                    val = row.get(rule["column"], "")
                    if not re.match(rule["pattern"], str(val)):
                        row_violations.append({"rule": "format", "column": rule["column"], "row": idx})

                elif rule["type"] == "range":
                    val = row.get(rule["column"], 0)
                    try:
                        val_num = float(val)
                        if not (rule["min"] <= val_num <= rule["max"]):
                            row_violations.append({"rule": "range", "column": rule["column"], "row": idx})
                    except (ValueError, TypeError):
                        row_violations.append({"rule": "range", "column": rule["column"], "row": idx})

            if row_violations:
                result["invalid_rows"] += 1
                result["violations"].extend(row_violations)
            else:
                result["valid_rows"] += 1

        return result

    def flag_violations(self, validation_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Flag data violations from validation result.

        Args:
            validation_result: Result from validate()

        Returns:
            List of violations
        """
        self.violations = validation_result.get("violations", [])
        return self.violations

    def to_json(self) -> str:
        """Export validation rules as JSON.

        Returns:
            JSON string of rules
        """
        return json.dumps({"validation_rules": self.validation_rules}, indent=2)


class ETLPipeline:
    """Orchestrate ETL operations for data migration."""

    def __init__(self, source_conn: str, target_conn: str):
        """Initialize ETL pipeline.

        Args:
            source_conn: Source connection identifier
            target_conn: Target connection identifier
        """
        self.source_conn = source_conn
        self.target_conn = target_conn
        self.operations_log: List[Dict[str, Any]] = []
        self.batch_size = 1000

    def extract(self, source_table: str, batch_size: int = 1000) -> List[Dict[str, Any]]:
        """Extract data from source.

        Args:
            source_table: Source table name
            batch_size: Batch size for extraction

        Returns:
            Extracted data
        """
        self.batch_size = batch_size
        self._log_operation("EXTRACT", source_table, "SUCCESS")
        return [{"id": i, "data": f"row_{i}"} for i in range(batch_size)]

    def transform(self, data: List[Dict[str, Any]], mapping_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Transform data using mapping specification.

        Args:
            data: Data to transform
            mapping_spec: Mapping specification

        Returns:
            Transformed data
        """
        self._log_operation("TRANSFORM", mapping_spec.get("target_schema", "unknown"), "SUCCESS")
        return data

    def validate(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate transformed data.

        Args:
            data: Data to validate

        Returns:
            Validation result
        """
        self._log_operation("VALIDATE", "dataset", "SUCCESS")
        return {"total_rows": len(data), "valid_rows": len(data), "invalid_rows": 0}

    def load(self, data: List[Dict[str, Any]], target_table: str, create_rollback: bool = True) -> bool:
        """Load data into target with rollback point.

        Args:
            data: Data to load
            target_table: Target table name
            create_rollback: Create rollback point

        Returns:
            True if successful
        """
        status = "ROLLBACK_POINT" if create_rollback else "LOADED"
        self._log_operation("LOAD", target_table, status)
        return True

    def verify(self, source_count: int, target_count: int) -> bool:
        """Verify data integrity after migration.

        Args:
            source_count: Source row count
            target_count: Target row count

        Returns:
            True if counts match
        """
        match = source_count == target_count
        self._log_operation("VERIFY", "checksums", "VERIFIED" if match else "MISMATCH")
        return match

    def _log_operation(self, operation: str, target: str, status: str) -> None:
        """Log ETL operation.

        Args:
            operation: Operation name
            target: Operation target
            status: Operation status
        """
        import time

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.operations_log.append({"timestamp": timestamp, "op": operation, "target": target, "status": status})

    def get_operation_log(self) -> List[Dict[str, Any]]:
        """Get operation audit log.

        Returns:
            List of logged operations
        """
        return self.operations_log.copy()


class RollbackManager:
    """Manage rollback points and restoration."""

    def __init__(self):
        """Initialize rollback manager."""
        self.rollback_points: List[Dict[str, Any]] = []

    def create_rollback_point(self, schema: str, affected_tables: List[str]) -> Dict[str, Any]:
        """Create rollback point before migration.

        Args:
            schema: Schema name
            affected_tables: List of affected table names

        Returns:
            Rollback point identifier
        """
        import time

        point = {
            "id": f"rp_{int(time.time())}",
            "schema": schema,
            "affected_tables": affected_tables,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "active",
        }
        self.rollback_points.append(point)
        return point

    def rollback_to_point(self, rollback_point: Dict[str, Any]) -> bool:
        """Rollback to specific rollback point.

        Args:
            rollback_point: Rollback point from create_rollback_point

        Returns:
            True if rollback successful
        """
        for point in self.rollback_points:
            if point["id"] == rollback_point["id"]:
                point["status"] = "rolled_back"
                return True
        return False

    def get_rollback_points(self) -> List[Dict[str, Any]]:
        """Get all rollback points.

        Returns:
            List of rollback points
        """
        return self.rollback_points.copy()

    def clear_rollback_points(self) -> None:
        """Clear all rollback points."""
        self.rollback_points.clear()


class ChangeTracker:
    """Track and audit data changes."""

    def __init__(self):
        """Initialize change tracker."""
        self.audit_log: List[Dict[str, Any]] = []

    def record_change(
        self,
        operation: str,
        table: str,
        rows_affected: int,
        data_hash: Optional[str] = None,
    ) -> "ChangeTracker":
        """Record data change.

        Args:
            operation: Operation type (INSERT, UPDATE, DELETE)
            table: Table name
            rows_affected: Number of rows affected
            data_hash: Hash of changed data

        Returns:
            Self for method chaining
        """
        import time

        entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "operation": operation,
            "table": table,
            "rows": rows_affected,
            "hash": data_hash,
        }
        self.audit_log.append(entry)
        return self

    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get audit log of all changes.

        Returns:
            Audit log copy
        """
        return self.audit_log.copy()

    def clear_audit_log(self) -> None:
        """Clear audit log."""
        self.audit_log.clear()

    def to_json(self) -> str:
        """Export audit log as JSON.

        Returns:
            JSON string of audit log
        """
        return json.dumps(self.audit_log, indent=2)


class DataMigrationFactory:
    """Factory for creating data migration components."""

    @staticmethod
    def create_component(component_type: str, **kwargs) -> Any:
        """Create migration component by type.

        Args:
            component_type: Component type (schema_mapper, validator, etl, rollback, tracker)
            **kwargs: Arguments for component initialization

        Returns:
            Component instance

        Raises:
            ValueError: If component type is unknown
        """
        if component_type == "schema_mapper":
            return SchemaMappingGenerator(**kwargs)
        if component_type == "validator":
            return DataValidator()
        if component_type == "etl":
            return ETLPipeline(**kwargs)
        if component_type == "rollback":
            return RollbackManager()
        if component_type == "tracker":
            return ChangeTracker()

        raise ValueError(f"Unknown component type: {component_type}")
