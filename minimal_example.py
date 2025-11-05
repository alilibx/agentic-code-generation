#!/usr/bin/env python3
"""
MINIMAL CODE GENERATION EXAMPLE
This is the absolute minimum code you need to generate functions from a policy
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline import PolicyPipeline

# 1. Create pipeline
pipeline = PolicyPipeline(storage_dir="generated")

# 2. Process your policy file
result = pipeline.process_policy_file(
    "policies/techstart_travel_policy.txt",  # Your policy file
    company_name="TechStart",          # Your company name
    generate_tests=True                       # Optional: generate tests
)

# 3. Use the generated functions
if result['success']:
    print(f"✅ Generated: {result['file_path']}")
    
    # Import and use
    module = pipeline.storage.import_function(result['company_id'])
    
    # Call any function
    cabin_check = module.check_cabin_class("manager", "international", 8.0)
    print(f"Cabin allowed: {cabin_check['cabin']}")
else:
    print(f"❌ Error: {result['error']}")
