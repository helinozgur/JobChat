from flask import Blueprint, jsonify, session, current_app as app

bp = Blueprint("status", __name__)

@bp.route("/api/status")
def get_status():
    prof = session.get("profession_obj") or {}
    return jsonify({
        "status": "healthy",
        "version": "3.0.0-modular",
        "has_session": bool(session.get("cv_content")),
        "profession": prof.get("display_name", "Belirlenmedi"),
        "profession_confidence": prof.get("confidence", None),
        "needs_manual_profession": session.get("needs_manual_profession", True),
        "ollama_configured": True,
        "ollama_model": app.config["OLLAMA_MODEL"]
    })
