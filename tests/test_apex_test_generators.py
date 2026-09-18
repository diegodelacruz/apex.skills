"""Unit tests for apex_test_generators module."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from apex_test_generators import (  # noqa: E402
    PerformanceTestGenerator,
    RegressionTestValidator,
    SeleniumTestGenerator,
    TestGeneratorFactory,
)


class TestSeleniumTestGenerator:
    """Test SeleniumTestGenerator class."""

    @pytest.mark.unit
    def test_create_selenium_generator(self):
        """Create Selenium test generator."""
        gen = SeleniumTestGenerator("https://apex.example.com")
        assert gen.base_url == "https://apex.example.com"
        assert isinstance(gen.test_specs, list)

    @pytest.mark.unit
    def test_init_trims_trailing_slash(self):
        """Initialize trims trailing slash from URL."""
        gen = SeleniumTestGenerator("https://apex.example.com/")
        assert gen.base_url == "https://apex.example.com"

    @pytest.mark.unit
    def test_generate_element_interaction_test(self):
        """Generate element interaction test."""
        gen = SeleniumTestGenerator("https://apex.example.com")
        test = gen.generate_element_interaction_test(page_id=1, item_id="P1_USERNAME", interaction_type="input")

        assert test["type"] == "element_interaction"
        assert test["page_id"] == 1
        assert test["item_id"] == "P1_USERNAME"

    @pytest.mark.unit
    def test_generate_form_submission_test(self):
        """Generate form submission test."""
        gen = SeleniumTestGenerator("https://apex.example.com")
        test = gen.generate_form_submission_test(
            page_id=2, form_items=["P2_NAME", "P2_EMAIL"], expected_message="Success"
        )

        assert test["type"] == "form_submission"
        assert len(test["form_items"]) == 2
        assert test["expected_message"] == "Success"

    @pytest.mark.unit
    def test_generate_navigation_test(self):
        """Generate navigation test."""
        gen = SeleniumTestGenerator("https://apex.example.com")
        test = gen.generate_navigation_test(page_id=1, target_page=2, button_id="btnNext")

        assert test["type"] == "navigation"
        assert test["source_page"] == 1
        assert test["target_page"] == 2

    @pytest.mark.unit
    def test_add_xpath_locator(self):
        """Add XPath locator to test."""
        gen = SeleniumTestGenerator("https://apex.example.com")
        gen.generate_element_interaction_test(page_id=1, item_id="P1_TEST", interaction_type="click")
        gen.add_xpath_locator("//input[@id='P1_TEST']", "Username field")

        assert gen.test_specs[-1]["locator"]["type"] == "xpath"

    @pytest.mark.unit
    def test_add_wait_strategy(self):
        """Configure wait strategy."""
        gen = SeleniumTestGenerator("https://apex.example.com")
        gen.add_wait_strategy("explicit", timeout=20)

        assert gen.wait_strategy == "explicit"
        assert gen.wait_timeout == 20

    @pytest.mark.unit
    def test_to_json(self):
        """Export tests as JSON."""
        gen = SeleniumTestGenerator("https://apex.example.com")
        gen.generate_element_interaction_test(page_id=1, item_id="P1_TEST", interaction_type="input")
        json_str = gen.to_json()

        data = json.loads(json_str)
        assert "tests" in data
        assert len(data["tests"]) == 1

    @pytest.mark.unit
    def test_to_dict(self):
        """Export tests as dictionary."""
        gen = SeleniumTestGenerator("https://apex.example.com")
        gen.generate_element_interaction_test(page_id=1, item_id="P1_TEST", interaction_type="input")
        result = gen.to_dict()

        assert isinstance(result, dict)
        assert "tests" in result

    @pytest.mark.unit
    def test_method_chaining(self):
        """Test method chaining."""
        gen = SeleniumTestGenerator("https://apex.example.com")
        gen.generate_element_interaction_test(page_id=1, item_id="P1_TEST", interaction_type="input")
        gen.add_xpath_locator("//input[@id='P1_TEST']")
        gen.add_wait_strategy("explicit")

        assert len(gen.test_specs) == 1
        assert gen.wait_strategy == "explicit"


class TestPerformanceTestGenerator:
    """Test PerformanceTestGenerator class."""

    @pytest.mark.unit
    def test_create_performance_generator(self):
        """Create performance test generator."""
        gen = PerformanceTestGenerator("https://apex.example.com")
        assert gen.base_url == "https://apex.example.com"
        assert isinstance(gen.performance_tests, list)

    @pytest.mark.unit
    def test_generate_load_test(self):
        """Generate load test."""
        gen = PerformanceTestGenerator("https://apex.example.com")
        test = gen.generate_load_test(page_id=1, concurrent_users=10, duration_seconds=60)

        assert test["type"] == "load_test"
        assert test["concurrent_users"] == 10
        assert test["duration_seconds"] == 60

    @pytest.mark.unit
    def test_generate_stress_test(self):
        """Generate stress test."""
        gen = PerformanceTestGenerator("https://apex.example.com")
        test = gen.generate_stress_test(page_id=1, start_users=5, max_users=100, increment=5)

        assert test["type"] == "stress_test"
        assert test["start_users"] == 5
        assert test["max_users"] == 100

    @pytest.mark.unit
    def test_generate_endurance_test(self):
        """Generate endurance test."""
        gen = PerformanceTestGenerator("https://apex.example.com")
        test = gen.generate_endurance_test(page_id=1, concurrent_users=50, duration_seconds=3600)

        assert test["type"] == "endurance_test"
        assert test["concurrent_users"] == 50
        assert test["duration_seconds"] == 3600

    @pytest.mark.unit
    def test_performance_to_json(self):
        """Export performance tests as JSON."""
        gen = PerformanceTestGenerator("https://apex.example.com")
        gen.generate_load_test(page_id=1, concurrent_users=10, duration_seconds=60)
        json_str = gen.to_json()

        data = json.loads(json_str)
        assert "performance_tests" in data
        assert len(data["performance_tests"]) == 1

    @pytest.mark.unit
    def test_performance_to_dict(self):
        """Export performance tests as dictionary."""
        gen = PerformanceTestGenerator("https://apex.example.com")
        gen.generate_load_test(page_id=1, concurrent_users=10, duration_seconds=60)
        result = gen.to_dict()

        assert isinstance(result, dict)
        assert "performance_tests" in result


class TestRegressionTestValidator:
    """Test RegressionTestValidator class."""

    @pytest.mark.unit
    def test_create_validator(self):
        """Create regression test validator."""
        validator = RegressionTestValidator()
        assert validator.baseline is None
        assert validator.deviation_threshold == 0.10

    @pytest.mark.unit
    def test_compare_results_create_baseline(self):
        """Compare results creates baseline if not exists."""
        validator = RegressionTestValidator()
        current = {"test1": {"response_time": 100}}

        result = validator.compare_results(current)

        assert result["status"] == "baseline_created"
        assert validator.baseline is not None

    @pytest.mark.unit
    def test_compare_results_with_baseline(self):
        """Compare current results to baseline."""
        validator = RegressionTestValidator()
        baseline = {"test1": {"response_time": 100}}
        current = {"test1": {"response_time": 105}}

        result = validator.compare_results(current, baseline)

        assert "matches" in result
        assert "deviations" in result
        assert "details" in result

    @pytest.mark.unit
    def test_flag_regressions(self):
        """Flag tests with regressions."""
        validator = RegressionTestValidator()
        comparison = {
            "details": [
                {"test": "test1", "status": "deviation"},
                {"test": "test2", "status": "pass"},
            ]
        }

        regressions = validator.flag_regressions(comparison)

        assert len(regressions) == 1
        assert regressions[0]["test"] == "test1"

    @pytest.mark.unit
    def test_generate_regression_report(self):
        """Generate regression test report."""
        validator = RegressionTestValidator()
        regressions = [{"test": "test1", "status": "deviation"}]

        report = validator.generate_regression_report(regressions)

        assert report["status"] == "fail"
        assert report["regression_count"] == 1

    @pytest.mark.unit
    def test_regression_to_json(self):
        """Export validator state as JSON."""
        validator = RegressionTestValidator()
        validator.baseline = {"test1": {"value": 100}}
        validator.current_results = {"test1": {"value": 105}}

        json_str = validator.to_json()
        data = json.loads(json_str)

        assert "baseline" in data
        assert "current" in data

    @pytest.mark.unit
    def test_deviation_threshold_customization(self):
        """Customize deviation threshold."""
        validator = RegressionTestValidator()
        validator.deviation_threshold = 0.20

        assert validator.deviation_threshold == 0.20


class TestTestGeneratorFactory:
    """Test TestGeneratorFactory class."""

    @pytest.mark.unit
    def test_factory_create_selenium(self):
        """Factory creates Selenium generator."""
        gen = TestGeneratorFactory.create_generator("selenium", base_url="https://apex.example.com")
        assert isinstance(gen, SeleniumTestGenerator)

    @pytest.mark.unit
    def test_factory_create_performance(self):
        """Factory creates performance generator."""
        gen = TestGeneratorFactory.create_generator("performance", base_url="https://apex.example.com")
        assert isinstance(gen, PerformanceTestGenerator)

    @pytest.mark.unit
    def test_factory_create_regression(self):
        """Factory creates regression validator."""
        validator = TestGeneratorFactory.create_generator("regression")
        assert isinstance(validator, RegressionTestValidator)

    @pytest.mark.unit
    def test_factory_invalid_type(self):
        """Factory raises error for invalid type."""
        with pytest.raises(ValueError, match="Unknown generator type"):
            TestGeneratorFactory.create_generator("invalid")

    @pytest.mark.unit
    def test_factory_with_kwargs(self):
        """Factory passes kwargs correctly."""
        gen = TestGeneratorFactory.create_generator("selenium", base_url="https://custom.example.com")
        assert gen.base_url == "https://custom.example.com"


class TestIntegration:
    """Integration tests for test generators."""

    @pytest.mark.unit
    def test_full_selenium_workflow(self):
        """Test full Selenium test generation workflow."""
        gen = SeleniumTestGenerator("https://apex.example.com")
        gen.add_wait_strategy("explicit", timeout=15)
        gen.generate_element_interaction_test(page_id=1, item_id="P1_USERNAME", interaction_type="input")
        gen.generate_form_submission_test(page_id=2, form_items=["P2_NAME", "P2_EMAIL"], expected_message="Success")

        result = gen.to_dict()

        assert len(result["tests"]) == 2
        assert result["wait_strategy"] == "explicit"

    @pytest.mark.unit
    def test_full_performance_workflow(self):
        """Test full performance testing workflow."""
        gen = PerformanceTestGenerator("https://apex.example.com")
        gen.generate_load_test(page_id=1, concurrent_users=10, duration_seconds=60)
        gen.generate_stress_test(page_id=2, start_users=5, max_users=100)

        result = gen.to_dict()

        assert len(result["performance_tests"]) == 2
        assert result["performance_tests"][0]["type"] == "load_test"

    @pytest.mark.unit
    def test_regression_validation_workflow(self):
        """Test regression validation workflow."""
        validator = RegressionTestValidator()
        baseline = {"test1": {"response_time": 100, "throughput": 50}}
        current = {"test1": {"response_time": 105, "throughput": 49}}

        comparison = validator.compare_results(current, baseline)
        regressions = validator.flag_regressions(comparison)
        report = validator.generate_regression_report(regressions)

        assert isinstance(report, dict)
        assert "status" in report
