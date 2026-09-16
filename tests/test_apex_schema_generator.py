#!/usr/bin/env python3
"""Unit tests for apex_schema_generator.py (Oracle schema DDL builder)."""

import json

import pytest

from scripts.apex_schema_generator import (
    ApexSchemaSpec,
    Column,
    Constraint,
    FunctionSpec,
    IndexSpec,
    PackageSpec,
    ProcedureSpec,
    SequenceSpec,
    TableSpec,
    ViewSpec,
)


class TestApexSchemaSpec:
    """Test ApexSchemaSpec builder and schema creation."""

    def test_create_empty_schema(self):
        """Test creating an empty schema."""
        schema = ApexSchemaSpec(owner="SCOTT", application_id=100)
        assert schema.owner == "SCOTT"
        assert schema.application_id == 100
        assert len(schema.tables) == 0
        assert len(schema.views) == 0

    def test_create_simple_table(self):
        """Test creating a simple table."""
        schema = ApexSchemaSpec(owner="SCOTT")
        table = schema.create_table("employees")
        assert len(schema.tables) == 1
        assert table.table_name == "employees"

    def test_add_column_to_table(self):
        """Test adding columns to a table."""
        schema = ApexSchemaSpec(owner="SCOTT")
        table = schema.create_table("employees")
        table.add_column("emp_id", "NUMBER", precision=5)
        table.add_column("emp_name", "VARCHAR2", length=100)

        assert len(table.columns) == 2
        assert table.columns[0].name == "emp_id"
        assert table.columns[1].name == "emp_name"

    def test_add_constraint_to_table(self):
        """Test adding constraints to a table."""
        schema = ApexSchemaSpec(owner="SCOTT")
        table = schema.create_table("employees")
        table.add_column("emp_id", "NUMBER")
        table.add_constraint("pk_emp", "PRIMARY KEY", ["emp_id"])

        assert len(table.constraints) == 1
        assert table.constraints[0].constraint_type == "PRIMARY KEY"

    def test_create_table_with_columns_inline(self):
        """Test creating table with columns passed at creation."""
        schema = ApexSchemaSpec(owner="SCOTT")
        columns = [
            Column(name="emp_id", data_type="NUMBER", nullable=False),
            Column(name="emp_name", data_type="VARCHAR2", length=100),
            Column(name="salary", data_type="NUMBER", precision=10, scale=2),
        ]
        table = schema.create_table("employees", columns=columns)

        assert len(table.columns) == 3

    def test_create_view(self):
        """Test creating a view."""
        schema = ApexSchemaSpec(owner="SCOTT")
        view = schema.create_view(
            "v_employees",
            "SELECT emp_id, emp_name FROM employees WHERE salary > 50000",
        )

        assert len(schema.views) == 1
        assert view.view_name == "v_employees"
        assert "SELECT" in view.select_query

    def test_create_index(self):
        """Test creating an index."""
        schema = ApexSchemaSpec(owner="SCOTT")
        schema.create_table("employees")
        index = schema.create_index(
            "idx_emp_name",
            table_name="employees",
            columns=["emp_name"],
        )

        assert len(schema.indexes) == 1
        assert index.unique is False

    def test_create_unique_index(self):
        """Test creating a unique index."""
        schema = ApexSchemaSpec(owner="SCOTT")
        index = schema.create_index(
            "idx_emp_email",
            table_name="employees",
            columns=["email"],
            unique=True,
        )

        assert index.unique is True

    def test_create_sequence(self):
        """Test creating a sequence."""
        schema = ApexSchemaSpec(owner="SCOTT")
        seq = schema.create_sequence(
            "seq_emp_id",
            start_with=1,
            increment_by=1,
            cache=20,
        )

        assert len(schema.sequences) == 1
        assert seq.sequence_name == "seq_emp_id"
        assert seq.start_with == 1

    def test_create_procedure(self):
        """Test creating a procedure."""
        schema = ApexSchemaSpec(owner="SCOTT")
        proc = schema.create_procedure(
            "get_employee",
            params=[("p_emp_id", "IN", "NUMBER")],
            pl_sql_code="SELECT * FROM employees WHERE emp_id = p_emp_id;",
        )

        assert len(schema.procedures) == 1
        assert proc.procedure_name == "get_employee"
        assert len(proc.params) == 1

    def test_create_function(self):
        """Test creating a function."""
        schema = ApexSchemaSpec(owner="SCOTT")
        func = schema.create_function(
            "calc_bonus",
            params=[("p_salary", "IN", "NUMBER")],
            return_type="NUMBER",
            pl_sql_code="RETURN p_salary * 0.1;",
        )

        assert len(schema.functions) == 1
        assert func.function_name == "calc_bonus"
        assert func.return_type == "NUMBER"

    def test_create_package(self):
        """Test creating a package."""
        schema = ApexSchemaSpec(owner="SCOTT")
        pkg = schema.create_package(
            "pkg_employees",
            package_spec="PROCEDURE get_employee(p_id IN NUMBER);",
            package_body="PROCEDURE get_employee(p_id IN NUMBER) AS BEGIN NULL; END;",
        )

        assert len(schema.packages) == 1
        assert pkg.package_name == "pkg_employees"
        assert pkg.package_body is not None

    def test_complex_schema(self):
        """Test building a complex schema with multiple objects."""
        schema = ApexSchemaSpec(owner="SCOTT", application_id=100)

        # Create departments table
        dept_table = schema.create_table("departments", comment="All departments")
        dept_table.add_column("dept_id", "NUMBER", precision=3, nullable=False)
        dept_table.add_column("dept_name", "VARCHAR2", length=30, nullable=False)
        dept_table.add_constraint("pk_dept", "PRIMARY KEY", ["dept_id"])

        # Create employees table
        emp_table = schema.create_table("employees", comment="All employees")
        emp_table.add_column("emp_id", "NUMBER", precision=5, nullable=False)
        emp_table.add_column("emp_name", "VARCHAR2", length=100, nullable=False)
        emp_table.add_column("salary", "NUMBER", precision=10, scale=2)
        emp_table.add_column("dept_id", "NUMBER", precision=3)
        emp_table.add_constraint("pk_emp", "PRIMARY KEY", ["emp_id"])
        emp_table.add_constraint(
            "fk_emp_dept",
            "FOREIGN KEY",
            columns=["dept_id"],
            references_table="departments",
            references_column="dept_id",
            on_delete="SET NULL",
        )

        # Create index
        schema.create_index("idx_emp_name", "employees", ["emp_name"])

        # Create view
        schema.create_view(
            "v_emp_details",
            "SELECT e.emp_id, e.emp_name, d.dept_name FROM employees e JOIN departments d ON e.dept_id = d.dept_id",
        )

        # Create sequence
        schema.create_sequence("seq_emp_id", start_with=1000)

        # Create procedure
        schema.create_procedure(
            "get_employees_by_dept",
            params=[("p_dept_id", "IN", "NUMBER")],
            pl_sql_code="SELECT * FROM employees WHERE dept_id = p_dept_id;",
        )

        # Verify counts
        assert len(schema.tables) == 2
        assert len(schema.indexes) == 1
        assert len(schema.views) == 1
        assert len(schema.sequences) == 1
        assert len(schema.procedures) == 1

    def test_schema_to_dict(self):
        """Test exporting schema to dictionary."""
        schema = ApexSchemaSpec(owner="SCOTT")
        schema.create_table("employees")
        schema.create_view("v_employees", "SELECT * FROM employees")

        schema_dict = schema.to_dict()
        assert isinstance(schema_dict, dict)
        assert schema_dict["schema"]["owner"] == "SCOTT"
        assert len(schema_dict["tables"]) == 1
        assert len(schema_dict["views"]) == 1

    def test_schema_to_json(self):
        """Test exporting schema to JSON."""
        schema = ApexSchemaSpec(owner="SCOTT")
        schema.create_table("employees")

        json_str = schema.to_json()
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["schema"]["owner"] == "SCOTT"

    def test_generate_ddl(self):
        """Test generating DDL from schema."""
        schema = ApexSchemaSpec(owner="SCOTT")
        table = schema.create_table("employees")
        table.add_column("emp_id", "NUMBER")
        table.add_column("emp_name", "VARCHAR2", length=100)
        table.add_constraint("pk_emp", "PRIMARY KEY", ["emp_id"])

        ddl = schema.generate_ddl()
        assert "CREATE TABLE" in ddl
        assert "SCOTT.employees" in ddl
        assert "PRIMARY KEY" in ddl


