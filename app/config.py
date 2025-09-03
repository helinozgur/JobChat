import os, tempfile
from dotenv import load_dotenv

load_dotenv()

def load_config():
    return {
        # ---- Ollama ----
        "OLLAMA_BASE_URL": os.environ.get("OLLAMA_URL", "http://localhost:11434"),
        "OLLAMA_MODEL": os.environ.get("OLLAMA_MODEL", "qwen2.5:7b-instruct"),
        "OLLAMA_TIMEOUT": int(os.environ.get("OLLAMA_TIMEOUT", "60")),

        # ---- Meslek eşiği ----
        "PROF_CONF_THRESHOLD": float(os.environ.get("PROF_CONF_THRESHOLD", "0.6")),

        # ---- Flask secret ----
        "SECRET_KEY": os.environ.get("SECRET_KEY", "ats-career-coach-v3"),

        # ---- Server-side session ----
        "SESSION_TYPE": os.environ.get("SESSION_TYPE", "filesystem"),
        "SESSION_FILE_DIR": os.path.join(tempfile.gettempdir(), "jobchat_sessions"),
        "SESSION_PERMANENT": False,
        "SESSION_USE_SIGNER": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "SESSION_COOKIE_SECURE": False,  # local geliştirme
    }
