"""
Test Generator Module
Automatically generates unit tests for policy functions.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta


class TestGenerator:
    """Generates comprehensive unit tests for policy functions"""

    def __init__(self, company_id: str):
        self.company_id = company_id

    def generate_tests(self, parsed_rules: Dict[str, Any]) -> str:
        """
        Generate complete test suite for policy functions

        Args:
            parsed_rules: Parsed policy rules

        Returns:
            String containing pytest test code
        """
        test_parts = []

        # Add header and imports
        test_parts.append(self._generate_test_header())

        # Generate tests for each function type
        if parsed_rules.get('cabin_class_rules'):
            test_parts.append(self._generate_cabin_class_tests())

        if parsed_rules.get('cost_approval_rules'):
            test_parts.append(self._generate_cost_approval_tests())

        if parsed_rules.get('advance_booking_rules'):
            test_parts.append(self._generate_advance_booking_tests())

        if parsed_rules.get('airline_preference_rules'):
            test_parts.append(self._generate_airline_preference_tests())

        if parsed_rules.get('baggage_rules'):
            test_parts.append(self._generate_baggage_tests())

        # Add integration tests
        test_parts.append(self._generate_integration_tests())

        return '\n\n'.join(test_parts)

    def _generate_test_header(self) -> str:
        """Generate test file header"""
        return f'''"""
Generated Unit Tests for {self.company_id} Policy Functions
Auto-generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Run with: pytest test_{self.company_id}.py -v
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Import the generated policy module
# Adjust path as needed
sys.path.insert(0, str(Path(__file__).parent.parent / "generated" / "functions"))

try:
    import {self.company_id} as policy
except ImportError:
    pytest.skip(f"Policy module {{self.company_id}} not found", allow_module_level=True)


class TestPolicyFunctions:
    """Test suite for policy functions"""

    def setup_method(self):
        """Setup for each test"""
        self.company_id = "{self.company_id}"
'''

    def _generate_cabin_class_tests(self) -> str:
        """Generate cabin class function tests"""
        return '''
    # ========== Cabin Class Tests ==========

    def test_cabin_class_executive_international_long(self):
        """Test executive on long international flight"""
        result = policy.check_cabin_class(
            employee_level="executive",
            flight_type="international",
            duration_hours=10.0
        )
        assert result["allowed"] == True
        assert result["cabin"] in ["business", "first"]
        assert result["company_id"] == self.company_id

    def test_cabin_class_manager_domestic_short(self):
        """Test manager on short domestic flight"""
        result = policy.check_cabin_class(
            employee_level="manager",
            flight_type="domestic",
            duration_hours=2.0
        )
        assert result["allowed"] == True
        assert result["cabin"] == "economy"

    def test_cabin_class_staff_economy_only(self):
        """Test staff gets economy only"""
        result = policy.check_cabin_class(
            employee_level="staff",
            flight_type="international",
            duration_hours=12.0
        )
        assert result["cabin"] == "economy"

    def test_cabin_class_requested_upgrade(self):
        """Test requesting cabin upgrade"""
        result = policy.check_cabin_class(
            employee_level="manager",
            flight_type="domestic",
            duration_hours=3.0,
            requested_cabin="business"
        )
        # Should require approval or be denied
        assert "requires_approval" in result

    def test_cabin_class_normalization(self):
        """Test input normalization"""
        result = policy.check_cabin_class(
            employee_level="Senior Manager",
            flight_type="International",
            duration_hours=8.0
        )
        assert result["allowed"] == True
        assert "cabin" in result

    @pytest.mark.parametrize("level,flight_type,hours,expected_cabin", [
        ("executive", "international", 8.0, "business"),
        ("staff", "domestic", 2.0, "economy"),
        ("manager", "international", 12.0, "premium_economy"),
    ])
    def test_cabin_class_combinations(self, level, flight_type, hours, expected_cabin):
        """Test various cabin class combinations"""
        result = policy.check_cabin_class(level, flight_type, hours)
        assert result["cabin"] is not None
'''

    def _generate_cost_approval_tests(self) -> str:
        """Generate cost approval function tests"""
        return '''
    # ========== Cost Approval Tests ==========

    def test_cost_approval_under_threshold(self):
        """Test cost under approval threshold"""
        result = policy.check_cost_approval(
            employee_level="manager",
            trip_cost=500.0
        )
        assert "requires_approval" in result
        assert "threshold" in result
        assert result["company_id"] == self.company_id

    def test_cost_approval_over_threshold(self):
        """Test cost over approval threshold"""
        result = policy.check_cost_approval(
            employee_level="staff",
            trip_cost=5000.0
        )
        assert result["requires_approval"] == True
        assert result["approval_level"] in ["manager", "director"]

    def test_cost_approval_executive_higher_limit(self):
        """Test executives have higher thresholds"""
        result = policy.check_cost_approval(
            employee_level="executive",
            trip_cost=3000.0
        )
        # Executives should have higher threshold
        assert "threshold" in result

    def test_cost_approval_emergency_trip(self):
        """Test emergency trip gets higher threshold"""
        result = policy.check_cost_approval(
            employee_level="manager",
            trip_cost=2000.0,
            trip_type="emergency"
        )
        assert "threshold" in result

    @pytest.mark.parametrize("level,cost,should_need_approval", [
        ("staff", 2000, True),
        ("manager", 500, False),
        ("executive", 10000, True),
    ])
    def test_cost_approval_levels(self, level, cost, should_need_approval):
        """Test cost approval for different levels"""
        result = policy.check_cost_approval(level, cost)
        assert "requires_approval" in result
