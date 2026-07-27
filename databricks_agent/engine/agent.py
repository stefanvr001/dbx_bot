"""
Databricks Customer Service AI Agent Core Orchestrator.
Combines Policy Disambiguation, Tool Selection, Execution, and Response Generation.
MLflow PyFunc and Mosaic AI Agent Framework compatible.
"""
from typing import Dict, Any, List, Optional, Tuple
import databricks_agent.tools
from databricks_agent.tools.registry import tool_registry
from databricks_agent.engine.policy_extractor import PolicyExtractor

class CustomerServiceAgent:
    """Databricks AI Customer Service Agent Orchestrator."""
    
    def __init__(self):
        self.registry = tool_registry

    def process_message(
        self, 
        message: str, 
        customer_identifier: Optional[str] = None,
        override_policy_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process incoming customer correspondence or message.
        
        Args:
            message: Raw customer text / email / query.
            customer_identifier: Optional customer email or phone number.
            override_policy_number: Explicit policy number if already disambiguated by user.
            
        Returns:
            Dict containing agent response, tool execution logs, and disambiguation status.
        """
        message_clean = message.strip()
        
        # 1. Disambiguate policy context
        if override_policy_number:
            policy_context = {
                "status": "SINGLE_POLICY_FOUND",
                "policy_number": override_policy_number,
                "needs_disambiguation": False
            }
        else:
            policy_context = PolicyExtractor.resolve_policy_context(message_clean, customer_identifier)
            
        # If policy is ambiguous or missing, return prompt to user
        if policy_context["needs_disambiguation"]:
            return {
                "status": "DISAMBIGUATION_REQUIRED",
                "policy_context": policy_context,
                "agent_response": policy_context["disambiguation_prompt"],
                "tool_called": None,
                "tool_result": None
            }
            
        policy_number = policy_context["policy_number"]
        
        # 2. Intent Classification and Tool Routing
        tool_name, tool_kwargs = self._select_tool_and_args(message_clean, policy_number)
        
        if not tool_name:
            # Fallback to general policy summary if intent unrecognized
            tool_name = "get_policy_summary"
            tool_kwargs = {"policy_number": policy_number}
            
        # 3. Execute Tool via Tool Registry
        tool_result = self.registry.execute(tool_name, **tool_kwargs)
        
        # 4. Synthesize final response
        agent_response = self._synthesize_response(message_clean, tool_name, tool_result)
        
        return {
            "status": "SUCCESS",
            "policy_number": policy_number,
            "intent_detected": tool_name,
            "tool_called": tool_name,
            "tool_parameters": tool_kwargs,
            "tool_result": tool_result,
            "agent_response": agent_response
        }

    def _select_tool_and_args(self, message: str, policy_number: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Determine intent and route to appropriate registered tool.
        In Databricks production, this calls Foundation Model Tool Calling (Llama 3.3 / DBRX).
        Here we use intelligent semantic keyword & intent matching.
        """
        msg_lower = message.lower()
        
        # Intent: Vehicle Noting of Interest
        if any(kw in msg_lower for kw in ["noting of interest", "noted interest", "bank confirmation", "vehicle noting", "financier"]):
            # Extract potential bank name or vehicle reg
            bank = None
            for b in ["standard bank", "absa", "nedbank", "fnb", "wesbank"]:
                if b in msg_lower:
                    bank = b.title()
                    break
            return "send_vehicle_noting_of_interest", {
                "policy_number": policy_number,
                "financial_institution": bank
            }
            
        # Intent: Policy Schedule Document
        elif any(kw in msg_lower for kw in ["policy schedule", "schedule document", "send schedule", "copy of policy", "policy document"]):
            return "send_policy_schedule", {
                "policy_number": policy_number
            }
            
        # Intent: Insurance Certificate / Tax / Border
        elif any(kw in msg_lower for kw in ["certificate", "confirmation of cover", "border cross", "tax invoice"]):
            cert_type = "CONFIRMATION_OF_COVER"
            if "border" in msg_lower:
                cert_type = "BORDER_CROSSING"
            elif "tax" in msg_lower:
                cert_type = "TAX_INVOICE"
            return "send_insurance_certificate", {
                "policy_number": policy_number,
                "certificate_type": cert_type
            }
            
        # Intent: Debit Order & Billing Questions
        elif any(kw in msg_lower for kw in ["debit order", "debit date", "billing", "bank account", "payment date", "debit amount", "how much is my debit"]):
            return "get_debit_order_info", {
                "policy_number": policy_number
            }
            
        # Intent: Payment History
        elif any(kw in msg_lower for kw in ["payment history", "past payments", "ledger", "statement"]):
            return "get_payment_history", {
                "policy_number": policy_number,
                "num_months": 6
            }
            
        # Intent: Policy Terms and Conditions / Clause Q&A
        elif any(kw in msg_lower for kw in ["terms", "conditions", "excess", "exclusion", "covered", "clause", "what is covered", "rules"]):
            return "search_policy_terms_and_conditions", {
                "policy_number": policy_number,
                "query": message
            }
            
        # Intent: Policy Overview / Details
        elif any(kw in msg_lower for kw in ["policy details", "status", "summary", "overview"]):
            return "get_policy_summary", {
                "policy_number": policy_number
            }
            
        return None, {}

    def _synthesize_response(self, user_message: str, tool_name: str, tool_result: Dict[str, Any]) -> str:
        """Format final customer response based on tool execution result."""
        if tool_result.get("status") == "ERROR":
            return f"I ran into an issue while processing your request: {tool_result.get('error')}"
            
        data = tool_result.get("data", {})
        
        if tool_name == "send_policy_schedule":
            return (
                f"I have successfully generated and dispatched your Policy Schedule for **{data['policy_number']}**.\n\n"
                f"• **Destination**: `{data['recipient_email']}`\n"
                f"• **File Name**: `{data['file_name']}`\n"
                f"• **Download Link**: {data['download_url']}"
            )
            
        elif tool_name == "send_vehicle_noting_of_interest":
            return (
                f"Your Vehicle Noting of Interest confirmation certificate has been issued for **{data['policy_number']}**.\n\n"
                f"• **Vehicle**: {data['vehicle']}\n"
                f"• **Financial Institution**: {data['financial_institution']}\n"
                f"• **Sent To**: `{data['recipient_email']}`\n"
                f"• **Download Certificate**: {data['download_url']}"
            )
            
        elif tool_name == "get_debit_order_info":
            return (
                f"Here are the debit order details for policy **{data['policy_number']}** ({data['product_type']}):\n\n"
                f"• **Debit Day**: {data['debit_day']}\n"
                f"• **Debit Amount**: {data['debit_amount']}\n"
                f"• **Bank & Account**: {data['bank_name']} ({data['account_number_masked']})\n"
                f"• **Last Debit Date**: {data['last_successful_debit_date']} ({data['last_debit_status']})\n"
                f"• **Next Debit Date**: {data['next_debit_date']}"
            )
            
        elif tool_name == "search_policy_terms_and_conditions":
            clauses = data.get("relevant_terms_and_conditions", [])
            clauses_text = "\n\n".join([f"**[{c['section']}]**\n_{c['text']}_" for c in clauses])
            return (
                f"Here is what your policy terms and conditions state regarding **'{data['query']}'** for **{data['policy_number']}** ({data['policy_type']}):\n\n"
                f"{clauses_text}"
            )
            
        elif tool_name == "get_policy_summary":
            return (
                f"Policy Summary for **{data['policy_number']}** ({data['product_type']}):\n\n"
                f"• **Status**: {data['status']}\n"
                f"• **Premium**: {data['premium_amount']} per month\n"
                f"• **Basic Excess**: {data['basic_excess']}\n"
                f"• **Inception Date**: {data['start_date']}\n"
                f"• **Cover Details**: {data['cover_details']}"
            )
            
        return data.get("message", "Your request has been processed successfully.")

# Global Agent Instance
agent = CustomerServiceAgent()
