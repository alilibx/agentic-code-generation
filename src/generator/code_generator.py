"""
Code Generator Module
Generates Python functions from parsed policy rules.
"""

from typing import Dict, List, Any
from datetime import datetime


class CodeGenerator:
    """Generates executable Python code from policy rules"""

    def __init__(self, company_name: str):
        self.company_name = company_name
        self.company_id = company_name.upper().replace(' ', '_')

    def generate_policy_module(self, parsed_rules: Dict[str, Any]) -> str:
        """
        Generate a complete Python module with policy functions

        Args:
            parsed_rules: Parsed policy rules dictionary

        Returns:
            String containing complete Python module code
        """
        code_parts = []

        # Add header and imports
        code_parts.append(self._generate_header(parsed_rules['metadata']))

        # Add helper functions
        code_parts.append(self._generate_helpers())

        # Generate function for each rule type
        # Always generate core travel policy functions for completeness
        code_parts.append(self._generate_cabin_class_function(
            parsed_rules.get('cabin_class_rules', [])
        ))

        code_parts.append(self._generate_cost_approval_function(
            parsed_rules.get('cost_approval_rules', [])
        ))

        code_parts.append(self._generate_advance_booking_function(
            parsed_rules.get('advance_booking_rules', [])
        ))

        code_parts.append(self._generate_airline_preference_function(
            parsed_rules.get('airline_preference_rules', [])
        ))

        code_parts.append(self._generate_baggage_function(
            parsed_rules.get('baggage_rules', [])
        ))

        # Add utility function to list all available functions
        code_parts.append(self._generate_registry_function())

        return '\n\n'.join(code_parts)

    def _generate_header(self, metadata: Dict[str, str]) -> str:
        """Generate module header with imports and metadata"""
        return f'''"""
Generated Policy Functions for {metadata.get('company_name', 'Unknown Company')}
Auto-generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Policy Version: {metadata.get('policy_version', '1.0')}

This module contains executable policy checking functions.
All functions return structured dictionaries with policy decisions.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum


# Company identifier
COMPANY_ID = "{self.company_id}"
POLICY_VERSION = "{metadata.get('policy_version', '1.0')}"


class EmployeeLevel(Enum):
    """Employee level enumeration"""
    EXECUTIVE = "executive"
    SENIOR_MANAGER = "senior_manager"
    MANAGER = "manager"
    STAFF = "staff"
    CONTRACTOR = "contractor"


class CabinClass(Enum):
    """Flight cabin class enumeration"""
    FIRST = "first"
    BUSINESS = "business"
    PREMIUM_ECONOMY = "premium_economy"
    ECONOMY = "economy"


class FlightType(Enum):
    """Flight type enumeration"""
    INTERNATIONAL = "international"
    DOMESTIC = "domestic"
'''

    def _generate_helpers(self) -> str:
        """Generate helper functions"""
        return '''
def normalize_employee_level(level: str) -> str:
    """Normalize employee level string"""
    level = level.lower().replace(' ', '_').replace('-', '_')
    level_mapping = {
        'exec': 'executive',
        'ceo': 'executive',
        'cto': 'executive',
        'cfo': 'executive',
        'vp': 'executive',
        'sr_manager': 'senior_manager',
        'senior_mgr': 'senior_manager',
        'mgr': 'manager',
        'employee': 'staff',
        'worker': 'staff'
    }
    return level_mapping.get(level, level)


def normalize_cabin_class(cabin: str) -> str:
    """Normalize cabin class string"""
    cabin = cabin.lower().replace(' ', '_').replace('-', '_')
    cabin_mapping = {
        'first_class': 'first',
        '1st': 'first',
        'business_class': 'business',
        'biz': 'business',
        'premium_eco': 'premium_economy',
        'prem_economy': 'premium_economy',
        'eco': 'economy',
        'coach': 'economy'
    }
    return cabin_mapping.get(cabin, cabin)


def normalize_flight_type(flight_type: str) -> str:
    """Normalize flight type string"""
    flight_type = flight_type.lower()
    if 'international' in flight_type or 'intl' in flight_type:
        return 'international'
    return 'domestic'
'''

    def _generate_cabin_class_function(self, rules: List[Any]) -> str:
        """Generate cabin class checking function"""
        # Build logic based on rules
        rules_logic = []

        for rule in rules:
            conditions = rule.conditions
            level = conditions.get('employee_level', 'unknown')
            duration = conditions.get('flight_duration', 0)
            cabin = conditions.get('cabin_class', 'economy')

            rules_logic.append(f"        ('{level}', {duration}, '{cabin}')")

        rules_str = ',\n'.join(rules_logic) if rules_logic else "        # No rules defined"

        return f'''
def check_cabin_class(
    employee_level: str,
    flight_type: str,
    duration_hours: float,
    requested_cabin: Optional[str] = None
) -> Dict[str, Any]:
    """
    Check if a cabin class is allowed for an employee

    Args:
        employee_level: Employee's job level (executive, senior_manager, manager, staff)
        flight_type: Type of flight (international, domestic)
        duration_hours: Flight duration in hours
        requested_cabin: Requested cabin class (optional)

    Returns:
        Dictionary with:
        - allowed: bool - Whether the cabin class is allowed
        - cabin: str - Allowed cabin class
        - requires_approval: bool - Whether approval is needed
        - reason: str - Explanation of the decision
    """
    level = normalize_employee_level(employee_level)
    flight = normalize_flight_type(flight_type)

    # Default to economy
    allowed_cabin = "economy"
    requires_approval = False

    # Apply policy rules
    if level == "executive":
        if flight == "international" and duration_hours >= 6:
            allowed_cabin = "business"
        elif duration_hours >= 4:
            allowed_cabin = "premium_economy"
    elif level == "senior_manager":
        if flight == "international" and duration_hours >= 8:
            allowed_cabin = "business"
        elif duration_hours >= 5:
            allowed_cabin = "premium_economy"
    elif level == "manager":
        if flight == "international" and duration_hours >= 10:
            allowed_cabin = "premium_economy"
    # Staff and contractors: economy only

    # Check if requested cabin matches allowed
    if requested_cabin:
        req_cabin = normalize_cabin_class(requested_cabin)
        if req_cabin == allowed_cabin:
            allowed = True
            reason = f"{{req_cabin.title()}} class is allowed for {{level}} on {{flight}} flights of {{duration_hours}} hours"
        elif req_cabin in ["first", "business"] and allowed_cabin in ["economy", "premium_economy"]:
            allowed = False
            requires_approval = True
            reason = f"{{req_cabin.title()}} class requires manager approval. Standard allowance is {{allowed_cabin}}"
        else:
            allowed = True if req_cabin == "economy" else False
            reason = f"Requested {{req_cabin}} vs allowed {{allowed_cabin}}"
    else:
        allowed = True
        reason = f"Standard cabin class for {{level}}: {{allowed_cabin}}"

    return {{
        "allowed": allowed,
        "cabin": allowed_cabin,
        "requires_approval": requires_approval,
        "reason": reason,
        "policy_applied": "cabin_class_policy",
        "company_id": COMPANY_ID
    }}
'''

    def _generate_cost_approval_function(self, rules: List[Any]) -> str:
        """Generate cost approval checking function"""
        # Find the highest threshold
        threshold = 1000.0  # Default
        if rules:
            threshold = max(rule.conditions.get('threshold', 1000) for rule in rules)

        return f'''
def check_cost_approval(
    employee_level: str,
    trip_cost: float,
    trip_type: str = "standard"
) -> Dict[str, Any]:
    """
    Check if a trip cost requires manager approval

    Args:
        employee_level: Employee's job level
        trip_cost: Total trip cost in USD
        trip_type: Type of trip (standard, emergency, conference)

    Returns:
        Dictionary with approval requirements and thresholds
    """
    level = normalize_employee_level(employee_level)

    # Define approval thresholds by level
    thresholds = {{
        "executive": {threshold * 3},
        "senior_manager": {threshold * 2},
        "manager": {threshold * 1.5},
        "staff": {threshold},
        "contractor": {threshold * 0.5}
    }}

    threshold_amount = thresholds.get(level, {threshold})

    # Emergency trips have higher thresholds
    if trip_type == "emergency":
        threshold_amount *= 1.5

    requires_approval = trip_cost > threshold_amount
    approval_level = "manager" if requires_approval else "none"

    if trip_cost > threshold_amount * 2:
        approval_level = "director"

    return {{
        "requires_approval": requires_approval,
        "approval_level": approval_level,
        "threshold": threshold_amount,
        "amount": trip_cost,
        "over_budget": trip_cost - threshold_amount if requires_approval else 0,
        "reason": f"Cost ${{trip_cost:,.2f}} {{('exceeds' if requires_approval else 'within')}} ${{threshold_amount:,.2f}} threshold for {{level}}",
        "policy_applied": "cost_approval_policy",
        "company_id": COMPANY_ID
    }}
'''

    def _generate_advance_booking_function(self, rules: List[Any]) -> str:
        """Generate advance booking checking function"""
        # Find minimum days required
        min_days = 7  # Default
        if rules:
            min_days = max(rule.conditions.get('min_days', 7) for rule in rules)

        return f'''
def check_advance_booking(
    booking_date: str,
    travel_date: str,
    trip_type: str = "standard"
) -> Dict[str, Any]:
    """
    Check if booking is made within required advance window

    Args:
        booking_date: Date of booking (YYYY-MM-DD)
        travel_date: Date of travel (YYYY-MM-DD)
        trip_type: Type of trip (standard, emergency, conference)

    Returns:
        Dictionary with booking validity and requirements
    """
    try:
        booking_dt = datetime.strptime(booking_date, "%Y-%m-%d")
        travel_dt = datetime.strptime(travel_date, "%Y-%m-%d")
    except ValueError:
        return {{
            "valid": False,
            "reason": "Invalid date format. Use YYYY-MM-DD",
            "policy_applied": "advance_booking_policy"
        }}

    days_advance = (travel_dt - booking_dt).days

    # Different requirements by trip type
    if trip_type == "emergency":
        required_days = 0
        waived = True
    elif trip_type == "conference":
        required_days = {min_days * 2}
        waived = False
    else:
        required_days = {min_days}
        waived = False

    valid = days_advance >= required_days or waived

    return {{
        "valid": valid,
        "days_advance": days_advance,
        "required_days": required_days,
        "waived": waived,
        "penalty": "May incur higher fares" if not valid else "None",
        "reason": f"Booked {{days_advance}} days in advance. Required: {{required_days}} days",
        "policy_applied": "advance_booking_policy",
        "company_id": COMPANY_ID
    }}
'''

    def _generate_airline_preference_function(self, rules: List[Any]) -> str:
        """Generate airline preference checking function"""
        # Extract preferred airlines
        preferred = ["Delta", "United", "American", "Southwest"]
        if rules and rules[0].conditions.get('preferred_airlines'):
            preferred = rules[0].conditions['preferred_airlines']

        preferred_str = ', '.join(f'"{a}"' for a in preferred)

        return f'''
def check_airline_preference(
    airline_name: str,
    reason: str = "best_price"
) -> Dict[str, Any]:
    """
    Check if an airline is in the preferred list

    Args:
        airline_name: Name of the airline
        reason: Reason for selection (best_price, schedule, loyalty)

    Returns:
        Dictionary with airline approval status
    """
    preferred_airlines = [{preferred_str}]

    airline_normalized = airline_name.strip().title()
    is_preferred = airline_normalized in preferred_airlines

    # Non-preferred airlines need justification
    needs_justification = not is_preferred

    return {{
        "approved": True,  # All airlines allowed, preference noted
        "is_preferred": is_preferred,
        "needs_justification": needs_justification,
        "preferred_airlines": preferred_airlines,
        "reason": f"{{'Preferred' if is_preferred else 'Non-preferred'}} airline: {{airline_normalized}}",
        "policy_applied": "airline_preference_policy",
        "company_id": COMPANY_ID
    }}
'''

    def _generate_baggage_function(self, rules: List[Any]) -> str:
        """Generate baggage allowance checking function"""
        max_bags = 2  # Default
        if rules:
            max_bags = max(rule.conditions.get('max_bags', 2) for rule in rules)

        return f'''
def check_baggage_allowance(
    employee_level: str,
    num_bags: int,
    trip_duration_days: int
) -> Dict[str, Any]:
    """
    Check baggage allowance for an employee

    Args:
        employee_level: Employee's job level
        num_bags: Number of checked bags requested
        trip_duration_days: Duration of trip in days

    Returns:
        Dictionary with baggage allowance decision
    """
    level = normalize_employee_level(employee_level)

    # Base allowance by level
    base_allowance = {{
        "executive": {max_bags + 1},
        "senior_manager": {max_bags},
        "manager": {max_bags},
        "staff": {max_bags - 1} if {max_bags} > 1 else 1,
        "contractor": 1
    }}

    allowed_bags = base_allowance.get(level, 1)

    # Extended trips get +1 bag
    if trip_duration_days > 7:
        allowed_bags += 1

    approved = num_bags <= allowed_bags
    overage = max(0, num_bags - allowed_bags)

    return {{
        "approved": approved,
        "allowed_bags": allowed_bags,
        "requested_bags": num_bags,
        "overage": overage,
        "overage_fee": overage * 35 if overage > 0 else 0,
        "reason": f"Requested {{num_bags}} bags. Allowance: {{allowed_bags}} for {{level}}",
        "policy_applied": "baggage_allowance_policy",
        "company_id": COMPANY_ID
    }}
'''

    def _generate_registry_function(self) -> str:
        """Generate function registry for AI discovery"""
        return '''
def get_available_functions() -> List[Dict[str, Any]]:
    """
    Get list of all available policy functions with descriptions

    Returns:
        List of function metadata dictionaries
    """
    return [
        {
            "name": "check_cabin_class",
            "description": "Check if a cabin class is allowed for an employee based on level, flight type, and duration",
            "parameters": {
                "employee_level": "Employee job level (executive, senior_manager, manager, staff)",
                "flight_type": "Type of flight (international, domestic)",
                "duration_hours": "Flight duration in hours",
                "requested_cabin": "Requested cabin class (optional)"
            },
            "returns": "Dictionary with allowed cabin, approval requirements, and reason"
        },
        {
            "name": "check_cost_approval",
            "description": "Check if a trip cost requires manager approval based on employee level and amount",
            "parameters": {
                "employee_level": "Employee job level",
                "trip_cost": "Total trip cost in USD",
                "trip_type": "Type of trip (standard, emergency, conference)"
            },
            "returns": "Dictionary with approval requirements and thresholds"
        },
        {
            "name": "check_advance_booking",
            "description": "Check if booking is made within required advance window",
            "parameters": {
                "booking_date": "Date of booking (YYYY-MM-DD)",
                "travel_date": "Date of travel (YYYY-MM-DD)",
                "trip_type": "Type of trip (standard, emergency, conference)"
            },
            "returns": "Dictionary with booking validity and requirements"
        },
        {
            "name": "check_airline_preference",
            "description": "Check if an airline is in the preferred list",
            "parameters": {
                "airline_name": "Name of the airline",
                "reason": "Reason for selection"
            },
            "returns": "Dictionary with airline approval status"
        },
        {
            "name": "check_baggage_allowance",
            "description": "Check baggage allowance for an employee",
            "parameters": {
                "employee_level": "Employee job level",
                "num_bags": "Number of checked bags",
                "trip_duration_days": "Duration of trip in days"
            },
            "returns": "Dictionary with baggage allowance decision"
        }
    ]


if __name__ == "__main__":
    # Example usage
    print(f"Policy Functions for {COMPANY_ID}")
    print(f"Version: {POLICY_VERSION}")
    print("\\nAvailable Functions:")
    for func in get_available_functions():
        print(f"  - {func['name']}: {func['description']}")
'''
