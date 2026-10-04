"""
ShikshaSetu Unified Database Adapter.
Supports SQLite (default/fallback) and MySQL via PyMySQL.
Includes schema support for 5 Scheme Officers, Student Bank Details, Document Verification, and DBT.
"""
import os, random, sqlite3, logging
from datetime import datetime

DB_ENGINE = os.environ.get("DB_ENGINE", "sqlite").lower()
DB_FILE = os.environ.get("DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "shikshasetu.db"))

# MySQL configuration
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_DB = os.environ.get("MYSQL_DB", "shikshasetu")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))


class DictConnection:
    """Wrapper around PyMySQL connection to emulate SQLite row_factory behavior."""
    def __init__(self, pymysql_conn):
        self.raw_conn = pymysql_conn

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.raw_conn.rollback()
        else:
            self.raw_conn.commit()
        self.raw_conn.close()

    def execute(self, sql, params=None):
        mysql_sql = sql.replace("?", "%s")
        cursor = self.raw_conn.cursor()
        cursor.execute(mysql_sql, params or ())
        return cursor

    def executescript(self, sql_script):
        cursor = self.raw_conn.cursor()
        for statement in sql_script.split(";"):
            stmt = statement.strip()
            if stmt:
                cursor.execute(stmt)

    def executemany(self, sql, seq_params):
        mysql_sql = sql.replace("?", "%s")
        cursor = self.raw_conn.cursor()
        cursor.executemany(mysql_sql, seq_params)
        return cursor


def conn():
    """Returns database connection based on DB_ENGINE environment variable."""
    if DB_ENGINE == "mysql":
        try:
            import pymysql
            from pymysql.cursors import DictCursor
            raw = pymysql.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DB,
                port=MYSQL_PORT,
                cursorclass=DictCursor,
                autocommit=True
            )
            return DictConnection(raw)
        except Exception as err:
            logging.warning(f"MySQL connection failed ({err}), falling back to SQLite.")
            pass

    c = sqlite3.connect(DB_FILE, timeout=10)
    c.row_factory = sqlite3.Row
    return c


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def audit(actor, action, detail=""):
    with conn() as c:
        c.execute("INSERT INTO audit_log(actor,action,detail,ts) VALUES(?,?,?,?)", (actor, action, detail, now()))


def notify(apaar, msg):
    with conn() as c:
        c.execute("INSERT INTO notifications(apaar_id,message,created_at) VALUES(?,?,?)", (apaar, msg, now()))


def eligible(level):
    with conn() as c:
        cur = c.execute("SELECT * FROM schemes")
        rows = cur.fetchall()
        return [r for r in rows if level in r["levels"].split(",")]


SCHEMA_SQLITE = """
CREATE TABLE IF NOT EXISTS schemes(id INTEGER PRIMARY KEY, code TEXT, name TEXT, portal TEXT, levels TEXT,
  income_limit INTEGER, amount INTEGER, needs_net INTEGER DEFAULT 0, officer_name TEXT, officer_username TEXT);

CREATE TABLE IF NOT EXISTS officers(id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, name TEXT, scheme_id INTEGER, role TEXT, portal TEXT);

CREATE TABLE IF NOT EXISTS gov_registry(apaar_id TEXT PRIMARY KEY, name TEXT, tribe TEXT, is_st INTEGER,
  st_cert_valid INTEGER, income INTEGER, income_cert_valid INTEGER, institution TEXT, institution_recognised INTEGER,
  level TEXT, enrolled INTEGER, net_jrf INTEGER, state TEXT, district TEXT);

CREATE TABLE IF NOT EXISTS students(apaar_id VARCHAR(50) PRIMARY KEY, name TEXT, state TEXT, district TEXT, family_id INTEGER, lang TEXT,
  bank_name TEXT DEFAULT 'State Bank of India', account_no TEXT DEFAULT '98765432101', ifsc TEXT DEFAULT 'SBIN0001234', bank_balance INTEGER DEFAULT 0, password TEXT DEFAULT '123456');

CREATE TABLE IF NOT EXISTS applications(id INTEGER PRIMARY KEY AUTOINCREMENT, apaar_id TEXT, scheme_id INTEGER, status TEXT,
  remarks TEXT, created_at TEXT, updated_at TEXT);

CREATE TABLE IF NOT EXISTS documents(id INTEGER PRIMARY KEY AUTOINCREMENT, apaar_id TEXT, doc_type TEXT, source TEXT, ref TEXT, fetched_at TEXT,
  file_name TEXT DEFAULT '', verification_status TEXT DEFAULT 'VERIFIED', verification_note TEXT DEFAULT 'Pre-verified by DigiLocker/Issuer');

CREATE TABLE IF NOT EXISTS verification_results(id INTEGER PRIMARY KEY AUTOINCREMENT, application_id INTEGER, source TEXT,
  check_name TEXT, result TEXT, detail TEXT);

CREATE TABLE IF NOT EXISTS review_queue(id INTEGER PRIMARY KEY AUTOINCREMENT, application_id INTEGER, reason TEXT,
  status TEXT DEFAULT 'OPEN', officer_note TEXT);

CREATE TABLE IF NOT EXISTS disbursements(id INTEGER PRIMARY KEY AUTOINCREMENT, application_id INTEGER, amount INTEGER, dbt_status TEXT, date TEXT, transaction_ref TEXT DEFAULT '');

CREATE TABLE IF NOT EXISTS notifications(id INTEGER PRIMARY KEY AUTOINCREMENT, apaar_id TEXT, message TEXT, created_at TEXT);

CREATE TABLE IF NOT EXISTS audit_log(id INTEGER PRIMARY KEY AUTOINCREMENT, actor TEXT, action TEXT, detail TEXT, ts TEXT);
"""

