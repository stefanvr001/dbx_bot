from typing import List, Dict, Any, Optional

class PolicyVectorStore:
    """Databricks Vector Search index simulation over policy T&Cs."""

    def __init__(self):
        # Sample document chunks indexed from policy terms & conditions PDFs
        self.documents = [
            {
                "chunk_id": "tc_motor_001",
                "policy_type": "Comprehensive Motor Vehicle",
                "section": "General Terms & Definitions",
                "content": "The policy provides comprehensive cover against accidental damage, theft, hijacking, and third-party financial liability up to R10,000,000 per occurrence. All drivers must hold a valid driver's license."
            },
            {
                "chunk_id": "tc_motor_002",
                "policy_type": "Comprehensive Motor Vehicle",
                "section": "Vehicle Noting of Interest & Financiers",
                "content": "Where a vehicle is financed under a hire purchase or lease agreement, the title holder / financial institution's interest must be noted on the policy schedule. A official Certificate of Noting of Interest can be issued directly to the financial institution upon request."
            },
            {
                "chunk_id": "tc_motor_003",
                "policy_type": "Comprehensive Motor Vehicle",
                "section": "Excess & Deductibles",
                "content": "A basic excess of R2,500 applies to all accident claims. An additional excess of R1,500 applies if the driver is under 25 years of age or has held a driver's license for less than 2 years. Windscreen replacement incurs a flat excess of R500."
            },
            {
                "chunk_id": "tc_debit_001",
                "policy_type": "General Terms",
                "section": "Premium Payments & Debit Orders",
                "content": "Premiums are payable monthly in advance via automatic electronic debit order on the selected debit day (e.g. 1st, 15th, or 25th of each month). A grace period of 15 days applies. If a debit order fails, a double debit order will be presented on the following payment date."
            },
            {
                "chunk_id": "tc_cancellation_001",
                "policy_type": "General Terms",
                "section": "Cancellation & Policy Schedule Requests",
                "content": "The policyholder may request a policy schedule, endorsement certificate, or tax invoice at any time free of charge. The policy may be cancelled by providing 30 days written notice."
            },
            {
                "chunk_id": "tc_home_001",
                "policy_type": "Home Contents & Buildings",
                "section": "Building & Contents Cover",
                "content": "Covers physical damage to buildings caused by storm, flood, fire, explosion, or burst water pipes. Geyser replacement cover includes damage up to R15,000 per incident."
            }
        ]

    def search(self, query: str, policy_type: Optional[str] = None, top_k: int = 3) -> List[Dict[str, Any]]:
        query_words = set(query.lower().split())
        scored_docs = []

        for doc in self.documents:
            # Filter by policy_type if provided
            if policy_type and policy_type.lower() not in doc["policy_type"].lower() and doc["policy_type"] != "General Terms":
                continue

            text = f"{doc['section']} {doc['content']}".lower()
            match_score = sum(1 for word in query_words if word in text)

            # Simple keyword relevance weighting
            if match_score > 0:
                scored_docs.append((match_score, doc))

        # Sort descending by relevance score
        scored_docs.sort(key=lambda x: x[0], reverse=True)

        results = [doc for score, doc in scored_docs[:top_k]]

        # Fallback if no specific keyword match
        if not results:
            results = self.documents[:top_k]

        return results

# Global Vector Store instance
vector_store = PolicyVectorStore()
