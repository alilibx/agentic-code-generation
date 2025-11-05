#!/usr/bin/env python3
"""
Interactive usage - Use Python REPL to experiment
"""

# Run this in terminal:
# source venv/bin/activate
# python -i interactive_usage.py

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline import PolicyPipeline

# Initialize pipeline
pipeline = PolicyPipeline(storage_dir="generated")

print("""
================================================================================
INTERACTIVE MODE - Ready to use!
================================================================================

Try these commands:

1. Process a policy:
   >>> result = pipeline.process_policy_file(
   ...     "policies/acme_corp_travel_policy.txt",
   ...     company_name="ACME Corporation"
   ... )

2. Load the generated module:
   >>> module = pipeline.storage.import_function("ACME_CORPORATION")

3. Call functions:
   >>> module.check_cabin_class("manager", "international", 8.0)
   >>> module.check_cost_approval("staff", 2000)
   >>> module.check_baggage_allowance("executive", 3, 7)

4. List available functions:
   >>> module.get_available_functions()

5. Process from text directly (without a file):
   >>> policy_text = '''
   ... Company: My Company
   ... Managers can book business class for international flights over 8 hours.
   ... '''
   >>> result = pipeline.process_policy(policy_text, company_name="My Company")

================================================================================
""")
