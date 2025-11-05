# 🚀 Quick Start Guide

## What Was Built

A complete **Policy-to-Code Pipeline** that converts plain text policies into executable Python functions with Azure OpenAI integration.

## ✨ Key Features

1. **📝 Policy Parser** - Converts plain text to structured rules
2. **🔄 Code Generator** - Creates Python functions automatically
3. **📦 Function Storage** - Versions and stores generated code
4. **🧪 Test Generator** - Auto-generates pytest test suites
5. **🤖 Azure OpenAI Integration** - Natural language policy queries
6. **⚡ Zero Dependencies** - Core works without external packages

## 🎯 5-Minute Quick Start

### 1. Run the Demo

```bash
python examples/quick_start.py
```

This will:
- Load the ACME Corp travel policy
- Generate Python functions
- Create unit tests
- Demonstrate usage

**Expected Output:**
```
🚀 Policy-to-Code Pipeline - Quick Start

Step 1: Creating pipeline...
Step 2: Processing policy...
[1/5] Parsing policy text... ✓
[2/5] Generating Python functions... ✓
[3/5] Storing functions... ✓
[4/5] Registering functions... ✓
[5/5] Generating unit tests... ✓

✅ Success!
Generated files:
  📄 Functions: generated/functions/ACME_CORPORATION.py
  🧪 Tests: generated/tests/test_ACME_CORPORATION.py

Available Functions:
✓ check_cabin_class
✓ check_cost_approval
✓ check_advance_booking
✓ check_airline_preference
✓ check_baggage_allowance

🎉 That's it! Your policy is now executable code.
```

### 2. Use Generated Functions

```python
# The functions are already imported!
from src.pipeline import PolicyPipeline

pipeline = PolicyPipeline()
module = pipeline.storage.import_function("ACME_CORPORATION")

# Check if a manager can book business class
result = module.check_cabin_class(
    employee_level="manager",
    flight_type="international",
    duration_hours=10.0
)

print(result)
# Output: {'allowed': True, 'cabin': 'premium_economy', ...}
```

### 3. Run Tests

```bash
pytest generated/tests/test_ACME_CORPORATION.py -v
```

### 4. Try Azure OpenAI (Optional)

Set up your credentials:
```bash
cp config/.env.example .env
# Edit .env with your Azure OpenAI credentials
```

Run the full demo:
```bash
python examples/demo_azure_openai.py
```

## 📁 What Was Generated

```
agentic-rules-to-code/
├── src/                    # Core pipeline code
│   ├── generator/          # Parse & generate functions
│   ├── storage/            # Version control & storage
│   ├── testing/            # Test generation
│   ├── ai_integration/     # Azure OpenAI client
│   └── pipeline.py         # Main orchestrator
│
├── examples/               # Demo scripts
│   ├── quick_start.py      # 👈 Start here!
│   └── demo_azure_openai.py
│
├── policies/               # Example policies
│   ├── acme_corp_travel_policy.txt
│   └── techstart_travel_policy.txt
│
├── generated/              # Output directory
│   ├── functions/          # Generated Python code
│   ├── tests/              # Generated test suites
│   ├── versions/           # Version history
│   └── metadata/           # Policy metadata
│
├── docs/                   # Documentation
│   └── USAGE_GUIDE.md      # Complete guide
│
├── README.md               # Full documentation
└── requirements.txt        # Optional dependencies
```

## 🎓 Usage Patterns

### Pattern 1: Process Your Own Policy

```python
from src.pipeline import PolicyPipeline

pipeline = PolicyPipeline()

# Write your policy in plain text
policy_text = """
Company: My Company
Managers can book business class for flights over 8 hours.
Travel over $2000 requires approval.
"""

# Process it
result = pipeline.process_policy(
    policy_text,
    company_name="My Company",
    generate_tests=True
)

print(f"Generated: {result['file_path']}")
```

### Pattern 2: Use Simple Client (No Azure)

```python
from src.ai_integration.azure_openai_client import SimplePolicyClient

client = SimplePolicyClient()
client.load_policy_functions("generated/functions/ACME_CORPORATION.py")

# Call functions directly
result = client.call_function(
    "check_cabin_class",
    employee_level="manager",
    flight_type="international",
    duration_hours=8.0
)
```

### Pattern 3: Azure OpenAI Integration

