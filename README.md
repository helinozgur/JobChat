# JobChat# 1) sanal ortam (opsiyonel)
python -m venv .venv && . .venv/Scripts/activate  # (Windows PowerShell'de: .venv\Scripts\Activate.ps1)

# 2) bağımlılıklar
pip install -r requirements.txt

# 3) .env (opsiyonel)
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=qwen2.5:7b-instruct
# PROF_CONF_THRESHOLD=0.6
# SECRET_KEY=ats-career-coach-v3-ultra

# 4) çalıştır
python run.py

Ollama notu: CLI olmasa bile HTTP ile çalışır. Model yoksa:

curl -N http://localhost:11434/api/pull -H "Content-Type: application/json" -d "{\"name\":\"qwen2.5:7b-instruct\"}"


/api/chat yoksa kod otomatik /api/generate’a düşer.