# id, code, name, portal, levels, income_limit, amount, needs_net, officer_name, officer_username
SCHEMES = [
    (1, "PRE", "Pre-Matric Scholarship", "NSP", "PRE_MATRIC", 250000, 3500, 0, "Sh. Rajesh Kumar", "pre_officer"),
    (2, "POST", "Post-Matric Scholarship", "NSP", "POST_MATRIC,TOP_CLASS", 250000, 8000, 0, "Smt. Sunita Murmu", "post_officer"),
    (3, "TOP", "Top Class Education", "SFMP", "TOP_CLASS", 800000, 150000, 0, "Dr. Arvind Marandi", "top_officer"),
    (4, "NFST", "National Fellowship (NFST)", "SFMP", "RESEARCH", 0, 372000, 1, "Prof. D. Soren", "nfst_officer"),
    (5, "NOS", "National Overseas Scholarship", "NOS Portal", "OVERSEAS", 600000, 1500000, 0, "Sh. K. L. Meena", "nos_officer"),
]

OFFICERS = [
    (1, "pre_officer", "officer123", "Sh. Rajesh Kumar", 1, "Pre-Matric Scheme Nodal Officer", "National Scholarship Portal (NSP)"),
    (2, "post_officer", "officer123", "Smt. Sunita Murmu", 2, "Post-Matric Scheme Nodal Officer", "National Scholarship Portal (NSP)"),
    (3, "top_officer", "officer123", "Dr. Arvind Marandi", 3, "Top Class Education Scheme Officer", "Special Financial Management Portal (SFMP)"),
    (4, "nfst_officer", "officer123", "Prof. D. Soren", 4, "National Fellowship (NFST) Officer", "SFMP Research Fellowships Portal"),
    (5, "nos_officer", "officer123", "Sh. K. L. Meena", 5, "National Overseas Scholarship (NOS) Officer", "NOS International Portal"),
    (6, "admin", "officer123", "Director General (Scholarships)", 0, "Ministry Central Administrator", "MoTA Central Command Portal"),
]

STATES = {
    "Jharkhand": (["Ranchi", "Gumla"], ["Munda", "Oraon", "Santhal"]),
    "Odisha": (["Mayurbhanj", "Koraput"], ["Kondh", "Majhi", "Santal"]),
    "Chhattisgarh": (["Bastar", "Surguja"], ["Gond", "Netam", "Korram"]),
    "Madhya Pradesh": (["Jhabua", "Mandla"], ["Baiga", "Bhil", "Marko"]),
    "Tamil Nadu": (["Nilgiris", "Dharmapuri"], ["Toda", "Irula", "Kota"]),
    "Gujarat": (["Dahod", "Narmada"], ["Bhil", "Rathwa", "Vasava"]),
    "Rajasthan": (["Banswara", "Udaipur"], ["Meena", "Garasia", "Damor"]),
    "Maharashtra": (["Gadchiroli", "Nandurbar"], ["Gond", "Warli", "Pawara"]),
}
FIRST = ["Asha", "Ravi", "Meena", "Karthik", "Sunita", "Bhim", "Lakshmi", "Rohit", "Anita", "Suresh", "Geeta", "Manoj",
         "Kavita", "Deepak", "Sita", "Arjun", "Pooja", "Vikram", "Radha", "Sanjay"]
