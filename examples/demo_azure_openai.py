#!/usr/bin/env python3
"""
Demo: Complete Policy Pipeline with Azure OpenAI Integration

This demo shows the complete workflow:
1. Load policy from text file
2. Generate Python functions
3. Store with versioning
4. Generate tests
5. Integrate with Azure OpenAI
6. Query using natural language

Requirements:
    pip install openai python-dotenv

Environment Variables:
    AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
    AZURE_OPENAI_API_KEY=your-api-key
"""

import sys
import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pipeline import PolicyPipeline
from ai_integration.azure_openai_client import AzureOpenAIPolicyClient, SimplePolicyClient


def demo_pipeline():
    """Demonstrate the complete policy processing pipeline"""
    print("=" * 80)
    print("DEMO: Policy-to-Code Pipeline")
    print("=" * 80)

    # Initialize pipeline
    pipeline = PolicyPipeline(storage_dir="generated")

    # Process ACME Corp policy
    print("\n📄 Processing ACME Corp Travel Policy...")
    print("-" * 80)

    policy_file = Path(__file__).parent.parent / "policies" / "acme_corp_travel_policy.txt"

    if not policy_file.exists():
        print(f"Error: Policy file not found: {policy_file}")
        return None

    result = pipeline.process_policy_file(
        str(policy_file),
        company_name="ACME Corporation",
        generate_tests=True
    )

    if not result['success']:
        print(f"Error processing policy: {result.get('error')}")
        return None

    print("\n✅ Policy processed successfully!")
    print(f"   Company ID: {result['company_id']}")
    print(f"   Version: {result['version']}")
    print(f"   Functions: {result['file_path']}")
    print(f"   Tests: {result.get('test_file', 'Not generated')}")

    return result


def demo_simple_client(company_id: str):
    """Demonstrate using the simple policy client (no Azure required)"""
    print("\n" + "=" * 80)
    print("DEMO: Simple Policy Client (Direct Function Calls)")
    print("=" * 80)

    # Initialize simple client
    client = SimplePolicyClient()

    # Load policy functions
    policy_file = Path("generated") / "functions" / f"{company_id}.py"

    if not policy_file.exists():
        print(f"Error: Policy functions not found: {policy_file}")
        return

    print(f"\n📦 Loading policy functions from: {policy_file}")
    client.load_policy_functions(str(policy_file))

    # List available functions
    print("\n📋 Available Functions:")
    for i, func in enumerate(client.list_functions(), 1):
        print(f"   {i}. {func['name']}: {func['description']}")

    # Example queries
    print("\n" + "=" * 80)
    print("EXAMPLE QUERIES")
    print("=" * 80)

    # Query 1: Cabin class
    print("\n1️⃣ Query: Can a manager book business class for 8-hour international flight?")
    print("-" * 80)

    result = client.call_function(
        "check_cabin_class",
        employee_level="manager",
        flight_type="international",
        duration_hours=8.0,
        requested_cabin="business"
    )

    print(f"   Allowed: {result.get('allowed')}")
    print(f"   Standard Cabin: {result.get('cabin')}")
    print(f"   Requires Approval: {result.get('requires_approval')}")
    print(f"   Reason: {result.get('reason')}")

    # Query 2: Cost approval
    print("\n2️⃣ Query: Does a $2,500 trip for a senior manager need approval?")
    print("-" * 80)

    result = client.call_function(
        "check_cost_approval",
        employee_level="senior_manager",
        trip_cost=2500.0
    )

    print(f"   Requires Approval: {result.get('requires_approval')}")
    print(f"   Threshold: ${result.get('threshold'):,.2f}")
    print(f"   Approval Level: {result.get('approval_level')}")
    print(f"   Reason: {result.get('reason')}")

    # Query 3: Advance booking
    print("\n3️⃣ Query: Is booking 10 days in advance sufficient?")
    print("-" * 80)

    result = client.call_function(
        "check_advance_booking",
        booking_date="2024-06-01",
        travel_date="2024-06-11"
    )

    print(f"   Valid: {result.get('valid')}")
    print(f"   Days Advance: {result.get('days_advance')}")
    print(f"   Required Days: {result.get('required_days')}")
    print(f"   Reason: {result.get('reason')}")

    # Query 4: Baggage
    print("\n4️⃣ Query: Can an executive bring 3 bags on a 5-day trip?")
    print("-" * 80)

    result = client.call_function(
        "check_baggage_allowance",
        employee_level="executive",
        num_bags=3,
        trip_duration_days=5
    )

    print(f"   Approved: {result.get('approved')}")
    print(f"   Allowed Bags: {result.get('allowed_bags')}")
    print(f"   Overage: {result.get('overage')} bags")
    print(f"   Overage Fee: ${result.get('overage_fee'):.2f}")


