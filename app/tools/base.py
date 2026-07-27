"""
Base class for Policy Tools in Databricks Customer Service Agent.
Enforces the mandatory `policy_number` parameter rule.
"""
import inspect
from typing import Dict, Any, Callable, Optional, List, get_type_hints

class BasePolicyTool:
    """
    Abstract Base Class for Agent Tools.
    Enforces parameter signature rules (policy_number as required parameter).
    """
    
    def __init__(self, func: Callable, name: Optional[str] = None, description: Optional[str] = None):
        self.func = func
        self.name = name or func.__name__
        self.description = description or (func.__doc__.strip() if func.__doc__ else f"Tool {self.name}")
        
        # Inspect parameter signature
        sig = inspect.signature(func)
        self.parameters = sig.parameters
        
        # Enforce requirement: policy_number must be present in function parameters
        if "policy_number" not in self.parameters:
            raise ValueError(f"Tool function '{self.name}' must accept 'policy_number' as a parameter.")
            
    def get_openai_schema(self) -> Dict[str, Any]:
        """Convert tool signature to OpenAI / Databricks Tool Calling JSON Schema."""
        properties = {}
        required = []
        
        type_hints = get_type_hints(self.func)
        
        for param_name, param in self.parameters.items():
            param_type = type_hints.get(param_name, str)
            
            # Map Python types to JSON Schema types
            json_type = "string"
            if param_type == int:
                json_type = "integer"
            elif param_type == float:
                json_type = "number"
            elif param_type == bool:
                json_type = "boolean"
            elif param_type in (list, List):
                json_type = "array"
            elif param_type in (dict, Dict):
                json_type = "object"
                
            param_doc = f"Parameter {param_name}"
            if param_name == "policy_number":
                param_doc = "The unique policy reference number (e.g. POL-1001)."
                
            properties[param_name] = {
                "type": json_type,
                "description": param_doc
            }
            
            # If parameter has no default value, mark as required
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
                
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }

    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute tool function with parameter validation."""
        policy_number = kwargs.get("policy_number")
        if not policy_number:
            return {
                "status": "ERROR",
                "error": "Missing required parameter 'policy_number'."
            }
        
        # Sanitize policy number formatting
        kwargs["policy_number"] = str(policy_number).strip().upper()
        
        # Filter kwargs to match function signature
        valid_kwargs = {k: v for k, v in kwargs.items() if k in self.parameters and v is not None}
        
        try:
            result = self.func(**valid_kwargs)
            return {
                "status": "SUCCESS",
                "tool": self.name,
                "policy_number": kwargs["policy_number"],
                "data": result
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "tool": self.name,
                "error": str(e)
            }
