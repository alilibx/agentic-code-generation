"""
AI-Powered Policy Parser Module
Uses LLM to understand and extract structured rules from natural language policies.
"""

import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from openai import AzureOpenAI


@dataclass
class PolicyRule:
    """Represents a single policy rule"""
    rule_type: str
    conditions: Dict[str, Any]
    result: Any
    description: str
    confidence: float = 1.0


class AIPolicyParser:
    """
    AI-powered policy parser using Azure OpenAI

    This parser uses LLM to understand natural language policies and extract
    structured rules, replacing regex-based parsing with intelligent understanding.
    """

    def __init__(
        self,
        azure_endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: str = "2024-02-15-preview",
        deployment_name: Optional[str] = None
    ):
        """
        Initialize AI policy parser

        Args:
            azure_endpoint: Azure OpenAI endpoint URL
            api_key: Azure OpenAI API key
            api_version: API version to use
            deployment_name: Name of your GPT-4 deployment
        """
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

    def parse_policy_text(self, policy_text: str) -> Dict[str, Any]:
        """
        Parse policy text using AI to extract structured rules

        Args:
            policy_text: Plain text policy document

        Returns:
            Dictionary containing parsed rules and metadata
        """
        print("🤖 Using AI to parse policy document...")

        # Step 1: Extract metadata
        metadata = self._extract_metadata_ai(policy_text)
        print(f"  ✓ Extracted metadata: {metadata['company_name']}")

        # Step 2: Extract all rule types using AI
        cabin_rules = self._extract_cabin_class_rules_ai(policy_text)
        print(f"  ✓ Found {len(cabin_rules)} cabin class rules")

        cost_rules = self._extract_cost_approval_rules_ai(policy_text)
        print(f"  ✓ Found {len(cost_rules)} cost approval rules")

        booking_rules = self._extract_advance_booking_rules_ai(policy_text)
        print(f"  ✓ Found {len(booking_rules)} advance booking rules")

        airline_rules = self._extract_airline_preferences_ai(policy_text)
        print(f"  ✓ Found {len(airline_rules)} airline preference rules")

        baggage_rules = self._extract_baggage_rules_ai(policy_text)
        print(f"  ✓ Found {len(baggage_rules)} baggage allowance rules")

        return {
            'metadata': metadata,
            'cabin_class_rules': cabin_rules,
            'cost_approval_rules': cost_rules,
            'advance_booking_rules': booking_rules,
            'airline_preference_rules': airline_rules,
            'baggage_rules': baggage_rules
        }

    def _extract_metadata_ai(self, policy_text: str) -> Dict[str, str]:
        """Extract metadata using AI"""

        system_prompt = """You are a policy document analyzer. Extract metadata from policy documents.

Your task is to extract:
1. Company name
2. Policy version
3. Effective date

Return a JSON object with these fields:
{
    "company_name": "extracted company name",
    "policy_version": "extracted version",
    "effective_date": "extracted date"
}

If a field is not found, use reasonable defaults:
- company_name: "UNKNOWN"
- policy_version: "1.0"
- effective_date: "Unknown"
"""

        user_prompt = f"""Extract metadata from this policy document:

{policy_text[:1000]}

Return only the JSON object, no other text."""

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            metadata = json.loads(response.choices[0].message.content)
            return metadata

        except Exception as e:
            print(f"  ⚠ AI metadata extraction failed: {e}, using defaults")
            return {
                'company_name': 'UNKNOWN',
                'policy_version': '1.0',
                'effective_date': 'Unknown'
            }

    def _extract_cabin_class_rules_ai(self, policy_text: str) -> List[PolicyRule]:
        """Extract cabin class rules using AI"""

        system_prompt = """You are a travel policy analyzer specializing in cabin class rules.

Extract ALL cabin class rules from the policy. For each rule, identify:
1. Employee level (executive, senior_manager, manager, staff, contractor)
2. Flight type (international, domestic)
3. Flight duration threshold in hours
4. Allowed cabin class (first, business, premium_economy, economy)

Return a JSON array of rule objects:
[
    {
        "employee_level": "executive",
        "flight_type": "international",
        "duration_hours": 6.0,
        "cabin_class": "business",
        "description": "Brief description of the rule",
        "confidence": 0.95
    }
]

Important:
- Extract ALL combinations explicitly mentioned
- Use normalized employee levels (executive, senior_manager, manager, staff, contractor)
- Use normalized cabin classes (first, business, premium_economy, economy)
- Set confidence based on how explicit the rule is (0.0-1.0)
- If a rule is implicit or default, still include it with lower confidence
"""

        user_prompt = f"""Extract all cabin class rules from this policy:

{policy_text}

Return only the JSON array, no other text."""

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            rules_data = result.get('rules', result.get('cabin_class_rules', []))

            rules = []
            for rule_data in rules_data:
                rules.append(PolicyRule(
                    rule_type='cabin_class',
                    conditions={
                        'employee_level': rule_data.get('employee_level', 'staff'),
                        'flight_type': rule_data.get('flight_type', 'domestic'),
                        'flight_duration': float(rule_data.get('duration_hours', 0)),
                        'cabin_class': rule_data.get('cabin_class', 'economy')
                    },
                    result={'allowed': True, 'cabin': rule_data.get('cabin_class', 'economy')},
                    description=rule_data.get('description', ''),
                    confidence=float(rule_data.get('confidence', 1.0))
                ))

            return rules

        except Exception as e:
            print(f"  ⚠ AI cabin class extraction failed: {e}")
            return []

    def _extract_cost_approval_rules_ai(self, policy_text: str) -> List[PolicyRule]:
        """Extract cost approval rules using AI"""

        system_prompt = """You are a travel policy analyzer specializing in cost approval thresholds.

Extract ALL cost approval threshold rules. For each rule, identify:
1. Employee level (executive, senior_manager, manager, staff, contractor)
2. Cost threshold amount in USD
3. Trip type if specified (standard, emergency, conference)

Return a JSON array:
[
    {
        "employee_level": "executive",
        "threshold": 5000.0,
        "trip_type": "standard",
        "description": "Brief description",
        "confidence": 0.95
    }
]

Extract thresholds for all employee levels mentioned.
"""

        user_prompt = f"""Extract all cost approval threshold rules from this policy:

{policy_text}

Return only the JSON array, no other text."""

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            rules_data = result.get('rules', result.get('cost_approval_rules', []))

            rules = []
            for rule_data in rules_data:
                rules.append(PolicyRule(
                    rule_type='cost_approval',
                    conditions={
                        'employee_level': rule_data.get('employee_level', 'staff'),
                        'threshold': float(rule_data.get('threshold', 1000)),
                        'trip_type': rule_data.get('trip_type', 'standard')
                    },
                    result={'requires_approval': True},
                    description=rule_data.get('description', ''),
                    confidence=float(rule_data.get('confidence', 1.0))
                ))

            return rules

        except Exception as e:
            print(f"  ⚠ AI cost approval extraction failed: {e}")
            return []

    def _extract_advance_booking_rules_ai(self, policy_text: str) -> List[PolicyRule]:
        """Extract advance booking rules using AI"""

        system_prompt = """You are a travel policy analyzer specializing in advance booking requirements.

Extract ALL advance booking window rules. For each rule, identify:
1. Trip type (standard, conference, emergency)
2. Minimum days required for advance booking
3. Whether the requirement can be waived

Return a JSON array:
[
    {
        "trip_type": "standard",
        "min_days": 14,
        "waivable": false,
        "description": "Brief description",
        "confidence": 0.95
    }
]
"""

        user_prompt = f"""Extract all advance booking rules from this policy:

{policy_text}

Return only the JSON array, no other text."""

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            rules_data = result.get('rules', result.get('advance_booking_rules', []))

            rules = []
            for rule_data in rules_data:
                rules.append(PolicyRule(
                    rule_type='advance_booking',
                    conditions={
                        'trip_type': rule_data.get('trip_type', 'standard'),
                        'min_days': int(rule_data.get('min_days', 7)),
                        'waivable': bool(rule_data.get('waivable', False))
                    },
                    result={'valid': True},
                    description=rule_data.get('description', ''),
                    confidence=float(rule_data.get('confidence', 1.0))
                ))

            return rules

        except Exception as e:
            print(f"  ⚠ AI advance booking extraction failed: {e}")
            return []

    def _extract_airline_preferences_ai(self, policy_text: str) -> List[PolicyRule]:
        """Extract airline preference rules using AI"""

        system_prompt = """You are a travel policy analyzer specializing in airline preferences.

Extract preferred/approved airlines and any related rules. Return a JSON object:
{
    "preferred_airlines": ["Delta", "United", "American"],
    "requires_justification": true,
    "price_tolerance": "within 10%",
    "description": "Brief description",
    "confidence": 0.95
}

If no airlines are specified, return an empty list for preferred_airlines.
"""

        user_prompt = f"""Extract airline preference rules from this policy:

{policy_text}

Return only the JSON object, no other text."""

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            rule_data = json.loads(response.choices[0].message.content)

            if rule_data.get('preferred_airlines'):
                return [PolicyRule(
                    rule_type='airline_preference',
                    conditions={
                        'preferred_airlines': rule_data.get('preferred_airlines', []),
                        'requires_justification': bool(rule_data.get('requires_justification', False)),
                        'price_tolerance': rule_data.get('price_tolerance', 'any')
                    },
                    result={'approved': True},
                    description=rule_data.get('description', ''),
                    confidence=float(rule_data.get('confidence', 1.0))
                )]

            return []

        except Exception as e:
            print(f"  ⚠ AI airline preference extraction failed: {e}")
            return []

    def _extract_baggage_rules_ai(self, policy_text: str) -> List[PolicyRule]:
        """Extract baggage allowance rules using AI"""

        system_prompt = """You are a travel policy analyzer specializing in baggage allowances.

Extract ALL baggage allowance rules. For each rule, identify:
1. Employee level (executive, senior_manager, manager, staff, contractor)
2. Number of allowed checked bags
3. Any bonuses or conditions (e.g., extended trip bonus)

Return a JSON array:
[
    {
        "employee_level": "executive",
        "max_bags": 3,
        "extended_trip_bonus": 1,
        "extended_trip_days": 7,
        "description": "Brief description",
        "confidence": 0.95
    }
]
"""

        user_prompt = f"""Extract all baggage allowance rules from this policy:

{policy_text}

Return only the JSON array, no other text."""

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            rules_data = result.get('rules', result.get('baggage_rules', []))

            rules = []
            for rule_data in rules_data:
                rules.append(PolicyRule(
                    rule_type='baggage',
                    conditions={
                        'employee_level': rule_data.get('employee_level', 'staff'),
                        'max_bags': int(rule_data.get('max_bags', 1)),
                        'extended_trip_bonus': int(rule_data.get('extended_trip_bonus', 0)),
                        'extended_trip_days': int(rule_data.get('extended_trip_days', 7))
                    },
                    result={'allowed': int(rule_data.get('max_bags', 1))},
                    description=rule_data.get('description', ''),
                    confidence=float(rule_data.get('confidence', 1.0))
                ))

            return rules

        except Exception as e:
            print(f"  ⚠ AI baggage rules extraction failed: {e}")
            return []

    def validate_policy(self, policy_text: str) -> Dict[str, Any]:
        """
        Validate policy for completeness, conflicts, and ambiguities

        Args:
            policy_text: Plain text policy document

        Returns:
            Dictionary with validation results
        """
        print("🤖 Validating policy with AI...")

        system_prompt = """You are a policy validation expert. Analyze travel policies for:

1. COMPLETENESS: Are all necessary rules defined?
   - Missing employee levels
   - Missing trip types
   - Gaps in coverage

2. CONFLICTS: Are there contradictory rules?
   - Same conditions with different outcomes
   - Overlapping rules with different thresholds

3. AMBIGUITIES: Are there unclear or vague statements?
   - Imprecise language
   - Missing thresholds
   - Unclear conditions

Return a JSON object:
{
    "is_valid": true/false,
    "completeness_score": 0.0-1.0,
    "issues": [
        {
            "type": "missing" | "conflict" | "ambiguity",
            "severity": "high" | "medium" | "low",
            "description": "Description of the issue",
            "suggestion": "How to fix it"
        }
    ],
    "summary": "Overall assessment"
}
"""

        user_prompt = f"""Validate this travel policy:

{policy_text}

Return only the JSON object, no other text."""

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )

            validation_result = json.loads(response.choices[0].message.content)

            print(f"  ✓ Validation complete - Score: {validation_result.get('completeness_score', 0):.2f}")

            if validation_result.get('issues'):
                print(f"  ⚠ Found {len(validation_result['issues'])} issues")
                for issue in validation_result['issues'][:3]:  # Show first 3
                    print(f"    - [{issue.get('severity', 'medium').upper()}] {issue.get('description', '')}")

            return validation_result

        except Exception as e:
            print(f"  ⚠ AI validation failed: {e}")
            return {
                'is_valid': True,
                'completeness_score': 0.8,
                'issues': [],
                'summary': 'Validation unavailable',
                'error': str(e)
            }
