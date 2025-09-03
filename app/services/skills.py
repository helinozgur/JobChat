# app/services/skills.py
import logging
import re
from .llm_client import LLMClient
from ..utils import extract_json, normalize_token  # varsa; yoksa analyze içindeki util'i buraya taşıyın

log = logging.getLogger(__name__)

# Çok genel kısaltmalar (meslek bağımsız)
ALIASES = {
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "cv": "computer vision",
    "nlp": "natural language processing",
    "dl": "deep learning",
    "pm": "project management",
    "hr": "human resources",
    "qa": "quality assurance",
    "js": "javascript",
    "ts": "typescript",
    "nodejs": "node.js",
    "node": "node.js",
    "c sharp": "c#",
    ". net": ".net",
}

def canon(s: str) -> str:
    t = normalize_token(s)
    t = re.sub(r"[^a-z0-9#+. ]+", " ", t).strip()
    return ALIASES.get(t, t)

class SkillExtractor:
    @staticmethod
    def extract(text: str) -> list[str]:
        system = "You extract concise professional skills/technologies from text. Return STRICT JSON."
        user = f'''
Return only JSON: {{"skills": ["..."], "confidence": 0.0-1.0}}
TEXT:
{text[:2500]}
'''
        content = LLMClient.chat(
            [{"role":"system","content":system}, {"role":"user","content":user}],
            options={"temperature":0.0},
            timeout=90,
            format_json=True
        )
        obj = extract_json(content)
        skills = obj.get("skills") or []
        # uniq + sıralı
        seen, out = set(), []
        for s in skills:
            k = canon(s)
            if k and k not in seen:
                seen.add(k)
                out.append(s.strip())
        return out

class SkillAligner:
    @staticmethod
    def _fallback(job_skills: list[str], cv_skills: list[str]) -> dict:
        job_map = {canon(s): s for s in job_skills}
        cv_map  = {canon(s): s for s in cv_skills}
        matched_norm = job_map.keys() & cv_map.keys()
        missing_norm = job_map.keys() - matched_norm
        return {
            "matched": [job_map[k] for k in matched_norm],
            "missing": [job_map[k] for k in missing_norm],
            "deduped_cv": [cv_map[k] for k in cv_map.keys()],
        }

    @staticmethod
    def align(job_skills: list[str], cv_skills: list[str]) -> dict:
        # Önce hızlı deterministik normalizasyon (zaten çoğu işi çözer)
        base = SkillAligner._fallback(job_skills, cv_skills)
        # LLM ile ince düzeltme (zaman aşımında base’e döner)
        try:
            system = "You canonicalize/merge equivalent skill names and map overlaps. Return STRICT JSON only."
            user = f"""
Return JSON:
{{
  "matched": ["..."],      // items from job_skills that exist in cv_skills (after canonicalization)
  "missing": ["..."],      // items from job_skills not present in cv_skills
  "deduped_cv": ["..."]    // cv_skills without near-duplicates
}}
JOB_SKILLS: {job_skills[:50]}
CV_SKILLS: {cv_skills[:80]}
"""
            content = LLMClient.chat(
                [{"role":"system","content":system}, {"role":"user","content":user}],
                options={"temperature":0.0},
                timeout=90,
                format_json=True
            )
            obj = extract_json(content)
            # emniyetli birleşim: LLM çıktısı + base
            result = {
                "matched": obj.get("matched") or base["matched"],
                "missing": obj.get("missing") or base["missing"],
                "deduped_cv": obj.get("deduped_cv") or base["deduped_cv"],
            }
            return result
        except Exception as e:
            log.warning("SkillAligner LLM timeout/fail; using fallback. %s", e)
            return base
