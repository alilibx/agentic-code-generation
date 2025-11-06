# 🚀 Policy-to-Code Pipeline

> Transform plain text policies into executable Python functions with AI-powered generation

Convert corporate policies from plain English into production-ready Python code with **AI-powered parsing and code generation**. Perfect for travel policies, expense rules, compliance checks, and more.

## ✨ Features

- **🤖 AI-Powered Parsing**: Uses GPT-4 to understand natural language policies
- **🧠 Intelligent Code Generation**: AI generates custom Python functions from rules
- **✅ Policy Validation**: Detects conflicts, gaps, and ambiguities automatically
- **📝 Flexible Input**: No strict format required - write policies naturally
- **🔄 Automatic Code Generation**: Generates clean, executable Python functions
- **📦 Version Control**: Built-in versioning and storage system
- **🧪 Auto-Generated Tests**: Comprehensive pytest test suites
- **💬 Natural Language Queries**: Ask questions about policies in plain English
- **🔌 Easy Integration**: Works with existing Python projects

## 🆕 **NEW: AI-Powered Features**

The pipeline now uses **Azure OpenAI (GPT-4)** for:
- **Smart Policy Parsing**: Understands context and intent, not just patterns
- **Custom Code Generation**: Creates sophisticated logic beyond templates
- **Policy Validation**: Finds issues, conflicts, and missing rules
- **Natural Language Interface**: Ask questions, get answers

See [AI_FEATURES.md](AI_FEATURES.md) for complete documentation.

### Quick Comparison

| Feature | Before (v1) | Now (v2 - AI-Powered) |
|---------|-------------|----------------------|
| Policy Parsing | Regex patterns | LLM understanding |
| Code Generation | Fixed templates | AI-generated custom code |
| Validation | None | AI-powered analysis |
| Policy Format | Strict format | Natural language |

