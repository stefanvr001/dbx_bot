"""
Terms and Conditions RAG / Vector Search Tool for Databricks Customer Service Agent.
Retrieves relevant policy rules, exclusions, excess terms, and coverage clauses.
"""
from typing import Dict, Any, Optional
from databricks_agent.tools.registry import register_tool
from databricks_agent.db_store import db_store
from databricks_agent.vector_store import vector_store

@register_tool
def search_policy_terms_and_conditions(
    policy_number: str, 
    query: str, 
    section_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search policy wording, terms and conditions, exclusions, excess rules, and policy clauses using Databricks Vector Search.
    
    Args:
        policy_number: Mandatory unique policy number (e.g. POL-1001).
        query: Specific question or clause topic (e.g. 'What is the excess for young drivers?', 'Is flood damage covered?', 'What are the rules for noting financial interest?').
        section_filter: Optional specific section to filter search (e.g. 'Excess', 'Claims', 'General Terms').
    """
    policy = db_store.get_policy(policy_number)
    policy_type = policy["product_type"] if policy else None
    
    # Query simulated Databricks Vector Search index
    results = vector_store.search(query=query, policy_type=policy_type, top_k=3)
    
    formatted_chunks = []
    for doc in results:
        formatted_chunks.append({
            "section": doc["section"],
            "policy_type": doc["policy_type"],
            "text": doc["content"]
        })
        
    return {
        "success": True,
        "policy_number": policy_number,
        "policy_type": policy_type or "General Policy",
        "query": query,
        "results_found": len(formatted_chunks),
        "relevant_terms_and_conditions": formatted_chunks,
        "message": f"Found {len(formatted_chunks)} relevant terms & conditions clauses for query '{query}'."
    }
