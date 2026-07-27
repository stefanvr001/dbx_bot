"""
Policy Details and Debit Order Information Tools for Databricks Customer Service Agent.
"""
from typing import Dict, Any, Optional
from databricks_agent.tools.registry import register_tool
from databricks_agent.db_store import db_store

@register_tool
def get_debit_order_info(policy_number: str) -> Dict[str, Any]:
    """
    Retrieve debit order details (debit day, account details, bank name, payment frequency, last payment status, next payment date) for a policy.
    
    Args:
        policy_number: Mandatory unique policy number (e.g. POL-1001).
    """
    policy = db_store.get_policy(policy_number)
    if not policy:
        return {"success": False, "message": f"Policy '{policy_number}' not found."}
        
    debit_info = db_store.get_debit_order(policy_number)
    if not debit_info:
        return {"success": False, "message": f"No debit order instruction found for policy '{policy_number}'."}
        
    return {
        "success": True,
        "policy_number": policy_number,
        "product_type": policy["product_type"],
        "account_holder": debit_info["account_holder"],
        "bank_name": debit_info["bank_name"],
        "account_number_masked": debit_info["account_number_masked"],
        "branch_code": debit_info["branch_code"],
        "debit_day": f"Day {debit_info['debit_day']} of each month",
        "debit_amount": f"{policy['currency']} {debit_info['debit_amount']:.2f}",
        "last_successful_debit_date": debit_info["last_successful_debit_date"],
        "last_debit_status": debit_info["last_debit_status"],
        "next_debit_date": debit_info["next_debit_date"],
        "payment_frequency": debit_info["payment_frequency"],
        "message": f"Debit order for policy {policy_number} is scheduled for day {debit_info['debit_day']} of every month at {policy['currency']} {debit_info['debit_amount']:.2f}."
    }

@register_tool
def get_policy_summary(policy_number: str) -> Dict[str, Any]:
    """
    Retrieve high-level overview of a policy including status, premium, start date, excess, and insured items.
    
    Args:
        policy_number: Mandatory unique policy number (e.g. POL-1001).
    """
    policy = db_store.get_policy(policy_number)
    if not policy:
        return {"success": False, "message": f"Policy '{policy_number}' not found."}
        
    cust = db_store.customers.get(policy["customer_id"], {})
    vehicles = db_store.get_vehicles(policy_number)
    
    return {
        "success": True,
        "policy_number": policy_number,
        "policyholder_name": f"{cust.get('first_name', '')} {cust.get('last_name', '')}",
        "product_type": policy["product_type"],
        "status": policy["status"],
        "start_date": policy["start_date"],
        "premium_amount": f"{policy['currency']} {policy['premium_amount']:.2f}",
        "basic_excess": f"{policy['currency']} {policy['excess_amount']:.2f}",
        "cover_details": policy["cover_details"],
        "noted_vehicles": [f"{v['year']} {v['make']} {v['model']} ({v['registration_number']})" for v in vehicles] if vehicles else ["None"]
    }

@register_tool
def get_payment_history(policy_number: str, num_months: int = 6) -> Dict[str, Any]:
    """
    Retrieve recent premium payment ledger history for a policy.
    
    Args:
        policy_number: Mandatory unique policy number (e.g. POL-1001).
        num_months: Number of past billing cycles to return (default 6).
    """
    policy = db_store.get_policy(policy_number)
    if not policy:
        return {"success": False, "message": f"Policy '{policy_number}' not found."}
        
    debit_info = db_store.get_debit_order(policy_number)
    amount = policy["premium_amount"]
    curr = policy["currency"]
    
    # Generate mock past transactions
    history = [
        {"date": "2026-07-01", "amount": f"{curr} {amount:.2f}", "status": "PAID", "reference": f"DBT-{policy_number}-0726"},
        {"date": "2026-06-01", "amount": f"{curr} {amount:.2f}", "status": "PAID", "reference": f"DBT-{policy_number}-0626"},
        {"date": "2026-05-01", "amount": f"{curr} {amount:.2f}", "status": "PAID", "reference": f"DBT-{policy_number}-0526"},
        {"date": "2026-04-01", "amount": f"{curr} {amount:.2f}", "status": "PAID", "reference": f"DBT-{policy_number}-0426"},
    ][:num_months]
    
    return {
        "success": True,
        "policy_number": policy_number,
        "payment_history": history,
        "message": f"Retrieved {len(history)} recent payment records for policy {policy_number}."
    }
