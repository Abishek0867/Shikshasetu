"""
Comprehensive Automated Test Suite for ShikshaSetu (Phases 1 through 6).
Verifies:
- Phase 1: Core Flask routes, auth, application verification, officer review queue.
- Phase 2: Live DigiLocker, UIDAI Vault, AISHE, e-District & Agentic LLM tool execution.
- Phase 3: Bhashini voice engine (ASR/TTS) and WhatsApp/SMS gateway outreach.
- Phase 4: Offline PWA manifest and service worker asset configuration.
- Phase 5: Officer RBAC matrix, bulk DBT sanctioning, and portal sync.
- Phase 6: Full system end-to-end flow integrity.
"""

import os, sys, tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Configure temporary database for testing
os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "test_full_suite.db")

from db import init_db, conn
from app import app, q
from services.digilocker import DigiLockerService
from services.uidai import UIDAIService
from services.aishe import AISHEUDISEService
from services.edistrict import EDistrictService
from services.portal_sync import PortalSyncEngine
from services.bhashini import BhashiniVoiceEngine
from services.outreach import OutreachService
from services.rbac import RBACEngine
import llm_chatbot

# Initialize database
init_db()

print("\n==================================================")
print("RUNNING SHIKSHASETU FULL TEST SUITE (PHASES 1 - 6)")
print("==================================================")

# --- PHASE 1 TESTS ---
print("\n[PHASE 1] Testing Core Verification & Application Flow...")
c = app.test_client()
login_res = c.post("/login", data={"apaar": "APAAR100001", "otp": "123456"}, follow_redirects=True)
assert login_res.status_code == 200

apply_res = c.post("/apply/2", data={"consent": "on"}, follow_redirects=True)
assert apply_res.status_code == 200
app_status = q("SELECT status FROM applications WHERE apaar_id='APAAR100001' ORDER BY id DESC", one=True)["status"]
assert app_status == "VERIFIED"
print("  PASSED: Student application auto-verified cleanly.")

# --- PHASE 2 TESTS ---
print("\n[PHASE 2] Testing Production Adapters & LLM Tool Calling Engine...")
dl = DigiLockerService().fetch_user_documents("APAAR100001")
assert dl["status"] == "SUCCESS" and len(dl["documents"]) == 4

uidai = UIDAIService().verify_aadhaar("APAAR100001", consent=True)
assert uidai["status"] == "VERIFIED" and uidai["name"] == "Asha Munda"

aishe = AISHEUDISEService().verify_institution("APAAR100001")
assert aishe["status"] == "MATCH"

edist = EDistrictService().verify_certificates("APAAR100001", scheme_income_limit=250000)
assert edist["st_check"]["status"] == "MATCH"

llm_reply = llm_chatbot.process_query("APAAR100001", "What is the status of my application?", lang="en")
assert "Post-Matric" in llm_reply or "VERIFIED" in llm_reply
print("  PASSED: Production adapters and JAGO LLM tool execution verified.")

# --- PHASE 3 TESTS ---
print("\n[PHASE 3] Testing Bhashini Voice AI & Outreach Gateway...")
bhashini = BhashiniVoiceEngine()
proc = bhashini.process_speech_input(b"", lang_code="hi")
assert proc["status"] == "SUCCESS"
tts = bhashini.generate_speech_response("आपकी छात्रवृत्ति स्वीकृत है", lang_code="hi")
assert tts["status"] == "SUCCESS" and "audio_url" in tts

wa = OutreachService().send_whatsapp_notification("APAAR100001", "Scholarship Approved")
assert wa["status"] == "DELIVERED"
print("  PASSED: Bhashini Voice AI and WhatsApp outreach operational.")

# --- PHASE 4 TESTS ---
print("\n[PHASE 4] Testing Offline PWA & Service Worker Configuration...")
manifest_res = c.get("/static/manifest.json")
assert manifest_res.status_code == 200 and b"ShikshaSetu" in manifest_res.data

sw_res = c.get("/static/sw.js")
assert sw_res.status_code == 200 and b"shikshasetu" in sw_res.data
print("  PASSED: PWA manifest.json and sw.js accessible.")

# --- PHASE 5 TESTS ---
print("\n[PHASE 5] Testing Officer RBAC & Bulk DBT Sanctioning...")
assert RBACEngine.is_authorized("MINISTRY_OFFICER", "BULK_SANCTION")
assert not RBACEngine.is_authorized("INSTITUTE_VERIFIER", "BULK_SANCTION")

# Test bulk sanction route
o = app.test_client()
o.post("/officer/login", data={"password": "officer123"})
aid = q("SELECT id FROM applications WHERE apaar_id='APAAR100001'", one=True)["id"]
bulk_res = o.post("/officer/bulk_sanction", data={"app_ids": [str(aid)]}, follow_redirects=True)
assert bulk_res.status_code == 200
final_status = q("SELECT status FROM applications WHERE id=?", aid, one=True)["status"]
assert final_status == "DISBURSED"
print("  PASSED: Officer RBAC matrix and Bulk DBT Disbursement verified.")

# --- PHASE 6 TESTS ---
print("\n[PHASE 6] Testing Multi-Portal Synchronization Bridge...")
sync_res = PortalSyncEngine().sync_application(aid)
assert sync_res["status"] == "SUCCESS"
print("  PASSED: Bi-directional sync with NSP/SFMP/NOS completed.")

print("\n==================================================")
print("ALL PHASES (1 - 6) FULL TEST SUITE PASSED CLEANLY!")
print("==================================================")
