"""
Policy Parser Module
Parses plain text policy documents and extracts structured rules.
"""

import re
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class PolicyRule:
    """Represents a single policy rule"""
    rule_type: str
    conditions: Dict[str, Any]
    result: Any
    description: str


class PolicyParser:
    """Parses plain text policies into structured rules"""

    def __init__(self):
        self.rules = []
        self.metadata = {}

    def parse_policy_text(self, policy_text: str) -> Dict[str, Any]:
        """
        Parse policy text and extract rules

        Args:
            policy_text: Plain text policy document

        Returns:
            Dictionary containing parsed rules and metadata
        """
        lines = policy_text.strip().split('\n')

        # Extract metadata
        self.metadata = self._extract_metadata(lines)

        # Parse cabin class rules
        cabin_rules = self._parse_cabin_class_rules(policy_text)

        # Parse cost approval rules
        cost_rules = self._parse_cost_approval_rules(policy_text)

        # Parse advance booking rules
        booking_rules = self._parse_advance_booking_rules(policy_text)

        # Parse airline preference rules
        airline_rules = self._parse_airline_preferences(policy_text)

        # Parse baggage rules
        baggage_rules = self._parse_baggage_rules(policy_text)

        return {
            'metadata': self.metadata,
            'cabin_class_rules': cabin_rules,
            'cost_approval_rules': cost_rules,
            'advance_booking_rules': booking_rules,
            'airline_preference_rules': airline_rules,
            'baggage_rules': baggage_rules
        }

    def _extract_metadata(self, lines: List[str]) -> Dict[str, str]:
        """Extract company name and other metadata"""
        metadata = {
            'company_name': 'UNKNOWN',
            'policy_version': '1.0',
            'effective_date': 'Unknown'
        }

        for line in lines[:10]:  # Check first 10 lines
            if 'company' in line.lower() and ':' in line:
                metadata['company_name'] = line.split(':', 1)[1].strip()
            elif 'version' in line.lower() and ':' in line:
                metadata['policy_version'] = line.split(':', 1)[1].strip()
            elif 'effective' in line.lower() and ':' in line:
                metadata['effective_date'] = line.split(':', 1)[1].strip()

        return metadata

    def _parse_cabin_class_rules(self, text: str) -> List[PolicyRule]:
        """Parse cabin class rules from policy text"""
        rules = []

        # Pattern: "Level X can book Y class for Z hour flights"
        patterns = [
            r'(\w+(?:\s+\w+)*)\s+(?:can|may)\s+book\s+(\w+)\s+class\s+for\s+(\d+)\+?\s+hour',
            r'(\w+)\s+class\s+(?:is\s+)?allowed\s+for\s+(\w+(?:\s+\w+)*)\s+on\s+(\w+)\s+flights',
            r'(\w+(?:\s+\w+)*):?\s+(\w+)\s+class\s+for\s+(\w+)\s+flights\s+over\s+(\d+)\s+hours'
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                if len(groups) >= 3:
                    rules.append(PolicyRule(
                        rule_type='cabin_class',
                        conditions={
                            'employee_level': groups[0].lower().replace(' ', '_'),
                            'flight_duration': float(groups[2]) if groups[2].isdigit() else 0,
                            'cabin_class': groups[1].lower()
                        },
                        result={'allowed': True, 'cabin': groups[1].lower()},
                        description=match.group(0)
                    ))

        return rules

    def _parse_cost_approval_rules(self, text: str) -> List[PolicyRule]:
        """Parse cost approval threshold rules"""
        rules = []

        # Pattern: "$X requires approval" or "over $X needs approval"
        pattern = r'\$?([\d,]+)\s+(?:requires|needs)\s+(?:manager\s+)?approval'
        matches = re.finditer(pattern, text, re.IGNORECASE)

        for match in matches:
            amount = float(match.group(1).replace(',', ''))
            rules.append(PolicyRule(
                rule_type='cost_approval',
                conditions={'threshold': amount},
                result={'requires_approval': True},
                description=match.group(0)
            ))

        return rules

    def _parse_advance_booking_rules(self, text: str) -> List[PolicyRule]:
        """Parse advance booking window rules"""
        rules = []

        # Pattern: "X days advance" or "book X days before"
        pattern = r'(\d+)\s+days?\s+(?:advance|before|in\s+advance|prior)'
        matches = re.finditer(pattern, text, re.IGNORECASE)

        for match in matches:
            days = int(match.group(1))
            rules.append(PolicyRule(
                rule_type='advance_booking',
                conditions={'min_days': days},
                result={'valid': True},
                description=match.group(0)
            ))

        return rules

    def _parse_airline_preferences(self, text: str) -> List[PolicyRule]:
        """Parse preferred airline rules"""
        rules = []

        # Look for sections about airlines
        airline_section = re.search(
            r'(?:preferred|approved)\s+airlines?:?(.*?)(?:\n\n|\Z)',
            text,
            re.IGNORECASE | re.DOTALL
        )

        if airline_section:
            content = airline_section.group(1)
            # Extract airline names (common airlines)
            airlines = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', content)
            if airlines:
                rules.append(PolicyRule(
                    rule_type='airline_preference',
                    conditions={'preferred_airlines': airlines},
                    result={'approved': True},
                    description=airline_section.group(0)
                ))

        return rules

    def _parse_baggage_rules(self, text: str) -> List[PolicyRule]:
        """Parse baggage allowance rules"""
        rules = []

        # Pattern: "X checked bags" or "X pieces of luggage"
        pattern = r'(\d+)\s+(?:checked\s+)?(?:bag|piece)s?\s+(?:of\s+luggage)?'
        matches = re.finditer(pattern, text, re.IGNORECASE)

        for match in matches:
            count = int(match.group(1))
            rules.append(PolicyRule(
                rule_type='baggage',
                conditions={'max_bags': count},
                result={'allowed': count},
                description=match.group(0)
            ))

        return rules