'''

    def _generate_advance_booking_tests(self) -> str:
        """Generate advance booking function tests"""
        return '''
    # ========== Advance Booking Tests ==========

    def test_advance_booking_sufficient_time(self):
        """Test booking with sufficient advance time"""
        booking_date = datetime.now().strftime("%Y-%m-%d")
        travel_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

        result = policy.check_advance_booking(booking_date, travel_date)
        assert result["valid"] == True
        assert result["days_advance"] >= 7

    def test_advance_booking_insufficient_time(self):
        """Test booking with insufficient advance time"""
        booking_date = datetime.now().strftime("%Y-%m-%d")
        travel_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")

        result = policy.check_advance_booking(booking_date, travel_date)
        assert "valid" in result
        assert result["days_advance"] < 7

    def test_advance_booking_emergency_waived(self):
        """Test emergency trips waive advance booking"""
        booking_date = datetime.now().strftime("%Y-%m-%d")
        travel_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        result = policy.check_advance_booking(
            booking_date,
            travel_date,
            trip_type="emergency"
        )
        assert result["waived"] == True

    def test_advance_booking_invalid_date_format(self):
        """Test invalid date format handling"""
        result = policy.check_advance_booking("invalid", "2024-12-31")
        assert result["valid"] == False
        assert "Invalid date" in result["reason"]

    def test_advance_booking_conference(self):
        """Test conference trips need more advance time"""
        booking_date = datetime.now().strftime("%Y-%m-%d")
        travel_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")

        result = policy.check_advance_booking(
            booking_date,
            travel_date,
            trip_type="conference"
        )
        assert "required_days" in result
'''

    def _generate_airline_preference_tests(self) -> str:
        """Generate airline preference function tests"""
        return '''
    # ========== Airline Preference Tests ==========

    def test_airline_preferred(self):
        """Test preferred airline selection"""
        result = policy.check_airline_preference("Delta")
        assert result["approved"] == True
        assert "is_preferred" in result
        assert result["company_id"] == self.company_id

    def test_airline_non_preferred(self):
        """Test non-preferred airline selection"""
        result = policy.check_airline_preference("Budget Air")
        assert result["approved"] == True  # Allowed but noted
        assert "needs_justification" in result

    def test_airline_with_reason(self):
        """Test airline selection with reason"""
        result = policy.check_airline_preference(
            "United",
            reason="best_price"
        )
        assert "preferred_airlines" in result

    def test_airline_case_insensitive(self):
        """Test airline name is case insensitive"""
        result1 = policy.check_airline_preference("delta")
        result2 = policy.check_airline_preference("DELTA")
        result3 = policy.check_airline_preference("Delta")

        # All should return same preference status
        assert result1["is_preferred"] == result2["is_preferred"] == result3["is_preferred"]
'''

    def _generate_baggage_tests(self) -> str:
        """Generate baggage allowance function tests"""
        return '''
    # ========== Baggage Allowance Tests ==========

    def test_baggage_within_allowance(self):
        """Test baggage within allowance"""
        result = policy.check_baggage_allowance(
            employee_level="manager",
            num_bags=1,
            trip_duration_days=3
        )
        assert result["approved"] == True
        assert result["overage"] == 0

    def test_baggage_exceeds_allowance(self):
        """Test baggage exceeds allowance"""
        result = policy.check_baggage_allowance(
            employee_level="staff",
            num_bags=5,
            trip_duration_days=3
        )
        assert result["overage"] > 0
        assert result["overage_fee"] > 0

    def test_baggage_extended_trip_bonus(self):
        """Test extended trips get extra bag"""
        result_short = policy.check_baggage_allowance(
            employee_level="manager",
            num_bags=2,
            trip_duration_days=5
        )
        result_long = policy.check_baggage_allowance(
            employee_level="manager",
            num_bags=2,
            trip_duration_days=10
        )

        # Long trip should have higher or equal allowance
        assert result_long["allowed_bags"] >= result_short["allowed_bags"]

    def test_baggage_executive_higher_allowance(self):
        """Test executives get higher baggage allowance"""
        result_exec = policy.check_baggage_allowance(
            employee_level="executive",
            num_bags=3,
            trip_duration_days=5
        )
        result_staff = policy.check_baggage_allowance(
            employee_level="staff",
            num_bags=3,
            trip_duration_days=5
        )

        # Executive should have easier time with 3 bags
        assert result_exec["allowed_bags"] >= result_staff["allowed_bags"]
