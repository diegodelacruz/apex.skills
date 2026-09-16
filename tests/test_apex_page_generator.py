#!/usr/bin/env python3
"""Unit tests for apex_page_generator.py (ApexPageSpec builder and component classes)."""

import json

import pytest

from scripts.apex_page_generator import ApexButtonSpec, ApexItemSpec, ApexPageSpec, ApexRegionSpec


class TestApexPageSpec:
    """Test ApexPageSpec builder and page creation."""

    def test_create_blank_page(self):
        """Test creating a minimal blank page."""
        page = ApexPageSpec(
            app_id=100,
            page_number=1,
            page_name="Home",
            page_type="BLANK",
        )
        assert page.app_id == 100
        assert page.page_number == 1
        assert page.page_name == "Home"
        assert page.page_type == "BLANK"
        assert len(page.regions) == 0
        assert len(page.items) == 0

    def test_add_region(self):
        """Test adding a region to a page."""
        page = ApexPageSpec(app_id=100, page_number=1, page_name="Form", page_type="FORM")
        region = page.add_region(
            region_name="Form Region",
            region_type="FORM",
            template="Standard",
            display_sequence=10,
        )
        assert len(page.regions) == 1
        assert region.region_name == "Form Region"
        assert region.region_type == "FORM"

    def test_add_item_to_region(self):
        """Test adding an item (form field) to a region."""
        page = ApexPageSpec(app_id=100, page_number=2, page_name="User Form")
        region = page.add_region(region_name="Main Region")
        item = page.add_item(
            region_name="Main Region",
            item_name="USERNAME",
            item_type="TEXT_FIELD",
            label="Username",
            required=True,
        )
        assert len(page.items) == 1
        assert item.item_name == "USERNAME"
        assert item.required is True

    def test_add_multiple_items(self):
        """Test adding multiple items to different regions."""
        page = ApexPageSpec(app_id=100, page_number=3, page_name="Login")
        region = page.add_region(region_name="Login Region")

        email = page.add_item(
            region_name="Login Region",
            item_name="EMAIL",
            item_type="TEXT_FIELD",
            label="Email",
            display_sequence=10,
        )
        password = page.add_item(
            region_name="Login Region",
            item_name="PASSWORD",
            item_type="PASSWORD",
            label="Password",
            display_sequence=20,
        )

        assert len(page.items) == 2
        assert page.items[0].item_name == "EMAIL"
        assert page.items[1].item_name == "PASSWORD"

    def test_add_button(self):
        """Test adding a button to a page."""
        page = ApexPageSpec(app_id=100, page_number=4, page_name="Submit")
        button = page.add_button(
            button_name="SUBMIT",
            button_label="Submit",
            button_position="NEXT",
            action="SUBMIT",
        )
        assert len(page.buttons) == 1
        assert button.button_name == "SUBMIT"
        assert button.action == "SUBMIT"

    def test_add_process(self):
        """Test adding a PL/SQL process to a page."""
        page = ApexPageSpec(app_id=100, page_number=5, page_name="Process")
        process = page.add_process(
            process_name="SAVE_DATA",
            process_type="PLSQL",
            point="AFTER_SUBMIT",
            pl_sql_code="INSERT INTO my_table VALUES (:P5_ITEM);",
        )
        assert len(page.processes) == 1
        assert process.process_name == "SAVE_DATA"
        assert "INSERT" in process.pl_sql_code

    def test_add_validation(self):
        """Test adding a validation rule."""
        page = ApexPageSpec(app_id=100, page_number=6, page_name="Validated")
        validation = page.add_validation(
            validation_name="VAL_EMAIL",
            validation_type="ITEM_IN_VALIDATION_ERROR",
            item_name="EMAIL",
            expression1="^[^@]+@[^@]+\\.[^@]+$",
            error_message="Invalid email format",
        )
        assert len(page.validations) == 1
        assert validation.item_name == "EMAIL"
        assert "email" in validation.error_message.lower()

    def test_add_dynamic_action(self):
        """Test adding a dynamic action."""
        page = ApexPageSpec(app_id=100, page_number=7, page_name="Dynamic")
        da = page.add_dynamic_action(
            action_name="SHOW_DETAILS",
            event="CHANGE",
            affected_element="DROPDOWN",
            action_type="SHOW",
            affected_items=["DETAILS_REGION"],
        )
        assert len(page.dynamic_actions) == 1
        assert da.action_name == "SHOW_DETAILS"
        assert "DETAILS_REGION" in da.affected_items

    def test_complex_page_spec(self):
        """Test building a complex page with multiple components."""
        page = ApexPageSpec(
            app_id=100,
            page_number=100,
            page_name="Employee Manager",
            page_type="FORM",
        )

        # Add form region
        form_region = page.add_region(
            region_name="Employee Form",
            region_type="FORM",
            template="Standard",
        )

        # Add items
        page.add_item(
            region_name="Employee Form",
            item_name="EMP_ID",
            item_type="HIDDEN",
        )
        page.add_item(
            region_name="Employee Form",
            item_name="EMP_NAME",
            item_type="TEXT_FIELD",
            label="Name",
            required=True,
        )
        page.add_item(
            region_name="Employee Form",
            item_name="EMP_EMAIL",
            item_type="TEXT_FIELD",
            label="Email",
            required=True,
        )
        page.add_item(
            region_name="Employee Form",
            item_name="EMP_DEPT",
            item_type="SELECT_LIST",
            label="Department",
        )

        # Add buttons
        page.add_button(
            button_name="SAVE",
            button_label="Save",
            button_position="NEXT",
            action="SUBMIT",
        )
        page.add_button(
            button_name="CANCEL",
            button_label="Cancel",
            button_position="DELETE",
            action="REDIRECT",
            redirect_url="f?p=100:1",
        )

        # Add process
        page.add_process(
            process_name="SAVE_EMPLOYEE",
            process_type="PLSQL",
            point="AFTER_SUBMIT",
            pl_sql_code="INSERT INTO employees (name, email, dept) VALUES (:P100_EMP_NAME, :P100_EMP_EMAIL, :P100_EMP_DEPT);",
            when_button_pressed="SAVE",
        )

        # Add validation
        page.add_validation(
            validation_name="VAL_EMAIL_FORMAT",
            validation_type="ITEM_IN_VALIDATION_ERROR",
            item_name="EMP_EMAIL",
            error_message="Please enter a valid email",
        )

        # Verify counts
        assert len(page.regions) == 1
        assert len(page.items) == 4
        assert len(page.buttons) == 2
        assert len(page.processes) == 1
        assert len(page.validations) == 1

    def test_page_spec_to_dict(self):
        """Test exporting page spec to dictionary."""
        page = ApexPageSpec(app_id=100, page_number=1, page_name="Test")
        page.add_region(region_name="Main")
        page.add_item(
            region_name="Main",
            item_name="ITEM1",
            item_type="TEXT_FIELD",
            label="Item 1",
        )

        spec_dict = page.to_dict()
        assert isinstance(spec_dict, dict)
        assert spec_dict["page"]["app_id"] == 100
        assert spec_dict["page"]["page_name"] == "Test"
        assert len(spec_dict["regions"]) == 1
        assert len(spec_dict["items"]) == 1

    def test_page_spec_to_json(self):
        """Test exporting page spec to JSON."""
        page = ApexPageSpec(app_id=100, page_number=1, page_name="JSON Test")
        page.add_region(region_name="Main")
        page.add_button(button_name="OK", button_label="OK")

        json_str = page.to_json()
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["page"]["page_name"] == "JSON Test"
        assert len(parsed["buttons"]) == 1

    def test_item_with_default_value(self):
        """Test item with default value expression."""
        page = ApexPageSpec(app_id=100, page_number=1, page_name="Test")
        page.add_region(region_name="Main")
        item = page.add_item(
            region_name="Main",
            item_name="TODAY",
            item_type="DATE",
            label="Today",
            default_value="SYSDATE",
        )
        assert item.default_value == "SYSDATE"

    def test_item_with_help_text(self):
        """Test item with help text."""
        page = ApexPageSpec(app_id=100, page_number=1, page_name="Test")
        page.add_region(region_name="Main")
        item = page.add_item(
            region_name="Main",
            item_name="AGE",
            item_type="NUMBER",
            label="Age",
            help_text="Enter your age in years",
        )
        assert item.help_text == "Enter your age in years"

    def test_nested_regions(self):
        """Test region hierarchy (parent-child regions)."""
        page = ApexPageSpec(app_id=100, page_number=1, page_name="Nested")
        parent = page.add_region(region_name="Parent Region")
        child = page.add_region(
            region_name="Child Region",
            parent_region="Parent Region",
        )
        assert child.parent_region == "Parent Region"

    def test_button_with_region(self):
        """Test button attached to a region."""
        page = ApexPageSpec(app_id=100, page_number=1, page_name="RegionButton")
        page.add_region(region_name="Actions")
        button = page.add_button(
            button_name="ADD",
            button_label="Add New",
            region_name="Actions",
            button_position="CREATE",
        )
        assert button.region_name == "Actions"

    def test_readonly_item(self):
        """Test read-only item."""
        page = ApexPageSpec(app_id=100, page_number=1, page_name="Readonly")
        page.add_region(region_name="Display")
        item = page.add_item(
            region_name="Display",
            item_name="STATUS",
            item_type="TEXT_FIELD",
            label="Status",
            read_only=True,
        )
        assert item.read_only is True


