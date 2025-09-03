from flask import Blueprint, request, jsonify, session, current_app as app
from ..services.scraper import WebScraper
from ..services.pdf_processor import PDFProcessor
from ..services.profession import ProfessionDetector
from ..services.skills import SkillExtractor, SkillAligner
from ..services.company import CompanyExtractor
from ..services.analysis import CVAnalyzer
import re

bp = Blueprint("analyze", __name__)

# ---------------- helpers ----------------
def _normalize_token(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[\s\-_]+", " ", s)
    s = s.replace("’","'").replace("`","'")
    s = s.replace(". net", ".net")
    return s

def _coerce_extract_result(x):
    """
    SkillExtractor.extract bazen list, bazen dict dönebilir.
    Burada tek forma indiriyoruz: {"skills": [...], "alias_map": {...}, "noise": [...]}
    """
    if isinstance(x, dict):
        skills = x.get("skills") or []
        alias_map = x.get("alias_map") or {}
        noise = x.get("noise") or []
    elif isinstance(x, list):
        skills, alias_map, noise = x, {}, []
    else:
        skills, alias_map, noise = [], {}, []

    # uniq + trim
    seen, out = set(), []
    for s in skills:
        t = str(s).strip()
        n = _normalize_token(t)
        if n and n not in seen:
            seen.add(n)
            out.append(t)
    return {"skills": out, "alias_map": alias_map, "noise": noise}

def _simple_align(job_skills, cv_skills):
    """
    LLM çökerse/timeout olursa devreye giren basit eşleme.
    Sadece normalizasyon bazlı eşleme yapar.
    """
    j_norm = { _normalize_token(s): s for s in job_skills }
    c_norm = { _normalize_token(s): s for s in cv_skills }

    matched_norm = sorted(set(j_norm.keys()) & set(c_norm.keys()))
    matched = [j_norm[n] for n in matched_norm]
    missing_norm = sorted(k for k in j_norm.keys() if k not in c_norm)
    missing = [j_norm[n] for n in missing_norm]

    return {
        "matched": matched,
        "missing": missing,
        "job_canon": list(j_norm.values()),
        "cv_canon": list(c_norm.values()),
    }

# --------------- route -------------------
@bp.route("/api/analyze", methods=["POST"])
def analyze_cv():
    try:
        job_url = request.form.get("job_url", "").strip()
        file = request.files.get("cv")

        if not job_url:
            return jsonify({"error": "İş ilanı URL'si gerekli"}), 400
        if not file or not file.filename.lower().endswith(".pdf"):
            return jsonify({"error": "Geçerli bir PDF CV dosyası gerekli"}), 400

        app.logger.info(f"[Analyze] URL: {job_url}")

        job_description = WebScraper.fetch_job_description(job_url)
        cv_content = PDFProcessor.extract_text(file.read())
        if not cv_content.strip():
            return jsonify({"error": "CV'den metin çıkarılamadı. PDF formatını kontrol edin."}), 400

        # Şirket/persone
        company_meta = {}
        try:
            company_meta = CompanyExtractor.parse(job_description)
        except Exception as _:
            company_meta = {}

        # Meslek
        profession, conf = ProfessionDetector.detect(cv_content)
        needs_manual = conf < app.config["PROF_CONF_THRESHOLD"] or profession.name == "unknown"
        app.logger.info(f"[ProfessionDetector] {profession.display_name} (conf={conf:.2f})")

        # Yetenek çıkarımı (LLM) -> dict forma zorla
        job_raw = SkillExtractor.extract(job_description)
        cv_raw  = SkillExtractor.extract(cv_content)
        job_ex  = _coerce_extract_result(job_raw)
        cv_ex   = _coerce_extract_result(cv_raw)

        # Hizalama (LLM, başarısızsa basit fallback)
        try:
            alignment = SkillAligner.align(job_ex["skills"], cv_ex["skills"])
        except Exception as _:
            alignment = _simple_align(job_ex["skills"], cv_ex["skills"])

        matched = alignment.get("matched", [])
        missing = alignment.get("missing", [])
        job_canon = alignment.get("job_canon", job_ex["skills"])
        cv_canon  = alignment.get("cv_canon",  cv_ex["skills"])
        coverage = (len(matched) / max(1, len(job_canon))) if job_canon else 0.0

        # ATS
        analysis = CVAnalyzer.analyze_ats_score(
            job_description=job_description,
            cv_text=cv_content,
            job_skills=job_canon,
            matched_skills=matched,
            missing_skills_input=missing
        )

        # Cookie session 4KB limitine takılmamak için metinleri kısaltalım
        JOB_SNIPPET = 1200
        CV_SNIPPET  = 1200

        session.update({
            "job_description": job_description[:JOB_SNIPPET],
            "cv_content": cv_content[:CV_SNIPPET],
            "company_meta": company_meta,
            "profession_obj": {
                "name": profession.name,
                "display_name": profession.display_name,
                "description": profession.description,
                "keywords": profession.keywords,
                "technologies": profession.technologies,
                "confidence": float(conf)
            },
            "needs_manual_profession": bool(needs_manual),
            "cv_skills": cv_canon[:25],
            "job_skills": job_canon[:25],
            "matched_skills": matched[:25],
            "missing_skills": missing[:25],
        })

        app.logger.info(
            f"[Analyze] Profession={profession.display_name} (conf={conf:.2f}) "
            f"manual={needs_manual} ATS={analysis.score}"
        )

        return jsonify({
            "success": True,
            "profession_detection": {
                "needs_manual_input": needs_manual,
                "confidence": round(conf, 3),
                "required_fields": ["name", "display_name", "description"] if needs_manual else []
            },
            "company": company_meta,
            "profession": {
                "name": profession.name,
                "display_name": profession.display_name,
                "description": profession.description
            },
            "analysis": {
                "score": analysis.score,
                "similarity": round(analysis.similarity, 3),
                "coverage": round(coverage, 3),
                "missing": missing[:10],
                "issues": analysis.issues,
                "suggestions": analysis.suggestions,
                "sections": analysis.sections
            },
            "skills": {
                "job_skills": job_canon[:15],
                "cv_skills": cv_canon[:15],
                "matched_skills": matched[:15],
                "alias_maps": {
                    "job_alias_map": job_ex.get("alias_map", {}),
                    "cv_alias_map": cv_ex.get("alias_map", {}),
                },
                "noise": {
                    "job_noise": job_ex.get("noise", []),
                    "cv_noise": cv_ex.get("noise", []),
                }
            },
            "cv_preview": cv_content[:800]
        })

    except Exception as e:
        app.logger.exception("Analysis error")
        return jsonify({"error": f"Analiz hatası: {str(e)}"}), 500
