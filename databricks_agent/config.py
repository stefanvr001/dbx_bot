"""
Configuration settings for Databricks Customer Service Agent
"""
import os

DATABRICKS_CATALOG = os.getenv("DATABRICKS_CATALOG", "main")
DATABRICKS_SCHEMA = os.getenv("DATABRICKS_SCHEMA", "insurance_customer_service")

# Model configuration for Databricks Foundation Model Serving
DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "databricks-meta-llama-3-3-70b-instruct")

# Vector search configuration
VECTOR_SEARCH_INDEX = f"{DATABRICKS_CATALOG}.{DATABRICKS_SCHEMA}.policy_tc_index"

# Mock PDF / Document output directory
DOCUMENTS_OUTPUT_DIR = os.path.join(os.getcwd(), "generated_documents")