INST = ["Govt. High School", "Ranchi University", "IIT Bombay", "Tribal Residential School", "NIT Rourkela", "Govt. Arts College"]
LEVELS = ["PRE_MATRIC", "POST_MATRIC", "POST_MATRIC", "TOP_CLASS", "RESEARCH", "OVERSEAS"]
REASONS = ["Name mismatch with UIDAI record", "Income certificate expired or invalid",
           "Institution could not be confirmed in AISHE", "NET/JRF status could not be confirmed"]

DEMO = [
    ("APAAR100001", "Asha Munda", "Asha Munda", "Jharkhand", "Ranchi", "POST_MATRIC", 180000, 1, 1, 1, 0, "en", 1, "State Bank of India", "98765432101", "SBIN0001234", 0),
    ("APAAR100002", "Ravi Oraan", "Ravi Oraon", "Jharkhand", "Gumla", "POST_MATRIC", 200000, 1, 1, 1, 0, "hi", 2, "Punjab National Bank", "87654321092", "PUNB0004321", 0),
    ("APAAR100003", "Meena Toda", "Meena Toda", "Tamil Nadu", "Nilgiris", "POST_MATRIC", 150000, 1, 1, 1, 0, "ta", 3, "Canara Bank", "76543210983", "CNRB0005678", 8000),
    ("APAAR100004", "Karthik Toda", "Karthik Toda", "Tamil Nadu", "Nilgiris", "PRE_MATRIC", 150000, 1, 1, 1, 0, "ta", 3, "Canara Bank", "65432109874", "CNRB0005678", 0),
    ("APAAR100005", "Sunita Gond", "Sunita Gond", "Chhattisgarh", "Bastar", "TOP_CLASS", 500000, 1, 0, 1, 0, "hi", 4, "Bank of Baroda", "54321098765", "BARB0007890", 0),
    ("APAAR100006", "Bhim Bhil", "Bhim Bhil", "Gujarat", "Dahod", "RESEARCH", 400000, 1, 1, 1, 1, "en", 5, "Union Bank of India", "43210987656", "UBIN0002345", 0),
    ("APAAR100007", "Lakshmi Irula", "Lakshmi Irula", "Tamil Nadu", "Dharmapuri", "POST_MATRIC", 120000, 1, 1, -1, 0, "ta", 6, "Indian Overseas Bank", "32109876547", "IOBA0006789", 0),
]


