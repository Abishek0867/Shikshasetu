"""Mock government APIs. In production each route is replaced by the real service
(UIDAI, e-District, AISHE/UDISE+, APAAR, UGC-NTA, DigiLocker) behind the same adapter."""
from flask import Blueprint, jsonify
from db import conn

bp = Blueprint("mock", __name__, url_prefix="/mock")


def _rec(a):
    with conn() as c:
        r = c.execute("SELECT * FROM gov_registry WHERE apaar_id=?", (a,)).fetchone()
    return dict(r) if r else None


def _wrap(a, fn):
    r = _rec(a)
    return (jsonify(error="record not found"), 404) if not r else fn(r)


@bp.route("/uidai/<a>")
def uidai(a):
    return _wrap(a, lambda r: jsonify(name=r["name"], verified=True))


@bp.route("/edistrict/<a>")
def edistrict(a):
    return _wrap(a, lambda r: jsonify(is_st=bool(r["is_st"]), tribe=r["tribe"], st_cert_valid=bool(r["st_cert_valid"]),
                                      income=r["income"], income_cert_valid=bool(r["income_cert_valid"])))


@bp.route("/aishe/<a>")
def aishe(a):
    def f(r):
        if r["institution_recognised"] == -1:
            return jsonify(error="AISHE service temporarily unavailable"), 503
        return jsonify(institution=r["institution"], recognised=bool(r["institution_recognised"]))
    return _wrap(a, f)


@bp.route("/apaar/<a>")
def apaar(a):
    return _wrap(a, lambda r: jsonify(enrolled=bool(r["enrolled"]), level=r["level"]))


@bp.route("/ugc-nta/<a>")
def ugc(a):
    return _wrap(a, lambda r: jsonify(net_jrf=bool(r["net_jrf"])))


@bp.route("/digilocker/<a>/documents")
def digilocker(a):
    return _wrap(a, lambda r: jsonify(documents=[{"doc_type": t, "ref": f"DL-{i}-{a}"} for i, t in
                                                 enumerate(["Aadhaar", "ST Certificate", "Income Certificate", "Marksheet"])]))
