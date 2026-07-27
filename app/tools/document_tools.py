"""
Document Generation and Dispatch Tools for Databricks Customer Service Agent.
Handles Policy Schedule, Vehicle Noting of Interest, and Insurance Certificates.
"""
import os
import json
from typing import Dict, Any, Optional
from databricks_agent.tools.registry import register_tool
from databricks_agent.db_store import db_store
from databricks_agent.config import DOCUMENTS_OUTPUT_DIR

os.makedirs(DOCUMENTS_OUTPUT_DIR, exist_ok=True)

@register_tool
def send_policy_schedule(policy_number: str, recipient_email: Optional[str] = None, delivery_method: str = "EMAIL") -> Dict[str, Any]:
    """
    Generate and dispatch the official Policy Schedule document for an active insurance policy.
    
    Args:
        policy_number: Mandatory unique policy number (e.g. POL-1001).
        recipient_email: Destination email address. If omitted, uses policyholder's registered email.
        delivery_method: Delivery channel ('EMAIL', 'SMS_LINK', or 'DOWNLOAD_LINK').
    """
    policy = db_store.get_policy(policy_number)
    if not policy:
        return {
            "success": False,
            "message": f"Policy '{policy_number}' could not be found in Databricks records."
        }
        
    cust = db_store.customers.get(policy["customer_id"], {})
    target_email = recipient_email or cust.get("email", "policyholder@example.com")
    
    # Generate simulated policy schedule PDF artifact
    filename = f"Policy_Schedule_{policy_number}.pdf"
    file_path = os.path.join(DOCUMENTS_OUTPUT_DIR, filename)
    
    document_content = f"""
================================================================================
                    OFFICIAL INSURANCE POLICY SCHEDULE
================================================================================
Policy Number : {policy['policy_number']}
Customer Name : {cust.get('first_name', '')} {cust.get('last_name', '')}
Product Type  : {policy['product_type']}
Status        : {policy['status']}
Start Date    : {policy['start_date']}
Monthly Premium: {policy['currency']} {policy['premium_amount']:.2f}
Basic Excess  : {policy['currency']} {policy['excess_amount']:.2f}
Cover Details : {policy['cover_details']}
================================================================================
Generated via Databricks Customer Service Agent pipeline.
"""
    with open(file_path, "w") as f:
        f.write(document_content)
        
    return {
        "success": True,
        "document_type": "Policy Schedule",
        "policy_number": policy_number,
        "recipient_email": target_email,
        "delivery_method": delivery_method,
        "file_name": filename,
        "download_url": f"https://databricks-workspace.cloud/files/documents/{filename}",
        "message": f"Policy Schedule for policy {policy_number} successfully dispatched to {target_email} via {delivery_method}."
    }

@register_tool
def send_vehicle_noting_of_interest(
    policy_number: str, 
    vehicle_reg_or_vin: Optional[str] = None, 
    financial_institution: Optional[str] = None, 
    recipient_email: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate and dispatch a Vehicle Noting of Interest confirmation document for financial institutions / banks.
    
    Args:
        policy_number: Mandatory unique policy number (e.g. POL-1001).
        vehicle_reg_or_vin: Optional vehicle registration number or VIN number to filter.
        financial_institution: Bank or financier name (e.g. Standard Bank, ABSA, Nedbank).
        recipient_email: Email address to send the noting confirmation certificate to.
    """
    policy = db_store.get_policy(policy_number)
    if not policy:
        return {
            "success": False,
            "message": f"Policy '{policy_number}' not found."
        }
        
    vehicles = db_store.get_vehicles(policy_number)
    if not vehicles:
        return {
            "success": False,
            "message": f"No vehicles with financial interest noted on policy '{policy_number}'."
        }
        
    # Match specific vehicle if provided
    selected_vehicle = vehicles[0]
    if vehicle_reg_or_vin:
        for v in vehicles:
            if vehicle_reg_or_vin.lower() in v["registration_number"].lower() or vehicle_reg_or_vin.lower() in v["vin"].lower():
                selected_vehicle = v
                break
                
    financier = financial_institution or selected_vehicle.get("financial_institution", "Noted Financial Institution")
    cust = db_store.customers.get(policy["customer_id"], {})
    target_email = recipient_email or cust.get("email", "policyholder@example.com")
    
    filename = f"Noting_Of_Interest_{policy_number}_{selected_vehicle['registration_number'].replace(' ', '_')}.pdf"
    file_path = os.path.join(DOCUMENTS_OUTPUT_DIR, filename)
    
    document_content = f"""
================================================================================
              CONFIRMATION OF VEHICLE NOTING OF INTEREST
================================================================================
Policy Number     : {policy_number}
Policyholder      : {cust.get('first_name', '')} {cust.get('last_name', '')}
Vehicle           : {selected_vehicle['year']} {selected_vehicle['make']} {selected_vehicle['model']}
Registration No   : {selected_vehicle['registration_number']}
VIN               : {selected_vehicle['vin']}
Financier / Bank  : {financier}
Noting Status     : ACTIVE FIRST FINANCIAL INTEREST
================================================================================
This certificate confirms that the rights and interest of {financier} as title holder
have been recorded on Policy {policy_number}.
"""
    with open(file_path, "w") as f:
        f.write(document_content)
        
    return {
        "success": True,
        "document_type": "Vehicle Noting of Interest Confirmation",
        "policy_number": policy_number,
        "vehicle": f"{selected_vehicle['make']} {selected_vehicle['model']} ({selected_vehicle['registration_number']})",
        "financial_institution": financier,
        "recipient_email": target_email,
        "file_name": filename,
        "download_url": f"https://databricks-workspace.cloud/files/documents/{filename}",
        "message": f"Vehicle Noting of Interest certificate for {selected_vehicle['registration_number']} ({financier}) sent to {target_email}."
    }

@register_tool
def send_insurance_certificate(policy_number: str, certificate_type: str = "CONFIRMATION_OF_COVER", recipient_email: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate and send a standard Insurance Certificate (Confirmation of Cover, Tax Certificate, or Border Cross Certificate).
    
    Args:
        policy_number: Mandatory unique policy number (e.g. POL-1001).
        certificate_type: Type of certificate ('CONFIRMATION_OF_COVER', 'BORDER_CROSSING', 'TAX_INVOICE').
        recipient_email: Destination email address.
    """
    policy = db_store.get_policy(policy_number)
    if not policy:
        return {"success": False, "message": f"Policy '{policy_number}' not found."}
        
    cust = db_store.customers.get(policy["customer_id"], {})
    target_email = recipient_email or cust.get("email", "policyholder@example.com")
    
    filename = f"Certificate_{certificate_type}_{policy_number}.pdf"
    
    return {
        "success": True,
        "document_type": certificate_type,
        "policy_number": policy_number,
        "recipient_email": target_email,
        "file_name": filename,
        "message": f"{certificate_type} certificate for policy {policy_number} has been generated and emailed to {target_email}."
    }
