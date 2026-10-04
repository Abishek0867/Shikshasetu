"""JAGO chatbot (prototype): keyword intents in EN/HI/TA + tool-style DB lookups so answers are student-specific.
Phase 2: replace detect() with an LLM that calls the same tool functions."""
from db import conn, eligible
from i18n import CHAT, STATUS

KW = {
    "payment": ["payment", "money", "paid", "dbt", "भुगतान", "पैसा", "पैसे", "பணம்", "கட்டண"],
    "docs": ["document", "दस्तावेज", "ஆவண"],
    "elig": ["eligib", "apply", "पात्र", "आवेदन कर", "தகுதி"],
    "status": ["status", "application", "स्थिति", "आवेदन", "நிலை", "விண்ணப்ப"],
}


def detect(msg):
    m = msg.lower()
    return next((k for k, words in KW.items() if any(w in m for w in words)), "help")


def _apps(a):
    with conn() as c:
        return c.execute("""SELECT ap.*, sc.name scheme, d.amount, d.date, d.dbt_status,
              (SELECT reason FROM review_queue WHERE application_id=ap.id AND status='OPEN') reason
              FROM applications ap JOIN schemes sc ON sc.id=ap.scheme_id LEFT JOIN disbursements d ON d.application_id=ap.id
              WHERE ap.apaar_id=? ORDER BY ap.id DESC""", (a,)).fetchall()


def reply(apaar, msg, lang="en"):
    R, S, intent, apps = CHAT[lang], STATUS[lang], detect(msg), _apps(apaar)
    if intent == "help":
        return R["help"]
    if intent == "docs":
        with conn() as c:
            docs = [r["doc_type"] for r in c.execute("SELECT doc_type FROM documents WHERE apaar_id=?", (apaar,))]
        return R["docs"].format(docs=", ".join(docs)) if docs else R["nodocs"]
    if intent == "elig":
        with conn() as c:
            g = c.execute("SELECT level FROM gov_registry WHERE apaar_id=?", (apaar,)).fetchone()
        return R["elig"].format(schemes=", ".join(s["name"] for s in eligible(g["level"]))) if g else R["help"]
    if not apps:
        return R["noapp"]
    lines = []
    for p in apps[:2]:
        if intent == "payment":
            lines.append(R["paid"].format(amt=f"{p['amount']:,}", date=p["date"], scheme=p["scheme"], dbt=p["dbt_status"])
                         if p["status"] == "DISBURSED" else R["notpaid"].format(scheme=p["scheme"], status=S[p["status"]]))
        else:
            lines.append(f"{p['scheme']}: {S[p['status']]}.")
        if p["status"] in ("UNDER_REVIEW", "DEFICIENCY") and (p["reason"] or p["remarks"]):
            lines.append(R["reason"].format(r=p["reason"] or p["remarks"]))
    return " ".join(lines)
