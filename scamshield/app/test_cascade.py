"""
Test suite to verify the cascade classifier pipeline routing.
Tests both high confidence obvious cases (fast-path) and low confidence ambiguous cases (slow-path to LLM).
"""

import os
import sys

# Add current and models directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models"))

from web_server import analyze_api, MessageInput

def run_tests():
    print("=== STARTING CASCADE PIPELINE TESTS ===")

    # Test case 1: Obvious Scam (Guaranteed high confidence -> fast path)
    # The fast Naive Bayes classifier is highly confident on keywords like 'lottery win 25 lakh'
    scam_msg = MessageInput(message="Dear customer, you have won 25 lakh lottery from KBC! Call 1930 now.")
    response_scam = analyze_api(scam_msg)
    import json
    data_scam = json.loads(response_scam.body.decode())
    
    print("\n[TEST 1] Obvious Scam Message / High Confidence")
    print(f"Message: '{scam_msg.message}'")
    print(f"Detected Category: {data_scam.get('category')}")
    print(f"Confidence Score: {data_scam.get('confidence'):.2f}")
    print(f"Triage Path Route: {data_scam.get('route')}")
    print(f"Follow up status: {len(data_scam.get('follow_up_questions', []))} questions returned")

    # Assertions
    assert data_scam.get("route") == "fast_path", f"Expected fast_path but got {data_scam.get('route')}"
    assert len(data_scam.get("follow_up_questions", [])) == 0, "Obvious cases should not return follow-up questions"
    print("✔ TEST 1 PASSED: Obvious path routed correctly.")

    # Test case 2: Ambiguous Message (Low confidence -> LLM fallback path)
    # A short or out-of-vocabulary safe phrase yields low confidence
    amb_msg = MessageInput(message="Please call me.")
    response_amb = analyze_api(amb_msg)
    data_amb = json.loads(response_amb.body.decode())

    print("\n[TEST 2] Ambiguous Message / Low Confidence (Fallback to LLM / Simulated Questions)")
    print(f"Message: '{amb_msg.message}'")
    print(f"Detected Category: {data_amb.get('category')}")
    print(f"Confidence Score: {data_amb.get('confidence'):.2f}")
    print(f"Triage Path Route: {data_amb.get('route')}")
    print(f"Follow up Questions: {data_amb.get('follow_up_questions')}")

    # Assertions
    assert data_amb.get("route") == "llm_api", f"Expected llm_api but got {data_amb.get('route')}"
    assert len(data_amb.get("follow_up_questions", [])) > 0, "Ambiguous cases must return clarifying question items"
    print("✔ TEST 2 PASSED: Ambiguous slow-path triage fallback working correctly.")

    print("\n=== ALL CASCADE TRIAGE TESTS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_tests()
