"""
AI-Powered Code Generator Module
Uses LLM to generate Python functions from parsed policy rules.
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from openai import AzureOpenAI


class AICodeGenerator:
    """
    AI-powered code generator using Azure OpenAI

    This generator uses LLM to create sophisticated Python functions from policy rules,
    replacing template-based generation with intelligent code synthesis.
    """

    def __init__(
        self,
        company_name: str,
        azure_endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: str = "2024-02-15-preview",
        deployment_name: Optional[str] = None
    ):
        """
        Initialize AI code generator

        Args:
            company_name: Company name for the policy
            azure_endpoint: Azure OpenAI endpoint URL
            api_key: Azure OpenAI API key
            api_version: API version to use
            deployment_name: Name of your GPT-4 deployment
        """
        self.company_name = company_name
        self.company_id = company_name.upper().replace(' ', '_')

        self.endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.api_version = api_version
        self.deployment_name = deployment_name or os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")

        if not self.endpoint or not self.api_key:
            raise ValueError(
                "Azure OpenAI credentials not provided. "
                "Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY "
                "environment variables or pass them to constructor."
            )

        self.client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version
        )

    def generate_policy_module(self, parsed_rules: Dict[str, Any]) -> str:
        """
        Generate a complete Python module with policy functions using AI

        Args:
            parsed_rules: Parsed policy rules dictionary

        Returns:
            String containing complete Python module code
        """
        print("🤖 Using AI to generate Python code...")

        # Generate header and imports (can use template for this)
        header = self._generate_header(parsed_rules['metadata'])

        # Generate helper functions (can use template for this)
        helpers = self._generate_helpers()

        # Generate each policy function using AI
        print("  → Generating cabin class function with AI...")
        cabin_function = self._generate_function_ai(
            "check_cabin_class",
            parsed_rules.get('cabin_class_rules', []),
            "cabin class checking"
        )

        print("  → Generating cost approval function with AI...")
        cost_function = self._generate_function_ai(
            "check_cost_approval",
            parsed_rules.get('cost_approval_rules', []),
            "cost approval threshold checking"
        )

        print("  → Generating advance booking function with AI...")
        booking_function = self._generate_function_ai(
            "check_advance_booking",
            parsed_rules.get('advance_booking_rules', []),
            "advance booking window validation"
        )

        print("  → Generating airline preference function with AI...")
        airline_function = self._generate_function_ai(
            "check_airline_preference",
            parsed_rules.get('airline_preference_rules', []),
            "airline preference checking"
        )

        print("  → Generating baggage allowance function with AI...")
        baggage_function = self._generate_function_ai(
            "check_baggage_allowance",
            parsed_rules.get('baggage_rules', []),
            "baggage allowance validation"
        )

        # Generate registry function (template is fine for this)
        registry = self._generate_registry_function()

        # Combine all parts
        code_parts = [
            header,
            helpers,
            cabin_function,
            cost_function,
            booking_function,
            airline_function,
            baggage_function,
            registry
        ]

        print("  ✓ AI code generation complete")

        return '\n\n'.join(code_parts)

    def _generate_function_ai(
        self,
        function_name: str,
        rules: List[Any],
        purpose: str
    ) -> str:
        """
        Generate a policy function using AI

        Args:
            function_name: Name of the function to generate
            rules: List of policy rules
            purpose: Description of the function's purpose

        Returns:
            Generated Python function code
        """
        # Convert rules to a readable format for the AI
        rules_description = self._format_rules_for_ai(rules)

        system_prompt = f"""You are an expert Python developer specializing in policy automation.

Your task is to generate a Python function called `{function_name}` for {purpose}.

The function should:
1. Accept relevant parameters based on the rules provided
2. Implement ALL the policy rules accurately
3. Include comprehensive type hints (use typing module)
4. Have a detailed docstring explaining parameters and return value
5. Return a dictionary with the decision and reasoning
6. Handle edge cases gracefully
7. Use clear, readable code with comments for complex logic
8. Include the company_id constant in the return value

Return format:
- The return value must be a dictionary with keys like:
  * Main decision field (allowed, approved, valid, etc.)
  * Supporting fields (reason, threshold, etc.)
  * "policy_applied": a string identifying the policy
  * "company_id": COMPANY_ID constant

Code style:
- Use helper functions normalize_employee_level(), normalize_cabin_class(), normalize_flight_type() when appropriate
- Keep functions pure and testable
- Add inline comments for complex business logic
- Format the code nicely with proper indentation

Return ONLY the Python function code, no other text or markdown.
"""

        user_prompt = f"""Generate the `{function_name}` function.

COMPANY_ID = "{self.company_id}"

Policy Rules:
{rules_description}

Generate a complete, production-ready Python function."""

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )

            generated_code = response.choices[0].message.content

            # Clean up markdown code blocks if present
            if "```python" in generated_code:
                generated_code = generated_code.split("```python")[1].split("```")[0]
            elif "```" in generated_code:
                generated_code = generated_code.split("```")[1].split("```")[0]

            return generated_code.strip()

        except Exception as e:
            print(f"  ⚠ AI generation failed for {function_name}: {e}")
            # Fallback to a simple template
            return self._generate_fallback_function(function_name, purpose)

    def _format_rules_for_ai(self, rules: List[Any]) -> str:
        """Format rules into a readable description for AI"""
        if not rules:
            return "No specific rules provided. Generate a sensible default implementation."

        formatted = []
        for i, rule in enumerate(rules, 1):
            formatted.append(f"Rule {i}:")
            formatted.append(f"  Type: {rule.rule_type}")
            formatted.append(f"  Conditions: {json.dumps(rule.conditions, indent=4)}")
            formatted.append(f"  Result: {json.dumps(rule.result, indent=4)}")
            formatted.append(f"  Description: {rule.description}")
            if hasattr(rule, 'confidence'):
                formatted.append(f"  Confidence: {rule.confidence}")
            formatted.append("")

        return '\n'.join(formatted)

    def _generate_fallback_function(self, function_name: str, purpose: str) -> str:
        """Generate a fallback function if AI fails"""
        return f'''
def {function_name}(*args, **kwargs) -> Dict[str, Any]:
    """
    {purpose.title()}

    This is a fallback implementation.
    """
    return {{
        "error": "Function generation failed",
        "fallback": True,
        "policy_applied": "{function_name}",
        "company_id": COMPANY_ID
    }}
'''

    def _generate_header(self, metadata: Dict[str, str]) -> str:
        """Generate module header with imports and metadata"""
        return f'''"""
Generated Policy Functions for {metadata.get('company_name', self.company_name)}
Auto-generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Policy Version: {metadata.get('policy_version', '1.0')}

This module contains AI-generated executable policy checking functions.
All functions return structured dictionaries with policy decisions.

⚡ Generated using AI-powered code generation
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