```python
from src.ai_integration.azure_openai_client import AzureOpenAIPolicyClient

client = AzureOpenAIPolicyClient()
client.load_policy_functions("generated/functions/ACME_CORPORATION.py")

# Ask in natural language
result = client.query(
    "Can a manager book business class for a 10-hour flight?"
)

print(result['answer'])
# "Yes! Managers can book premium economy for..."
```

### Pattern 4: Interactive Chat

```python
client.chat()
# Starts an interactive session where you can ask questions
```

## 🔧 Supported Policy Types

The system handles these policy types automatically:

1. **Cabin Class Rules**
   - Employee level allowances
   - Flight duration thresholds
   - International vs domestic

2. **Cost Approval**
   - Spending thresholds by level
   - Approval requirements

3. **Advance Booking**
   - Booking windows
   - Emergency exceptions

4. **Airline Preferences**
   - Preferred carrier lists
   - Justification requirements

5. **Baggage Allowance**
   - Checked bag limits
   - Trip duration bonuses

## 📊 Example Policy Format

```text
Company: Your Company Name
Policy Version: 1.0
Effective Date: 2024-01-01

CABIN CLASS POLICY
------------------
Executives can book business class for international flights over 6 hours.
Managers can book premium economy for flights over 8 hours.
Staff must book economy class.

COST APPROVAL
-------------
Travel over $2000 requires manager approval.
Travel over $5000 requires director approval.

ADVANCE BOOKING
---------------
Book at least 7 days in advance for domestic travel.
Book at least 14 days in advance for international travel.
```

## 🧪 Testing

### Run Generated Tests

```bash
# Test specific policy
pytest generated/tests/test_ACME_CORPORATION.py -v

# Test all policies
pytest generated/tests/ -v

# With coverage
pytest generated/tests/ --cov=generated/functions
```

### Test Results Include

- ✅ Cabin class combinations
- ✅ Cost approval thresholds
- ✅ Booking window validations
- ✅ Edge cases
- ✅ Integration scenarios

## 🌐 Azure OpenAI Setup

### 1. Get Credentials

1. Create Azure OpenAI resource
2. Deploy GPT-4 model
3. Note endpoint and API key

### 2. Configure

```bash
# Copy template
cp config/.env.example .env

# Edit .env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4
```

### 3. Install Dependencies

```bash
pip install openai python-dotenv
```

### 4. Test

```bash
python examples/demo_azure_openai.py
```

## 📚 Next Steps

1. **Try It Out**
   ```bash
   python examples/quick_start.py
   ```

2. **Read the Docs**
   - `README.md` - Complete overview
   - `docs/USAGE_GUIDE.md` - Detailed usage
   - Example policies in `policies/`

3. **Create Your Policy**
   - Copy `policies/acme_corp_travel_policy.txt`
   - Modify for your needs
   - Process with pipeline

4. **Integrate**
   - Use generated functions in your app
   - Add Azure OpenAI for NL queries
   - Deploy to production

## 💡 Tips

- **Start Simple**: Use quick_start.py first
- **No Azure Needed**: Core features work without Azure OpenAI
- **Versioning**: Pipeline automatically versions your functions
- **Testing**: Tests are auto-generated for quality
- **Customization**: Extend parsers for custom policy types

## 🆘 Troubleshooting

**Q: Import errors?**
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
```

**Q: Azure OpenAI not working?**
- Check `.env` file exists
- Verify credentials are correct
- Install `openai` package

**Q: Functions not generated?**
- Check policy file format
- Ensure clear, explicit rules
- Review examples in `policies/`

## 🎉 Success Criteria

You've successfully set up the pipeline when:

- [x] `python examples/quick_start.py` runs without errors
- [x] Functions are generated in `generated/functions/`
- [x] Tests pass: `pytest generated/tests/ -v`
- [x] You can call functions from Python code

## 📞 Support

- **Documentation**: See `README.md` and `docs/`
- **Examples**: Check `examples/` directory
- **Issues**: Review error messages carefully

---

**🎊 Congratulations!**

You now have a complete policy automation system with:
- ✅ Policy parsing and code generation
- ✅ Automated testing
- ✅ Version control
- ✅ Azure OpenAI integration
- ✅ Complete documentation

Ready to automate your policies! 🚀
