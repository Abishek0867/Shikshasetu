"""
Phase 2 Integration Test Suite for ShikshaSetu.
Tests real API adapter contracts, JAGO AI LLM Tool Calling, Bhashini voice pipelines,
multi-channel WhatsApp/SMS delivery, and legacy portal synchronization.
"""

import os, sys, tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "t_phase2.db")

from db import init_db, conn
from phase2_bridge import (
    DigiLockerOAuthAdapter,
    UIDAIAadhaarVaultAdapter,
    AISHEUDISEAdapter,
    execute_jago_tool,
    llm_chat_agent,
    BhashiniVoiceAdapter,
    MultiChannelOutreachGateway,
    LegacyPortalBridge
)

# Initialize test database
init_db()

print("--> 1. Testing DigiLocker OAuth Adapter...")
dl_adapter = DigiLockerOAuthAdapter()
dl_res = dl_adapter.fetch_documents("APAAR100001")
assert dl_res["status"] == "SUCCESS"
assert len(dl_res["documents"]) == 4
print("    DigiLocker OAuth Adapter: OK")

print("--> 2. Testing UIDAI Aadhaar Vault Verification Adapter...")
uidai_adapter = UIDAIAadhaarVaultAdapter()
uidai_res = uidai_adapter.verify_identity("APAAR100001", consent_given=True)
assert uidai_res["status"] == "VERIFIED"
assert uidai_res["name"] == "Asha Munda"
assert "aadhaar_token" in uidai_res
print("    UIDAI Consent Verification Adapter: OK")

print("--> 3. Testing AISHE/UDISE+ Institute Recognition Adapter...")
aishe_adapter = AISHEUDISEAdapter()
aishe_res = aishe_adapter.verify_institution("APAAR100001")
assert aishe_res["status"] == "MATCH"
assert "Govt. Arts College" in aishe_res["institution_name"]
print("    AISHE/UDISE+ Institute Adapter: OK")

print("--> 4. Testing JAGO AI LLM Tool Calling Engine...")
tool_res = execute_jago_tool("lookup_application_status", {"apaar_id": "APAAR100003"})
assert "applications" in tool_res
assert len(tool_res["applications"]) > 0

elig_res = execute_jago_tool("check_scholarship_eligibility", {"apaar_id": "APAAR100001"})
assert "Post-Matric Scholarship" in elig_res["eligible_schemes"]
print("    JAGO AI LLM Tool Calling Engine: OK")

print("--> 5. Testing Phase 2 LLM Agent Loop (Conversational JAGO AI)...")
chat_resp_status = llm_chat_agent("APAAR100003", "What is the status of my application?")
assert "DISBURSED" in chat_resp_status or "Post-Matric" in chat_resp_status

chat_resp_elig = llm_chat_agent("APAAR100001", "Am I eligible to apply for any scholarship?")
assert "Post-Matric Scholarship" in chat_resp_elig
print("    Conversational LLM JAGO AI Loop: OK")

print("--> 6. Testing Bhashini Multilingual Voice Adapter...")
bhashini = BhashiniVoiceAdapter()
tts_res = bhashini.text_to_speech("आपकी छात्रवृत्ति स्वीकृत हो गई है", "hi")
assert tts_res["status"] == "SUCCESS"
assert tts_res["language"] == "hi"
print("    Bhashini Voice & Audio Adapter: OK")

print("--> 7. Testing Multi-Channel (WhatsApp / SMS) Outreach Gateway...")
gateway = MultiChannelOutreachGateway()
wa_res = gateway.send_whatsapp_alert("APAAR100001", "Your scholarship was sanctioned!")
assert wa_res["status"] == "DELIVERED"
assert wa_res["channel"] == "WhatsApp"
print("    Multi-Channel Gateway: OK")

print("--> 8. Testing Legacy Central/State Portal Sync Bridge (NSP, SFMP, NOS)...")
bridge = LegacyPortalBridge()
sync_res = bridge.push_application_event(1)
assert sync_res["status"] == "SYNCHRONIZED"
assert sync_res["target_portal"] in ["NSP", "SFMP", "NOS Portal"]
print("    Legacy Central/State Portal Sync Bridge: OK")

print("\n==================================================")
print("ALL PHASE 2 INTEGRATION TESTS PASSED SUCCESSFULLY!")
print("==================================================")