def init_db():
    """Initializes schema and populates seed data for active database connection."""
    with conn() as c:
        c.executescript(SCHEMA_SQLITE)

        # Ensure columns exist if table already created previously (migration safety)
        try:
            c.execute("ALTER TABLE students ADD COLUMN bank_name TEXT DEFAULT 'State Bank of India'")
        except Exception: pass
        try:
            c.execute("ALTER TABLE students ADD COLUMN account_no TEXT DEFAULT '98765432101'")
        except Exception: pass
        try:
            c.execute("ALTER TABLE students ADD COLUMN ifsc TEXT DEFAULT 'SBIN0001234'")
        except Exception: pass
        try:
            c.execute("ALTER TABLE students ADD COLUMN bank_balance INTEGER DEFAULT 0")
        except Exception: pass
        try:
            c.execute("ALTER TABLE students ADD COLUMN password TEXT DEFAULT '123456'")
        except Exception: pass
        try:
            c.execute("ALTER TABLE schemes ADD COLUMN officer_name TEXT")
            c.execute("ALTER TABLE schemes ADD COLUMN officer_username TEXT")
        except Exception: pass
        try:
            c.execute("ALTER TABLE documents ADD COLUMN file_name TEXT DEFAULT ''")
            c.execute("ALTER TABLE documents ADD COLUMN verification_status TEXT DEFAULT 'VERIFIED'")
            c.execute("ALTER TABLE documents ADD COLUMN verification_note TEXT DEFAULT 'Pre-verified by DigiLocker'")
        except Exception: pass

        cur = c.execute("SELECT COUNT(*) as n FROM schemes")
        res = cur.fetchone()
        count = res["n"] if isinstance(res, dict) else res[0]
        if count > 0:
            # Check officers table
            off_cur = c.execute("SELECT COUNT(*) as n FROM officers")
            off_res = off_cur.fetchone()
            if (off_res["n"] if isinstance(off_res, dict) else off_res[0]) == 0:
                c.executemany("INSERT OR REPLACE INTO officers VALUES(?,?,?,?,?,?,?)", OFFICERS)
            return

        c.executemany("INSERT INTO schemes VALUES(?,?,?,?,?,?,?,?,?,?)", SCHEMES)
        c.executemany("INSERT INTO officers VALUES(?,?,?,?,?,?,?)", OFFICERS)

        rnd = random.Random(7)
        rows, students = [], []
        for d in DEMO:
            ap, gname, aname, st, dist, lvl, inc, stc, incc, inst, net, lang, fam, bname, acc, ifsc, bal = d
            rows.append((ap, gname, gname.split()[-1], 1, stc, inc, incc, "Govt. Arts College", inst, lvl, 1, net, st, dist))
            students.append((ap, aname, st, dist, fam, lang, bname, acc, ifsc, bal, "123456"))

        for i in range(8, 141):
            ap = f"APAAR{100000 + i}"
            st = rnd.choice(list(STATES))
            dists, tribes = STATES[st]
            tribe, dist, lvl = rnd.choice(tribes), rnd.choice(dists), rnd.choice(LEVELS)
            name = f"{rnd.choice(FIRST)} {tribe}"
            rows.append((ap, name, tribe, int(rnd.random() < .96), int(rnd.random() < .95), rnd.randrange(80000, 900000, 10000),
                         int(rnd.random() < .9), rnd.choice(INST), int(rnd.random() < .92), lvl,
                         int(rnd.random() < .92), int(lvl == "RESEARCH" and rnd.random() < .7), st, dist))
            if i <= 45 and rows[-1][3]:
                students.append((ap, name, st, dist, 1000 + i, rnd.choice(["en", "hi", "ta"]),
                                 "State Bank of India", f"9876543{100+i}", "SBIN0001234", 0, "123456"))

        c.executemany("INSERT INTO gov_registry VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
        c.executemany("INSERT INTO students VALUES(?,?,?,?,?,?,?,?,?,?,?)", students)

        def add_app(ap, sid, status, reason=None):
            cur = c.execute("INSERT INTO applications(apaar_id,scheme_id,status,remarks,created_at,updated_at) VALUES(?,?,?,?,?,?)",
                            (ap, sid, status, "", now(), now()))
            aid = getattr(cur, "lastrowid", 1)
            if status == "UNDER_REVIEW":
                c.execute("INSERT INTO review_queue(application_id,reason) VALUES(?,?)", (aid, reason))
            if status == "DISBURSED":
                sc_cur = c.execute("SELECT amount FROM schemes WHERE id=?", (sid,))
                sc_res = sc_cur.fetchone()
                amt = sc_res["amount"] if isinstance(sc_res, dict) else sc_res[0]
                c.execute("INSERT INTO disbursements(application_id,amount,dbt_status,date,transaction_ref) VALUES(?,?,'SUCCESS',?,?)",
                          (aid, amt, now()[:10], f"DBT-PFMS-{aid}-2026"))

        add_app("APAAR100003", 2, "DISBURSED")
        add_app("APAAR100004", 1, "VERIFIED")
        lv = {r[0]: r[9] for r in rows}
        for s in students[7:]:
            if rnd.random() < .55:
                opts = [x for x in SCHEMES if lv[s[0]] in x[4].split(",")]
                if opts:
                    add_app(s[0], rnd.choice(opts)[0], rnd.choice(["UNDER_REVIEW", "VERIFIED", "SANCTIONED", "DISBURSED", "DISBURSED"]),
                            rnd.choice(REASONS))
