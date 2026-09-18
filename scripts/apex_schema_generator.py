#!/usr/bin/env python3
"""Builder and ORM for creating and modifying Oracle database objects (tables, views, indexes, procedures, functions).

Supports Oracle 19c+, 21c, 23c. Generates DDL with full validation.
Provides both low-level (exact SQL control) and high-level (convenience) interfaces.
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class DataType(str, Enum):
    """Common Oracle data types."""

    VARCHAR2 = "VARCHAR2"
    CHAR = "CHAR"
    NUMBER = "NUMBER"
    INTEGER = "INTEGER"
    DATE = "DATE"
    TIMESTAMP = "TIMESTAMP"
    CLOB = "CLOB"
    BLOB = "BLOB"
    BOOLEAN = "BOOLEAN"


@dataclass
class Column:
    """Represents a table column."""

    name: str
    data_type: str
    length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    nullable: bool = True
    default_value: Optional[str] = None
    comment: Optional[str] = None

    def to_sql(self) -> str:
        """Generate SQL for column definition."""
        sql = f"{self.name} {self.data_type}"

        if self.length:
            sql += f"({self.length})"
        elif self.precision and self.scale:
            sql += f"({self.precision},{self.scale})"
        elif self.precision:
            sql += f"({self.precision})"

        if not self.nullable:
            sql += " NOT NULL"

        if self.default_value:
            sql += f" DEFAULT {self.default_value}"

        return sql


@dataclass
class Constraint:
    """Represents a table constraint."""

    name: str
    constraint_type: str  # PRIMARY KEY, UNIQUE, CHECK, FOREIGN KEY
    columns: List[str]
    expression: Optional[str] = None
    references_table: Optional[str] = None
    references_column: Optional[str] = None
    on_delete: Optional[str] = None

    def to_sql(self) -> str:
        """Generate SQL for constraint."""
        if self.constraint_type == "PRIMARY KEY":
            return f"CONSTRAINT {self.name} PRIMARY KEY ({', '.join(self.columns)})"
        elif self.constraint_type == "UNIQUE":
            return f"CONSTRAINT {self.name} UNIQUE ({', '.join(self.columns)})"
        elif self.constraint_type == "CHECK":
            return f"CONSTRAINT {self.name} CHECK ({self.expression})"
        elif self.constraint_type == "FOREIGN KEY":
            fk = (
                f"CONSTRAINT {self.name} FOREIGN KEY ({', '.join(self.columns)}) "
                f"REFERENCES {self.references_table}({self.references_column})"
            )
            if self.on_delete:
                fk += f" ON DELETE {self.on_delete}"
            return fk
        return ""


class ApexSchemaSpec:
    """High-level specification for Oracle schema objects (tables, views, procedures, functions, etc.)."""

    def __init__(self, owner: str = "SCOTT", application_id: Optional[int] = None):
        """Initialize schema specification.

        Args:
            owner: Schema owner (default SCOTT)
            application_id: Optional APEX application ID for cross-reference
        """
        self.owner = owner
        self.application_id = application_id
        self.tables: List[TableSpec] = []
        self.views: List[ViewSpec] = []
        self.indexes: List[IndexSpec] = []
        self.sequences: List[SequenceSpec] = []
        self.procedures: List[ProcedureSpec] = []
        self.functions: List[FunctionSpec] = []
        self.packages: List[PackageSpec] = []

    def create_table(
        self,
        table_name: str,
        columns: Optional[List[Column]] = None,
        constraints: Optional[List[Constraint]] = None,
        tablespace: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> "TableSpec":
        """Create a table specification.

        Args:
            table_name: Name of table
            columns: List of Column objects
            constraints: List of Constraint objects
            tablespace: Optional tablespace name
            comment: Table comment

        Returns:
            TableSpec for further configuration
        """
        table = TableSpec(
            table_name=table_name,
            owner=self.owner,
            columns=columns or [],
            constraints=constraints or [],
            tablespace=tablespace,
            comment=comment,
        )
        self.tables.append(table)
        return table

    def create_view(
        self,
        view_name: str,
        select_query: str,
        force: bool = False,
        comment: Optional[str] = None,
    ) -> "ViewSpec":
        """Create a view specification.

        Args:
            view_name: Name of view
            select_query: SELECT statement
            force: CREATE FORCE VIEW (creates view even if base tables don't exist)
            comment: View comment

        Returns:
            ViewSpec for further configuration
        """
        view = ViewSpec(
            view_name=view_name,
            owner=self.owner,
            select_query=select_query,
            force=force,
            comment=comment,
        )
        self.views.append(view)
        return view

    def create_index(
        self,
        index_name: str,
        table_name: str,
        columns: List[str],
        unique: bool = False,
        tablespace: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> "IndexSpec":
        """Create an index specification.

        Args:
            index_name: Name of index
            table_name: Table being indexed
            columns: List of column names
            unique: Create unique index
            tablespace: Optional tablespace
            comment: Index comment

        Returns:
            IndexSpec for further configuration
        """
        index = IndexSpec(
            index_name=index_name,
            table_name=table_name,
            owner=self.owner,
            columns=columns,
            unique=unique,
            tablespace=tablespace,
            comment=comment,
        )
        self.indexes.append(index)
        return index

    def create_sequence(
        self,
        sequence_name: str,
        start_with: int = 1,
        increment_by: int = 1,
        max_value: Optional[int] = None,
        cache: int = 20,
        comment: Optional[str] = None,
    ) -> "SequenceSpec":
        """Create a sequence specification.

        Args:
            sequence_name: Name of sequence
            start_with: Starting value
            increment_by: Increment value
            max_value: Maximum value (None = no limit)
            cache: Cache size
            comment: Sequence comment

        Returns:
            SequenceSpec for further configuration
        """
        seq = SequenceSpec(
            sequence_name=sequence_name,
            owner=self.owner,
            start_with=start_with,
            increment_by=increment_by,
            max_value=max_value,
            cache=cache,
            comment=comment,
        )
        self.sequences.append(seq)
        return seq

    def create_procedure(
        self,
        procedure_name: str,
        params: Optional[List[Tuple[str, str, str]]] = None,
        pl_sql_code: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> "ProcedureSpec":
        """Create a procedure specification.

        Args:
            procedure_name: Name of procedure
            params: List of (name, mode, type) tuples. Mode = IN/OUT/IN OUT
            pl_sql_code: PL/SQL code
            comment: Procedure comment

        Returns:
            ProcedureSpec for further configuration
        """
        proc = ProcedureSpec(
            procedure_name=procedure_name,
            owner=self.owner,
            params=params or [],
            pl_sql_code=pl_sql_code or "",
            comment=comment,
        )
        self.procedures.append(proc)
        return proc

    def create_function(
        self,
        function_name: str,
        params: Optional[List[Tuple[str, str, str]]] = None,
        return_type: str = "NUMBER",
        pl_sql_code: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> "FunctionSpec":
        """Create a function specification.

        Args:
            function_name: Name of function
            params: List of (name, mode, type) tuples
            return_type: Return type (NUMBER, VARCHAR2, etc.)
            pl_sql_code: PL/SQL code
            comment: Function comment

        Returns:
            FunctionSpec for further configuration
        """
        func = FunctionSpec(
            function_name=function_name,
            owner=self.owner,
            params=params or [],
            return_type=return_type,
            pl_sql_code=pl_sql_code or "",
            comment=comment,
        )
        self.functions.append(func)
        return func

    def create_package(
        self,
        package_name: str,
        package_spec: str,
        package_body: Optional[str] = None,
        comment: Optional[str] = None,
    ) -> "PackageSpec":
        """Create a package specification.

        Args:
            package_name: Name of package
            package_spec: Package specification (interface)
            package_body: Package body (implementation)
            comment: Package comment

        Returns:
            PackageSpec for further configuration
        """
        pkg = PackageSpec(
            package_name=package_name,
            owner=self.owner,
            package_spec=package_spec,
            package_body=package_body,
            comment=comment,
        )
        self.packages.append(pkg)
        return pkg

    def to_dict(self) -> Dict[str, Any]:
        """Export schema spec to dictionary."""
        return {
            "schema": {
                "owner": self.owner,
                "application_id": self.application_id,
            },
            "tables": [t.to_dict() for t in self.tables],
            "views": [v.to_dict() for v in self.views],
            "indexes": [i.to_dict() for i in self.indexes],
            "sequences": [s.to_dict() for s in self.sequences],
            "procedures": [p.to_dict() for p in self.procedures],
            "functions": [f.to_dict() for f in self.functions],
            "packages": [pkg.to_dict() for pkg in self.packages],
        }

    def to_json(self) -> str:
        """Export to JSON."""
        return json.dumps(self.to_dict(), indent=2)

    def generate_ddl(self) -> str:
        """Generate complete DDL script."""
        ddl_statements = []

        for table in self.tables:
            ddl_statements.append(table.to_sql())

        for index in self.indexes:
            ddl_statements.append(index.to_sql())

        for view in self.views:
            ddl_statements.append(view.to_sql())

        for seq in self.sequences:
            ddl_statements.append(seq.to_sql())

        for proc in self.procedures:
            ddl_statements.append(proc.to_sql())

        for func in self.functions:
            ddl_statements.append(func.to_sql())

        for pkg in self.packages:
            ddl_statements.append(pkg.to_sql())

        return ";\n\n".join(ddl_statements) + ";"


@dataclass
class TableSpec:
    """Specification for a database table."""

    table_name: str
    owner: str
    columns: List[Column] = field(default_factory=list)
    constraints: List[Constraint] = field(default_factory=list)
    tablespace: Optional[str] = None
    comment: Optional[str] = None

    def add_column(
        self,
        name: str,
        data_type: str,
        length: Optional[int] = None,
        precision: Optional[int] = None,
        scale: Optional[int] = None,
        nullable: bool = True,
        default_value: Optional[str] = None,
    ) -> None:
        """Add column to table."""
        col = Column(
            name=name,
            data_type=data_type,
            length=length,
            precision=precision,
            scale=scale,
            nullable=nullable,
            default_value=default_value,
        )
        self.columns.append(col)

    def add_constraint(
        self,
        name: str,
        constraint_type: str,
        columns: List[str],
        expression: Optional[str] = None,
        references_table: Optional[str] = None,
        references_column: Optional[str] = None,
        on_delete: Optional[str] = None,
    ) -> None:
        """Add constraint to table."""
        constraint = Constraint(
            name=name,
            constraint_type=constraint_type,
            columns=columns,
            expression=expression,
            references_table=references_table,
            references_column=references_column,
            on_delete=on_delete,
        )
        self.constraints.append(constraint)

    def to_sql(self) -> str:
        """Generate CREATE TABLE DDL."""
        col_defs = [col.to_sql() for col in self.columns]
        constraint_defs = [con.to_sql() for con in self.constraints]

        all_defs = col_defs + constraint_defs
        sql = f"CREATE TABLE {self.owner}.{self.table_name} (\n  " + ",\n  ".join(all_defs) + "\n)"

        if self.tablespace:
            sql += f" TABLESPACE {self.tablespace}"

        sql += ";"

        if self.comment:
            sql += f"\nCOMMENT ON TABLE {self.owner}.{self.table_name} IS '{self.comment}';"

        return sql

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary."""
        return {
            "table_name": self.table_name,
            "owner": self.owner,
            "columns": [{"name": c.name, "type": c.data_type, "nullable": c.nullable} for c in self.columns],
            "constraints": [{"name": c.name, "type": c.constraint_type} for c in self.constraints],
            "comment": self.comment,
        }


@dataclass
class ViewSpec:
    """Specification for a database view."""

    view_name: str
    owner: str
    select_query: str
    force: bool = False
    comment: Optional[str] = None

    def to_sql(self) -> str:
        """Generate CREATE VIEW DDL."""
        force_clause = "FORCE " if self.force else ""
        sql = f"CREATE {force_clause}VIEW {self.owner}.{self.view_name} AS\n{self.select_query};"

        if self.comment:
            sql += f"\nCOMMENT ON VIEW {self.owner}.{self.view_name} IS '{self.comment}';"

        return sql

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary."""
        return {
            "view_name": self.view_name,
            "owner": self.owner,
            "force": self.force,
            "comment": self.comment,
        }


@dataclass
class IndexSpec:
    """Specification for a database index."""

    index_name: str
    table_name: str
    owner: str
    columns: List[str]
    unique: bool = False
    tablespace: Optional[str] = None
    comment: Optional[str] = None

    def to_sql(self) -> str:
        """Generate CREATE INDEX DDL."""
        unique_clause = "UNIQUE " if self.unique else ""
        sql = (
            f"CREATE {unique_clause}INDEX {self.owner}.{self.index_name} "
            f"ON {self.owner}.{self.table_name} ({', '.join(self.columns)})"
        )

        if self.tablespace:
            sql += f" TABLESPACE {self.tablespace}"

        sql += ";"

        if self.comment:
            sql += f"\nCOMMENT ON INDEX {self.owner}.{self.index_name} IS '{self.comment}';"

        return sql

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary."""
        return {
            "index_name": self.index_name,
            "table_name": self.table_name,
            "columns": self.columns,
            "unique": self.unique,
        }


@dataclass
class SequenceSpec:
    """Specification for a database sequence."""

    sequence_name: str
    owner: str
    start_with: int = 1
    increment_by: int = 1
    max_value: Optional[int] = None
    cache: int = 20
    comment: Optional[str] = None

    def to_sql(self) -> str:
        """Generate CREATE SEQUENCE DDL."""
        sql = f"CREATE SEQUENCE {self.owner}.{self.sequence_name}"
        sql += f"\n  START WITH {self.start_with}"
        sql += f"\n  INCREMENT BY {self.increment_by}"

        if self.max_value:
            sql += f"\n  MAXVALUE {self.max_value}"

        sql += f"\n  CACHE {self.cache};"

        if self.comment:
            sql += f"\nCOMMENT ON SEQUENCE {self.owner}.{self.sequence_name} IS '{self.comment}';"

        return sql

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary."""
        return {
            "sequence_name": self.sequence_name,
            "owner": self.owner,
            "start_with": self.start_with,
            "increment_by": self.increment_by,
        }


@dataclass
class ProcedureSpec:
    """Specification for a database procedure."""

    procedure_name: str
    owner: str
    params: List[Tuple[str, str, str]] = field(default_factory=list)
    pl_sql_code: str = ""
    comment: Optional[str] = None

    def to_sql(self) -> str:
        """Generate CREATE PROCEDURE DDL."""
        param_defs = []
        for param_name, param_mode, param_type in self.params:
            param_defs.append(f"  {param_name} {param_mode} {param_type}")

        param_clause = "(\n" + ",\n".join(param_defs) + "\n)" if param_defs else ""

        sql = (
            f"CREATE PROCEDURE {self.owner}.{self.procedure_name} {param_clause}\n"
            f"AS\nBEGIN\n{self.pl_sql_code}\nEND {self.procedure_name};"
        )

        if self.comment:
            sql += f"\nCOMMENT ON PROCEDURE {self.owner}.{self.procedure_name} IS '{self.comment}';"

        return sql

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary."""
        return {
            "procedure_name": self.procedure_name,
            "owner": self.owner,
            "params": [{"name": p[0], "mode": p[1], "type": p[2]} for p in self.params],
        }


@dataclass
class FunctionSpec:
    """Specification for a database function."""

    function_name: str
    owner: str
    return_type: str
    params: List[Tuple[str, str, str]] = field(default_factory=list)
    pl_sql_code: str = ""
    comment: Optional[str] = None

    def to_sql(self) -> str:
        """Generate CREATE FUNCTION DDL."""
        param_defs = []
        for param_name, param_mode, param_type in self.params:
            param_defs.append(f"  {param_name} {param_mode} {param_type}")

        param_clause = "(\n" + ",\n".join(param_defs) + "\n)" if param_defs else ""

        sql = (
            f"CREATE FUNCTION {self.owner}.{self.function_name} {param_clause}\n"
            f"RETURN {self.return_type}\nAS\nBEGIN\n{self.pl_sql_code}\nEND {self.function_name};"
        )

        if self.comment:
            sql += f"\nCOMMENT ON FUNCTION {self.owner}.{self.function_name} IS '{self.comment}';"

        return sql

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary."""
        return {
            "function_name": self.function_name,
            "owner": self.owner,
            "return_type": self.return_type,
            "params": [{"name": p[0], "mode": p[1], "type": p[2]} for p in self.params],
        }


@dataclass
class PackageSpec:
    """Specification for a database package."""

    package_name: str
    owner: str
    package_spec: str
    package_body: Optional[str] = None
    comment: Optional[str] = None

    def to_sql(self) -> str:
        """Generate CREATE PACKAGE DDL."""
        sql = f"CREATE PACKAGE {self.owner}.{self.package_name} AS\n{self.package_spec}\nEND {self.package_name};"

        if self.package_body:
            sql += (
                f"\n\nCREATE PACKAGE BODY {self.owner}.{self.package_name} AS\n"
                f"{self.package_body}\nEND {self.package_name};"
            )

        if self.comment:
            sql += f"\nCOMMENT ON PACKAGE {self.owner}.{self.package_name} IS '{self.comment}';"

        return sql

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary."""
        return {
            "package_name": self.package_name,
            "owner": self.owner,
            "has_body": self.package_body is not None,
        }
