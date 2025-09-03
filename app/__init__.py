import logging
from flask import Flask
from flask_cors import CORS
from flask_session import Session
from .config import load_config

def create_app():
    app = Flask(__name__, template_folder="../templates")
    cfg = load_config()
    app.config.update(cfg)

    app.secret_key = app.config["SECRET_KEY"]
    CORS(app)

    # ---- Server-side session ----
    Session(app)

    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

    # Blueprints
    from .routes.analyze import bp as analyze_bp
    from .routes.chat import bp as chat_bp
    from .routes.status import bp as status_bp
    from .routes.profession_override import bp as override_bp
    from .routes.root import bp as root

    app.register_blueprint(analyze_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(status_bp)
    app.register_blueprint(override_bp)
    app.register_blueprint(root)


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

    app.logger.info("🚀 ATS Career Coach v3 - Modular")
    app.logger.info(f"🤖 Ollama: {app.config['OLLAMA_BASE_URL']} - Model: {app.config['OLLAMA_MODEL']}")
    app.logger.info(f"🎯 Profession confidence threshold: {app.config['PROF_CONF_THRESHOLD']}")
    return app
