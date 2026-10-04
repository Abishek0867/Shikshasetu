"""JAGO AI Agentic Chatbot Engine with Tool-Calling capabilities."""
import json
from typing import Dict, Any, List
from db import conn, eligible
from i18n import CHAT, STATUS

TOOLS = [
    {
        "name": "get_application_status",
        "description": "Fetch application progress, remarks, and payment logs for a student.",
        "parameters": {"apaar_id": "string"}
    },
    {
        "name": "check_scheme_eligibility",
        "description": "Find eligible scholarship schemes for student based on enrolment level.",
        "parameters": {"apaar_id": "string"}
    },
    {
        "name": "list_documents",
        "description": "Retrieve documents present in the student's DigiLocker wallet.",
        "parameters": {"apaar_id": "string"}
    }
]

def execute_tool(name: str, apaar_id: str) -> Dict[str, Any]:
    if name == "get_application_status":
        with conn() as c:
            apps = c.execute("""
                SELECT ap.id, sc.name as scheme, ap.status, ap.remarks, d.amount, d.date, d.dbt_status
                FROM applications ap JOIN schemes sc ON sc.id=ap.scheme_id
                LEFT JOIN disbursements d ON d.application_id=ap.id
                WHERE ap.apaar_id=? ORDER BY ap.id DESC
            """, (apaar_id,)).fetchall()
        return {"applications": [dict(a) for a in apps]}
    
    elif name == "check_scheme_eligibility":
        with conn() as c:
            g = c.execute("SELECT level FROM gov_registry WHERE apaar_id=?", (apaar_id,)).fetchone()
        schemes = eligible(g["level"]) if g else []
        return {"eligible_schemes": [s["name"] for s in schemes]}

    elif name == "list_documents":
        with conn() as c:
            docs = c.execute("SELECT doc_type FROM documents WHERE apaar_id=?", (apaar_id,)).fetchall()
        return {"documents": [d["doc_type"] for d in docs]}

    return {"error": "Tool not found"}

def process_query(apaar_id: str, message: str, lang: str = "en") -> str:
    """Agentic query processor using structured tool execution."""
    msg = message.lower()
    S = STATUS[lang]
    
    if any(w in msg for w in ["status", "application", "where", "स्थिति", "आवेदन", "நிலை"]):
        data = execute_tool("get_application_status", apaar_id)
        apps = data.get("applications", [])
        if not apps:
            return CHAT[lang]["noapp"]
        latest = apps[0]
        st_text = S.get(latest["status"], latest["status"])
        res = f"{latest['scheme']}: {st_text}."
        if latest["remarks"]:
            res += f" {CHAT[lang]['reason'].format(r=latest['remarks'])}."
        if latest["amount"]:
            res += f" {CHAT[lang]['paid'].format(amt=f'{latest['amount']:,}', date=latest['date'], scheme=latest['scheme'], dbt=latest['dbt_status'])}"
        return res

    elif any(w in msg for w in ["eligib", "apply", "qualify", "पात्र", "தகுதி"]):
        data = execute_tool("check_scheme_eligibility", apaar_id)
        schemes = data.get("eligible_schemes", [])
        if schemes:
            return CHAT[lang]["elig"].format(schemes=", ".join(schemes))
        return CHAT[lang]["help"]

    elif any(w in msg for w in ["doc", "wallet", "digilocker", "दस्तावेज़", "ஆவண"]):
        data = execute_tool("list_documents", apaar_id)
        docs = data.get("documents", [])
        if docs:
            return CHAT[lang]["docs"].format(docs=", ".join(docs))
        return CHAT[lang]["nodocs"]

    return CHAT[lang]["help"]
