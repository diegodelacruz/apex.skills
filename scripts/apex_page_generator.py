#!/usr/bin/env python3
"""In-memory APEX page specifications.

This module does not connect to Oracle and must not be treated as an APEX CRUD
adapter. In particular it never accesses ``WWV_FLOW_*`` tables. Apply a reviewed
specification only through the authenticated App Builder or native APEX
export/import route governed by ``controlled_capabilities``.
"""

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ApexObject:
    """Base class for all APEX objects."""

    app_id: int
    object_type: str
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary."""
        return {
            "app_id": self.app_id,
            "object_type": self.object_type,
            "properties": self.properties,
        }

    def to_json(self) -> str:
        """Export to JSON."""
        return json.dumps(self.to_dict(), indent=2, default=str)


class ApexPageSpec:
    """High-level specification for an APEX page with regions, items, buttons, processes."""

    def __init__(
        self,
        app_id: int,
        page_number: int,
        page_name: str,
        page_type: str = "BLANK",
        parent_tab: Optional[str] = None,
        page_mode: str = "NORMAL",
        authentication_required: bool = True,
    ):
        """Initialize page specification.

        Args:
            app_id: Oracle APEX application ID
            page_number: Page number (must be unique within app)
            page_name: Display name of the page
            page_type: BLANK, FORM, REPORT, DASHBOARD, etc.
            parent_tab: Optional parent tab (for navigation hierarchy)
            page_mode: NORMAL, MODAL, etc.
            authentication_required: Require user to be authenticated
        """
        self.app_id = app_id
        self.page_number = page_number
        self.page_name = page_name
        self.page_type = page_type
        self.parent_tab = parent_tab
        self.page_mode = page_mode
        self.authentication_required = authentication_required
        self.regions: List[ApexRegionSpec] = []
        self.items: List[ApexItemSpec] = []
        self.buttons: List[ApexButtonSpec] = []
        self.processes: List[ApexProcessSpec] = []
        self.validations: List[ApexValidationSpec] = []
        self.dynamic_actions: List[ApexDynamicActionSpec] = []

    def add_region(
        self,
        region_name: str,
        region_type: str = "STATIC_CONTENT",
        template: Optional[str] = None,
        display_sequence: int = 10,
        parent_region: Optional[str] = None,
    ) -> "ApexRegionSpec":
        """Add region to page.

        Args:
            region_name: Display name
            region_type: STATIC_CONTENT, FORM, REPORT, CHART, etc.
            template: Region template name
            display_sequence: Display order
            parent_region: Parent region name for nesting

        Returns:
            ApexRegionSpec for further configuration
        """
        region = ApexRegionSpec(
            app_id=self.app_id,
            page_number=self.page_number,
            region_name=region_name,
            region_type=region_type,
            template=template,
            display_sequence=display_sequence,
            parent_region=parent_region,
        )
        self.regions.append(region)
        return region

    def add_item(
        self,
        region_name: str,
        item_name: str,
        item_type: str,
        label: Optional[str] = None,
        display_sequence: int = 10,
        default_value: Optional[str] = None,
        help_text: Optional[str] = None,
        required: bool = False,
        read_only: bool = False,
    ) -> "ApexItemSpec":
        """Add item to region.

        Args:
            region_name: Target region name
            item_name: Item name (P<page>_<item_name>)
            item_type: TEXT_FIELD, PASSWORD, TEXTAREA, SELECT_LIST, CHECKBOX, etc.
            label: Display label
            display_sequence: Display order
            default_value: Default value expression
            help_text: Help text for user
            required: Mark as required
            read_only: Mark as read-only

        Returns:
            ApexItemSpec for further configuration
        """
        item = ApexItemSpec(
            app_id=self.app_id,
            page_number=self.page_number,
            region_name=region_name,
            item_name=item_name,
            item_type=item_type,
            label=label or item_name,
            display_sequence=display_sequence,
            default_value=default_value,
            help_text=help_text,
            required=required,
            read_only=read_only,
        )
        self.items.append(item)
        return item

    def add_button(
        self,
        button_name: str,
        button_label: str,
        region_name: Optional[str] = None,
        button_position: str = "CREATE",
        display_sequence: int = 20,
        action: Optional[str] = None,
        redirect_url: Optional[str] = None,
    ) -> "ApexButtonSpec":
        """Add button to page or region.

        Args:
            button_name: Button name
            button_label: Display label
            region_name: Target region (None = page-level button)
            button_position: CREATE, PREVIOUS, NEXT, DELETE, EDIT, SAVE, RESET, CANCEL, etc.
            display_sequence: Display order
            action: Button action (SUBMIT, REDIRECT, EXECUTE_PLSQL, etc.)
            redirect_url: Target URL if action is REDIRECT

        Returns:
            ApexButtonSpec for further configuration
        """
        button = ApexButtonSpec(
            app_id=self.app_id,
            page_number=self.page_number,
            button_name=button_name,
            button_label=button_label,
            region_name=region_name,
            button_position=button_position,
            display_sequence=display_sequence,
            action=action,
            redirect_url=redirect_url,
        )
        self.buttons.append(button)
        return button

    def add_process(
        self,
        process_name: str,
        process_type: str = "PLSQL",
        point: str = "AFTER_SUBMIT",
        pl_sql_code: Optional[str] = None,
        when_button_pressed: Optional[str] = None,
    ) -> "ApexProcessSpec":
        """Add server-side process to page.

        Args:
            process_name: Process name
            process_type: PLSQL, CLOSE_DIALOG, etc.
            point: BEFORE_HEADER, AFTER_SUBMIT, BEFORE_FOOTER, etc.
            pl_sql_code: PL/SQL code to execute
            when_button_pressed: Execute only when this button is pressed

        Returns:
            ApexProcessSpec for further configuration
        """
        process = ApexProcessSpec(
            app_id=self.app_id,
            page_number=self.page_number,
            process_name=process_name,
            process_type=process_type,
            point=point,
            pl_sql_code=pl_sql_code,
            when_button_pressed=when_button_pressed,
        )
        self.processes.append(process)
        return process

    def add_validation(
        self,
        validation_name: str,
        validation_type: str = "ITEM_IN_VALIDATION_ERROR",
        item_name: Optional[str] = None,
        expression1: Optional[str] = None,
        expression2: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> "ApexValidationSpec":
        """Add validation to page or item.

        Args:
            validation_name: Validation name
            validation_type: Item-level or page-level validation type
            item_name: Target item (None = page-level)
            expression1: First validation expression
            expression2: Second validation expression (for range, etc.)
            error_message: Error message if validation fails

        Returns:
            ApexValidationSpec for further configuration
        """
        validation = ApexValidationSpec(
            app_id=self.app_id,
            page_number=self.page_number,
            validation_name=validation_name,
            validation_type=validation_type,
            item_name=item_name,
            expression1=expression1,
            expression2=expression2,
            error_message=error_message,
        )
        self.validations.append(validation)
        return validation

    def add_dynamic_action(
        self,
        action_name: str,
        event: str = "CHANGE",
        affected_element: Optional[str] = None,
        action_type: str = "SHOW",
        affected_items: Optional[List[str]] = None,
    ) -> "ApexDynamicActionSpec":
        """Add dynamic action (client-side JavaScript/AJAX behavior).

        Args:
            action_name: Action name
            event: CHANGE, CLICK, KEYUP, etc.
            affected_element: Item or region that triggers the action
            action_type: SHOW, HIDE, REFRESH, SUBMIT, EXECUTE_JAVASCRIPT, etc.
            affected_items: Items affected by the action

        Returns:
            ApexDynamicActionSpec for further configuration
        """
        da = ApexDynamicActionSpec(
            app_id=self.app_id,
            page_number=self.page_number,
            action_name=action_name,
            event=event,
            affected_element=affected_element,
            action_type=action_type,
            affected_items=affected_items or [],
        )
        self.dynamic_actions.append(da)
        return da

    def to_dict(self) -> Dict[str, Any]:
        """Export page spec to dictionary."""
        return {
            "page": {
                "app_id": self.app_id,
                "page_number": self.page_number,
                "page_name": self.page_name,
                "page_type": self.page_type,
                "parent_tab": self.parent_tab,
                "page_mode": self.page_mode,
                "authentication_required": self.authentication_required,
            },
            "regions": [r.to_dict() for r in self.regions],
            "items": [i.to_dict() for i in self.items],
            "buttons": [b.to_dict() for b in self.buttons],
            "processes": [p.to_dict() for p in self.processes],
            "validations": [v.to_dict() for v in self.validations],
            "dynamic_actions": [da.to_dict() for da in self.dynamic_actions],
        }

    def to_json(self) -> str:
        """Export to JSON."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class ApexRegionSpec:
    """Specification for an APEX region."""

    app_id: int
    page_number: int
    region_name: str
    region_type: str = "STATIC_CONTENT"
    template: Optional[str] = None
    display_sequence: int = 10
    parent_region: Optional[str] = None
    source: Optional[str] = None
    source_type: str = "NONE"
    height: Optional[int] = None
    width: Optional[int] = None
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary."""
        return {
            "region_name": self.region_name,
            "region_type": self.region_type,
            "template": self.template,
            "display_sequence": self.display_sequence,
            "parent_region": self.parent_region,
            "source": self.source,
            "source_type": self.source_type,
            "height": self.height,
            "width": self.width,
            "properties": self.properties,
        }


@dataclass
class ApexItemSpec:
    """Specification for an APEX item (form field)."""

    app_id: int
    page_number: int
    region_name: str
    item_name: str
    item_type: str
    label: str
    display_sequence: int = 10
    default_value: Optional[str] = None
    help_text: Optional[str] = None
    required: bool = False
    read_only: bool = False
    colspan: int = 1
    rowspan: int = 1
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary."""
        return {
            "item_name": self.item_name,
            "item_type": self.item_type,
            "label": self.label,
            "display_sequence": self.display_sequence,
            "default_value": self.default_value,
            "help_text": self.help_text,
            "required": self.required,
            "read_only": self.read_only,
            "colspan": self.colspan,
            "rowspan": self.rowspan,
            "properties": self.properties,
        }


