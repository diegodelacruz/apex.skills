#!/usr/bin/env python3
"""Oracle APEX automated test generation framework."""

import json
from typing import Any, Dict, List, Optional


class SeleniumTestGenerator:
    """Generate Selenium tests for APEX UI interactions."""

    def __init__(self, base_url: str):
        """Initialize Selenium test generator.

        Args:
            base_url: APEX instance base URL
        """
        self.base_url = base_url.rstrip("/")
        self.test_specs: List[Dict[str, Any]] = []
        self.wait_strategy = "implicit"
        self.wait_timeout = 10

    def generate_element_interaction_test(
        self,
        page_id: int,
        item_id: str,
        interaction_type: str,
        test_values: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Generate element interaction test.

        Args:
            page_id: APEX page number
            item_id: Item ID (P{page_id}_{name})
            interaction_type: Type (input, click, select, etc)
            test_values: Values to test with

        Returns:
            Test specification dictionary
        """
        test_spec = {
            "type": "element_interaction",
            "page_id": page_id,
            "item_id": item_id,
            "interaction": interaction_type,
            "locator": {"type": "id", "value": item_id},
            "test_values": test_values or [],
            "wait_timeout": self.wait_timeout,
        }
        self.test_specs.append(test_spec)
        return test_spec

    def generate_form_submission_test(
        self,
        page_id: int,
        form_items: List[str],
        expected_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate form submission test.

        Args:
            page_id: APEX page number
            form_items: List of item IDs in form
            expected_message: Expected success message

        Returns:
            Test specification dictionary
        """
        test_spec = {
            "type": "form_submission",
            "page_id": page_id,
            "form_items": form_items,
            "expected_message": expected_message,
            "validation_enabled": True,
        }
        self.test_specs.append(test_spec)
        return test_spec

    def generate_navigation_test(
        self,
        page_id: int,
        target_page: int,
        button_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate page navigation test.

        Args:
            page_id: Starting page ID
            target_page: Target page ID
            button_id: Button element ID (optional)

        Returns:
            Test specification dictionary
        """
        test_spec = {
            "type": "navigation",
            "source_page": page_id,
            "target_page": target_page,
            "button_id": button_id,
            "wait_for_page_load": True,
        }
        self.test_specs.append(test_spec)
        return test_spec

    def add_xpath_locator(self, xpath: str, description: Optional[str] = None) -> "SeleniumTestGenerator":
        """Add XPath locator to last test.

        Args:
            xpath: XPath expression
            description: Locator description

        Returns:
            Self for method chaining
        """
        if self.test_specs:
            self.test_specs[-1]["locator"] = {
                "type": "xpath",
                "value": xpath,
                "description": description,
            }
        return self

    def add_wait_strategy(self, strategy: str, timeout: int = 10) -> "SeleniumTestGenerator":
        """Configure wait strategy.

        Args:
            strategy: Wait type (implicit, explicit, dynamic)
            timeout: Timeout in seconds

        Returns:
            Self for method chaining
        """
        self.wait_strategy = strategy
        self.wait_timeout = timeout
        return self

    def to_json(self) -> str:
        """Export tests as JSON.

        Returns:
            JSON string of test specifications
        """
        return json.dumps({"tests": self.test_specs, "wait_strategy": self.wait_strategy}, indent=2)

    def to_dict(self) -> Dict[str, Any]:
        """Export tests as dictionary.

        Returns:
            Dictionary of test specifications
        """
        return {"tests": self.test_specs, "wait_strategy": self.wait_strategy}


class PerformanceTestGenerator:
    """Generate performance testing scenarios."""

    def __init__(self, base_url: str):
        """Initialize performance test generator.

        Args:
            base_url: APEX instance base URL
        """
        self.base_url = base_url.rstrip("/")
        self.performance_tests: List[Dict[str, Any]] = []

    def generate_load_test(
        self,
        page_id: int,
        concurrent_users: int,
        duration_seconds: int,
        ramp_up_time: int = 60,
    ) -> Dict[str, Any]:
        """Generate load test scenario.

        Args:
            page_id: APEX page to test
            concurrent_users: Number of concurrent users
            duration_seconds: Test duration in seconds
            ramp_up_time: Time to reach concurrent users

        Returns:
            Test specification dictionary
        """
        test_spec = {
            "type": "load_test",
            "page_id": page_id,
            "concurrent_users": concurrent_users,
            "duration_seconds": duration_seconds,
            "ramp_up_seconds": ramp_up_time,
            "metrics": ["response_time", "throughput", "error_rate"],
        }
        self.performance_tests.append(test_spec)
        return test_spec

    def generate_stress_test(
        self,
        page_id: int,
        start_users: int,
        max_users: int,
        increment: int = 5,
    ) -> Dict[str, Any]:
        """Generate stress test scenario.

        Args:
            page_id: APEX page to test
            start_users: Starting number of users
            max_users: Maximum users before timeout
            increment: User increment per step

        Returns:
            Test specification dictionary
        """
        test_spec = {
            "type": "stress_test",
            "page_id": page_id,
            "start_users": start_users,
            "max_users": max_users,
            "increment": increment,
            "stop_on_failure": True,
            "metrics": ["breaking_point", "error_threshold"],
        }
        self.performance_tests.append(test_spec)
        return test_spec

    def generate_endurance_test(self, page_id: int, concurrent_users: int, duration_seconds: int) -> Dict[str, Any]:
        """Generate endurance test scenario.

        Args:
            page_id: APEX page to test
            concurrent_users: Number of concurrent users
            duration_seconds: Test duration in seconds (typically 3600+)

        Returns:
            Test specification dictionary
        """
        test_spec = {
            "type": "endurance_test",
            "page_id": page_id,
            "concurrent_users": concurrent_users,
            "duration_seconds": duration_seconds,
            "check_memory_leaks": True,
            "check_connection_leaks": True,
            "metrics": ["memory_stability", "response_time_trend"],
        }
        self.performance_tests.append(test_spec)
        return test_spec

    def to_json(self) -> str:
        """Export performance tests as JSON.

        Returns:
            JSON string of test specifications
        """
        return json.dumps({"performance_tests": self.performance_tests}, indent=2)

    def to_dict(self) -> Dict[str, Any]:
        """Export performance tests as dictionary.

        Returns:
            Dictionary of test specifications
        """
        return {"performance_tests": self.performance_tests}


class RegressionTestValidator:
    """Validate regression tests against baselines."""

    def __init__(self):
        """Initialize regression test validator."""
        self.baseline: Optional[Dict[str, Any]] = None
        self.current_results: Optional[Dict[str, Any]] = None
        self.deviation_threshold = 0.10  # 10% deviation threshold

    def compare_results(
        self, current_results: Dict[str, Any], baseline: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compare current results to baseline.

        Args:
            current_results: Current test results
            baseline: Baseline results (optional, uses stored if not provided)

        Returns:
            Comparison report dictionary
        """
        self.current_results = current_results

        if baseline:
            self.baseline = baseline

        if not self.baseline:
            self.baseline = current_results
            return {"status": "baseline_created", "test_count": len(current_results)}

        comparison = {"matches": 0, "deviations": 0, "details": []}

        for test_name, current_metrics in current_results.items():
            baseline_metrics = self.baseline.get(test_name, {})

            if not baseline_metrics:
                comparison["details"].append(
                    {
                        "test": test_name,
                        "status": "new_test",
                        "baseline": None,
                        "current": current_metrics,
                    }
                )
                continue

            # Compare metrics
            has_deviation = False
            for metric_name, current_value in current_metrics.items():
                baseline_value = baseline_metrics.get(metric_name, 0)

                if baseline_value == 0:
                    continue

                deviation = abs(current_value - baseline_value) / baseline_value
                if deviation > self.deviation_threshold:
                    has_deviation = True

            if has_deviation:
                comparison["deviations"] += 1
                comparison["details"].append(
                    {
                        "test": test_name,
                        "status": "deviation",
                        "baseline": baseline_metrics,
                        "current": current_metrics,
                    }
                )
            else:
                comparison["matches"] += 1

        return comparison

    def flag_regressions(self, comparison: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Flag tests with regressions.

        Args:
            comparison: Comparison report from compare_results

        Returns:
            List of regressed tests
        """
        regressions = []
        for detail in comparison.get("details", []):
            if detail["status"] in ("deviation", "failure"):
                regressions.append(detail)
        return regressions

    def generate_regression_report(self, regressions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate regression test report.

        Args:
            regressions: List of regressed tests

        Returns:
            Report dictionary
        """
        report = {
            "status": "pass" if not regressions else "fail",
            "regression_count": len(regressions),
            "deviation_threshold": self.deviation_threshold,
            "regressions": regressions,
        }
        return report

    def to_json(self) -> str:
        """Export report as JSON.

        Returns:
            JSON string representation
        """
        return json.dumps(
            {
                "baseline": self.baseline,
                "current": self.current_results,
                "threshold": self.deviation_threshold,
            },
            indent=2,
        )


class TestGeneratorFactory:
    """Factory for creating test generators."""

    @staticmethod
    def create_generator(gen_type: str, **kwargs) -> Any:
        """Create test generator by type.

        Args:
            gen_type: Generator type (selenium, performance, regression)
            **kwargs: Arguments for generator initialization

        Returns:
            Generator instance

        Raises:
            ValueError: If generator type is unknown
        """
        if gen_type == "selenium":
            return SeleniumTestGenerator(**kwargs)
        if gen_type == "performance":
            return PerformanceTestGenerator(**kwargs)
        if gen_type == "regression":
            return RegressionTestValidator()

        raise ValueError(f"Unknown generator type: {gen_type}")
