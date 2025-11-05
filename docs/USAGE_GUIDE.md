# Usage Guide

Complete guide to using the Policy-to-Code Pipeline.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Writing Policies](#writing-policies)
3. [Processing Policies](#processing-policies)
4. [Using Generated Functions](#using-generated-functions)
5. [Azure OpenAI Integration](#azure-openai-integration)
6. [Testing](#testing)
7. [Advanced Usage](#advanced-usage)
8. [Troubleshooting](#troubleshooting)

## Getting Started

### Installation

```bash
# Clone repository
git clone <repo-url>
cd agentic-rules-to-code

# Optional: Install dependencies for Azure OpenAI
pip install -r requirements.txt
```

### First Run

```bash
# Run the quick start example
python examples/quick_start.py
```

This processes an example policy and demonstrates basic usage.

## Writing Policies

### Policy Format

Policies should be written in plain text with clear structure:

```text
Company: Your Company Name
Policy Version: 1.0
Effective Date: 2024-01-01

SECTION 1: CABIN CLASS RULES

Executives can book business class for international flights over 6 hours.
Managers can book premium economy for flights over 8 hours.
Staff must book economy class.

SECTION 2: COST APPROVAL

Travel over $2000 requires manager approval.
Travel over $5000 requires director approval.

SECTION 3: ADVANCE BOOKING

Book at least 7 days in advance for domestic travel.
Book at least 14 days in advance for international travel.
```

### Supported Rule Types

#### 1. Cabin Class Rules

Pattern examples:
- "Executives can book business class for international flights over 6 hours"
- "Managers: premium economy for flights over 8 hours"
- "Staff: economy class only"

Key elements:
- Employee level (executive, manager, staff)
- Cabin class (business, premium economy, economy)
- Flight type (international, domestic)
- Duration threshold (hours)

#### 2. Cost Approval Rules

Pattern examples:
- "Travel over $2000 requires manager approval"
- "$5000 needs director approval"
- "Expenses above $1500 require approval"

Key elements:
- Dollar amount threshold
- Approval level needed

#### 3. Advance Booking Rules

Pattern examples:
- "Book 7 days in advance"
- "14 days advance booking required"
- "Minimum 21 days before travel"

Key elements:
- Number of days
- Requirement type

#### 4. Airline Preferences

Pattern examples:
- "Preferred airlines: Delta, United, American"
- "Approved carriers: Southwest, JetBlue"

Key elements:
- List of airline names

#### 5. Baggage Rules

Pattern examples:
- "2 checked bags allowed"
- "Executives: 3 pieces of luggage"
- "Maximum 1 checked bag for staff"

Key elements:
- Number of bags
- Employee level (if specified)

### Best Practices

1. **Be Specific**: Use concrete numbers and clear categories
   - ✅ "Managers can book business class for flights over 8 hours"
   - ❌ "Managers can sometimes book business class"

2. **Use Consistent Terms**: Stick to standard employee levels
   - executive, senior_manager, manager, staff, contractor

3. **Include Context**: Add metadata at the top
   ```text
   Company: ACME Corp
   Policy Version: 2.1
   Effective Date: 2024-01-01
   ```

4. **Organize Clearly**: Use sections and headings
   ```text
   ========================================
   SECTION 1: CABIN CLASS POLICY
   ========================================
   ```

5. **Be Explicit**: State both what IS and ISN'T allowed
   - "Executives can book business class..."
   - "Staff must book economy class only"

## Processing Policies

### Method 1: Using the Pipeline

```python
from src.pipeline import PolicyPipeline

pipeline = PolicyPipeline()

# Process from file
result = pipeline.process_policy_file(
    "policies/my_policy.txt",
    company_name="My Company",
    generate_tests=True
)

# Check result
if result['success']:
    print(f"Generated: {result['file_path']}")
    print(f"Version: {result['version']}")
else:
    print(f"Error: {result['error']}")
```

### Method 2: Using Quick Generate

```python
from src.pipeline import quick_generate

policy_text = """
Company: Test Co
Managers can book business class for international flights over 8 hours.
"""

code = quick_generate(
    policy_text,
    company_name="Test Co",
    output_file="my_policy.py"
)

print(code)
```

### Method 3: Command Line

```python
# In pipeline.py, run directly
python src/pipeline.py
```

### Processing Options

```python
result = pipeline.process_policy(
    policy_text=policy_text,
    company_name="My Company",
    generate_tests=True,      # Generate pytest tests
    auto_version=True          # Auto-increment version
)
```

## Using Generated Functions

### Import and Use

```python
from src.pipeline import PolicyPipeline

pipeline = PolicyPipeline()

# Import the generated module
module = pipeline.storage.import_function("MY_COMPANY")

# Call functions
result = module.check_cabin_class(
    employee_level="manager",
    flight_type="international",
    duration_hours=8.0
)

print(result)
# {
#   "allowed": True,
#   "cabin": "premium_economy",
#   "requires_approval": False,
#   "reason": "Premium economy is allowed...",
#   "company_id": "MY_COMPANY"
# }
```

### Available Functions

All generated modules include:

1. **check_cabin_class()**
   ```python
   result = module.check_cabin_class(
       employee_level="manager",
       flight_type="international",
       duration_hours=8.0,
       requested_cabin="business"  # optional
   )
   ```

2. **check_cost_approval()**
   ```python
   result = module.check_cost_approval(
       employee_level="manager",
       trip_cost=2500.0,
       trip_type="standard"  # or "emergency", "conference"
   )
   ```

3. **check_advance_booking()**
   ```python
   result = module.check_advance_booking(
       booking_date="2024-06-01",
       travel_date="2024-06-15",
       trip_type="standard"
   )
   ```

4. **check_airline_preference()**
   ```python
   result = module.check_airline_preference(
       airline_name="Delta",
       reason="best_price"
   )
   ```

5. **check_baggage_allowance()**
   ```python
   result = module.check_baggage_allowance(
       employee_level="manager",
       num_bags=2,
       trip_duration_days=5
   )
   ```

6. **get_available_functions()**
   ```python
   functions = module.get_available_functions()
   for func in functions:
       print(f"{func['name']}: {func['description']}")
   ```

### Return Values

All functions return dictionaries with:
- Specific result fields (varies by function)
- `company_id`: Company identifier
- `policy_applied`: Which policy was used
- Explanation/reason fields

## Azure OpenAI Integration

### Setup

1. **Get Azure OpenAI Credentials**
   - Create an Azure OpenAI resource
   - Deploy a GPT-4 model
   - Note your endpoint and API key

2. **Configure Environment**
   ```bash
   cp config/.env.example .env
   # Edit .env with your credentials
   ```

3. **Install Dependencies**
   ```bash
   pip install openai python-dotenv
   ```

### Basic Usage

```python
from src.ai_integration.azure_openai_client import AzureOpenAIPolicyClient

# Initialize client
client = AzureOpenAIPolicyClient()

# Load policy functions
client.load_policy_functions("generated/functions/ACME_CORP.py")

# Ask questions
result = client.query(
    "Can a manager book business class for a 10-hour flight to London?"
)

print(result['answer'])
# Functions called: check_cabin_class
```

### Interactive Chat

```python
# Start interactive chat session
client.chat()
```

```
Travel Policy Assistant
Ask questions about travel policies. Type 'quit' to exit.

You: Can I book business class?
Assistant: That depends on your job level and flight details. Can you
tell me:
1. Your job level (manager, staff, executive, etc.)
2. Flight type (international or domestic)
3. Flight duration in hours

You: I'm a manager, international flight, 10 hours
Assistant: Yes! As a manager, you can book premium economy class for
international flights over 8 hours. The 10-hour flight qualifies.

For business class, you would need manager approval as it exceeds
your standard allowance.
```

### Advanced Queries

```python
# Multi-turn conversation
conversation = []

result1 = client.query(
    "I'm planning a trip to Tokyo",
    conversation_history=conversation
)
conversation = result1['conversation']

result2 = client.query(
    "How many bags can I bring?",
    conversation_history=conversation
)

# The AI remembers context from previous questions
```

### Function Calling

The client automatically:
1. Understands user intent
2. Extracts parameters
3. Calls appropriate functions
4. Formats results into natural language

Example:
```
User: "Can a senior manager book business for a 9-hour international flight?"

AI internally:
  1. Identifies function: check_cabin_class
  2. Extracts params: {
       employee_level: "senior_manager",
       flight_type: "international",
       duration_hours: 9.0
     }
  3. Calls function
  4. Returns: "Yes, senior managers can book business class..."
```

## Testing

### Run Generated Tests

```bash
# Run tests for specific policy
pytest generated/tests/test_ACME_CORP.py -v

# Run all tests
pytest generated/tests/ -v

# With coverage
pytest generated/tests/ --cov=generated/functions
```

### Test Structure

Generated tests include:
- ✅ Basic functionality tests
- ✅ Edge case tests
- ✅ Parametrized tests
- ✅ Integration tests
- ✅ Performance tests

### Add Custom Tests

```python
# In generated/tests/test_ACME_CORP.py

def test_my_custom_scenario():
    """Test specific business scenario"""
    result = policy.check_cabin_class(
        employee_level="manager",
        flight_type="international",
        duration_hours=8.0
    )

    assert result['cabin'] == 'premium_economy'
    assert result['requires_approval'] == False
```

## Advanced Usage

### Version Management

```python
# List all versions
history = pipeline.storage.get_version_history("ACME_CORP")
for version in history:
    print(f"Version {version['version']}: {version['created_at']}")

# Load specific version
function_data = pipeline.storage.load_function(
    "ACME_CORP",
    version="1.0.0"
)

# Delete old versions
pipeline.storage.delete_function("ACME_CORP", version="1.0.0")
```

### Multiple Companies

```python
# Process multiple policies
companies = [
    ("policies/acme.txt", "ACME Corp"),
    ("policies/techstart.txt", "TechStart"),
    ("policies/global.txt", "Global Inc")
]

for policy_file, company_name in companies:
    result = pipeline.process_policy_file(policy_file, company_name)
    print(f"Processed: {company_name}")

# List all companies
companies = pipeline.storage.list_companies()
print(companies)  # ['ACME_CORP', 'TECHSTART', 'GLOBAL_INC']
```

### Function Registry

```python
from src.storage.function_storage import FunctionRegistry

registry = FunctionRegistry(pipeline.storage)

# Search functions across all companies
results = registry.search_functions("cabin")

for result in results:
    print(f"{result['company_id']}: {result['name']}")
```

### Custom Storage Location

```python
pipeline = PolicyPipeline(storage_dir="custom/path")
```

## Troubleshooting

### Issue: Import Errors

**Problem**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
```

### Issue: Azure OpenAI Authentication Failed

**Problem**: `Error: Azure OpenAI client not initialized`

**Solution**:
1. Check `.env` file exists and has correct values
2. Verify endpoint URL format: `https://xxx.openai.azure.com/`
3. Confirm API key is valid
4. Check deployment name matches your Azure deployment

### Issue: Generated Functions Not Found

**Problem**: `Function not found: COMPANY_NAME`

**Solution**:
1. Verify policy was processed successfully
2. Check file exists: `generated/functions/COMPANY_NAME.py`
3. Use exact company_id (uppercase, underscores): `ACME_CORP` not `Acme Corp`

### Issue: Tests Failing

**Problem**: Generated tests fail

**Solution**:
1. Check generated functions exist
2. Verify module path in test file
3. Run with verbose flag: `pytest -v` to see details
4. Check if policy rules were parsed correctly

### Issue: Policy Not Parsing Correctly

**Problem**: Rules not extracted from policy text

**Solution**:
1. Check policy follows format guidelines
2. Use clear, explicit language
3. Include numbers and thresholds
4. Review examples in `policies/` directory
5. Test with simple policies first

### Getting Help

1. **Check Examples**: Review `examples/` directory
2. **Read Docs**: See `docs/` for detailed guides
3. **Run Demos**: Execute demo scripts to see working examples
4. **Enable Debug**: Set `DEBUG=true` in `.env`

## Next Steps

- **Customize Policies**: Write your own policy documents
- **Extend Functionality**: Add custom rule types
- **Deploy**: Integrate with your applications
- **Scale**: Process multiple policies
- **Monitor**: Track function usage and performance

For more information:
- See `README.md` for overview
- See `docs/API.md` for API reference
- See `docs/EXTENDING.md` for customization guide