def demo_azure_openai(company_id: str):
    """Demonstrate Azure OpenAI integration"""
    print("\n" + "=" * 80)
    print("DEMO: Azure OpenAI Integration (Natural Language Queries)")
    print("=" * 80)

    # Check for credentials
    if not os.getenv("AZURE_OPENAI_ENDPOINT") or not os.getenv("AZURE_OPENAI_API_KEY"):
        print("\n⚠️  Azure OpenAI credentials not found!")
        print("\nTo use Azure OpenAI integration, set these environment variables:")
        print("   export AZURE_OPENAI_ENDPOINT='https://your-resource.openai.azure.com/'")
        print("   export AZURE_OPENAI_API_KEY='your-api-key'")
        print("\nOr create a .env file with these values.")
        print("\nSkipping Azure OpenAI demo...")
        return

    try:
        # Initialize Azure OpenAI client
        client = AzureOpenAIPolicyClient(
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
        )

        # Load policy functions
        policy_file = Path("generated") / "functions" / f"{company_id}.py"
        print(f"\n📦 Loading policy functions for Azure OpenAI...")
        client.load_policy_functions(str(policy_file))

        # Example natural language queries
        print("\n" + "=" * 80)
        print("NATURAL LANGUAGE QUERIES")
        print("=" * 80)

        queries = [
            "Can I book business class if I'm a manager flying to Tokyo (10 hours)?",
            "I'm a staff member and my trip costs $2,000. Do I need approval?",
            "Is it okay to book a flight 5 days before departure for a conference?",
            "How many bags can a senior manager check for a 2-week trip?"
        ]

        for i, query in enumerate(queries, 1):
            print(f"\n{i}️⃣ Question: {query}")
            print("-" * 80)

            result = client.query(query)

            if result.get('error'):
                print(f"   ❌ Error: {result['error']}")
            else:
                print(f"   💬 Answer: {result['answer']}\n")

                if result.get('function_calls'):
                    print(f"   📞 Functions Called:")
                    for call in result['function_calls']:
                        print(f"      - {call['function']}({call['arguments']})")

    except Exception as e:
        print(f"\n❌ Error with Azure OpenAI: {str(e)}")
        print("\nMake sure:")
        print("   1. You have 'openai' package installed: pip install openai")
        print("   2. Your credentials are correct")
        print("   3. Your deployment name is correct")


def demo_interactive_chat(company_id: str):
    """Start an interactive chat session"""
    print("\n" + "=" * 80)
    print("DEMO: Interactive Chat Session")
    print("=" * 80)

    # Check for credentials
    if not os.getenv("AZURE_OPENAI_ENDPOINT") or not os.getenv("AZURE_OPENAI_API_KEY"):
        print("\n⚠️  Azure OpenAI credentials required for interactive chat.")
        print("Skipping interactive demo...")
        return

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    try:
        client = AzureOpenAIPolicyClient(
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
        )

        policy_file = Path("generated") / "functions" / f"{company_id}.py"
        client.load_policy_functions(str(policy_file))

        print("\nStarting interactive chat...")
        print("You can ask questions about the travel policy.")
        print("Type 'quit' to exit.\n")

        client.chat()

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def main():
    """Main demo function"""
    print("""
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                                                                          ║
    ║               POLICY-TO-CODE PIPELINE DEMONSTRATION                      ║
    ║                                                                          ║
    ║  This demo shows the complete workflow from policy text to AI-powered   ║
    ║  question answering using Azure OpenAI.                                  ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """)

    # Step 1: Process policy
    result = demo_pipeline()

    if not result:
        print("\n❌ Demo failed: Could not process policy")
        return

    company_id = result['company_id']

    # Step 2: Demo simple client (no Azure required)
    demo_simple_client(company_id)

    # Step 3: Demo Azure OpenAI (if credentials available)
    demo_azure_openai(company_id)

    # Step 4: Offer interactive chat
    print("\n" + "=" * 80)
    response = input("\nWould you like to try the interactive chat? (y/N): ").strip().lower()

    if response == 'y':
        demo_interactive_chat(company_id)

    # Final summary
    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print("\nGenerated Files:")
    print(f"   • Functions: {result['file_path']}")
    print(f"   • Tests: {result.get('test_file', 'N/A')}")
    print(f"   • Version: {result['version']}")

    print("\nNext Steps:")
    print("   1. Review generated functions in 'generated/functions/'")
    print("   2. Run tests with: pytest generated/tests/")
    print("   3. Customize Azure OpenAI prompts in ai_integration/")
    print("   4. Process more policies from 'policies/' directory")

    print("\n✨ Thank you for trying the Policy-to-Code Pipeline! ✨\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