@dataclass
class ApexButtonSpec:
    """Specification for an APEX button."""

    app_id: int
    page_number: int
    button_name: str
    button_label: str
    region_name: Optional[str] = None
    button_position: str = "CREATE"
    display_sequence: int = 20
    action: Optional[str] = None
    redirect_url: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary."""
        return {
            "button_name": self.button_name,
            "button_label": self.button_label,
            "region_name": self.region_name,
            "button_position": self.button_position,
            "display_sequence": self.display_sequence,
            "action": self.action,
            "redirect_url": self.redirect_url,
            "properties": self.properties,
        }


@dataclass
class ApexProcessSpec:
    """Specification for a server-side process."""

    app_id: int
    page_number: int
    process_name: str
    process_type: str = "PLSQL"
    point: str = "AFTER_SUBMIT"
    pl_sql_code: Optional[str] = None
    when_button_pressed: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary."""
        return {
            "process_name": self.process_name,
            "process_type": self.process_type,
            "point": self.point,
            "pl_sql_code": self.pl_sql_code,
            "when_button_pressed": self.when_button_pressed,
            "properties": self.properties,
        }


@dataclass
class ApexValidationSpec:
    """Specification for a validation rule."""

    app_id: int
    page_number: int
    validation_name: str
    validation_type: str
    item_name: Optional[str] = None
    expression1: Optional[str] = None
    expression2: Optional[str] = None
    error_message: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary."""
        return {
            "validation_name": self.validation_name,
            "validation_type": self.validation_type,
            "item_name": self.item_name,
            "expression1": self.expression1,
            "expression2": self.expression2,
            "error_message": self.error_message,
            "properties": self.properties,
        }


@dataclass
class ApexDynamicActionSpec:
    """Specification for a dynamic action (client-side behavior)."""

    app_id: int
    page_number: int
    action_name: str
    event: str = "CHANGE"
    affected_element: Optional[str] = None
    action_type: str = "SHOW"
    affected_items: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary."""
        return {
            "action_name": self.action_name,
            "event": self.event,
            "affected_element": self.affected_element,
            "action_type": self.action_type,
            "affected_items": self.affected_items,
            "properties": self.properties,
        }
