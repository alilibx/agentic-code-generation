"""
Policy-to-Code Pipeline
Main orchestrator that connects all components.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from generator.policy_parser import PolicyParser
from generator.code_generator import CodeGenerator
from storage.function_storage import FunctionStorage, FunctionRegistry
from testing.test_generator import TestGenerator


class PolicyPipeline:
    """
    Main pipeline for converting policies to executable code

    This orchestrates the entire workflow:
    1. Parse policy text
    2. Generate Python functions
    3. Store with versioning
    4. Generate tests
    5. Make available for AI integration
    """

    def __init__(self, storage_dir: str = "generated"):
        """
        Initialize the pipeline

        Args:
            storage_dir: Directory for storing generated files
        """
        self.storage_dir = Path(storage_dir)
        self.storage = FunctionStorage(str(self.storage_dir))
        self.registry = FunctionRegistry(self.storage)

        # Create output directories
        self.tests_dir = self.storage_dir / "tests"
        self.tests_dir.mkdir(exist_ok=True, parents=True)

        print(f"Pipeline initialized. Storage: {self.storage_dir}")

    def process_policy(
        self,
        policy_text: str,
        company_name: str,
        generate_tests: bool = True,
        auto_version: bool = True
    ) -> Dict[str, Any]:
        """
        Process a policy text through the complete pipeline

        Args:
            policy_text: Plain text policy document
            company_name: Company name/identifier
            generate_tests: Whether to generate unit tests
            auto_version: Whether to auto-increment version

        Returns:
            Dictionary with all generated artifacts
        """
        print("=" * 70)
        print(f"PROCESSING POLICY FOR: {company_name}")
        print("=" * 70)

        results = {
            "company_name": company_name,
            "company_id": company_name.upper().replace(' ', '_'),
            "timestamp": datetime.now().isoformat(),
            "success": False
        }

        try:
            # Step 1: Parse policy text
            print("\n[1/5] Parsing policy text...")
            parser = PolicyParser()
            parsed_rules = parser.parse_policy_text(policy_text)
            print(f"  ✓ Parsed {len(parsed_rules)} rule categories")
            results['parsed_rules'] = parsed_rules

            # Step 2: Generate Python code
            print("\n[2/5] Generating Python functions...")
            generator = CodeGenerator(company_name)
            function_code = generator.generate_policy_module(parsed_rules)
            print(f"  ✓ Generated {function_code.count('def ')} functions")
            results['function_code'] = function_code

            # Step 3: Store with versioning
            print("\n[3/5] Storing functions...")
            save_result = self.storage.save_function(
                company_id=results['company_id'],
                function_code=function_code,
                metadata=parsed_rules['metadata'],
                version=None if auto_version else "1.0.0"
            )
            print(f"  ✓ Saved as version {save_result['version']}")
            print(f"  ✓ File: {save_result['file_path']}")
            results.update(save_result)

            # Step 4: Register functions
            print("\n[4/5] Registering functions...")
            module = self.storage.import_function(results['company_id'])
            registry_info = self.registry.register_functions(results['company_id'], module)
            print(f"  ✓ Registered {len(registry_info.get('functions', []))} functions")
            results['registry'] = registry_info

            # Step 5: Generate tests
            if generate_tests:
                print("\n[5/5] Generating unit tests...")
                test_gen = TestGenerator(results['company_id'])
                test_code = test_gen.generate_tests(parsed_rules)

                test_file = self.tests_dir / f"test_{results['company_id']}.py"
                with open(test_file, 'w') as f:
                    f.write(test_code)

                print(f"  ✓ Generated test suite: {test_file}")
                results['test_file'] = str(test_file)
            else:
                print("\n[5/5] Skipping test generation")

            results['success'] = True
            print("\n" + "=" * 70)
            print("✓ PIPELINE COMPLETED SUCCESSFULLY")
            print("=" * 70)

        except Exception as e:
            print(f"\n✗ ERROR: {str(e)}")
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
        Process a policy from a text file

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
        report.append("POLICY PIPELINE SUMMARY REPORT")
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
    output_file: Optional[str] = None
) -> str:
    """
    Quick utility to generate policy functions without full pipeline

    Args:
        policy_text: Policy text
        company_name: Company name
        output_file: Optional output file path

    Returns:
        Generated Python code
    """
    parser = PolicyParser()
    parsed = parser.parse_policy_text(policy_text)

    generator = CodeGenerator(company_name)
    code = generator.generate_policy_module(parsed)

    if output_file:
        with open(output_file, 'w') as f:
            f.write(code)
        print(f"Generated: {output_file}")

    return code


if __name__ == "__main__":
    # Example usage
    print("Policy-to-Code Pipeline")
    print("=" * 70)

    pipeline = PolicyPipeline()

    # Show current policies
    print("\nCurrent Policies:")
    print(pipeline.generate_summary_report())
