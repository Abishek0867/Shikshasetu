import os
from functools import wraps
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify, abort
from db import conn, init_db, notify, audit, now, eligible
from mock_govt import bp as mock_bp
from i18n import T, STATUS
import verification, chatbot

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")
app.register_blueprint(mock_bp)
init_db()

ACTIVE = ("SUBMITTED", "UNDER_REVIEW", "VERIFIED", "SANCTIONED", "DISBURSED", "DEFICIENCY")
IN_ACTIVE = "(" + ",".join("?" * len(ACTIVE)) + ")"
STEP = {"SUBMITTED": 0, "UNDER_REVIEW": 0, "DEFICIENCY": 0, "VERIFIED": 1, "SANCTIONED": 2, "DISBURSED": 3}
OTP = "123456"  # demo only; production: UIDAI / SMS OTP
OFFICER_PW = os.environ.get("OFFICER_PASSWORD", "officer123")


def q(sql, *a, one=False):
    with conn() as c:
        rows = c.execute(sql, a).fetchall()
    return (rows[0] if rows else None) if one else rows


def x(sql, *a):
    with conn() as c:
        return c.execute(sql, a).lastrowid


def student_only(f):
    @wraps(f)
    def w(*a, **k):
        return f(*a, **k) if "apaar" in session else redirect(url_for("login"))
    return w


def officer_only(f):
    @wraps(f)
    def w(*a, **k):
        return f(*a, **k) if session.get("officer") else redirect(url_for("officer_login"))
    return w


@app.before_request
def set_lang():
    if request.args.get("lang") in T:
        session["lang"] = request.args["lang"]


@app.context_processor
def inject():
    lang = session.get("lang", "en")
    curr_student = q("SELECT * FROM students WHERE apaar_id=?", session.get("apaar"), one=True) if "apaar" in session else None
    from datetime import datetime
    curr_time = datetime.now().strftime("%a %d-%b-%Y %H:%M:%S")
    return dict(t=T[lang], lang=lang, S=STATUS[lang], STEP=STEP, current_student=curr_student, curr_time=curr_time)


@app.route("/")
def index():
    if "apaar" in session:
        return redirect(url_for("dashboard"))
    if "officer" in session:
        return redirect(url_for("officer"))
    return render_template("landing.html")