'''

    def _generate_integration_tests(self) -> str:
        """Generate integration tests"""
        return '''
    # ========== Integration Tests ==========

    def test_function_registry_exists(self):
        """Test that function registry is available"""
        assert hasattr(policy, 'get_available_functions')
        functions = policy.get_available_functions()
        assert len(functions) > 0
        assert isinstance(functions, list)

    def test_all_functions_return_dicts(self):
        """Test all functions return dictionaries"""
        # Test each main function
        result1 = policy.check_cabin_class("manager", "domestic", 3.0)
        result2 = policy.check_cost_approval("manager", 1000.0)
        result3 = policy.check_airline_preference("Delta")
        result4 = policy.check_baggage_allowance("manager", 2, 5)

        for result in [result1, result2, result3, result4]:
            assert isinstance(result, dict)
            assert "company_id" in result or "policy_applied" in result

    def test_company_id_consistency(self):
        """Test all functions return consistent company ID"""
        result1 = policy.check_cabin_class("manager", "domestic", 3.0)
        result2 = policy.check_cost_approval("manager", 1000.0)

        assert result1["company_id"] == result2["company_id"] == self.company_id

    def test_realistic_trip_scenario(self):
        """Test a realistic complete trip scenario"""
        # Manager booking international business trip
        employee = "manager"

        # Check cabin class for 8-hour international flight
        cabin_result = policy.check_cabin_class(
            employee_level=employee,
            flight_type="international",
            duration_hours=8.0
        )

        # Check cost approval for $2500 trip
        cost_result = policy.check_cost_approval(
            employee_level=employee,
            trip_cost=2500.0
        )

        # Check advance booking (14 days ahead)
        today = datetime.now().strftime("%Y-%m-%d")
        travel = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
        booking_result = policy.check_advance_booking(today, travel)

        # Check baggage (2 bags for 5-day trip)
        baggage_result = policy.check_baggage_allowance(
            employee_level=employee,
            num_bags=2,
            trip_duration_days=5
        )

        # All checks should pass or have clear approval paths
        assert cabin_result["allowed"] == True
        assert booking_result["valid"] == True
        assert baggage_result["approved"] == True


# ========== Performance Tests ==========

class TestPerformance:
    """Performance and stress tests"""

    def test_function_performance(self):
        """Test function executes quickly"""
        import time

        start = time.time()
        for _ in range(100):
            policy.check_cabin_class("manager", "domestic", 3.0)
        elapsed = time.time() - start

        # 100 calls should take less than 1 second
        assert elapsed < 1.0

    def test_all_functions_importable(self):
        """Test all declared functions are importable"""
        functions = policy.get_available_functions()

        for func_info in functions:
            func_name = func_info["name"]
            assert hasattr(policy, func_name), f"Function {func_name} not found in module"


# ========== Edge Case Tests ==========

class TestEdgeCases:
    """Edge case and error handling tests"""

    def test_empty_string_inputs(self):
        """Test handling of empty string inputs"""
        result = policy.check_cabin_class("", "domestic", 3.0)
        assert isinstance(result, dict)

    def test_zero_duration(self):
        """Test zero duration flight"""
        result = policy.check_cabin_class("manager", "domestic", 0.0)
        assert isinstance(result, dict)

    def test_negative_cost(self):
        """Test negative cost handling"""
        result = policy.check_cost_approval("manager", -100.0)
        assert isinstance(result, dict)

    def test_very_long_flight(self):
        """Test very long flight duration"""
        result = policy.check_cabin_class("executive", "international", 24.0)
        assert result["allowed"] == True

    def test_many_bags(self):
        """Test requesting many bags"""
        result = policy.check_baggage_allowance("staff", 10, 3)
        assert result["overage"] > 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
'''

    def generate_test_data(self) -> str:
        """Generate test data file with example test cases"""
        return '''"""
Test Data for Policy Function Testing
Contains example test cases for various scenarios
"""

TEST_CASES = {
    "cabin_class": [
        {
            "id": "cc_001",
            "input": {
                "employee_level": "executive",
                "flight_type": "international",
                "duration_hours": 10.0
            },
            "expected": {
                "allowed": True,
                "cabin": "business"
            }
        },
        {
            "id": "cc_002",
            "input": {
                "employee_level": "staff",
                "flight_type": "domestic",
                "duration_hours": 3.0
            },
            "expected": {
                "allowed": True,
                "cabin": "economy"
            }
        }
    ],
    "cost_approval": [
        {
            "id": "ca_001",
            "input": {
                "employee_level": "manager",
                "trip_cost": 500.0
            },
            "expected": {
                "requires_approval": False
            }
        },
        {
            "id": "ca_002",
            "input": {
                "employee_level": "staff",
                "trip_cost": 3000.0
            },
            "expected": {
                "requires_approval": True
            }
        }
    ]
}
'''
