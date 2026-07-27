import json
from typing import Dict, Any
from databricks_agent.tools.registry import tool_registry

class MCPServerAdapter:
    """Standard MCP Server protocol adapter."""
    
    def __init__(self):
        self.registry = tool_registry
        
    def handle_request(self, request_json: str) -> str:
        """
        Process JSON-RPC 2.0 requests from MCP clients.
        
        Supported Methods:
        - `tools/list`: Return catalog of registered tools & parameter schemas.
        - `tools/call`: Execute a specified tool with parameters.
        """
        try:
            req = json.loads(request_json)
        except Exception as e:
            return json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": f"Parse error: {str(e)}"},
                "id": None
            })
            
        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})
        
        if method == "tools/list":
            manifest = self.registry.to_mcp_manifest()
            return json.dumps({
                "jsonrpc": "2.0",
                "result": manifest,
                "id": req_id
            }, indent=2)
            
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if not tool_name:
                return json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32602, "message": "Missing 'name' in tools/call params."},
                    "id": req_id
                })
                
            result = self.registry.execute(tool_name, **arguments)
            
            return json.dumps({
                "jsonrpc": "2.0",
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ],
                    "isError": result.get("status") == "ERROR"
                },
                "id": req_id
            }, indent=2)
            
        else:
            return json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Method '{method}' not found."},
                "id": req_id
            })

# Singleton instance
mcp_server = MCPServerAdapter()