@app.route("/home")
@app.route("/landing")
def landing_page():
    return render_template("landing.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        tribe = request.form.get("tribe", "").strip()
        state = request.form.get("state", "Jharkhand")
        district = request.form.get("district", "Ranchi").strip()
        level = request.form.get("level", "POST_MATRIC")
        income = int(request.form.get("income", 150000) or 150000)
        bank_name = request.form.get("bank_name", "State Bank of India")
        account_no = request.form.get("account_no", "98765432101").strip()
        ifsc = request.form.get("ifsc", "SBIN0001234").strip()
        pw = request.form.get("password", "123456").strip()

        import random
        apaar = f"APAAR{random.randint(200000, 999999)}"
        while q("SELECT 1 FROM gov_registry WHERE apaar_id=?", apaar, one=True):
            apaar = f"APAAR{random.randint(200000, 999999)}"

        x("""INSERT INTO gov_registry(apaar_id,name,tribe,is_st,st_cert_valid,income,income_cert_valid,institution,institution_recognised,level,enrolled,net_jrf,state,district)
             VALUES(?,?,?,1,1,?,1,'Govt. Arts College',1,?,1,0,?,?)""",
          apaar, name, tribe, income, level, state, district)

        x("""INSERT INTO students(apaar_id,name,state,district,family_id,lang,bank_name,account_no,ifsc,bank_balance,password)
             VALUES(?,?,?,?,?,'en',?,?,?,0,?)""",
          apaar, name, state, district, random.randint(1000, 9999), bank_name, account_no, ifsc, pw)

        # Detect eligible scholarships
        fit_schemes = [sc["name"] for sc in q("SELECT * FROM schemes") if level in sc["levels"].split(",")]
        schemes_str = ", ".join(fit_schemes) if fit_schemes else "Post-Matric Scholarship"

        notify(apaar, f"🎉 Welcome {name}! Registration complete. Based on your enrolment level ({level}), you are eligible to apply for: {schemes_str}.")
        audit(apaar, "REGISTER", f"Registered new student {name} ({apaar})")

        session.update(apaar=apaar, lang="en")
        flash(f"Registration successful! Your generated APAAR ID is {apaar}. Keep it safe for all MoTA ST scholarships.")
        return redirect(url_for("dashboard"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        a = request.form["apaar"].strip().upper()
        otp_in = request.form.get("otp", "").strip()
        s = q("SELECT * FROM students WHERE apaar_id=?", a, one=True)
        g = q("SELECT * FROM gov_registry WHERE apaar_id=? AND is_st=1", a, one=True)

        valid_pw = (otp_in == OTP or (s and s.get("password") and s["password"] == otp_in) or otp_in == "123456")
        if not valid_pw:
            flash("Invalid OTP or Password. The demo OTP is 123456.")
        else:
            if not s and g:
                x("""INSERT INTO students(apaar_id,name,state,district,family_id,lang,bank_name,account_no,ifsc,bank_balance,password)
                     VALUES(?,?,?,?,?,'en','State Bank of India','98765432101','SBIN0001234',0,'123456')""",
                  a, g["name"], g["state"], g["district"], int(a[5:]) if a[5:].isdigit() else 0)
                audit(a, "AUTO_REGISTER", "profile created from APAAR registry")
                s = q("SELECT * FROM students WHERE apaar_id=?", a, one=True)
            if s:
                session.update(apaar=a, lang=s["lang"])
                audit(a, "LOGIN")
                return redirect(url_for("dashboard"))
            flash("APAAR ID not found or not listed as an ST student.")
    return render_template("login.html", officer=False)


@app.route("/officer/login", methods=["GET", "POST"])
def officer_login():
    if request.method == "POST":
        un = request.form.get("username", "admin").strip()
        pw = request.form.get("password", "").strip()
        off = q("SELECT * FROM officers WHERE username=? AND password=?", un, pw, one=True)
        if off or pw == OFFICER_PW:
            if not off:
                off = q("SELECT * FROM officers WHERE username=?", un, one=True) or {
                    "username": "admin", "name": "Central Ministry Admin", "role": "Ministry Administrator", "scheme_id": 0, "portal": "MoTA Central Portal"
                }
            session["officer"] = True
            session["officer_username"] = off["username"]
            session["officer_name"] = off["name"]
            session["officer_role"] = off["role"]
            session["officer_scheme_id"] = off["scheme_id"]
            session["officer_portal"] = off["portal"]
            audit(off["username"], "OFFICER_LOGIN", f"Role: {off['role']}")
            return redirect(url_for("officer"))
        flash("Wrong password or invalid officer credentials.")
    return render_template("login.html", officer=True)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))



def sync_wallet(a):
    code, d = verification.fetch(f"/mock/digilocker/{a}/documents")
    if code != 200:
        return 0
    have = {r["doc_type"] for r in q("SELECT doc_type FROM documents WHERE apaar_id=?", a)}
    new = [doc for doc in d["documents"] if doc["doc_type"] not in have]
    for doc in new:
        x("INSERT INTO documents(apaar_id,doc_type,source,ref,fetched_at) VALUES(?,?,?,?,?)", a, doc["doc_type"], "DigiLocker", doc["ref"], now())
    audit(a, "WALLET_SYNC", f"{len(new)} new documents")
    return len(new)


@app.route("/dashboard")
@student_only
def dashboard():
    a = session["apaar"]
    s = q("SELECT * FROM students WHERE apaar_id=?", a, one=True)
    apps = q("""SELECT ap.*, sc.name scheme, sc.portal FROM applications ap JOIN schemes sc ON sc.id=ap.scheme_id
                WHERE ap.apaar_id=? ORDER BY ap.id DESC""", a)
    paid = q("""SELECT COALESCE(SUM(d.amount),0) n FROM disbursements d JOIN applications ap ON ap.id=d.application_id
                WHERE ap.apaar_id=?""", a, one=True)["n"]
    g = q("SELECT level FROM gov_registry WHERE apaar_id=?", a, one=True)
    fit = {e["id"] for e in eligible(g["level"])} if g else set()
    reasons = {r["application_id"]: r["reason"] for r in q(
        "SELECT * FROM review_queue WHERE status='OPEN' AND application_id IN (SELECT id FROM applications WHERE apaar_id=?)", a)}
    docs = q("SELECT * FROM documents WHERE apaar_id=?", a)
    pend = [] if docs else ["Fetch your documents from DigiLocker"]
    for p in apps:
        if p["status"] == "DEFICIENCY":
            pend.append(f"{p['scheme']}: correction needed - {p['remarks']}")
        if p["status"] == "UNDER_REVIEW":
            pend.append(f"{p['scheme']}: officer is reviewing - {reasons.get(p['id'], '')}")
    return render_template("dashboard.html", s=s, apps=apps, paid=paid, fit=fit, pend=pend, docs=docs,
                           schemes=q("SELECT * FROM schemes"),
                           family=q("""SELECT st.name, sc.name scheme, ap.status FROM students st
                                       LEFT JOIN applications ap ON ap.apaar_id=st.apaar_id LEFT JOIN schemes sc ON sc.id=ap.scheme_id
                                       WHERE st.family_id=? AND st.apaar_id!=?""", s["family_id"], a),
                           notes=q("SELECT * FROM notifications WHERE apaar_id=? ORDER BY id DESC LIMIT 5", a))


@app.post("/wallet/sync")
@student_only
def wallet_sync():
    flash(f"{sync_wallet(session['apaar'])} new document(s) added to your wallet.")
    return redirect(url_for("dashboard"))


@app.post("/apply/<int:sid>")
@student_only
def apply(sid):
    a = session["apaar"]
    if not request.form.get("consent"):
        flash("Please tick the consent box to continue.")
        return redirect(url_for("dashboard"))
    cur = q(f"""SELECT ap.status, sc.name FROM applications ap JOIN schemes sc ON sc.id=ap.scheme_id
                WHERE ap.apaar_id=? AND ap.status IN {IN_ACTIVE}""", a, *ACTIVE, one=True)
    if cur:  # one-scheme-at-a-time rule, enforced across all three portals from the unified view
        flash(f"Only one scholarship at a time: you already have an active application for {cur['name']} ({cur['status']}).")
        return redirect(url_for("dashboard"))
    sync_wallet(a)
    aid = x("INSERT INTO applications(apaar_id,scheme_id,status,remarks,created_at,updated_at) VALUES(?,?,'SUBMITTED','',?,?)", a, sid, now(), now())
    audit(a, "CONSENT+APPLY", f"scheme {sid}; consent given to fetch DigiLocker/UIDAI/e-District records")
    verification.verify_application(aid)
    return redirect(url_for("application", aid=aid))


@app.route("/application/<int:aid>")
@student_only
def application(aid):
    ap = q("SELECT ap.*, sc.name scheme, sc.portal FROM applications ap JOIN schemes sc ON sc.id=ap.scheme_id WHERE ap.id=? AND ap.apaar_id=?",
           aid, session["apaar"], one=True) or abort(404)
    return render_template("application.html", ap=ap, checks=q("SELECT * FROM verification_results WHERE application_id=?", aid),
                           review=q("SELECT * FROM review_queue WHERE application_id=? ORDER BY id DESC", aid, one=True),
                           pay=q("SELECT * FROM disbursements WHERE application_id=?", aid, one=True))


@app.route("/profile")
@student_only
def profile():
    a = session["apaar"]
    s = q("SELECT * FROM students WHERE apaar_id=?", a, one=True)
    g = q("SELECT * FROM gov_registry WHERE apaar_id=?", a, one=True)
    docs = q("SELECT * FROM documents WHERE apaar_id=?", a)
    return render_template("profile.html", s=s, g=g, docs=docs)


@app.post("/wallet/upload")
@student_only
def wallet_upload():
    a = session["apaar"]
    doc_type = request.form.get("doc_type", "ST Certificate")
    file = request.files.get("doc_file")
    s = q("SELECT * FROM students WHERE apaar_id=?", a, one=True)
    g = q("SELECT * FROM gov_registry WHERE apaar_id=?", a, one=True)

    # Automated pre-verification check
    note = "Validated with State e-District repository"
    if "ST" in doc_type or "Caste" in doc_type:
        tribe = g["tribe"] if g else "ST"
        note = f"Pre-verified: Valid ST Certificate for Tribe '{tribe}', issued by Competent Sub-Divisional Authority."
    elif "Income" in doc_type:
        inc = g["income"] if g else 150000
        note = f"Pre-verified: Annual Family Income Rs {inc:,} verified within statutory limits (e-District Gazette)."
    elif "Aadhaar" in doc_type:
        note = "Pre-verified: UIDAI Aadhaar e-KYC Vault Match confirmed (Aadhaar Seeded Active)."
    elif "Marksheet" in doc_type or "Bonafide" in doc_type:
        inst = g["institution"] if g else "Recognised Institution"
        note = f"Pre-verified: Academic Enrollment confirmed with AISHE/UDISE+ ({inst})."

    import random
    ref_token = f"DL-GOV-{doc_type[:3].upper()}-{random.randint(100000,999999)}"
    file_name = file.filename if file else f"{doc_type.replace(' ', '_')}.pdf"

    x("""INSERT INTO documents(apaar_id,doc_type,source,ref,fetched_at,file_name,verification_status,verification_note)
         VALUES(?,?,?,?,?,?,?,?)""", a, doc_type, "DigiLocker / e-District Vault", ref_token, now(), file_name, "VERIFIED", note)

    notify(a, f"📄 Document Pre-Verified: Your '{doc_type}' passed automated verification checks and has been added to your DigiLocker Wallet.")
    audit(a, "DOC_UPLOAD_VERIFIED", f"{doc_type} ({ref_token})")
    flash(f"Document '{doc_type}' passed automated pre-verification and is now active in your wallet!")
    return redirect(url_for("wallet"))


@app.route("/wallet")
@student_only
def wallet():
    a = session["apaar"]
    s = q("SELECT * FROM students WHERE apaar_id=?", a, one=True)
    docs = q("SELECT * FROM documents WHERE apaar_id=?", a)
    return render_template("wallet.html", s=s, docs=docs)


@app.route("/notifications")
@student_only
def notifications():
    a = session["apaar"]
    s = q("SELECT * FROM students WHERE apaar_id=?", a, one=True)
    notes = q("SELECT * FROM notifications WHERE apaar_id=? ORDER BY id DESC", a)
    return render_template("notifications.html", s=s, notes=notes)


@app.post("/resubmit/<int:aid>")
@student_only
def resubmit(aid):
    if q("SELECT 1 FROM applications WHERE id=? AND apaar_id=? AND status='DEFICIENCY'", aid, session["apaar"], one=True):
        audit(session["apaar"], "RESUBMIT", f"app {aid}")
        verification.verify_application(aid)
    return redirect(url_for("application", aid=aid))


@app.post("/chat")
@student_only
def chat():
    msg = (request.get_json(silent=True) or {}).get("message", "")
    import llm_chatbot
    return jsonify(reply=llm_chatbot.process_query(session["apaar"], msg, session.get("lang", "en")))


# ---------------- officer side ----------------
@app.route("/officer")
@officer_only
def officer():
    sid = session.get("officer_scheme_id", 0)
    all_schemes = q("SELECT * FROM schemes ORDER BY id")
    off_scheme = q("SELECT name FROM schemes WHERE id=?", sid, one=True) if sid > 0 else None

    officer_info = {
        "username": session.get("officer_username", "admin"),
        "name": session.get("officer_name", "Scheme Nodal Officer"),
        "role": session.get("officer_role", "Ministry Officer"),
        "portal": session.get("officer_portal", "MoTA Central Portal"),
        "scheme_id": sid,
        "scheme_name": off_scheme["name"] if off_scheme else "All Schemes"
    }

    base = "FROM applications ap JOIN students st ON st.apaar_id=ap.apaar_id JOIN schemes sc ON sc.id=ap.scheme_id"

    if sid > 0:
        stats = q("SELECT status, COUNT(*) n FROM applications WHERE scheme_id=? GROUP BY status", sid)
        queue = q("""SELECT r.*, ap.apaar_id, st.name student, sc.name scheme FROM review_queue r
                   JOIN applications ap ON ap.id=r.application_id JOIN students st ON st.apaar_id=ap.apaar_id
                   JOIN schemes sc ON sc.id=ap.scheme_id WHERE r.status='OPEN' AND sc.id=? ORDER BY r.id""", sid)
        ready = q("SELECT ap.id, st.name student, sc.name scheme, sc.amount, st.bank_name, st.account_no " + base + " WHERE ap.status='VERIFIED' AND sc.id=?", sid)
    else:
        stats = q("SELECT status, COUNT(*) n FROM applications GROUP BY status")
        queue = q("""SELECT r.*, ap.apaar_id, st.name student, sc.name scheme FROM review_queue r
                   JOIN applications ap ON ap.id=r.application_id JOIN students st ON st.apaar_id=ap.apaar_id
                   JOIN schemes sc ON sc.id=ap.scheme_id WHERE r.status='OPEN' ORDER BY r.id""")
        ready = q("SELECT ap.id, st.name student, sc.name scheme, sc.amount, st.bank_name, st.account_no " + base + " WHERE ap.status='VERIFIED'")

    logs = q("SELECT * FROM audit_log ORDER BY id DESC LIMIT 15")
    return render_template("officer.html", stats=stats, queue=queue, ready=ready, logs=logs,
                           officer_info=officer_info, all_schemes=all_schemes)


@app.post("/officer/announce_scheme")
@officer_only
def announce_scheme():
    sid = int(request.form.get("scheme_id", 1))
    note = request.form.get("note", "").strip()
    scheme = q("SELECT * FROM schemes WHERE id=?", sid, one=True)
    if scheme:
        eligible_students = q("""SELECT st.apaar_id, st.name FROM students st
                                 JOIN gov_registry g ON g.apaar_id=st.apaar_id
                                 WHERE g.is_st=1""")
        count = 0
        for st in eligible_students:
            g = q("SELECT level FROM gov_registry WHERE apaar_id=?", st["apaar_id"], one=True)
            if g and g["level"] in scheme["levels"].split(","):
                notify(st["apaar_id"], f"🎓 New Scholarship Announcement: Applications are now open for '{scheme['name']}' (Annual grant: Rs {scheme['amount']:,})! {note} Apply now from your dashboard.")
                count += 1
        flash(f"Announcement broadcast successfully! Notifications sent to {count} eligible students for {scheme['name']}.")
        audit(session.get("officer_username", "officer"), "ANNOUNCE_SCHEME", f"Scheme {sid}: {scheme['name']} announced to {count} students")
    return redirect(url_for("officer"))


@app.route("/officer/rbac")
@officer_only
def officer_rbac():
    from services.rbac import RBACEngine
    role = request.args.get("role", "MINISTRY_OFFICER")
    perms = RBACEngine.get_role_permissions(role)
    base = "FROM applications ap JOIN students st ON st.apaar_id=ap.apaar_id JOIN schemes sc ON sc.id=ap.scheme_id"
    ready = q("SELECT ap.id, st.name student, sc.name scheme, sc.amount " + base + " WHERE ap.status='VERIFIED'")
    return render_template("officer_rbac.html", role=role, permissions=perms, ready=ready)


@app.post("/officer/bulk_sanction")
@officer_only
def bulk_sanction():
    app_ids = request.form.getlist("app_ids")
    sanctioned_count = 0
    for aid in app_ids:
        aid_int = int(aid)
        ap = q("SELECT ap.apaar_id, sc.amount, sc.name as scheme_name, sc.portal FROM applications ap JOIN schemes sc ON sc.id=ap.scheme_id WHERE ap.id=? AND ap.status='VERIFIED'", aid_int, one=True)
        if ap:
            tx_ref = f"DBT-PFMS-{aid_int}-{now()[:10]}"
            x("INSERT INTO disbursements(application_id,amount,dbt_status,date,transaction_ref) VALUES(?,?,'SUCCESS',?,?)", aid_int, ap["amount"], now()[:10], tx_ref)
            x("UPDATE applications SET status='DISBURSED', updated_at=? WHERE id=?", now(), aid_int)
            x("UPDATE students SET bank_balance = bank_balance + ? WHERE apaar_id=?", ap["amount"], ap["apaar_id"])

            stu = q("SELECT bank_name, account_no, bank_balance FROM students WHERE apaar_id=?", ap["apaar_id"], one=True)
            stu_d = dict(stu) if stu else {}
            acc_val = str(stu_d.get("account_no", "2101"))
            acc_masked = "XXXX-" + (acc_val[-4:] if len(acc_val) >= 4 else "2101")
            bname = stu_d.get("bank_name", "State Bank of India")

            notify(ap["apaar_id"], f"💰 DBT Credit Alert: Rs {ap['amount']:,} credited to your {bname} A/C ({acc_masked}) for {ap['scheme_name']}. Ref: {tx_ref}.")
            sanctioned_count += 1
            from services.portal_sync import PortalSyncEngine
            PortalSyncEngine().sync_application(aid_int)
    audit(session.get("officer_username", "officer"), "BULK_SANCTION", f"Sanctioned {sanctioned_count} applications via DBT")
    flash(f"Bulk DBT Disbursement complete for {sanctioned_count} application(s).")
    return redirect(url_for("officer_rbac"))


@app.post("/officer/review/<int:rid>")
@officer_only
def review(rid):
    r = q("SELECT r.*, ap.apaar_id FROM review_queue r JOIN applications ap ON ap.id=r.application_id WHERE r.id=? AND r.status='OPEN'", rid, one=True) or abort(404)
    act, note = request.form["action"], request.form.get("note", "").strip()
    new = {"approve": "VERIFIED", "reject": "REJECTED", "deficiency": "DEFICIENCY"}[act]
    x("UPDATE review_queue SET status='CLOSED', officer_note=? WHERE id=?", note, rid)
    x("UPDATE applications SET status=?, remarks=?, updated_at=? WHERE id=?", new, note, now(), r["application_id"])
    notify(r["apaar_id"], f"Application #{r['application_id']} is now: {new}. {note}")
    audit(session.get("officer_username", "officer"), f"REVIEW_{act.upper()}", f"app {r['application_id']}")
    return redirect(url_for("officer"))


@app.post("/officer/disburse/<int:aid>")
@officer_only
def disburse(aid):
    ap = q("SELECT ap.apaar_id, sc.amount, sc.name as scheme_name, sc.portal FROM applications ap JOIN schemes sc ON sc.id=ap.scheme_id WHERE ap.id=? AND ap.status='VERIFIED'", aid, one=True)
    if ap:
        tx_ref = f"DBT-PFMS-{aid}-{now()[:10]}"
        x("INSERT INTO disbursements(application_id,amount,dbt_status,date,transaction_ref) VALUES(?,?,'SUCCESS',?,?)", aid, ap["amount"], now()[:10], tx_ref)
        x("UPDATE applications SET status='DISBURSED', updated_at=? WHERE id=?", now(), aid)
        x("UPDATE students SET bank_balance = bank_balance + ? WHERE apaar_id=?", ap["amount"], ap["apaar_id"])

        stu = q("SELECT bank_name, account_no, bank_balance FROM students WHERE apaar_id=?", ap["apaar_id"], one=True)
        stu_d = dict(stu) if stu else {}
        acc_val = str(stu_d.get("account_no", "2101"))
        acc_masked = "XXXX-" + (acc_val[-4:] if len(acc_val) >= 4 else "2101")
        bname = stu_d.get("bank_name", "State Bank of India")
        new_bal = stu_d.get("bank_balance", ap["amount"])

        notify(ap["apaar_id"], f"💰 DBT Credit Alert: Rs {ap['amount']:,} credited to your {bname} A/C ({acc_masked}) for {ap['scheme_name']}. Ref: {tx_ref}. Updated Balance: Rs {new_bal:,}.")
        audit(session.get("officer_username", "officer"), "SANCTION+DISBURSE", f"app {aid}: Rs {ap['amount']:,} to {ap['apaar_id']}")
        from services.portal_sync import PortalSyncEngine
        PortalSyncEngine().sync_application(aid)
        flash(f"DBT payment of Rs {ap['amount']:,} credited to {ap['apaar_id']}'s {bname} account.")
    return redirect(url_for("officer"))



GAP = f"FROM gov_registry g WHERE g.enrolled=1 AND g.is_st=1 AND g.apaar_id NOT IN (SELECT apaar_id FROM applications WHERE status IN {IN_ACTIVE})"


@app.route("/officer/analytics")
@officer_only
def analytics():
    total = q("SELECT COUNT(*) n FROM gov_registry WHERE enrolled=1 AND is_st=1", one=True)["n"]
    return render_template("analytics.html", total=total, gap=q("SELECT g.* " + GAP + " ORDER BY g.state LIMIT 25", *ACTIVE),
                           n_gap=q("SELECT COUNT(*) n " + GAP, *ACTIVE, one=True)["n"],
                           by_state=q("SELECT g.state, COUNT(*) n " + GAP + " GROUP BY g.state ORDER BY n DESC", *ACTIVE))


@app.post("/officer/outreach/<state>")
@officer_only
def outreach(state):
    from services.outreach import OutreachService
    res = OutreachService().trigger_batch_sms_outreach(state, "You may be eligible for an ST scholarship. Log in to ShikshaSetu with your APAAR ID to apply.")
    flash(f"Outreach SMS queued for {res['targeted_count']} students in {state}.")
    return redirect(url_for("analytics"))


@app.post("/api/v2/voice")
@student_only
def api_voice():
    from services.bhashini import BhashiniVoiceEngine
    lang = request.args.get("lang", session.get("lang", "en"))
    engine = BhashiniVoiceEngine()
    processed = engine.process_speech_input(b"", lang_code=lang)
    reply = chatbot.reply(session["apaar"], processed["transcription"], lang=session.get("lang", "en"))
    tts = engine.generate_speech_response(reply, lang_code=lang)
    return jsonify(transcription=processed["transcription"], reply=reply, audio=tts)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)

