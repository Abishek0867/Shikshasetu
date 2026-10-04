"""Unified Verification Layer: one adapter call per source, exceptions go to manual review (never auto-reject)."""
from difflib import SequenceMatcher
from flask import current_app
from db import conn, notify, audit, now


def fetch(path):
    # Prototype: in-process call to the mock API. Production: requests.get(GOV_API_BASE + path, timeout=5)
    r = current_app.test_client().get(path)
    return r.status_code, (r.get_json() or {})


def run_checks(student, scheme):
    a, out = student["apaar_id"], []

    def chk(src, name, path, fn):
        code, d = fetch(path)
        out.append((src, name, "UNAVAILABLE", d.get("error", "Source unavailable")) if code != 200 else (src, name, *fn(d)))

    def name_fn(d):
        same = SequenceMatcher(None, student["name"].lower(), d["name"].lower()).ratio() == 1.0
        return ("MATCH" if same else "MISMATCH", f"Name on application '{student['name']}' differs from UIDAI record '{d['name']}'" if not same else "Name matches UIDAI record")

    def st_fn(d):
        ok = d["is_st"] and d["st_cert_valid"]
        return ("MATCH", f"ST certificate valid ({d['tribe']})") if ok else ("MISMATCH", "ST certificate missing or invalid")

    def inc_fn(d):
        lim = scheme["income_limit"]
        if not d["income_cert_valid"]:
            return "MISMATCH", "Income certificate expired or invalid"
        if lim and d["income"] > lim:
            return "MISMATCH", f"Income Rs {d['income']:,} exceeds limit Rs {lim:,}"
        return "MATCH", f"Income Rs {d['income']:,} within limit"

    def inst_fn(d):
        return ("MATCH", f"{d['institution']} is recognised") if d["recognised"] else ("MISMATCH", "Institution not recognised in AISHE")

    def lvl_fn(d):
        if not d["enrolled"]:
            return "MISMATCH", "Not shown as enrolled in APAAR"
        if d["level"] not in scheme["levels"].split(","):
            return "MISMATCH", f"Study level {d['level']} is not covered by this scheme"
        return "MATCH", f"Enrolled at level {d['level']}"

    chk("UIDAI", "Identity / name", f"/mock/uidai/{a}", name_fn)
    chk("e-District", "ST certificate", f"/mock/edistrict/{a}", st_fn)
    chk("e-District", "Income certificate", f"/mock/edistrict/{a}", inc_fn)
    chk("AISHE", "Institution", f"/mock/aishe/{a}", inst_fn)
    chk("APAAR", "Enrolment & level", f"/mock/apaar/{a}", lvl_fn)
    if scheme["needs_net"]:
        chk("UGC-NTA", "NET/JRF", f"/mock/ugc-nta/{a}",
            lambda d: ("MATCH", "NET/JRF qualified") if d["net_jrf"] else ("MISMATCH", "No NET/JRF record found"))
    return out


def verify_application(aid):
    with conn() as c:
        ap = c.execute("SELECT * FROM applications WHERE id=?", (aid,)).fetchone()
        stu = c.execute("SELECT * FROM students WHERE apaar_id=?", (ap["apaar_id"],)).fetchone()
        sch = c.execute("SELECT * FROM schemes WHERE id=?", (ap["scheme_id"],)).fetchone()
    results = run_checks(stu, sch)
    bad = [r for r in results if r[2] != "MATCH"]
    with conn() as c:
        c.execute("DELETE FROM verification_results WHERE application_id=?", (aid,))
        c.executemany("INSERT INTO verification_results(application_id,source,check_name,result,detail) VALUES(?,?,?,?,?)",
                      [(aid, *r) for r in results])
        status = "UNDER_REVIEW" if bad else "VERIFIED"
        c.execute("UPDATE applications SET status=?, updated_at=? WHERE id=?", (status, now(), aid))
        if bad:
            c.execute("INSERT INTO review_queue(application_id,reason) VALUES(?,?)",
                      (aid, "; ".join(f"{r[0]}: {r[3]}" for r in bad)))
    notify(stu["apaar_id"], f"Application #{aid} ({sch['name']}): " +
           ("all checks passed, awaiting sanction." if not bad else "sent for manual review. You do not need to re-apply."))
    audit("system", "VERIFY", f"app {aid}: {len(results) - len(bad)}/{len(results)} checks matched")
    return status
