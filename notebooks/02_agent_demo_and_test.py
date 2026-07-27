# Databricks Notebook: 02_agent_demo_and_test
# COMMAND ----------
# MAGIC %md
# MAGIC # Customer Service AI Agent - Interactive Execution & Testing Notebook
# MAGIC 
# MAGIC Demonstrates policy entity extraction, multi-policy disambiguation, tool calling, 
# MAGIC document generation, debit order inquiries, terms & conditions vector search, MCP server protocol,
# MAGIC and seamless tool extensibility.

# COMMAND ----------
import sys
import os
import json

# Add project root directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from databricks_agent.engine.agent import agent
from databricks_agent.tools.registry import tool_registry, register_tool
from databricks_agent.mcp.mcp_server import mcp_server

# COMMAND ----------
# MAGIC %md
# MAGIC ## Scenario 1: Document Request (Policy Schedule)
# MAGIC Customer asks: *"Hi, please email me a copy of my policy schedule for POL-1001."*

# COMMAND ----------
print("--- SCENARIO 1: Policy Schedule Intent ---")
res1 = agent.process_message("Hi, please email me a copy of my policy schedule for POL-1001.")
print(f"Status        : {res1['status']}")
print(f"Intent Detected: {res1['intent_detected']}")
print(f"Tool Called   : {res1['tool_called']}")
print("\nAgent Response:")
print(res1['agent_response'])

# COMMAND ----------
# MAGIC %md
# MAGIC ## Scenario 2: Vehicle Noting of Interest Confirmation
# MAGIC Customer asks: *"Standard Bank is asking for a confirmation of vehicle noting of interest for POL-1001."*

# COMMAND ----------
print("\n--- SCENARIO 2: Vehicle Noting of Interest Intent ---")
res2 = agent.process_message("Standard Bank is asking for a confirmation of vehicle noting of interest for POL-1001.")
print(f"Status        : {res2['status']}")
print(f"Tool Called   : {res2['tool_called']}")
print(f"Parameters    : {res2['tool_parameters']}")
print("\nAgent Response:")
print(res2['agent_response'])

# COMMAND ----------
# MAGIC %md
# MAGIC ## Scenario 3: Debit Order & Billing Questions
# MAGIC Customer asks: *"What day of the month is my debit order taken for POL-1001 and how much is it?"*

# COMMAND ----------
print("\n--- SCENARIO 3: Debit Order Info Intent ---")
res3 = agent.process_message("What day of the month is my debit order taken for POL-1001 and how much is it?")
print(f"Status        : {res3['status']}")
print(f"Tool Called   : {res3['tool_called']}")
print("\nAgent Response:")
print(res3['agent_response'])

# COMMAND ----------
# MAGIC %md
# MAGIC ## Scenario 4: Policy Terms & Conditions Vector Q&A
# MAGIC Customer asks: *"What is my excess amount for accident claims on POL-1001?"*

# COMMAND ----------
print("\n--- SCENARIO 4: Terms & Conditions Q&A Intent ---")
res4 = agent.process_message("What is my excess amount for accident claims on POL-1001?")
print(f"Status        : {res4['status']}")
print(f"Tool Called   : {res4['tool_called']}")
print("\nAgent Response:")
print(res4['agent_response'])

# COMMAND ----------
# MAGIC %md
# MAGIC ## Scenario 5: Multi-Policy Disambiguation Flow
# MAGIC Customer with multiple active policies (`john.doe@example.com` has `POL-1001` and `POL-1002`) asks:
# MAGIC *"I want to check my debit order details."* (No policy number specified).

# COMMAND ----------
print("\n--- SCENARIO 5: Multi-Policy Disambiguation ---")
res5 = agent.process_message("I want to check my debit order details.", customer_identifier="john.doe@example.com")
print(f"Status        : {res5['status']}")
print(f"Needs Disambiguation: {res5['policy_context']['needs_disambiguation']}")
print("\nAgent Response (Disambiguation Prompt):")
print(res5['agent_response'])

print("\nUser clarifies: 'I mean POL-1002'")
res5_clarified = agent.process_message("I mean POL-1002", override_policy_number="POL-1002")
print(f"Status        : {res5_clarified['status']}")
print(f"Resolved Policy: {res5_clarified['policy_number']}")
print("\nAgent Response:")
print(res5_clarified['agent_response'])

# COMMAND ----------
# MAGIC %md
# MAGIC ## Scenario 6: Tool Extensibility (Adding a New Tool in 3 Lines of Code!)

# COMMAND ----------
print("\n--- SCENARIO 6: Easy Tool Extensibility ---")

@register_tool
def update_contact_email(policy_number: str, new_email: str) -> dict:
    """
    Update policyholder primary contact email address.
    
    Args:
        policy_number: Mandatory unique policy number (e.g. POL-1001).
        new_email: New email address.
    """
    return {
        "success": True,
        "policy_number": policy_number,
        "new_email": new_email,
        "message": f"Updated primary contact email for policy {policy_number} to {new_email}."
    }

print(f"Updated tool list: {tool_registry.list_tools()}")
exec_new_tool = tool_registry.execute("update_contact_email", policy_number="POL-1001", new_email="john.doe.new@example.com")
print(f"Executed new tool result: {exec_new_tool}")

# COMMAND ----------
# MAGIC %md
# MAGIC ## Scenario 7: MCP Server JSON-RPC Protocol Execution

# COMMAND ----------
print("\n--- SCENARIO 7: MCP Server Interface ---")
mcp_list_req = json.dumps({
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": "1"
})
mcp_list_resp = mcp_server.handle_request(mcp_list_req)
print("MCP Manifest Export (First tool entry preview):")
manifest_json = json.loads(mcp_list_resp)
print(json.dumps(manifest_json["result"]["tools"][0], indent=2))
