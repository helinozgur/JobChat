from flask import Blueprint, request, jsonify, session, current_app as app

bp = Blueprint("override", __name__)

@bp.route("/api/profession/override", methods=["POST"])
def profession_override():
    try:
        data = request.get_json(force=True, silent=False)
        name = str(data.get("name","")).strip()
        display_name = str(data.get("display_name","")).strip()
        description = str(data.get("description","")).strip()
        keywords = data.get("keywords") or []
        technologies = data.get("technologies") or []

        if not name or not display_name or not description:
            return jsonify({"error":"name, display_name ve description zorunludur"}), 400
        if not isinstance(keywords, list) or not isinstance(technologies, list):
            return jsonify({"error":"keywords ve technologies list olmalıdır"}), 400

        session["profession_obj"] = {
            "name": name,
            "display_name": display_name,
            "description": description,
            "keywords": keywords,
            "technologies": technologies,
            "confidence": 1.0
        }
        session["needs_manual_profession"] = False

        return jsonify({"ok": True, "profession": session["profession_obj"]})
    except Exception as e:
        app.logger.exception("Profession override error")
        return jsonify({"error": f"Override hatası: {str(e)}"}), 400