**Ready to try it?** See [Getting Started with AI](#-ai-powered-quick-start) below!

## 🎯 Use Cases

- **Travel Policy Automation**: Automate travel approval workflows
- **Expense Management**: Validate expenses against company policies
- **Compliance Checking**: Ensure regulatory compliance automatically
- **HR Policy Enforcement**: Automate PTO, benefits, and policy checks
- **Custom Business Rules**: Any text-based rules → executable code

## 🏃 AI-Powered Quick Start

### 1. Installation

```bash
git clone <repository-url>
cd agentic-rules-to-code

# Install dependencies (required for AI features)
pip install -r requirements.txt
```

### 2. Configure Azure OpenAI

Create a `.env` file:
```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4
```

### 3. Run the AI Demo

```bash
python3 ai_example.py
```

This will:
1. 🤖 Parse policies using AI (natural language understanding)
2. ✅ Validate policies for completeness and conflicts
3. 🧠 Generate custom Python functions with AI
4. 🧪 Create comprehensive unit tests
5. 📊 Show validation results and generated code

### 4. Use AI-Powered Pipeline in Your Code

```python
from src.ai_pipeline import AIPolicyPipeline

# Create AI-powered pipeline
pipeline = AIPolicyPipeline()

# Process your policy with AI
result = pipeline.process_policy_file(
    "policies/my_policy.txt",
    validate_first=True  # AI validation before processing
)

# Use the AI-generated functions
module = pipeline.storage.import_function(result['company_id'])
decision = module.check_cabin_class("manager", "international", 8.0)
print(decision)
```

## 🔄 Classic (Non-AI) Quick Start

**Note**: The classic regex-based pipeline is still available but AI-powered is recommended.

```bash
# Run classic pipeline without AI
python examples/quick_start.py
```

See [AI_FEATURES.md](AI_FEATURES.md) for detailed comparison.

## 📚 Documentation

### 📖 Complete Documentation

- **[AI_FEATURES.md](AI_FEATURES.md)** - Complete guide to AI-powered features (NEW!)
  - How AI parsing works
  - AI code generation
  - Policy validation
  - Usage examples
  - API reference
  - Best practices

### Core Components

#### 🤖 AI-Powered Components (NEW)

1. **AI Policy Parser** (`src/ai_integration/ai_policy_parser.py`)
   - LLM-based natural language understanding
   - Context-aware rule extraction
   - Policy validation and conflict detection
   - Confidence scoring

2. **AI Code Generator** (`src/ai_integration/ai_code_generator.py`)
   - AI-generated custom Python functions
   - Sophisticated logic beyond templates
   - Adaptive to policy complexity
   - Production-ready code output

3. **AI Pipeline** (`src/ai_pipeline.py`)
   - End-to-end AI-powered orchestration
   - Integrated validation step
   - Comprehensive error handling
   - Progress reporting

#### 📝 Classic Components

4. **Policy Parser** (`src/generator/policy_parser.py`)
   - Regex-based parsing (legacy)
   - Pattern matching
   - Structured rule extraction

5. **Code Generator** (`src/generator/code_generator.py`)
   - Template-based generation (legacy)
   - Fixed patterns
   - Type-safe output

6. **Function Storage** (`src/storage/function_storage.py`)
   - Versions generated code
   - Manages function registry
   - Enables code reuse

7. **Test Generator** (`src/testing/test_generator.py`)
   - Creates comprehensive test suites
   - Includes edge cases
   - Parametrized tests

8. **Azure OpenAI Client** (`src/ai_integration/azure_openai_client.py`)
   - Natural language queries
   - Function calling integration
   - Interactive chat mode

### AI-Powered Pipeline Workflow

```
┌─────────────────┐
│  Policy Text    │  (Natural Language - Flexible Format)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 🤖 AI Validation│  (Detect conflicts, gaps, ambiguities)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 🧠 AI Parser    │  (LLM-based understanding)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 🤖 AI Generator │  (Custom code generation)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Function Storage│  (Version & Store)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Test Generator │  (Create tests)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 💬 AI Chat      │  (Natural language queries)
└─────────────────┘
```

## 🎓 Examples

### Example 1: Process a Policy

```python
from src.pipeline import PolicyPipeline

pipeline = PolicyPipeline()

# Your policy as text
policy_text = """
Company: Acme Corp

Managers can book business class for international flights over 8 hours.
Staff must book economy class.

Travel over $2000 requires manager approval.
"""

# Process it
result = pipeline.process_policy(
    policy_text,
    company_name="Acme Corp",
    generate_tests=True
)

print(f"Generated: {result['file_path']}")
```

### Example 2: Use Generated Functions

```python
# Load the generated module
module = pipeline.storage.import_function("ACME_CORP")

# Check cabin class
result = module.check_cabin_class(
    employee_level="manager",
    flight_type="international",
    duration_hours=10.0
)

print(f"Allowed cabin: {result['cabin']}")
print(f"Reason: {result['reason']}")
```

### Example 3: Azure OpenAI Integration

```python
from src.ai_integration.azure_openai_client import AzureOpenAIPolicyClient

# Set up client
client = AzureOpenAIPolicyClient(
    azure_endpoint="https://your-resource.openai.azure.com/",
    api_key="your-key"
)

# Load policy functions
client.load_policy_functions("generated/functions/ACME_CORP.py")

# Ask questions in natural language
result = client.query(
    "Can I book business class if I'm a manager flying to Tokyo?"
)

print(result['answer'])
```

### Example 4: Interactive Chat

```python
client.chat()  # Starts interactive session
```

```
You: Can a staff member book business class?
Assistant: No, according to the policy, staff members must book economy
class only. Business class is reserved for managers and above on
qualifying flights.

You: What about a 10-hour flight?
Assistant: Even for a 10-hour flight, staff members are only approved
for economy class. However, they could request an exception with
manager approval.
```

## 🔧 Configuration

### Azure OpenAI Setup

1. Create a `.env` file:

```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4
```

2. Use in code:

```python
from dotenv import load_dotenv
load_dotenv()

# Client will automatically use environment variables
client = AzureOpenAIPolicyClient()
```

### Custom Storage Location

```python
pipeline = PolicyPipeline(storage_dir="my_custom_path")
```

## 📁 Project Structure

```
agentic-rules-to-code/
├── src/
│   ├── generator/          # Parse & generate code
│   │   ├── policy_parser.py
│   │   └── code_generator.py
│   ├── storage/            # Version & store functions
│   │   └── function_storage.py
│   ├── testing/            # Generate tests
│   │   └── test_generator.py
│   ├── ai_integration/     # Azure OpenAI integration
│   │   └── azure_openai_client.py
│   └── pipeline.py         # Main orchestrator
├── examples/
│   ├── quick_start.py      # Simple example
│   └── demo_azure_openai.py # Full demo
├── policies/               # Example policies
│   ├── acme_corp_travel_policy.txt
│   └── techstart_travel_policy.txt
├── generated/              # Output directory
│   ├── functions/          # Generated code
│   ├── tests/              # Generated tests
│   ├── versions/           # Version history
│   └── metadata/           # Policy metadata
├── tests/                  # Pipeline tests
├── config/                 # Configuration files
└── README.md
```

## 🧪 Testing

### Run Generated Tests

```bash
# Test a specific policy
pytest generated/tests/test_ACME_CORP.py -v

# Test all policies
pytest generated/tests/ -v

# With coverage
pytest generated/tests/ --cov=generated/functions --cov-report=html
```

### Run Pipeline Tests

```bash
pytest tests/ -v
```

## 🎯 Supported Policy Types

The pipeline currently supports:

- ✅ **Cabin Class Rules**: Flight class eligibility
- ✅ **Cost Approval**: Spending thresholds
- ✅ **Advance Booking**: Booking window requirements
- ✅ **Airline Preferences**: Preferred airline lists
- ✅ **Baggage Allowance**: Checked bag limits
- ✅ **Custom Rules**: Extend with your own parsers

### Adding Custom Policy Types

1. Add parser method to `PolicyParser`
2. Add generator method to `CodeGenerator`
3. Add test cases to `TestGenerator`

See `docs/EXTENDING.md` for details.

## 🔌 Integration Examples

### With Flask API

```python
from flask import Flask, request, jsonify
from src.pipeline import PolicyPipeline

app = Flask(__name__)
pipeline = PolicyPipeline()

@app.route('/check-policy', methods=['POST'])
def check_policy():
    data = request.json
    module = pipeline.storage.import_function("ACME_CORP")

    result = module.check_cabin_class(
        data['employee_level'],
        data['flight_type'],
        data['duration_hours']
    )

    return jsonify(result)
```

### With LangChain

```python
from langchain.tools import StructuredTool
from src.ai_integration.azure_openai_client import SimplePolicyClient

client = SimplePolicyClient()
client.load_policy_functions("generated/functions/ACME_CORP.py")

# Convert to LangChain tools
tools = []
for func_info in client.list_functions():
    tool = StructuredTool.from_function(
        func=client.function_map[func_info['name']],
        name=func_info['name'],
        description=func_info['description']
    )
    tools.append(tool)
```

## 📈 Performance

- **Parsing**: ~100ms for typical policy document
- **Code Generation**: ~50ms per policy
- **Function Execution**: <1ms per call
- **Azure OpenAI Query**: 1-3s (depends on API)

## 🛠️ Development

### Setup Development Environment

```bash
pip install -r requirements.txt
pip install -e .
```

### Code Quality

```bash
# Format code
black src/ examples/

# Lint
flake8 src/ examples/

# Type checking
mypy src/
```

## 📊 Roadmap

- [x] **AI-powered policy parsing**
- [x] **AI-powered code generation**
- [x] **Policy validation and conflict detection**
- [ ] Support for more policy types
- [ ] Web UI for policy management
- [ ] Support for other LLM providers (Anthropic, OpenAI)
- [ ] Policy diff and merge tools
- [ ] Cloud deployment templates
- [ ] Learning from user corrections

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 💬 Support

- **Issues**: Report bugs on GitHub Issues
- **Questions**: Use GitHub Discussions
- **Documentation**: See `docs/` directory

## 🙏 Acknowledgments

Built with:
- Azure OpenAI for AI capabilities
- Python standard library (no heavy dependencies!)
- pytest for testing
- Your awesome policies!

---

**Made with ❤️ for automating policies**

Start automating your policies today! 🚀
