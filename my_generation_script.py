#!/usr/bin/env python3
"""
Simple script to generate code from a policy file
Step-by-step example without using the pre-made examples
"""

import sys
from pathlib import Path

# Add src to path so we can import the pipeline
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline import PolicyPipeline

def main():
    print("=" * 80)
    print("STEP-BY-STEP CODE GENERATION")
    print("=" * 80)
    
    # STEP 1: Create the pipeline
    print("\n📦 STEP 1: Creating the Policy Pipeline")
    print("-" * 80)
    pipeline = PolicyPipeline(storage_dir="generated")
    print("✅ Pipeline created!")
    
    # STEP 2: Choose your policy file
    print("\n📄 STEP 2: Loading Policy File")
    print("-" * 80)
    policy_file = "policies/acme_corp_travel_policy.txt"
    company_name = "ACME Corporation"
    
    print(f"Policy file: {policy_file}")
    print(f"Company name: {company_name}")
    
    # STEP 3: Process the policy (this does the magic!)
    print("\n🔄 STEP 3: Processing Policy (Generating Code)")
    print("-" * 80)
    
    result = pipeline.process_policy_file(
        policy_file,
        company_name=company_name,
        generate_tests=True  # Set to False if you don't want tests
    )
    
    # STEP 4: Check the results
    print("\n✅ STEP 4: Results")
    print("-" * 80)
    
    if result['success']:
        print("SUCCESS! Code generated successfully!\n")
        print(f"📁 Generated files:")
        print(f"   • Functions: {result['file_path']}")
        print(f"   • Tests: {result['test_file']}")
        print(f"   • Version: {result['version']}")
        print(f"   • Company ID: {result['company_id']}")
    else:
        print(f"❌ ERROR: {result.get('error')}")
        return
    
    # STEP 5: Use the generated functions
    print("\n🎯 STEP 5: Using Generated Functions")
    print("-" * 80)
    
    # Import the generated module
    module = pipeline.storage.import_function(result['company_id'])
    
    # Example 1: Check cabin class
    print("\nExample 1: Check cabin class for a manager")
    cabin_result = module.check_cabin_class(
        employee_level="manager",
        flight_type="international",
        duration_hours=8.0
    )
    print(f"  Result: {cabin_result['cabin']}")
    print(f"  Reason: {cabin_result['reason']}")
    
    # Example 2: Check cost approval
    print("\nExample 2: Check if $2,500 trip needs approval")
    cost_result = module.check_cost_approval(
        employee_level="manager",
        trip_cost=2500.0
    )
    print(f"  Needs approval: {cost_result['requires_approval']}")
    print(f"  Reason: {cost_result['reason']}")
    
    # STEP 6: List all available functions
    print("\n📋 STEP 6: Available Functions")
    print("-" * 80)
    
    functions = module.get_available_functions()
    for i, func in enumerate(functions, 1):
        print(f"{i}. {func['name']}")
        print(f"   {func['description']}")
    
    print("\n" + "=" * 80)
    print("✨ DONE! Your policy is now executable Python code!")
    print("=" * 80)
    
    print("\n💡 Next steps:")
    print("   1. Check the generated code in:", result['file_path'])
    print("   2. Run the tests: pytest", result['test_file'])
    print("   3. Import and use in your own code:")
    print(f"      from generated.functions import {result['company_id']}")

if __name__ == "__main__":
    main()
