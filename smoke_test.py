"""Run: python smoke_test.py  -> exercises the whole demo flow against a temporary database."""
import os, sys, tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "t.db")
from app import app, q

def login(c, apaar):
    return c.post("/login", data={"apaar": apaar, "otp": "123456"}, follow_redirects=True)

def apply(c, sid):
    return c.post(f"/apply/{sid}", data={"consent": "on"}, follow_redirects=True)

def status(apaar):
    return q("SELECT status FROM applications WHERE apaar_id=? ORDER BY id DESC", apaar, one=True)["status"]

# 1 clean student -> auto verified
c = app.test_client(); assert login(c, "APAAR100001").status_code == 200
assert apply(c, 2).status_code == 200 and status("APAAR100001") == "VERIFIED"
r = apply(c, 3); assert b"Only one scholarship at a time" in r.data          # one-scheme rule
assert "Post-Matric" in c.post("/chat", json={"message": "am I eligible?"}).get_json()["reply"]
# 2 mismatch -> manual review, not rejected
c2 = app.test_client(); login(c2, "APAAR100002"); apply(c2, 2); assert status("APAAR100002") == "UNDER_REVIEW"
print("chat hi:", c2.post("/chat", json={"message": "मेरी स्थिति क्या है"}).get_json()["reply"])
# 3 expired income cert, 4 AISHE outage, 5 fellowship with NET
c3 = app.test_client(); login(c3, "APAAR100005"); apply(c3, 3); assert status("APAAR100005") == "UNDER_REVIEW"
c4 = app.test_client(); login(c4, "APAAR100007"); apply(c4, 2); assert status("APAAR100007") == "UNDER_REVIEW"
assert "UNAVAILABLE" in c4.get("/application/" + str(q("SELECT id FROM applications WHERE apaar_id='APAAR100007'", one=True)["id"])).get_data(as_text=True)
c5 = app.test_client(); login(c5, "APAAR100006"); apply(c5, 4); assert status("APAAR100006") == "VERIFIED"
# family + paid student, tamil chat
c6 = app.test_client(); login(c6, "APAAR100003")
d = c6.get("/dashboard").get_data(as_text=True); assert "Karthik Toda" in d and "8,000" in d
print("chat ta:", c6.post("/chat", json={"message": "பணம் எப்போது"}).get_json()["reply"])
# officer
o = app.test_client(); assert b"Wrong" in o.post("/officer/login", data={"password": "x"}, follow_redirects=True).data
o.post("/officer/login", data={"password": "officer123"})
assert o.get("/officer").status_code == 200 and o.get("/officer/analytics").status_code == 200
rid = q("SELECT r.id FROM review_queue r JOIN applications a ON a.id=r.application_id WHERE a.apaar_id='APAAR100002' AND r.status='OPEN'", one=True)["id"]
o.post(f"/officer/review/{rid}", data={"action": "deficiency", "note": "Upload correct name"}); assert status("APAAR100002") == "DEFICIENCY"
c2.post("/resubmit/" + str(q("SELECT id FROM applications WHERE apaar_id='APAAR100002'", one=True)["id"])); assert status("APAAR100002") == "UNDER_REVIEW"
aid = q("SELECT id FROM applications WHERE apaar_id='APAAR100001'", one=True)["id"]
o.post(f"/officer/disburse/{aid}"); assert status("APAAR100001") == "DISBURSED"
print("chat en:", c.post("/chat", json={"message": "when will I get payment?"}).get_json()["reply"])
# student cannot open officer pages; gap analytics + outreach
assert c.get("/officer").status_code == 302
o.post("/officer/outreach/Odisha")
# auto-register from registry
c7 = app.test_client(); assert b"Welcome" in login(c7, "APAAR100120").data
assert app.test_client().get("/mock/uidai/APAAR100001").get_json()["name"] == "Asha Munda"
print("ALL CHECKS PASSED")
