import re
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from typing import Dict, Any, List, Optional

class PolicyExtractor:

    EMAIL_REGEX = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
    PHONE_REGEX = r"\b(?:\+?\d{1,3}[\s\-]?)?(?:\(?\d{2,4}\)?[\s\-]?)?\d{3,4}[\s\-]?\d{4}\b"
    ID_REGEX = r"\b\d{13}\b"
    POLICY_REGEX = r"\b[A-Z0-9\-]{6,25}\b"

    @classmethod
    def extract_identifiers(cls, text: str) -> Dict[str, List[str]]:

        emails = list(set(re.findall(cls.EMAIL_REGEX, text, flags=re.IGNORECASE)))

        phones = list(set(
            re.sub(r"[^\d+]", "", p)
            for p in re.findall(cls.PHONE_REGEX, text)
        ))

        ids = list(set(re.findall(cls.ID_REGEX, text)))

        possible_policies = list(set(
            p.upper()
            for p in re.findall(cls.POLICY_REGEX, text)
        ))

        return {
            "emails": emails,
            "phones": phones,
            "ids": ids,
            "policy_numbers": possible_policies
        }

    @classmethod
    def extract_policies(cls, text: str) -> List[str]:

        identifiers = cls.extract_identifiers(text)
        found = []

        spark = SparkSession.getActiveSession() or SparkSession.builder.getOrCreate()
        df = spark.table(
            "classic_demo.insurance_customer_service.customer_identifiers"
        )

        identifiers_to_find = (
            identifiers["emails"] +
            identifiers["phones"] +
            identifiers["ids"] +
            identifiers["policy_numbers"]
        )

        result = (
            df.filter(col("identifier").isin(identifiers_to_find))
            .select("policy_number")
            .distinct()
        )

        found = [r.policy_number for r in result.collect()]

        return found

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

        extracted = cls.extract_policies(text)

        if len(extracted) == 1:
            pol_num = extracted[0]
            # pol = db_store.get_policy(pol_num)
            pol = pol_num
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
                # pol = db_store.get_policy(pol_num)
                pol = pol_num
                if pol:
                    policies_info.append({
                        "policy_number": pol_num,
                        # "product_type": pol["product_type"],
                        # "status": pol["status"]
                        "product_type": "Unknown Product", 
                        "status": "Unknown"
                    })
                else:
                    policies_info.append(
                        {
                            "policy_number": pol_num, 
                            "product_type": "Unknown Product", 
                            "status": "Unknown"
                        }
                    )
                    
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
