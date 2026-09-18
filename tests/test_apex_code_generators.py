"""Unit tests for apex_code_generators module."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from apex_code_generators import (  # noqa: E402
    ApexCodeGeneratorFactory,
    ApexFormGenerator,
    ApexJavaScriptGenerator,
    ApexReportGenerator,
    ApexValidationGenerator,
)


class TestApexFormGenerator:
    """Test ApexFormGenerator class."""

    @pytest.mark.unit
    def test_create_form_generator(self):
        """Create form generator for table."""
        gen = ApexFormGenerator("EMPLOYEES")
        assert gen.table_name == "EMPLOYEES"
        assert isinstance(gen.form_spec, dict)

    @pytest.mark.unit
    def test_generate_from_table(self):
        """Generate form from table."""
        gen = ApexFormGenerator("EMPLOYEES")
        result = gen.generate_from_table()

        assert result["table_name"] == "EMPLOYEES"
        assert "form_name" in result
        assert result["form_name"] == "FEMPLOYEES_FORM"

    @pytest.mark.unit
    def test_add_validation_rules(self):
        """Add validation rules to form."""
        gen = ApexFormGenerator("EMPLOYEES")
        gen.add_validation_rules()

        assert len(gen.validation_rules) > 0
        assert any(r["type"] == "required" for r in gen.validation_rules)

    @pytest.mark.unit
    def test_add_readonly_fields(self):
        """Mark fields as read-only."""
        gen = ApexFormGenerator("EMPLOYEES")
        gen.add_readonly_fields(["ID", "CREATED_DATE"])

        assert "ID" in gen.readonly_fields
        assert "CREATED_DATE" in gen.readonly_fields

    @pytest.mark.unit
    def test_form_to_json(self):
        """Export form as JSON."""
        gen = ApexFormGenerator("EMPLOYEES")
        json_str = gen.to_json()

        data = json.loads(json_str)
        assert data["table_name"] == "EMPLOYEES"

    @pytest.mark.unit
    def test_form_to_dict(self):
        """Export form as dictionary."""
        gen = ApexFormGenerator("EMPLOYEES")
        result = gen.to_dict()

        assert isinstance(result, dict)
        assert "table_name" in result

    @pytest.mark.unit
    def test_form_chaining(self):
        """Test method chaining."""
        gen = ApexFormGenerator("EMPLOYEES")
        result = gen.add_validation_rules().add_readonly_fields(["ID"]).to_dict()

        assert isinstance(result, dict)
        assert len(gen.readonly_fields) > 0


class TestApexReportGenerator:
    """Test ApexReportGenerator class."""

    @pytest.mark.unit
    def test_create_report_generator(self):
        """Create report generator from query."""
        query = "SELECT * FROM EMPLOYEES"
        gen = ApexReportGenerator(query)

        assert gen.query == query
        assert isinstance(gen.report_spec, dict)

    @pytest.mark.unit
    def test_generate_from_query(self):
        """Generate report from query."""
        query = "SELECT ID, NAME FROM EMPLOYEES"
        gen = ApexReportGenerator(query)
        result = gen.generate_from_query()

        assert result["query"] == query
        assert "report_name" in result

    @pytest.mark.unit
    def test_add_columns_formatting(self):
        """Add column formatting to report."""
        gen = ApexReportGenerator("SELECT * FROM EMPLOYEES")
        formats = {"SALARY": "currency", "START_DATE": "date"}
        gen.add_columns_formatting(formats)

        assert gen.report_spec["formatting"] == formats

    @pytest.mark.unit
    def test_add_filters(self):
        """Add filter fields to report."""
        gen = ApexReportGenerator("SELECT * FROM EMPLOYEES")
        gen.add_filters(["DEPARTMENT", "STATUS"])

        assert len(gen.filters) == 2
        assert any(f["column"] == "DEPARTMENT" for f in gen.filters)

    @pytest.mark.unit
    def test_report_to_json(self):
        """Export report as JSON."""
        gen = ApexReportGenerator("SELECT * FROM EMPLOYEES")
        json_str = gen.to_json()

        data = json.loads(json_str)
        assert "query" in data

    @pytest.mark.unit
    def test_report_chaining(self):
        """Test method chaining."""
        gen = ApexReportGenerator("SELECT * FROM EMPLOYEES")
        result = gen.add_columns_formatting({"SALARY": "currency"}).add_filters(["DEPT"]).to_dict()

        assert isinstance(result, dict)
        assert len(gen.filters) > 0


class TestApexValidationGenerator:
    """Test ApexValidationGenerator class."""

    @pytest.mark.unit
    def test_create_validation_generator(self):
        """Create validation generator."""
        gen = ApexValidationGenerator()
        assert isinstance(gen.plsql_validations, list)

    @pytest.mark.unit
    def test_generate_plsql_validations(self):
        """Generate PL/SQL validations."""
        gen = ApexValidationGenerator()
        plsql = gen.generate_plsql_validations("EMPLOYEES")

        assert "PROCEDURE" in plsql.upper()
        assert "employees" in plsql.lower()

    @pytest.mark.unit
    def test_generate_javascript_validations(self):
        """Generate JavaScript validations."""
        gen = ApexValidationGenerator()
        js = gen.generate_javascript_validations()

        assert "function" in js
        assert "validate" in js.lower()

    @pytest.mark.unit
    def test_validation_storage(self):
        """Validations stored in generator."""
        gen = ApexValidationGenerator()
        gen.generate_plsql_validations("TABLE1")
        gen.generate_plsql_validations("TABLE2")

        assert len(gen.plsql_validations) == 2


class TestApexJavaScriptGenerator:
    """Test ApexJavaScriptGenerator class."""

    @pytest.mark.unit
    def test_create_javascript_generator(self):
        """Create JavaScript generator."""
        gen = ApexJavaScriptGenerator()
        assert isinstance(gen.interactions, list)

    @pytest.mark.unit
    def test_generate_item_interactions(self):
        """Generate item interactions."""
        gen = ApexJavaScriptGenerator()
        js = gen.generate_item_interactions()

        assert "apex.item" in js
        assert "change" in js

    @pytest.mark.unit
    def test_generate_conditional_display(self):
        """Generate conditional display logic."""
        gen = ApexJavaScriptGenerator()
        js = gen.generate_conditional_display()

        assert "if" in js
        assert "show" in js or "hide" in js

    @pytest.mark.unit
    def test_generate_calculations(self):
        """Generate calculation logic."""
        gen = ApexJavaScriptGenerator()
        js = gen.generate_calculations()

        assert "parseFloat" in js or "Number" in js

    @pytest.mark.unit
    def test_javascript_storage(self):
        """JavaScript interactions stored."""
        gen = ApexJavaScriptGenerator()
        gen.generate_item_interactions()
        gen.generate_conditional_display()

        assert len(gen.interactions) == 2


class TestApexCodeGeneratorFactory:
    """Test ApexCodeGeneratorFactory class."""

    @pytest.mark.unit
    def test_factory_create_form_generator(self):
        """Factory creates form generator."""
        gen = ApexCodeGeneratorFactory.create_generator("form", table_name="EMPLOYEES")
        assert isinstance(gen, ApexFormGenerator)

    @pytest.mark.unit
    def test_factory_create_report_generator(self):
        """Factory creates report generator."""
        gen = ApexCodeGeneratorFactory.create_generator("report", query="SELECT * FROM EMPLOYEES")
        assert isinstance(gen, ApexReportGenerator)

    @pytest.mark.unit
    def test_factory_create_validation_generator(self):
        """Factory creates validation generator."""
        gen = ApexCodeGeneratorFactory.create_generator("validation")
        assert isinstance(gen, ApexValidationGenerator)

    @pytest.mark.unit
    def test_factory_create_javascript_generator(self):
        """Factory creates JavaScript generator."""
        gen = ApexCodeGeneratorFactory.create_generator("javascript")
        assert isinstance(gen, ApexJavaScriptGenerator)

    @pytest.mark.unit
    def test_factory_invalid_type(self):
        """Factory raises error for invalid type."""
        with pytest.raises(ValueError, match="Unknown generator type"):
            ApexCodeGeneratorFactory.create_generator("invalid")

    @pytest.mark.unit
    def test_factory_with_kwargs(self):
        """Factory passes kwargs correctly."""
        gen = ApexCodeGeneratorFactory.create_generator("form", table_name="PRODUCTS")
        assert gen.table_name == "PRODUCTS"


class TestIntegration:
    """Integration tests for code generators."""

    @pytest.mark.unit
    def test_full_workflow_form_generation(self):
        """Test full form generation workflow."""
        gen = ApexFormGenerator("ORDERS")
        gen.add_validation_rules().add_readonly_fields(["ORDER_ID", "CREATED_DATE"])

        form_spec = gen.to_dict()

        assert form_spec["table_name"] == "ORDERS"
        assert form_spec["form_name"] == "FORDERS_FORM"
        assert len(gen.readonly_fields) == 2

    @pytest.mark.unit
    def test_full_workflow_report_generation(self):
        """Test full report generation workflow."""
        query = "SELECT ORDER_ID, CUSTOMER_NAME, TOTAL FROM ORDERS"
        gen = ApexReportGenerator(query)
        gen.add_columns_formatting({"TOTAL": "currency"})
        gen.add_filters(["CUSTOMER_NAME", "ORDER_DATE"])

        report_spec = gen.to_dict()

        assert report_spec["query"] == query
        assert len(gen.filters) == 2

    @pytest.mark.unit
    def test_generators_independence(self):
        """Test that generators don't interfere with each other."""
        form_gen = ApexFormGenerator("TABLE1")
        report_gen = ApexReportGenerator("SELECT * FROM TABLE2")

        form_gen.add_validation_rules()
        report_gen.add_filters(["COLUMN1"])

        assert form_gen.table_name == "TABLE1"
        assert report_gen.query == "SELECT * FROM TABLE2"
