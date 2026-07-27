import re
from typing import Dict, Any, List, Optional, Tuple
from databricks_agent.db_store import db_store

class PolicyExtractor:
    """Extracts policy references and handles multi-policy disambiguation."""
    
    POLICY_REGEX = r'\b(POL[-_]?\d{3,6})\b'
    
    @classmethod
    def extract_policies(cls, text: str, customer_identifier: Optional[str] = None) -> List[str]:
        """
        Extract explicit policy numbers from correspondence text or customer lookup.
        """
        found_policies = set()
        
        # 1. Regex match explicit policy numbers in text (e.g., POL-1001, POL1002)
        matches = re.findall(cls.POLICY_REGEX, text, flags=re.IGNORECASE)
        for m in matches:
            formatted = m.upper().replace('_', '-')
            if not formatted.startswith("POL-") and formatted.startswith("POL"):
                formatted = "POL-" + formatted[3:]
            found_policies.add(formatted)
            
        # 2. If no explicit policy number in text, try looking up by customer email or phone
        if not found_policies and customer_identifier:
            matched_db_policies = db_store.find_policies_by_customer_identifier(customer_identifier)
            for pol in matched_db_policies:
                found_policies.add(pol["policy_number"])
                
        return sorted(list(found_policies))
        
    @classmethod
    def resolve_policy_context(cls, text: str, customer_identifier: Optional[str] = None) -> Dict[str, Any]:
        """
        Disambiguate policy context from customer correspondence.
        
        Returns:
            Dict containing status:
            - 'SINGLE_POLICY_FOUND': Exactly 1 policy identified.
            - 'MULTIPLE_POLICIES_AMBIGUOUS': Multiple policies found; requires user clarification.
            - 'NO_POLICY_FOUND': No policy identified; prompts user to provide policy number.
        """
        extracted = cls.extract_policies(text, customer_identifier)
        
        if len(extracted) == 1:
            pol_num = extracted[0]
            pol = db_store.get_policy(pol_num)
            return {
                "status": "SINGLE_POLICY_FOUND",
                "policy_number": pol_num,
                "policy_details": pol,
                "needs_disambiguation": False,
                "message": f"Identified policy {pol_num}."
            }
            
        elif len(extracted) > 1:
            policies_info = []
            for pol_num in extracted:
                pol = db_store.get_policy(pol_num)
                if pol:
                    policies_info.append({
                        "policy_number": pol_num,
                        "product_type": pol["product_type"],
                        "status": pol["status"]
                    })
                else:
                    policies_info.append({"policy_number": pol_num, "product_type": "Unknown Product", "status": "Unknown"})
                    
            options_text = "\n".join([f"  • {p['policy_number']} - {p['product_type']} ({p['status']})" for p in policies_info])
            
            return {
                "status": "MULTIPLE_POLICIES_AMBIGUOUS",
                "extracted_policies": extracted,
                "policies_info": policies_info,
                "needs_disambiguation": True,
                "disambiguation_prompt": (
                    f"We found multiple active policies associated with your request:\n{options_text}\n\n"
                    f"Please specify which policy number you would like us to apply this request to (e.g. '{extracted[0]}')."
                ),
                "message": f"Multiple policies detected ({', '.join(extracted)}). Disambiguation required."
            }
            
        else:
            return {
                "status": "NO_POLICY_FOUND",
                "needs_disambiguation": True,
                "disambiguation_prompt": (
                    "Could you please provide your policy number (e.g., POL-1001) so I can access your details and assist you?"
                ),
                "message": "No policy number identified in message."
            }
