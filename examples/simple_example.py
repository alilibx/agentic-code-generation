"""
Simple Example - Process a Policy with AI

This is the simplest example of using the AI-powered pipeline.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pipeline import PolicyPipeline
from dotenv import load_dotenv


def main():
    # Load environment variables
    load_dotenv()

    # Create pipeline
    pipeline = PolicyPipeline()

    # Process a policy file
    result = pipeline.process_policy_file(
        str(Path(__file__).parent.parent / "policies" / "acme_corp_travel_policy.txt"),
        validate_first=True
    )

    if result['success']:
        print(f"\n✅ Success!")
        print(f"Generated {result['function_count']} functions")
        print(f"File: {result['file_path']}")

        # Test a generated function
        module = pipeline.storage.import_function(result['company_id'])

        # Get available functions
        functions = module.get_available_functions()
        print(f"\nAvailable functions:")
        for func in functions:
            print(f"  - {func['name']}")
    else:
        print(f"\n❌ Failed: {result.get('error')}")


if __name__ == "__main__":
    main()