class TestApexRegionSpec:
    """Test ApexRegionSpec class."""

    def test_region_to_dict(self):
        """Test region export to dictionary."""
        region = ApexRegionSpec(
            app_id=100,
            page_number=1,
            region_name="Test Region",
            region_type="STATIC_CONTENT",
        )
        spec_dict = region.to_dict()
        assert spec_dict["region_name"] == "Test Region"
        assert spec_dict["region_type"] == "STATIC_CONTENT"


class TestApexItemSpec:
    """Test ApexItemSpec class."""

    def test_item_to_dict(self):
        """Test item export to dictionary."""
        item = ApexItemSpec(
            app_id=100,
            page_number=1,
            region_name="Main",
            item_name="TEST_ITEM",
            item_type="TEXT_FIELD",
            label="Test Item",
        )
        spec_dict = item.to_dict()
        assert spec_dict["item_name"] == "TEST_ITEM"
        assert spec_dict["item_type"] == "TEXT_FIELD"
        assert spec_dict["required"] is False


class TestApexButtonSpec:
    """Test ApexButtonSpec class."""

    def test_button_to_dict(self):
        """Test button export to dictionary."""
        button = ApexButtonSpec(
            app_id=100,
            page_number=1,
            button_name="TEST_BTN",
            button_label="Test",
            button_position="CREATE",
        )
        spec_dict = button.to_dict()
        assert spec_dict["button_name"] == "TEST_BTN"
        assert spec_dict["button_label"] == "Test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
