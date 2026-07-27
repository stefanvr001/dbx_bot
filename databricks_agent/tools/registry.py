"""
Central Tool Registry for Databricks Customer Service Agent.
Provides decorator-based tool registration, MCP server export, and Unity Catalog compatibility.
"""
from typing import Dict, Any, List, Optional, Callable
from databricks_agent.tools.base import BasePolicyTool

class ToolRegistry:
    """Registry managing all policy intent tools."""
    
    def __init__(self):
        self._tools: Dict[str, BasePolicyTool] = {}
        
    def register(self, func: Optional[Callable] = None, name: Optional[str] = None, description: Optional[str] = None):
        """
        Decorator or direct method to register a tool function.
        
        Example:
            @tool_registry.register
            def send_policy_schedule(policy_number: str, recipient_email: str) -> dict:
                ...
        """
        def decorator(f: Callable):
            tool_obj = BasePolicyTool(f, name=name, description=description)
            self._tools[tool_obj.name] = tool_obj
            return f
            
        if func is None:
            return decorator
        return decorator(func)
        
    def get_tool(self, name: str) -> Optional[BasePolicyTool]:
        """Retrieve tool object by name."""
        return self._tools.get(name)
        
    def list_tools(self) -> List[str]:
        """List names of all registered tools."""
        return list(self._tools.keys())
        
    def to_openai_tools(self) -> List[Dict[str, Any]]:
        """Export all registered tools to OpenAI / Databricks Tool calling format."""
        return [tool.get_openai_schema() for tool in self._tools.values()]
        
    def to_mcp_manifest(self) -> Dict[str, Any]:
        """Export tool catalog in Model Context Protocol (MCP) server JSON format."""
        mcp_tools = []
        for tool in self._tools.values():
            schema = tool.get_openai_schema()["function"]
            mcp_tools.append({
                "name": schema["name"],
                "description": schema["description"],
                "inputSchema": schema["parameters"]
            })
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": {
                "name": "databricks-insurance-policy-mcp",
                "version": "1.0.0"
            },
            "capabilities": {
                "tools": {}
            },
            "tools": mcp_tools
        }

    def to_uc_functions(self, catalog: str = "main", schema: str = "insurance_customer_service") -> List[str]:
        """Generate SQL DDL commands to register tools as Databricks Unity Catalog AI Functions."""
        uc_statements = []
        for tool in self._tools.values():
            func_schema = tool.get_openai_schema()["function"]
            params_sql = []
            for param_name, param_info in func_schema["parameters"]["properties"].items():
                sql_type = "STRING"
                if param_info["type"] == "integer":
                    sql_type = "INT"
                elif param_info["type"] == "number":
                    sql_type = "DOUBLE"
                elif param_info["type"] == "boolean":
                    sql_type = "BOOLEAN"
                params_sql.append(f"{param_name} {sql_type} COMMENT '{param_info['description']}'")
                
            ddl = (
                f"CREATE OR REPLACE FUNCTION {catalog}.{schema}.{tool.name}(\n  " +
                ",\n  ".join(params_sql) +
                f"\n)\nRETURNS STRING\nCOMMENT '{tool.description}'\n" +
                "LANGUAGE PYTHON\nAS $$\n  # Unity Catalog Python Function Implementation\n  return 'SUCCESS'\n$$;"
            )
            uc_statements.append(ddl)
        return uc_statements

    def execute(self, name: str, **kwargs) -> Dict[str, Any]:
        """Execute a registered tool by name."""
        tool = self.get_tool(name)
        if not tool:
            return {
                "status": "ERROR",
                "error": f"Tool '{name}' is not registered in the tool registry. Available tools: {self.list_tools()}"
            }
        return tool.execute(**kwargs)

# Global Tool Registry Singleton
tool_registry = ToolRegistry()
register_tool = tool_registry.register
