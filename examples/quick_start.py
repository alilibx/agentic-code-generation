#!/usr/bin/env python3
"""
Quick Start Example - Minimal code to get started

This is the simplest way to use the policy pipeline:
1. Load a policy text file
2. Generate functions
3. Use them!

Run: python examples/quick_start.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pipeline import PolicyPipeline


def main():
    print("🚀 Policy-to-Code Pipeline - Quick Start\n")

    # Step 1: Create pipeline
    print("Step 1: Creating pipeline...")
    pipeline = PolicyPipeline(storage_dir="generated")

    # Step 2: Process a policy
    print("Step 2: Processing policy...\n")

    policy_file = Path(__file__).parent.parent / "policies" / "acme_corp_travel_policy.txt"

    result = pipeline.process_policy_file(
        str(policy_file),
        company_name="ACME Corporation",
        generate_tests=True
    )

    if result['success']:
        print("\n✅ Success!")
        print(f"\nGenerated files:")
        print(f"  📄 Functions: {result['file_path']}")
        print(f"  🧪 Tests: {result['test_file']}")

        # Step 3: Use the functions
        print("\n" + "="*60)
        print("Step 3: Using generated functions...")
        print("="*60)

        # Import the generated module
        module = pipeline.storage.import_function(result['company_id'])

        # Call a function
        print("\nExample: Check cabin class for a manager")
        result = module.check_cabin_class(
            employee_level="manager",
            flight_type="international",
            duration_hours=8.0
        )

        print(f"\n  Allowed Cabin: {result['cabin']}")
        print(f"  Requires Approval: {result['requires_approval']}")
        print(f"  Reason: {result['reason']}")

        # Show all available functions
        print("\n" + "="*60)
        print("Available Functions:")
        print("="*60)

        for func in module.get_available_functions():
            print(f"\n✓ {func['name']}")
            print(f"  {func['description']}")

        print("\n🎉 That's it! Your policy is now executable code.\n")

    else:
        print(f"❌ Error: {result.get('error')}")


if __name__ == "__main__":
    main()
