"""
Azure OpenAI Integration Module
Integrates policy functions with Azure OpenAI using function calling.
"""

import os
import json
from typing import Dict, List, Any, Optional, Callable
import importlib.util


class AzureOpenAIPolicyClient:
    """
    Azure OpenAI client with policy function integration

    This client enables natural language queries about travel policies
    and automatically calls the appropriate policy functions.
    """

    def __init__(
        self,
        azure_endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: str = "2024-02-15-preview",
        deployment_name: str = "gpt-4"
    ):
        """
        Initialize Azure OpenAI client

        Args:
            azure_endpoint: Azure OpenAI endpoint URL
            api_key: Azure OpenAI API key
            api_version: API version to use
            deployment_name: Name of your GPT-4 deployment
        """
        self.endpoint = azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.api_version = api_version
        self.deployment_name = deployment_name

        self.policy_module = None
        self.function_map = {}
        self.client = None

        # Initialize OpenAI client
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Azure OpenAI client"""
        try:
            from openai import AzureOpenAI

            if not self.endpoint or not self.api_key:
                raise ValueError(
                    "Azure OpenAI credentials not provided. "
                    "Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY "
                    "environment variables or pass them to constructor."
                )

            self.client = AzureOpenAI(
                azure_endpoint=self.endpoint,
                api_key=self.api_key,
                api_version=self.api_version
            )

        except ImportError:
            print("Warning: openai package not installed. Install with: pip install openai")
            self.client = None

    def load_policy_functions(self, policy_module_path: str) -> None:
        """
        Load policy functions from a generated module

        Args:
            policy_module_path: Path to the generated policy module (.py file)
        """
        # Import the module
        spec = importlib.util.spec_from_file_location("policy_module", policy_module_path)
        self.policy_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.policy_module)

        # Build function map
        if hasattr(self.policy_module, 'get_available_functions'):
            functions_info = self.policy_module.get_available_functions()

            for func_info in functions_info:
                func_name = func_info['name']
                if hasattr(self.policy_module, func_name):
                    self.function_map[func_name] = getattr(self.policy_module, func_name)

            print(f"Loaded {len(self.function_map)} policy functions")
        else:
            print("Warning: Policy module does not have get_available_functions()")

    def get_function_definitions(self) -> List[Dict[str, Any]]:
        """
        Get OpenAI function definitions for all loaded policy functions

        Returns:
            List of function definition dictionaries
        """
        if not self.policy_module or not hasattr(self.policy_module, 'get_available_functions'):
            return []

        functions_info = self.policy_module.get_available_functions()
        openai_functions = []

        for func_info in functions_info:
            # Convert to OpenAI function format
            openai_func = {
                "type": "function",
                "function": {
                    "name": func_info['name'],
                    "description": func_info['description'],
                    "parameters": {
                        "type": "object",
                        "properties": self._convert_parameters(func_info['parameters']),
                        "required": list(func_info['parameters'].keys())
                    }
                }
            }
            openai_functions.append(openai_func)

        return openai_functions

    def _convert_parameters(self, params: Dict[str, str]) -> Dict[str, Dict[str, str]]:
        """
        Convert parameter descriptions to OpenAI schema format

        Args:
            params: Dictionary of parameter names and descriptions

        Returns:
            OpenAI parameter schema
        """
        properties = {}

        for param_name, param_desc in params.items():
            # Infer type from description
            param_type = "string"
            if "cost" in param_name or "amount" in param_name or "duration" in param_name or "num_" in param_name:
                param_type = "number"

            properties[param_name] = {
                "type": param_type,
                "description": param_desc
            }

        return properties

    def query(
        self,
        user_question: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Process a user question about travel policy

        Args:
            user_question: Natural language question
            conversation_history: Previous conversation messages
            max_iterations: Maximum function calling iterations

        Returns:
            Dictionary with answer and metadata
        """
        if not self.client:
            return {
                "error": "Azure OpenAI client not initialized. Check credentials.",
                "answer": None
            }

        if not self.function_map:
            return {
                "error": "No policy functions loaded. Call load_policy_functions() first.",
                "answer": None
            }

        # Build messages
        messages = conversation_history or []
        messages.append({
            "role": "user",
            "content": user_question
        })

        # Add system message if not present
        if not any(msg['role'] == 'system' for msg in messages):
            messages.insert(0, {
                "role": "system",
                "content": self._get_system_prompt()
            })

        # Get function definitions
        tools = self.get_function_definitions()

        # Iterative function calling
        iteration = 0
        function_calls = []

        while iteration < max_iterations:
            try:
                # Call Azure OpenAI
                response = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto"
                )

                message = response.choices[0].message

                # Check if function call is requested
                if message.tool_calls:
                    # Execute function calls
                    for tool_call in message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)

                        print(f"Calling function: {function_name}({function_args})")

                        # Execute the function
                        if function_name in self.function_map:
                            function_result = self.function_map[function_name](**function_args)
                            function_calls.append({
                                "function": function_name,
                                "arguments": function_args,
                                "result": function_result
                            })

                            # Add function result to messages
                            messages.append({
                                "role": "assistant",
                                "content": None,
                                "tool_calls": [tool_call]
                            })
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps(function_result)
                            })

                    iteration += 1
                else:
                    # No more function calls, return the answer
                    return {
                        "answer": message.content,
                        "function_calls": function_calls,
                        "iterations": iteration,
                        "conversation": messages
                    }

            except Exception as e:
                return {
                    "error": f"Error during query: {str(e)}",
                    "answer": None,
                    "function_calls": function_calls
                }

        return {
            "error": "Max iterations reached",
            "answer": "Could not complete query within iteration limit",
            "function_calls": function_calls
        }

    def _get_system_prompt(self) -> str:
        """Get system prompt for the AI assistant"""
        return """You are a helpful corporate travel policy assistant.

Your role is to answer questions about company travel policies by calling the appropriate policy checking functions.

When a user asks about travel policies:
1. Identify what policy aspect they're asking about (cabin class, costs, booking, etc.)
2. Extract the relevant parameters from their question
3. Call the appropriate policy function(s)
4. Explain the results in a clear, friendly way

Always:
- Be specific about policy rules
- Explain WHY a decision was made
- Suggest alternatives if something is not allowed
- Be helpful and professional

If information is missing, ask the user for clarification.
"""

    def chat(self):
        """
        Start an interactive chat session

        This provides a simple CLI interface for testing
        """
        print("=" * 60)
        print("Travel Policy Assistant (Azure OpenAI)")
        print("=" * 60)
        print("Ask questions about travel policies. Type 'quit' to exit.\n")

        conversation = []

        while True:
            try:
                user_input = input("You: ").strip()

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break

                if not user_input:
                    continue

                # Get response
                result = self.query(user_input, conversation)

                if result.get('error'):
                    print(f"\nError: {result['error']}\n")
                    continue

                # Display answer
                print(f"\nAssistant: {result['answer']}\n")

                # Show function calls if any
                if result.get('function_calls'):
                    print("(Functions called:")
                    for call in result['function_calls']:
                        print(f"  - {call['function']}")
                    print(")\n")

                # Update conversation
                conversation = result.get('conversation', [])

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}\n")


