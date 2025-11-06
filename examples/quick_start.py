"""
Policy Generation Quick Start

This script demonstrates the AI-powered policy-to-code pipeline.

Usage:
    python examples/quick_start.py
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pipeline import PolicyPipeline
from dotenv import load_dotenv


def main():
    """Main demonstration of AI-powered pipeline"""

    # Load environment variables
    load_dotenv()

    print("\n" + "=" * 70)
    print("🤖 AI-POWERED POLICY-TO-CODE PIPELINE DEMONSTRATION")
    print("=" * 70)

    # Check for Azure OpenAI credentials
    if not os.getenv("AZURE_OPENAI_ENDPOINT") or not os.getenv("AZURE_OPENAI_API_KEY"):
        print("\n❌ ERROR: Azure OpenAI credentials not found!")
        print("\nPlease set the following environment variables:")
        print("  - AZURE_OPENAI_ENDPOINT")
        print("  - AZURE_OPENAI_API_KEY")
        print("  - AZURE_OPENAI_DEPLOYMENT (optional, defaults to 'gpt-4')")
        print("\nYou can add these to a .env file in the project root.")
        sys.exit(1)

    # Initialize the pipeline
    pipeline = PolicyPipeline()

    # Example 1: Process the ACME Corp policy with AI
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Process Existing Policy with AI")
    print("=" * 70)

    policy_file = Path(__file__).parent / "policies" / "acme_corp_travel_policy.txt"

    if policy_file.exists():
        print(f"\n📄 Processing: {policy_file.name}")

        result = pipeline.process_policy_file(
            str(policy_file),
            validate_first=True,  # Validate policy before processing
            generate_tests=True
        )

        if result['success']:
            print("\n✅ Success!")
            print(f"\n📊 Results:")
            print(f"   Company: {result['company_name']}")
            print(f"   Company ID: {result['company_id']}")
            print(f"   Version: {result['version']}")
            print(f"   Rules extracted: {result.get('total_rules', 0)}")
            print(f"   Functions generated: {result.get('function_count', 0)}")

            if 'validation' in result:
                val = result['validation']
                print(f"\n📋 Validation:")
                print(f"   Completeness score: {val.get('completeness_score', 0):.2f}")
                print(f"   Issues found: {len(val.get('issues', []))}")

                if val.get('issues'):
                    print(f"\n   Issues:")
                    for issue in val['issues'][:5]:  # Show first 5
                        print(f"      [{issue.get('severity', 'medium').upper()}] {issue.get('description', '')}")

            print(f"\n📁 Generated files:")
            print(f"   - Code: {result['file_path']}")
            if 'test_file' in result:
                print(f"   - Tests: {result['test_file']}")

            # Example 2: Test the generated functions
            print("\n" + "=" * 70)
            print("EXAMPLE 2: Test Generated Functions")
            print("=" * 70)

            try:
                # Import the generated module
                from storage.function_storage import FunctionStorage

                storage = FunctionStorage()
                policy_module = storage.import_function(result['company_id'])

                print(f"\n✓ Imported generated module for {result['company_id']}")

                # Test cabin class function
                print("\n🧪 Testing check_cabin_class():")
                cabin_result = policy_module.check_cabin_class(
                    employee_level="senior_manager",
                    flight_type="international",
                    duration_hours=9.0,
                    requested_cabin="business"
                )
                print(f"   Input: Senior Manager, International, 9 hours, Business class")
                print(f"   Result: {cabin_result['allowed']}")
                print(f"   Reason: {cabin_result['reason']}")

                # Test cost approval function
                print("\n🧪 Testing check_cost_approval():")
                cost_result = policy_module.check_cost_approval(
                    employee_level="manager",
                    trip_cost=2500.0,
                    trip_type="standard"
                )
                print(f"   Input: Manager, $2,500, Standard trip")
                print(f"   Requires approval: {cost_result['requires_approval']}")
                print(f"   Reason: {cost_result['reason']}")

                # Test advance booking function
                print("\n🧪 Testing check_advance_booking():")
                booking_result = policy_module.check_advance_booking(
                    booking_date="2024-01-15",
                    travel_date="2024-02-01",
                    trip_type="conference"
                )
                print(f"   Input: Conference trip, 17 days advance")
                print(f"   Valid: {booking_result['valid']}")
                print(f"   Reason: {booking_result['reason']}")

                print("\n✅ All function tests passed!")

            except Exception as e:
                print(f"\n❌ Error testing functions: {e}")
                import traceback
                traceback.print_exc()

        else:
            print(f"\n❌ Failed: {result.get('error', 'Unknown error')}")

    else:
        print(f"\n❌ Policy file not found: {policy_file}")

    # Example 3: Process a custom policy text
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Process Custom Policy Text with AI")
    print("=" * 70)

    custom_policy = """
Company: TechStart Inc
Version: 1.0
Effective Date: 2024-06-01

TRAVEL POLICY

Cabin Class:
- All employees fly economy class on domestic flights
- For international flights over 8 hours, managers and above can fly premium economy
- Executives can fly business class on international flights over 10 hours

Cost Limits:
- Trips under $2,000 don't need approval
- Trips over $2,000 need manager approval
- Trips over $5,000 need director approval

Booking:
- Book at least 7 days in advance
- Emergency travel is exempt from advance booking requirements

Airlines:
- Preferred: Delta, United
- Other airlines require justification

Baggage:
- Standard allowance: 1 checked bag
- International trips: 2 checked bags
"""

    print("\n📝 Processing custom policy text...")

    custom_result = pipeline.process_policy(
        policy_text=custom_policy,
        company_name="TechStart Inc",
        validate_first=True,
        generate_tests=True
    )

    if custom_result['success']:
        print("\n✅ Custom policy processed successfully!")
        print(f"   Rules extracted: {custom_result.get('total_rules', 0)}")
        print(f"   Functions generated: {custom_result.get('function_count', 0)}")
        print(f"   Version: {custom_result['version']}")
        print(f"   File: {custom_result['file_path']}")
    else:
        print(f"\n❌ Failed: {custom_result.get('error', 'Unknown error')}")

    # Show all policies
    print("\n" + "=" * 70)
    print("ALL POLICIES")
    print("=" * 70)
    print(pipeline.generate_summary_report())

    print("\n" + "=" * 70)
    print("✅ DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\n💡 Next steps:")
    print("   1. Check the generated/ directory for your policy functions")
    print("   2. Import and use the functions in your application")
    print("   3. Run the generated tests with: pytest generated/tests/")
    print("   4. Use the Azure OpenAI chat interface for natural language queries")
    print("\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
