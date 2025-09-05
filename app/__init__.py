# app/__init__.py
import logging
from pathlib import Path
from flask import Flask
from flask_cors import CORS
from flask_session import Session
from .config import load_config

def create_app():
    # ---- Yol kurulumları (mutlak) ----
    here = Path(__file__).resolve().parent          # app/
    project_root = here.parent                      # proje kökü
    templates_dir = project_root / "templates"
    static_dir    = project_root / "static"
    session_dir   = project_root / ".flask_session"
    session_dir.mkdir(exist_ok=True)

    # ---- Flask app ----
    app = Flask(
        __name__,
        template_folder=str(templates_dir),
        static_folder=str(static_dir),
    )

    # ---- Config ----
    cfg = load_config()
    app.config.update(cfg)

    # Session (server-side)
    app.config.setdefault("SECRET_KEY", "change-me")
    app.config.setdefault("SESSION_TYPE", "filesystem")
    app.config.setdefault("SESSION_FILE_DIR", str(session_dir))
    app.config.setdefault("SESSION_PERMANENT", False)
    app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")
    app.config.setdefault("SESSION_COOKIE_SECURE", False)  # HTTPS’de True yapın
    Session(app)

    # CORS (API için)
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})

    # Logging
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

    # ---- Blueprints ----
    from .routes.analyze import bp as analyze_bp
    from .routes.chat import bp as chat_bp
    from .routes.status import bp as status_bp
    from .routes.profession_override import bp as override_bp
    from .routes.root import bp as root_bp

    app.register_blueprint(analyze_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(status_bp)
    app.register_blueprint(override_bp)
    app.register_blueprint(root_bp)

    # ---- Error handlers ----
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Endpoint bulunamadı"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.exception("Internal server error")
        return {"error": "Sunucu hatası"}, 500

    @app.errorhandler(413)
    def file_too_large(error):
        return {"error": "Dosya çok büyük. Maksimum 10MB"}, 413

    # ---- Boot log ----
    app.logger.info("🚀 ATS Career Coach v3 - Modular")
    app.logger.info(f"🤖 Ollama: {app.config.get('OLLAMA_BASE_URL')} - Model: {app.config.get('OLLAMA_MODEL')}")
    app.logger.info(f"🎯 Profession confidence threshold: {app.config.get('PROF_CONF_THRESHOLD')}")

    return app
