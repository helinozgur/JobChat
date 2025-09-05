# app/routes/analyze.py
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
    s = re.sub(r"[\s\-_/]+", " ", s)
    s = s.replace("’", "'").replace("`", "'")
    s = s.replace(". net", ".net")
    return s

def _coerce_extract_result(x):
    """
    SkillExtractor.extract bazen list, bazen dict dönebilir.
    Her durumda şu şemaya indir:
    {"skills": [...], "alias_map": {...}, "noise": [...]}
    """
    if isinstance(x, dict):
        skills = x.get("skills") or []
        alias_map = x.get("alias_map") or {}
        noise = x.get("noise") or []
    elif isinstance(x, list):
        skills, alias_map, noise = x, {}, []
    else:
        skills, alias_map, noise = [], {}, []

    # uniq + trim (normalize ederek benzersizleştir)
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
    LLM hizalama başarısız olursa devreye giren basit eşleme.
    Normalizasyon üzerine set kesişimi/diff.
    """
    j_norm = { _normalize_token(s): s for s in job_skills }
    c_norm = { _normalize_token(s): s for s in cv_skills }

    matched_norm = set(j_norm) & set(c_norm)
    missing_norm = set(j_norm) - set(c_norm)

    matched = [j_norm[n] for n in sorted(matched_norm)]
    missing = [j_norm[n] for n in sorted(missing_norm)]

    return {
        "matched": matched,
        "missing": missing,
        "job_canon": list(j_norm.values()),
        "cv_canon": list(c_norm.values()),
    }

def _final_consistency(job_canon, cv_canon, matched, missing):
    """
    LLM'den gelen matched/missing listelerini normalize ederek yeniden üret
    ve çakışma varsa düzelt (aynı skill hem matched hem missing olmayacak).
    """
    j_norm = { _normalize_token(s): s for s in job_canon }
    c_norm = { _normalize_token(s): s for s in cv_canon }

    matched_norm = set(j_norm) & set(c_norm)
    # missing = job - cv
    missing_norm = set(j_norm) - set(c_norm)

    matched_fixed = [j_norm[n] for n in sorted(matched_norm)]
    missing_fixed = [j_norm[n] for n in sorted(missing_norm)]

    return matched_fixed, missing_fixed

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

        # --- veri çıkar ---
        job_description = WebScraper.fetch_job_description(job_url)
        cv_content = PDFProcessor.extract_text(file.read())
        if not cv_content.strip():
            return jsonify({"error": "CV'den metin çıkarılamadı. PDF formatını kontrol edin."}), 400

        # Şirket/persona (opsiyonel)
        try:
            company_meta = CompanyExtractor.parse(job_description) or {}
        except Exception:
            company_meta = {}

        # Meslek tespiti
        profession, conf = ProfessionDetector.detect(cv_content)
        needs_manual = conf < app.config["PROF_CONF_THRESHOLD"] or profession.name == "unknown"
        app.logger.info(f"[ProfessionDetector] {profession.display_name} (conf={conf:.2f})")

        # Yetenek çıkar (LLM) -> dict'e zorla
        job_raw = SkillExtractor.extract(job_description)
        cv_raw  = SkillExtractor.extract(cv_content)
        job_ex  = _coerce_extract_result(job_raw)
        cv_ex   = _coerce_extract_result(cv_raw)

        # Hizalama (LLM -> fallback)
        try:
            alignment = SkillAligner.align(job_ex["skills"], cv_ex["skills"])
        except Exception:
            alignment = _simple_align(job_ex["skills"], cv_ex["skills"])

        job_canon = alignment.get("job_canon") or job_ex["skills"]
        cv_canon  = alignment.get("cv_canon")  or cv_ex["skills"]
        matched   = alignment.get("matched")   or []
        missing   = alignment.get("missing")   or []

        # 🔒 Son tutarlılık düzeltmesi: normalize kesişim/fark
        matched, missing = _final_consistency(job_canon, cv_canon, matched, missing)

        coverage = (len(matched) / max(1, len(job_canon))) if job_canon else 0.0

        # ATS skor (hizalanmış listelerle)
        analysis = CVAnalyzer.analyze_ats_score(
            job_description=job_description,
            cv_text=cv_content,
            job_skills=job_canon,
            matched_skills=matched,
            missing_skills_input=missing
        )

        # Cookie session limiti için kırp
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