class TestTableSpec:
    """Test TableSpec class."""

    def test_column_to_sql(self):
        """Test SQL generation for column."""
        col = Column(name="emp_id", data_type="NUMBER", precision=5, nullable=False)
        sql = col.to_sql()
        assert "emp_id" in sql
        assert "NUMBER(5)" in sql
        assert "NOT NULL" in sql

    def test_column_with_default(self):
        """Test column with default value."""
        col = Column(
            name="status",
            data_type="VARCHAR2",
            length=10,
            default_value="'ACTIVE'",
        )
        sql = col.to_sql()
        assert "DEFAULT 'ACTIVE'" in sql

    def test_table_to_sql(self):
        """Test SQL generation for table."""
        table = TableSpec(table_name="employees", owner="SCOTT")
        table.add_column("emp_id", "NUMBER")
        table.add_column("emp_name", "VARCHAR2", length=100)

        sql = table.to_sql()
        assert "CREATE TABLE" in sql
        assert "SCOTT.employees" in sql
        assert "emp_id" in sql

    def test_constraint_to_sql_primary_key(self):
        """Test SQL for primary key constraint."""
        constraint = Constraint(
            name="pk_emp",
            constraint_type="PRIMARY KEY",
            columns=["emp_id"],
        )
        sql = constraint.to_sql()
        assert "PRIMARY KEY" in sql
        assert "pk_emp" in sql

    def test_constraint_to_sql_foreign_key(self):
        """Test SQL for foreign key constraint."""
        constraint = Constraint(
            name="fk_emp_dept",
            constraint_type="FOREIGN KEY",
            columns=["dept_id"],
            references_table="departments",
            references_column="dept_id",
            on_delete="CASCADE",
        )
        sql = constraint.to_sql()
        assert "FOREIGN KEY" in sql
        assert "departments" in sql
        assert "CASCADE" in sql