class SimplePolicyClient:
    """
    Simple policy client without Azure OpenAI dependency

    Useful for testing and development without Azure credentials
    """

    def __init__(self):
        self.policy_module = None
        self.function_map = {}

    def load_policy_functions(self, policy_module_path: str) -> None:
        """Load policy functions from a generated module"""
        spec = importlib.util.spec_from_file_location("policy_module", policy_module_path)
        self.policy_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.policy_module)

        if hasattr(self.policy_module, 'get_available_functions'):
            functions_info = self.policy_module.get_available_functions()
            for func_info in functions_info:
                func_name = func_info['name']
                if hasattr(self.policy_module, func_name):
                    self.function_map[func_name] = getattr(self.policy_module, func_name)

    def call_function(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """
        Call a policy function directly

        Args:
            function_name: Name of the function to call
            **kwargs: Function arguments

        Returns:
            Function result dictionary
        """
        if function_name not in self.function_map:
            return {
                "error": f"Function '{function_name}' not found",
                "available_functions": list(self.function_map.keys())
            }

        try:
            result = self.function_map[function_name](**kwargs)
            return result
        except Exception as e:
            return {
                "error": f"Error calling function: {str(e)}"
            }

    def list_functions(self) -> List[Dict[str, Any]]:
        """List all available functions"""
        if hasattr(self.policy_module, 'get_available_functions'):
            return self.policy_module.get_available_functions()
        return []
