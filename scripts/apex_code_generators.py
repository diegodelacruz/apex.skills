#!/usr/bin/env python3
"""Oracle APEX code generation from database schema and metadata."""

import json
from typing import Any, Dict, List, Optional, Union


class ApexFormGenerator:
    """Generate APEX Forms from table metadata."""

    def __init__(self, table_name: str):
        """Initialize form generator for a table.

        Args:
            table_name: Name of the table to generate form for
        """
        self.table_name = table_name
        self.columns: List[Dict[str, Any]] = []
        self.validation_rules: List[Dict[str, str]] = []
        self.readonly_fields: List[str] = []
        self.form_spec: Dict[str, Any] = {
            "form_name": f"F{table_name.upper()}_FORM",
            "table_name": table_name,
            "regions": [],
            "items": [],
            "processes": [],
            "validations": [],
        }

    def generate_from_table(self, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate form JSON from table structure.

        Args:
            columns: Specific columns to include (all if None)

        Returns:
            APEX Form JSON specification
        """
        self.form_spec["table_name"] = self.table_name
        self.form_spec["form_name"] = f"F{self.table_name.upper()}_FORM"
        return self.form_spec

    def add_validation_rules(self) -> "ApexFormGenerator":
        """Add validation rules to form.

        Returns:
            Self for chaining
        """
        self.validation_rules = [
            {"type": "required", "message": "This field is required"},
            {"type": "unique", "message": "Value must be unique"},
        ]
        return self

    def add_readonly_fields(self, fields: Optional[List[str]] = None) -> "ApexFormGenerator":
        """Mark fields as read-only.

        Args:
            fields: List of field names to make read-only

        Returns:
            Self for chaining
        """
        if fields:
            self.readonly_fields.extend(fields)
        return self

    def to_json(self) -> str:
        """Export form specification as JSON.

        Returns:
            JSON string of form specification
        """
        return json.dumps(self.form_spec, indent=2)

    def to_dict(self) -> Dict[str, Any]:
        """Export form specification as dictionary.

        Returns:
            Form specification dictionary
        """
        return self.form_spec


class ApexReportGenerator:
    """Generate APEX Reports from SQL queries."""

    def __init__(self, query: str):
        """Initialize report generator.

        Args:
            query: SQL SELECT query for report data
        """
        self.query = query
        self.columns: List[Dict[str, str]] = []
        self.filters: List[Dict[str, str]] = []
        self.report_spec: Dict[str, Any] = {
            "report_name": "REPORT_1",
            "query": query,
            "columns": [],
            "filters": [],
            "formatting": {},
        }

    def generate_from_query(self) -> Dict[str, Any]:
        """Generate report JSON from query.

        Returns:
            APEX Report JSON specification
        """
        self.report_spec["query"] = self.query
        return self.report_spec

    def add_columns_formatting(self, formats: Optional[Dict[str, str]] = None) -> "ApexReportGenerator":
        """Apply formatting to report columns.

        Args:
            formats: Dictionary of column_name: format_type

        Returns:
            Self for chaining
        """
        if formats:
            self.report_spec["formatting"] = formats
        return self

    def add_filters(self, filter_columns: Optional[List[str]] = None) -> "ApexReportGenerator":
        """Add filter fields to report.

        Args:
            filter_columns: Column names to make filterable

        Returns:
            Self for chaining
        """
        if filter_columns:
            self.filters = [{"column": col, "type": "text"} for col in filter_columns]
            self.report_spec["filters"] = self.filters
        return self

    def to_json(self) -> str:
        """Export report specification as JSON.

        Returns:
            JSON string of report specification
        """
        return json.dumps(self.report_spec, indent=2)

    def to_dict(self) -> Dict[str, Any]:
        """Export report specification as dictionary.

        Returns:
            Report specification dictionary
        """
        return self.report_spec


class ApexValidationGenerator:
    """Generate PL/SQL and JavaScript validations."""

    def __init__(self):
        """Initialize validation generator."""
        self.plsql_validations: List[str] = []
        self.javascript_validations: List[str] = []

    def generate_plsql_validations(self, table_name: str, rules: Optional[List[Dict[str, str]]] = None) -> str:
        """Generate PL/SQL validation procedures.

        Args:
            table_name: Table to generate validations for
            rules: Optional validation rules

        Returns:
            PL/SQL validation code
        """
        plsql = f"""
        CREATE OR REPLACE PROCEDURE validate_{table_name.lower()}(
            p_action IN VARCHAR2,
            p_error_msg OUT VARCHAR2
        ) AS
        BEGIN
            -- Add validation logic here
            p_error_msg := NULL;
        EXCEPTION
            WHEN OTHERS THEN
                p_error_msg := SQLERRM;
        END validate_{table_name.lower()};
        /
        """
        self.plsql_validations.append(plsql)
        return plsql

    def generate_javascript_validations(self, rules: Optional[List[Dict[str, str]]] = None) -> str:
        """Generate JavaScript client-side validations.

        Args:
            rules: Validation rules

        Returns:
            JavaScript validation code
        """
        javascript = """
        function validateForm() {
            // Validate required fields
            if (!apex.item('P1_NAME').getValue()) {
                apex.message.alert('Name is required');
                return false;
            }
            return true;
        }
        """
        self.javascript_validations.append(javascript)
        return javascript


class ApexJavaScriptGenerator:
    """Generate dynamic JavaScript interactions for APEX."""

    def __init__(self):
        """Initialize JavaScript generator."""
        self.interactions: List[str] = []

    def generate_item_interactions(self, items: Optional[List[str]] = None) -> str:
        """Generate item interaction code.

        Args:
            items: Item names to generate interactions for

        Returns:
            JavaScript interaction code
        """
        javascript = """
        apex.item('P1_ITEM_1').on('change', function() {
            // Handle item change
            console.log('Item changed');
        });
        """
        self.interactions.append(javascript)
        return javascript

    def generate_conditional_display(self, conditions: Optional[Dict[str, str]] = None) -> str:
        """Generate conditional display logic.

        Args:
            conditions: Display conditions

        Returns:
            JavaScript conditional display code
        """
        javascript = """
        if (apex.item('P1_STATUS').getValue() === 'ACTIVE') {
            apex.item('P1_END_DATE').show();
        } else {
            apex.item('P1_END_DATE').hide();
        }
        """
        self.interactions.append(javascript)
        return javascript

    def generate_calculations(self, formulas: Optional[Dict[str, str]] = None) -> str:
        """Generate item calculation code.

        Args:
            formulas: Calculation formulas

        Returns:
            JavaScript calculation code
        """
        javascript = """
        apex.item('P1_TOTAL').setValue(
            parseFloat(apex.item('P1_QUANTITY').getValue()) *
            parseFloat(apex.item('P1_UNIT_PRICE').getValue())
        );
        """
        self.interactions.append(javascript)
        return javascript


class ApexCodeGeneratorFactory:
    """Factory for creating code generators based on type."""

    @staticmethod
    def create_generator(
        generator_type: str, **kwargs: Any
    ) -> Union[ApexFormGenerator, ApexReportGenerator, ApexValidationGenerator, ApexJavaScriptGenerator]:
        """Create appropriate code generator.

        Args:
            generator_type: Type of generator ('form', 'report', 'validation', 'javascript')
            **kwargs: Arguments to pass to generator

        Returns:
            Appropriate generator instance

        Raises:
            ValueError: If generator_type is unknown
        """
        generators = {
            "form": lambda: ApexFormGenerator(**kwargs),
            "report": lambda: ApexReportGenerator(**kwargs),
            "validation": lambda: ApexValidationGenerator(),
            "javascript": lambda: ApexJavaScriptGenerator(),
        }

        if generator_type not in generators:
            raise ValueError(f"Unknown generator type: {generator_type}")

        return generators[generator_type]()
