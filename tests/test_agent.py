"""
Automated Test Suite for Databricks Customer Service Agent.
Validates intent tool calls, multi-policy disambiguation, RAG search, document creation, and tool registration.
"""
import sys
import os
import unittest
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from databricks_agent.engine.agent import agent
from databricks_agent.tools.registry import tool_registry, register_tool
from databricks_agent.mcp.mcp_server import mcp_server
from databricks_agent.engine.policy_extractor import PolicyExtractor
from databricks_agent.db_store import db_store

from databricks_agent.engine.chat_history import ChatHistoryStore

class TestDatabricksAgent(unittest.TestCase):
    
    def test_01_policy_extraction_single(self):
        res = PolicyExtractor.resolve_policy_context("Please help with POL-1001")
        self.assertEqual(res["status"], "SINGLE_POLICY_FOUND")
        self.assertEqual(res["policy_number"], "POL-1001")
        self.assertFalse(res["needs_disambiguation"])
        
    def test_02_policy_extraction_multiple(self):
        res = PolicyExtractor.resolve_policy_context("I have questions about POL-1001 and POL-1002")
        self.assertEqual(res["status"], "MULTIPLE_POLICIES_AMBIGUOUS")
        self.assertTrue(res["needs_disambiguation"])
        self.assertIn("POL-1001", res["extracted_policies"])
        self.assertIn("POL-1002", res["extracted_policies"])
        
    def test_03_customer_identifier_multi_policy(self):
        res = PolicyExtractor.resolve_policy_context("What is my premium?", customer_identifier="john.doe@example.com")
        self.assertEqual(res["status"], "MULTIPLE_POLICIES_AMBIGUOUS")
        self.assertTrue(res["needs_disambiguation"])
        
    def test_04_send_policy_schedule_tool(self):
        res = agent.process_message("Please send my policy schedule for POL-1001 to my email.")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["tool_called"], "send_policy_schedule")
        self.assertEqual(res["policy_number"], "POL-1001")
        self.assertTrue(res["tool_result"]["data"]["success"])
        self.assertIn("Policy Schedule", res["agent_response"])
        
    def test_05_send_vehicle_noting_tool(self):
        res = agent.process_message("Standard Bank needs confirmation of vehicle noting of interest for POL-1001.")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["tool_called"], "send_vehicle_noting_of_interest")
        self.assertTrue(res["tool_result"]["data"]["success"])
        self.assertIn("Vehicle Noting of Interest", res["agent_response"])
        
    def test_06_debit_order_tool(self):
        res = agent.process_message("When is my debit order taken for POL-1001?")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["tool_called"], "get_debit_order_info")
        self.assertTrue(res["tool_result"]["data"]["success"])
        self.assertIn("Debit Day", res["agent_response"])
        
    def test_07_terms_and_conditions_rag_tool(self):
        res = agent.process_message("What is the excess for accident claims on POL-1001?")
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["tool_called"], "search_policy_terms_and_conditions")
        self.assertTrue(res["tool_result"]["data"]["success"])
        self.assertIn("terms and conditions", res["agent_response"])
        
    def test_08_easy_tool_extensibility(self):
        @register_tool
        def cancel_policy_request(policy_number: str, reason: str = "Unspecified") -> dict:
            """
            Submit policy cancellation request.
            """
            return {"cancelled": True, "policy_number": policy_number, "reason": reason}
            
        self.assertIn("cancel_policy_request", tool_registry.list_tools())
        exec_res = tool_registry.execute("cancel_policy_request", policy_number="POL-1001", reason="Sold vehicle")
        self.assertTrue(exec_res["data"]["cancelled"])
        
    def test_09_mcp_server_jsonrpc(self):
        req = json.dumps({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_debit_order_info",
                "arguments": {"policy_number": "POL-1001"}
            },
            "id": 42
        })
        resp_json = mcp_server.handle_request(req)
        resp = json.loads(resp_json)
        self.assertEqual(resp["id"], 42)
        self.assertFalse(resp["result"]["isError"])
        self.assertIn("get_debit_order_info", resp["result"]["content"][0]["text"])

    def test_10_session_history_recording(self):
        """Session history is recorded when session_id is provided."""
        sid = "test-session-history-001"
        store = ChatHistoryStore()
        agent.history = store  # use fresh store

        res = agent.process_message(
            "Send policy schedule for POL-1001", session_id=sid
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["session_id"], sid)

        history = store.get_history(sid)
        self.assertEqual(len(history), 2)  # user + assistant
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[1]["role"], "assistant")
        self.assertIn("Policy Schedule", history[1]["content"])

    def test_11_session_history_multi_turn(self):
        """Multiple turns accumulate within the same session."""
        sid = "test-session-multi-turn-002"
        store = ChatHistoryStore()
        agent.history = store

        agent.process_message("Send policy schedule for POL-1001", session_id=sid)
        agent.process_message("When is my debit order taken for POL-1001?", session_id=sid)

        history = store.get_history(sid)
        self.assertEqual(len(history), 4)  # 2 turns x 2 messages

        # Verify conversation_history is returned in response
        res3 = agent.process_message("What is my excess on POL-1001?", session_id=sid)
        self.assertEqual(len(res3["conversation_history"]), 6)

    def test_12_no_history_without_session_id(self):
        """No history recorded when session_id is omitted."""
        store = ChatHistoryStore()
        agent.history = store

        res = agent.process_message("Send policy schedule for POL-1001")
        self.assertIsNone(res["session_id"])
        self.assertEqual(res["conversation_history"], [])

    def test_13_session_history_disambiguation_recorded(self):
        """Disambiguation prompts are also recorded in session history."""
        sid = "test-session-disambig-003"
        store = ChatHistoryStore()
        agent.history = store

        res = agent.process_message(
            "Check my debit order", session_id=sid,
            customer_identifier="john.doe@example.com"
        )
        self.assertEqual(res["status"], "DISAMBIGUATION_REQUIRED")
        history = store.get_history(sid)
        self.assertEqual(len(history), 2)
        self.assertIn("multiple", history[1]["content"].lower())

    def test_14_session_context_summary(self):
        """Context summary helper returns formatted conversation text."""
        store = ChatHistoryStore()
        store.record_turn("ctx-test", "Hello", "Hi there!")
        summary = store.get_context_summary("ctx-test")
        self.assertIn("Customer: Hello", summary)
        self.assertIn("Agent: Hi there!", summary)

    def test_15_session_clear(self):
        """Clearing a session removes all messages."""
        store = ChatHistoryStore()
        store.record_turn("clear-test", "msg", "resp")
        self.assertTrue(store.clear_session("clear-test"))
        self.assertEqual(store.get_history("clear-test"), [])

if __name__ == "__main__":
    unittest.main()

