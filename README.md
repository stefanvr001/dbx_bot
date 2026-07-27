# Databricks Customer Service Agent Framework

A production-grade, extensible customer service AI agent framework designed for **Databricks Mosaic AI Agent Framework**, **Unity Catalog AI Functions**, and **Model Context Protocol (MCP)**.

---

## 🌟 Key Capabilities

1. **Document Generation & Dispatch**:
   - `send_policy_schedule(policy_number, recipient_email, delivery_method)`
   - `send_vehicle_noting_of_interest(policy_number, vehicle_reg_or_vin, financial_institution, recipient_email)`
   - `send_insurance_certificate(policy_number, certificate_type, recipient_email)`

2. **Policy Info & Debit Order Inquiries**:
   - `get_debit_order_info(policy_number)` (Debit day, amount, bank account details, payment status)
   - `get_policy_summary(policy_number)` (Status, premium, excess, inception date)
   - `get_payment_history(policy_number, num_months)` (Historical payment ledger)

3. **Terms & Conditions Vector Search (RAG)**:
   - `search_policy_terms_and_conditions(policy_number, query, section_filter)` (Queries policy wording index for excess rules, exclusions, and claims procedures)

4. **Multi-Policy Disambiguation Engine**:
   - Parses customer correspondence/email to extract policy numbers.
   - If multiple active policies are linked to the customer, the agent automatically detects ambiguity and prompts the customer to specify which policy number to apply.

5. **Universal Tool Standard & Mandatory `policy_number`**:
   - Every tool enforces `policy_number: str` as a mandatory primary parameter.
   - Easily add new intent tools in **3 lines of Python code** using the `@register_tool` decorator.

6. **Model Context Protocol (MCP) & Databricks Unity Catalog**:
   - Exposes tools via **MCP JSON-RPC protocol** (`tools/list`, `tools/call`).
   - Generates Databricks **Unity Catalog SQL DDL statements** to register tools as UC AI Functions.

---

## 📁 Repository Structure

```
c:/sandbox/test_bot/
├── databricks_agent/
│   ├── __init__.py
│   ├── config.py                   # Catalog, Schema, Model & Vector Search config
│   ├── db_store.py                 # Mock Databricks Delta Lake data store
│   ├── vector_store.py             # Mock Databricks Vector Search RAG index
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── policy_extractor.py     # Multi-policy entity extraction & disambiguator
│   │   └── agent.py                # Core Agent orchestrator & response synthesizer
│   ├── tools/
│   │   ├── __init__.py             # Auto-registers all intent tools
│   │   ├── base.py                 # Base tool class & JSON Schema generator
│   │   ├── registry.py             # Central ToolRegistry & @register_tool decorator
│   │   ├── document_tools.py       # Policy Schedule & Vehicle Noting of Interest
│   │   ├── policy_tools.py         # Debit order details & policy info
│   │   └── terms_tools.py          # Policy Terms & Conditions Vector Q&A
│   └── mcp/
│       ├── __init__.py
│       └── mcp_server.py           # Model Context Protocol JSON-RPC server adapter
├── notebooks/
│   ├── 01_setup_delta_tables.py    # Databricks PySpark Delta tables setup
│   └── 02_agent_demo_and_test.py   # Databricks interactive execution & test notebook
├── tests/
│   └── test_agent.py               # Unit & Integration test suite
└── README.md                       # Architecture & deployment guide
```

---

## 🚀 Easy Tool Extensibility: Adding a New Tool

To add a new intent tool to the agent, simply create a function with type annotations and docstrings, then decorate it with `@register_tool`:

```python
from databricks_agent.tools.registry import register_tool

@register_tool
def update_debit_day(policy_number: str, new_debit_day: int) -> dict:
    """
    Update the preferred monthly debit order day for a policy.
    
    Args:
        policy_number: Mandatory unique policy reference (e.g. POL-1001).
        new_debit_day: Day of month (1 to 28).
    """
    # Business logic here...
    return {
        "success": True,
        "policy_number": policy_number,
        "new_debit_day": new_debit_day,
        "message": f"Updated debit order day for policy {policy_number} to Day {new_debit_day}."
    }
```
That's it! The tool is automatically:
- Validated for `policy_number` signature compliance.
- Exported to Databricks LLM Tool calling schema.
- Added to the MCP Manifest catalog (`mcp_server`).
- Generatable as a Databricks Unity Catalog SQL Function.

---

## 🛠️ How to Run & Verify

### 1. Run Automated Test Suite
```bash
python tests/test_agent.py
```

### 2. Run Interactive Demo Notebook
```bash
python notebooks/02_agent_demo_and_test.py
```

### 3. Export Unity Catalog Functions SQL
```python
from databricks_agent.tools.registry import tool_registry

ddl_statements = tool_registry.to_uc_functions(catalog="main", schema="insurance_customer_service")
for ddl in ddl_statements:
    print(ddl)
```

### 4. Run MCP Server Request
```python
import json
from databricks_agent.mcp.mcp_server import mcp_server

mcp_request = json.dumps({
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
        "name": "get_debit_order_info",
        "arguments": {"policy_number": "POL-1001"}
    },
    "id": 100
})
response = mcp_server.handle_request(mcp_request)
print(response)
```

---

## ☁️ Databricks Deployment Guide

1. **Deploy Data Layer**: Execute `notebooks/01_setup_delta_tables.py` in your Databricks Workspace to initialize Delta tables in Unity Catalog.
2. **Register UC Tools**: Execute `tool_registry.to_uc_functions()` in a SQL notebook to create Unity Catalog AI Functions.
3. **Deploy Mosaic AI Model Serving**: Wrap `CustomerServiceAgent` in an MLflow PyFunc model using `mlflow.pyfunc.log_model()` and deploy to a Databricks Model Serving endpoint.