class TestViewSpec:
    """Test ViewSpec class."""

    def test_view_to_sql(self):
        """Test SQL generation for view."""
        view = ViewSpec(
            view_name="v_employees",
            owner="SCOTT",
            select_query="SELECT * FROM employees WHERE salary > 50000",
        )
        sql = view.to_sql()
        assert "CREATE VIEW" in sql
        assert "v_employees" in sql
        assert "SELECT" in sql

    def test_view_force_to_sql(self):
        """Test FORCE VIEW SQL."""
        view = ViewSpec(
            view_name="v_test",
            owner="SCOTT",
            select_query="SELECT * FROM nonexistent_table",
            force=True,
        )
        sql = view.to_sql()
        assert "FORCE VIEW" in sql


class TestIndexSpec:
    """Test IndexSpec class."""

    def test_index_to_sql(self):
        """Test SQL generation for index."""
        index = IndexSpec(
            index_name="idx_emp_name",
            table_name="employees",
            owner="SCOTT",
            columns=["emp_name"],
        )
        sql = index.to_sql()
        assert "CREATE INDEX" in sql
        assert "idx_emp_name" in sql
        assert "emp_name" in sql

    def test_unique_index_to_sql(self):
        """Test unique index SQL."""
        index = IndexSpec(
            index_name="idx_email",
            table_name="employees",
            owner="SCOTT",
            columns=["email"],
            unique=True,
        )
        sql = index.to_sql()
        assert "UNIQUE INDEX" in sql


class TestSequenceSpec:
    """Test SequenceSpec class."""

    def test_sequence_to_sql(self):
        """Test SQL generation for sequence."""
        seq = SequenceSpec(
            sequence_name="seq_emp_id",
            owner="SCOTT",
            start_with=1000,
            increment_by=1,
        )
        sql = seq.to_sql()
        assert "CREATE SEQUENCE" in sql
        assert "START WITH 1000" in sql
        assert "INCREMENT BY 1" in sql


class TestProcedureSpec:
    """Test ProcedureSpec class."""

    def test_procedure_to_sql(self):
        """Test SQL generation for procedure."""
        proc = ProcedureSpec(
            procedure_name="get_employee",
            owner="SCOTT",
            params=[("p_emp_id", "IN", "NUMBER")],
            pl_sql_code="SELECT * INTO v_emp FROM employees WHERE emp_id = p_emp_id;",
        )
        sql = proc.to_sql()
        assert "CREATE PROCEDURE" in sql
        assert "get_employee" in sql
        assert "IN NUMBER" in sql


class TestFunctionSpec:
    """Test FunctionSpec class."""

    def test_function_to_sql(self):
        """Test SQL generation for function."""
        func = FunctionSpec(
            function_name="calc_bonus",
            owner="SCOTT",
            return_type="NUMBER",
            params=[("p_salary", "IN", "NUMBER")],
            pl_sql_code="RETURN p_salary * 0.1;",
        )
        sql = func.to_sql()
        assert "CREATE FUNCTION" in sql
        assert "calc_bonus" in sql
        assert "RETURN NUMBER" in sql


class TestPackageSpec:
    """Test PackageSpec class."""

    def test_package_to_sql(self):
        """Test SQL generation for package."""
        pkg = PackageSpec(
            package_name="pkg_employees",
            owner="SCOTT",
            package_spec="PROCEDURE get_employee(p_id IN NUMBER);",
            package_body="PROCEDURE get_employee(p_id IN NUMBER) AS BEGIN NULL; END;",
        )
        sql = pkg.to_sql()
        assert "CREATE PACKAGE" in sql
        assert "CREATE PACKAGE BODY" in sql
        assert "pkg_employees" in sql


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
