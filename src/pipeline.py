"""
Policy-to-Code Pipeline
Main orchestrator that uses AI for parsing and code generation.

This is the primary pipeline - uses Azure OpenAI for intelligent policy processing.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from ai_integration.ai_policy_parser import AIPolicyParser
from ai_integration.ai_code_generator import AICodeGenerator
from storage.function_storage import FunctionStorage, FunctionRegistry
from testing.test_generator import TestGenerator


class PolicyPipeline:
    """
    AI-powered pipeline for converting policies to executable code

    This orchestrates the entire workflow with AI:
    1. Parse policy text with AI (LLM-based understanding)
    2. Validate policy with AI (conflict detection, completeness)
    3. Generate Python functions with AI (intelligent code synthesis)
    4. Store with versioning
    5. Generate tests
    6. Make available for AI integration
    """

    def __init__(
        self,
        storage_dir: str = "generated",
        azure_endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        deployment_name: Optional[str] = None
    ):
        """
        Initialize the AI-powered pipeline

        Args:
            storage_dir: Directory for storing generated files
            azure_endpoint: Azure OpenAI endpoint (defaults to env var)
            api_key: Azure OpenAI API key (defaults to env var)
            deployment_name: Azure OpenAI deployment name (defaults to env var)
        """
        self.storage_dir = Path(storage_dir)
        self.storage = FunctionStorage(str(self.storage_dir))
        self.registry = FunctionRegistry(self.storage)

        # AI configuration
        self.azure_endpoint = azure_endpoint
        self.api_key = api_key
        self.deployment_name = deployment_name

        # Create output directories
        self.tests_dir = self.storage_dir / "tests"
        self.tests_dir.mkdir(exist_ok=True, parents=True)

        print("=" * 70)
        print("🤖 AI-POWERED POLICY PIPELINE")
        print("=" * 70)
        print(f"Storage: {self.storage_dir}")
        print(f"AI Model: {deployment_name or os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4')}")
        print("=" * 70)

    def process_policy(
        self,
        policy_text: str,
        company_name: str,
        generate_tests: bool = True,
        auto_version: bool = True,
        validate_first: bool = True
    ) -> Dict[str, Any]:
        """
        Process a policy text through the AI-powered pipeline

        Args:
            policy_text: Plain text policy document
            company_name: Company name/identifier
            generate_tests: Whether to generate unit tests
            auto_version: Whether to auto-increment version
            validate_first: Whether to validate policy before processing

        Returns:
            Dictionary with all generated artifacts
        """
        print("\n" + "=" * 70)
        print(f"🚀 PROCESSING POLICY FOR: {company_name}")
        print("=" * 70)

        results = {
            "company_name": company_name,
            "company_id": company_name.upper().replace(' ', '_'),
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "ai_powered": True
        }

        try:
            # Initialize AI components
            parser = AIPolicyParser(
                azure_endpoint=self.azure_endpoint,
                api_key=self.api_key,
                deployment_name=self.deployment_name
            )

            generator = AICodeGenerator(
                company_name=company_name,
                azure_endpoint=self.azure_endpoint,
                api_key=self.api_key,
                deployment_name=self.deployment_name
            )

            # Step 1: Validate policy (optional but recommended)
            if validate_first:
                print("\n[1/6] 🤖 Validating policy with AI...")
                validation_result = parser.validate_policy(policy_text)
                results['validation'] = validation_result

                if validation_result.get('issues'):
                    high_severity = [i for i in validation_result['issues'] if i.get('severity') == 'high']
                    if high_severity:
                        print(f"  ⚠ WARNING: Found {len(high_severity)} high-severity issues")
                        print(f"  ℹ Consider fixing these before proceeding")

                print(f"  ✓ Validation complete - Score: {validation_result.get('completeness_score', 0):.2f}")
            else:
                print("\n[1/6] Skipping validation")

            # Step 2: Parse policy text with AI
            print(f"\n[2/6] 🤖 Parsing policy with AI...")
            parsed_rules = parser.parse_policy_text(policy_text)

            # Count total rules
            total_rules = sum([
                len(parsed_rules.get('cabin_class_rules', [])),
                len(parsed_rules.get('cost_approval_rules', [])),
                len(parsed_rules.get('advance_booking_rules', [])),
                len(parsed_rules.get('airline_preference_rules', [])),
                len(parsed_rules.get('baggage_rules', []))
            ])
            print(f"  ✓ Extracted {total_rules} total rules using AI")
            results['parsed_rules'] = parsed_rules
            results['total_rules'] = total_rules

            # Step 3: Generate Python code with AI
            print(f"\n[3/6] 🤖 Generating Python code with AI...")
            function_code = generator.generate_policy_module(parsed_rules)
            print(f"  ✓ Generated {function_code.count('def ')} functions")
            results['function_code'] = function_code
            results['function_count'] = function_code.count('def ')

            # Step 4: Store with versioning
            print(f"\n[4/6] 💾 Storing functions...")
            save_result = self.storage.save_function(
                company_id=results['company_id'],
                function_code=function_code,
                metadata=parsed_rules['metadata'],
                version=None if auto_version else "1.0.0"
            )
            print(f"  ✓ Saved as version {save_result['version']}")
            print(f"  ✓ File: {save_result['file_path']}")
            results.update(save_result)

            # Step 5: Register functions
            print(f"\n[5/6] 📋 Registering functions...")
            module = self.storage.import_function(results['company_id'])
            registry_info = self.registry.register_functions(results['company_id'], module)
            print(f"  ✓ Registered {len(registry_info.get('functions', []))} functions")
            results['registry'] = registry_info

            # Step 6: Generate tests
            if generate_tests:
                print(f"\n[6/6] 🧪 Generating unit tests...")
                test_gen = TestGenerator(results['company_id'])
                test_code = test_gen.generate_tests(parsed_rules)

                test_file = self.tests_dir / f"test_{results['company_id']}.py"
                with open(test_file, 'w') as f:
                    f.write(test_code)

                print(f"  ✓ Generated test suite: {test_file}")
                results['test_file'] = str(test_file)
            else:
                print(f"\n[6/6] Skipping test generation")

            results['success'] = True

            print("\n" + "=" * 70)
            print("✅ AI PIPELINE COMPLETED SUCCESSFULLY")
            print("=" * 70)
            print(f"📊 Summary:")
            print(f"   - Rules extracted: {results.get('total_rules', 0)}")
            print(f"   - Functions generated: {results.get('function_count', 0)}")
            print(f"   - Version: {results.get('version', 'unknown')}")
            if validate_first and 'validation' in results:
                print(f"   - Validation score: {results['validation'].get('completeness_score', 0):.2f}")
            print("=" * 70 + "\n")

        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            results['error'] = str(e)
            results['success'] = False

        return results

    def process_policy_file(
        self,
        policy_file_path: str,
        company_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process a policy from a text file using AI

        Args:
            policy_file_path: Path to policy text file
            company_name: Company name (derived from filename if not provided)
            **kwargs: Additional arguments for process_policy

        Returns:
            Processing results
        """
        policy_path = Path(policy_file_path)

        if not policy_path.exists():
            return {
                "success": False,
                "error": f"File not found: {policy_file_path}"
            }

        # Read policy text
        with open(policy_path, 'r') as f:
            policy_text = f.read()

        # Derive company name from filename if not provided
        if not company_name:
            company_name = policy_path.stem.replace('policy_', '').replace('_', ' ').title()

        return self.process_policy(policy_text, company_name, **kwargs)

    def list_policies(self) -> Dict[str, Any]:
        """
        List all stored policies

        Returns:
            Dictionary with policy information
        """
        companies = self.storage.list_companies()

        policies = []
        for company_id in companies:
            history = self.storage.get_version_history(company_id)
            registry = self.registry.get_registry(company_id)

            policies.append({
                "company_id": company_id,
                "versions": len(history),
                "latest_version": history[-1]['version'] if history else None,
                "functions": len(registry.get('functions', [])) if registry else 0,
                "last_updated": history[-1]['created_at'] if history else None
            })

        return {
            "total_policies": len(policies),
            "policies": policies
        }

    def get_policy_info(self, company_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a policy

        Args:
            company_id: Company identifier

        Returns:
            Policy information
        """
        # Get version history
        history = self.storage.get_version_history(company_id)

        # Get registry
        registry = self.registry.get_registry(company_id)

        # Get latest function code
        function_data = self.storage.load_function(company_id)

        return {
            "company_id": company_id,
            "versions": history,
            "functions": registry.get('functions', []) if registry else [],
            "latest_version": history[-1] if history else None,
            "code_available": function_data is not None
        }

    def delete_policy(self, company_id: str) -> Dict[str, Any]:
        """
        Delete a policy and all its versions

        Args:
            company_id: Company identifier

        Returns:
            Deletion result
        """
        success = self.storage.delete_function(company_id)

        return {
            "success": success,
            "company_id": company_id,
            "message": f"Deleted all versions of {company_id}" if success else "Deletion failed"
        }

    def generate_summary_report(self) -> str:
        """
        Generate a summary report of all policies

        Returns:
            Formatted report string
        """
        policies = self.list_policies()

        report = []
        report.append("=" * 70)
        report.append("🤖 AI-POWERED POLICY PIPELINE SUMMARY REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Policies: {policies['total_policies']}")
        report.append("")

        for policy in policies['policies']:
            report.append(f"Company: {policy['company_id']}")
            report.append(f"  Versions: {policy['versions']}")
            report.append(f"  Latest: {policy['latest_version']}")
            report.append(f"  Functions: {policy['functions']}")
            report.append(f"  Updated: {policy['last_updated']}")
            report.append("")

        report.append("=" * 70)

        return '\n'.join(report)


def quick_generate(
    policy_text: str,
    company_name: str,
    output_file: Optional[str] = None,
    azure_endpoint: Optional[str] = None,
    api_key: Optional[str] = None,
    deployment_name: Optional[str] = None
) -> str:
    """
    Quick utility to generate policy functions with AI without full pipeline

    Args:
        policy_text: Policy text
        company_name: Company name
        output_file: Optional output file path
        azure_endpoint: Azure OpenAI endpoint
        api_key: Azure OpenAI API key
        deployment_name: Azure OpenAI deployment name

    Returns:
        Generated Python code
    """
    print("🤖 Quick AI Generation")
    print("=" * 70)

    parser = AIPolicyParser(
        azure_endpoint=azure_endpoint,
        api_key=api_key,
        deployment_name=deployment_name
    )
    parsed = parser.parse_policy_text(policy_text)

    generator = AICodeGenerator(
        company_name=company_name,
        azure_endpoint=azure_endpoint,
        api_key=api_key,
        deployment_name=deployment_name
    )
    code = generator.generate_policy_module(parsed)

    if output_file:
        with open(output_file, 'w') as f:
            f.write(code)
        print(f"\n✓ Generated: {output_file}")

    print("=" * 70)

    return code


if __name__ == "__main__":
    # Example usage
    print("🤖 AI-Powered Policy-to-Code Pipeline")
    print("=" * 70)

    pipeline = PolicyPipeline()

    # Show current policies
    print("\nCurrent Policies:")
    print(pipeline.generate_summary_report())
