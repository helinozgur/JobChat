# app/routes/chat.py
import json
import requests
import logging
from flask import Blueprint, request, jsonify, Response, session, current_app as app
from ..services.prompt import PromptGenerator
from ..models import ProfessionProfile

bp = Blueprint("chat", __name__)

@bp.route("/api/chat")
def chat_stream():
    question = request.args.get("question", "").strip()
    if not question:
        return jsonify({"error": "Soru boş olamaz"}), 400

    # ---- Session verileri
    job_description = session.get("job_description", "")
    cv_content      = session.get("cv_content", "")
    if not cv_content:
        return jsonify({"error": "Önce CV analizini yapın"}), 400

    needs_manual = session.get("needs_manual_profession", True)
    prof_dict    = session.get("profession_obj")
    if needs_manual or not prof_dict:
        return jsonify({
            "error": "Meslek tespit edilemedi. Lütfen arayüzden meslek bilgilerini girin.",
            "needs_manual_input": True
        }), 400

    # Skills hizalama sonuçları
    cv_skills      = session.get("cv_skills", []) or []
    job_skills     = session.get("job_skills", []) or []
    matched_skills = session.get("matched_skills", []) or []
    if not isinstance(cv_skills, list): cv_skills = []
    if not isinstance(job_skills, list): job_skills = []
    if not isinstance(matched_skills, list): matched_skills = []

    # Company persona (opsiyonel)
    company_meta = session.get("company_meta", {}) or {}

    # Meslek profili
    profession = ProfessionProfile(
        name=prof_dict.get("name", "unknown"),
        display_name=prof_dict.get("display_name", "Bilinmiyor"),
        keywords=prof_dict.get("keywords", []),
        technologies=prof_dict.get("technologies", []),
        description=prof_dict.get("description", "Meslek tespit edilemedi")
    )

    # Sistem promptu (company_meta ile)
    system_prompt = PromptGenerator.generate_system_prompt(profession, company_meta)

    company_snip = ""
    if company_meta:
        try:
            company_snip = f"\n**Şirket/Persona İpuçları:** {json.dumps(company_meta, ensure_ascii=False)}\n"
        except Exception:
            company_snip = ""

    # Konteks (LLM'e gidecek)
    context = f"""
**KULLANICI PROFİLİ**
Meslek: {profession.display_name}{' (LLM güven düşük — genel öneriler de ver)' if needs_manual else ''}
CV Yetenekleri: {', '.join(cv_skills[:10])}
İlan Yetenekleri: {', '.join(job_skills[:10])}
Eşleşen Yetenekler: {', '.join(matched_skills[:10])}
{company_snip}
**İŞ İLANI (kırpılmış):**
{job_description[:1500]}

**CV (kırpılmış):**
{cv_content[:1500]}

**SORU:**
{question}
""".strip()

    # ❗️Kritik: app context kapanmadan önce CONFIG ve LOGGER'ı capture et
    ollama_base   = app.config.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    ollama_model  = app.config.get("OLLAMA_MODEL", "qwen2.5:7b-instruct")
    ollama_timeout = int(app.config.get("OLLAMA_TIMEOUT", 60))
    log = app.logger  # Logger objesini kopyalamak güvenli

    def generate():
        # EventSource için reconnect süresi
        yield "retry: 10000\n\n"

        url = f"{ollama_base}/api/chat"
        payload = {
            "model": ollama_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": context},
            ],
            "stream": True,
            "options": {"temperature": 0.7, "top_p": 0.9, "max_tokens": 2000}
        }

        try:
            with requests.post(url, json=payload, stream=True, timeout=ollama_timeout) as r:
                r.raise_for_status()
                for raw in r.iter_lines(decode_unicode=True):
                    if not raw:
                        continue
                    try:
                        obj = json.loads(raw)
                    except Exception:
                        continue
                    yield f"data: {json.dumps(obj, ensure_ascii=False)}\n\n"
                    if obj.get("done"):
                        break

        except requests.exceptions.Timeout:
            yield _sse_pack({"error": "AI koç yanıt vermede gecikti (timeout). Lütfen tekrar deneyin.", "done": True})
        except requests.exceptions.ConnectionError:
            yield _sse_pack({"error": "Ollama bağlantısı kurulamadı. Servisin çalıştığını doğrulayın.", "done": True})
        except Exception as e:
            # current_app kullanmıyoruz; önceden alınan logger'ı kullanıyoruz
            try:
                log.exception("Chat streaming error")
            except Exception:
                logging.getLogger(__name__).exception("Chat streaming error (fallback logger)")
            yield _sse_pack({"error": f"Beklenmeyen hata: {str(e)}", "done": True})

        yield _sse_pack({"done": True})

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# ---------- Yardımcılar ----------
def _sse_pack(obj: dict) -> str:
    return f"data: {json.dumps(obj, ensure_ascii=False)}\n\n"
