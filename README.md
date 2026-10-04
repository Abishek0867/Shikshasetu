# ShikshaSetu: Unified MoTA Scholarship Module (Phase 1 & Phase 2)

SIH Problem Statement: **Ministry of Tribal Affairs (MoTA) Smart Automation**. A unified mobile-first platform integrating the five ST scholarship schemes (**Pre-Matric, Post-Matric, Top Class, NFST, NOS**) that currently sit across NSP, SFMP, and the NOS portal.

> **Honest Scope Note**: Government APIs (DigiLocker, UIDAI, e-District, AISHE/UDISE+, APAAR, UGC-NTA) are **mocked** in `mock_govt.py` for instant demo execution. Production adapters for sandbox/real government services are implemented in `phase2_bridge.py`. Scheme amounts and income limits are indicative demo values.

---

## Quick Run Instructions (2 Minutes)

### Option A: Via VS Code (Recommended)
1. Open this folder in **VS Code**.
2. Press `Ctrl+Shift+D` (Run and Debug menu).
3. Select **ShikshaSetu Web App (Flask)** and hit `F5` (or click Play).
4. Open your browser at `http://localhost:5000`.
5. Run tests anytime via VS Code Tasks (`Ctrl+Shift+B` -> **Run Smoke Tests** or **Run Phase 2 Integration Suite**).

### Option B: Via Terminal / Command Line
```bash
# 1. Activate virtual environment (optional)
python -m venv venv
venv\Scripts\activate            # On Windows PowerShell/CMD
# source venv/bin/activate       # On Linux/macOS

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run full automated smoke test suite (Phase 1)
python smoke_test.py

# 4. Run Phase 2 integration suite (LLM Tools, Bhashini Voice, Real Adapters, Portal Sync)
python phase2_test.py

# 5. Launch web application
python app.py                    # Access at http://localhost:5000
```
*Note: SQLite database (`shikshasetu.db`) is automatically initialized and seeded on first run. Delete `shikshasetu.db` to reset state.*

---

## Demo Accounts & Persona Guide

Students log in using their **APAAR ID** + OTP `123456`. Officers log in at `/officer/login` with password `officer123`.

| APAAR ID | Language | Story / Persona to Demo | Expected Outcome |
|---|---|---|---|
| `APAAR100001` | English | Clean record: applies to Post-Matric | All checks pass -> Status: **VERIFIED** |
| `APAAR100002` | Hindi | Name spelled differently in UIDAI (*Oraon* vs *Oraan*) | **Zero Auto-Rejection** -> Sent to **Manual Review Queue** |
| `APAAR100003` | Tamil | Already paid student; sibling `APAAR100004` active | **Family View** displayed; Tamil UI & Chatbot response |
| `APAAR100005` | Hindi | Expired income certificate on Top Class scheme | Enters Officer Review Queue for deficiency resolution |
| `APAAR100006` | English | Research scholar with NET/JRF qualification | NFST fellowship verified automatically -> **VERIFIED** |
| `APAAR100007` | Tamil | External AISHE API down/unreachable | Result marked `UNAVAILABLE`; student **not blocked** |

---

## Architecture Overview

```
 Student PWA (Jinja + CSS, mobile-first, EN/HI/TA)          Officer console (review queue, DBT, analytics)
            \                                                       /
             \______________  Flask API layer (app.py)  ____________/
                    |             |              |              |
            Scholarship      Document wallet   JAGO chatbot   Analytics
            service          (DigiLocker)      (chatbot.py)   (gap detection)
            (applications,                          |
             one-scheme rule)                       | tool-style lookups on the student's own data
                    |
        Unified Verification Layer (verification.py) & Phase 2 Adapters (phase2_bridge.py)
        one adapter call per source, results stored, mismatch => review_queue (never auto-reject)
                    |
   /mock/uidai  /mock/edistrict  /mock/aishe  /mock/apaar  /mock/ugc-nta  /mock/digilocker    (mock_govt.py)
                    |
              SQLite (db.py): schemes, gov_registry, students, applications, documents,
              verification_results, review_queue, disbursements, notifications, audit_log
```

---

## Key Design Principles & Features

1. **Adapter-Based Verification Layer**: `verification.fetch()` executes mock APIs in-process. In production, changing a single line routes calls to real government endpoints via `phase2_bridge.py`.
2. **Zero-Block Exception Routing**: Discrepancies (`MISMATCH` or `UNAVAILABLE`) route applications to the officer's `review_queue`. Students receive clear instructions without needing to re-apply.
3. **Cross-Portal One-Scheme Rule**: Single-window check prevents multi-scheme double-dipping across NSP, SFMP, and NOS portals.
4. **Audit Trail & Consent**: Ticking consent is mandatory before fetching document records. All logins, applications, reviews, disbursements, and outreach actions are logged to `audit_log`.
5. **Coverage Gap Analytics & Proactive Outreach**: Compares UDISE+/APAAR registry data with active applications to highlight unreached ST students by state and initiate SMS/WhatsApp outreach.

---

## Project Structure & File Guide

- `app.py`: Flask web application routes, auth, dashboards, officer review console, and gap analytics.
- `db.py`: SQLite database schema, initialization, seed data (demo students, registry, schemes), audit log.
- `verification.py`: Core verification engine executing automated multi-source checks with exception handling.
- `mock_govt.py`: Flask blueprint simulating government service endpoints (DigiLocker, UIDAI, AISHE, e-District, etc.).
- `chatbot.py`: JAGO assistant keyword intent engine supporting English, Hindi, and Tamil queries.
- `i18n.py`: Internationalization translations for UI strings, status codes, and chatbot replies.
- `phase2_bridge.py`: Phase 2 production architecture (DigiLocker OAuth, UIDAI Consent Vault, LLM Tool Engine, Bhashini Voice, Portal Sync Bridge).
- `smoke_test.py`: Phase 1 automated test suite exercising all demo scenarios.
- `phase2_test.py`: Automated test suite for Phase 2 LLM tool execution, voice adapters, and portal synchronization.
- `SIH_SUBMISSION_PACK.md`: Full SIH submission guide (PPT content, Mermaid diagrams, video recording script, impact metrics).
- `.vscode/`: Pre-configured VS Code debug launch targets (`launch.json`), tasks (`tasks.json`), and settings (`settings.json`).

---

## SIH Submission Deliverables

Full presentation outline, slide-by-slide guide, video recording script, and architecture diagrams can be found in [SIH_SUBMISSION_PACK.md](file:///c:/Users/acer/Downloads/shikshasetu-phase1/shikshasetu/SIH_SUBMISSION_PACK.md).
