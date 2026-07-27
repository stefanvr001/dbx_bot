"""
Mock Delta Lake / Databricks SQL database layer for Insurance Customer Service.
Simulates Delta tables for Policies, Vehicles, Debit Orders, and Documents.
"""
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, date

class DatabaseStore:
    """Simulated Databricks Delta Lake Data Repository."""
    
    def __init__(self):
        # Sample Customers
        self.customers = {
            "CUST-001": {
                "customer_id": "CUST-001",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "+27821234567",
                "policies": ["POL-1001", "POL-1002"]
            },
            "CUST-002": {
                "customer_id": "CUST-002",
                "first_name": "Sarah",
                "last_name": "Smith",
                "email": "sarah.smith@example.com",
                "phone": "+27839876543",
                "policies": ["POL-2005"]
            }
        }
        
        # Sample Policy Delta Table
        self.policies = {
            "POL-1001": {
                "policy_number": "POL-1001",
                "customer_id": "CUST-001",
                "product_type": "Comprehensive Motor Vehicle",
                "status": "ACTIVE",
                "start_date": "2023-01-15",
                "premium_amount": 1250.00,
                "currency": "ZAR",
                "excess_amount": 2500.00,
                "cover_details": "Comprehensive cover including third party, fire, theft, and accident damage."
            },
            "POL-1002": {
                "policy_number": "POL-1002",
                "customer_id": "CUST-001",
                "product_type": "Home Contents & Buildings",
                "status": "ACTIVE",
                "start_date": "2023-06-01",
                "premium_amount": 850.50,
                "currency": "ZAR",
                "excess_amount": 1500.00,
                "cover_details": "Building structure and household contents up to R1,500,000 value."
            },
            "POL-2005": {
                "policy_number": "POL-2005",
                "customer_id": "CUST-002",
                "product_type": "Commercial Vehicle Fleet",
                "status": "ACTIVE",
                "start_date": "2022-11-10",
                "premium_amount": 3400.00,
                "currency": "ZAR",
                "excess_amount": 5000.00,
                "cover_details": "Commercial vehicle coverage for business operations."
            }
        }
        
        # Sample Vehicle Noting of Interest Delta Table
        self.vehicles = {
            "POL-1001": [
                {
                    "policy_number": "POL-1001",
                    "make": "Toyota",
                    "model": "Hilux 2.8 GD-6",
                    "year": 2022,
                    "registration_number": "CA 123-456",
                    "vin": "AHTKB3CD401928374",
                    "financial_institution": "Standard Bank Vehicle and Asset Finance",
                    "noted_interest_status": "ACTIVE_FINANCIER"
                }
            ],
            "POL-2005": [
                {
                    "policy_number": "POL-2005",
                    "make": "Isuzu",
                    "model": "D-Max 250",
                    "year": 2021,
                    "registration_number": "GP 889-210",
                    "vin": "MPB34KL890012398",
                    "financial_institution": "ABSA Vehicle Finance",
                    "noted_interest_status": "ACTIVE_FINANCIER"
                }
            ]
        }
        
        # Sample Debit Order Delta Table
        self.debit_orders = {
            "POL-1001": {
                "policy_number": "POL-1001",
                "account_holder": "John Doe",
                "bank_name": "First National Bank (FNB)",
                "account_number_masked": "*****6789",
                "branch_code": "250655",
                "debit_day": 1, # 1st of every month
                "debit_amount": 1250.00,
                "last_successful_debit_date": "2026-07-01",
                "last_debit_status": "SUCCESSFUL",
                "next_debit_date": "2026-08-01",
                "payment_frequency": "MONTHLY"
            },
            "POL-1002": {
                "policy_number": "POL-1002",
                "account_holder": "John Doe",
                "bank_name": "First National Bank (FNB)",
                "account_number_masked": "*****6789",
                "branch_code": "250655",
                "debit_day": 1,
                "debit_amount": 850.50,
                "last_successful_debit_date": "2026-07-01",
                "last_debit_status": "SUCCESSFUL",
                "next_debit_date": "2026-08-01",
                "payment_frequency": "MONTHLY"
            },
            "POL-2005": {
                "policy_number": "POL-2005",
                "account_holder": "Sarah Smith",
                "bank_name": "Nedbank",
                "account_number_masked": "*****1234",
                "branch_code": "198765",
                "debit_day": 25,
                "debit_amount": 3400.00,
                "last_successful_debit_date": "2026-06-25",
                "last_debit_status": "SUCCESSFUL",
                "next_debit_date": "2026-07-25",
                "payment_frequency": "MONTHLY"
            }
        }
        
    def get_policy(self, policy_number: str) -> Optional[Dict[str, Any]]:
        """Retrieve policy details by policy_number."""
        return self.policies.get(policy_number.strip().upper())
        
    def get_debit_order(self, policy_number: str) -> Optional[Dict[str, Any]]:
        """Retrieve debit order information for a policy."""
        return self.debit_orders.get(policy_number.strip().upper())
        
    def get_vehicles(self, policy_number: str) -> List[Dict[str, Any]]:
        """Retrieve vehicle details and financial institution interest for a policy."""
        return self.vehicles.get(policy_number.strip().upper(), [])
        
    def find_policies_by_customer_identifier(self, identifier: str) -> List[Dict[str, Any]]:
        """Search policies by email, phone, or customer name."""
        identifier_lower = identifier.lower().strip()
        matched_policies = []
        for cust in self.customers.values():
            if (identifier_lower in cust["email"].lower() or 
                identifier_lower in cust["phone"] or 
                identifier_lower in f"{cust['first_name']} {cust['last_name']}".lower()):
                for pol_num in cust["policies"]:
                    if pol_num in self.policies:
                        matched_policies.append(self.policies[pol_num])
        return matched_policies

# Global database instance singleton
db_store = DatabaseStore()
