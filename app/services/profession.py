from typing import Tuple, Optional
from ..models import ProfessionProfile
from .llm_client import LLMClient
from ..utils import extract_json
from flask import current_app as app

class ProfessionDetector:
    """
    Tamamen LLM tabanlı meslek tespiti. Confidence döndürür.
    Eşik altıysa UI manuel girişi ister.
    """
    @staticmethod
    def detect(cv_text: str) -> Tuple[Optional[ProfessionProfile], float]:
        system = "ATS/HR uzmanısın. CV’den birincil mesleği çıkar. Sadece geçerli JSON döndür."
        user = f"""
CV'den meslek/profesyonu çıkar ve JSON ver.

Şema:
{{
  "name": "kebab-case key (örn: 'tile-setter', 'chief-financial-officer')",
  "display_name": "Doğal meslek adı",
  "description": "1 cümle özet",
  "keywords": ["terim1","terim2"],
  "technologies": ["araç/teknoloji/alan terimleri"],
  "seniority": "intern|junior|mid|senior|lead",
  "confidence": 0.0-1.0
}}

CV (first 4000 chars):
{cv_text[:4000]}
"""
        content = LLMClient.chat(
            [{"role":"system","content":system},{"role":"user","content":user}],
            options={"temperature":0.1, "top_p":0.9}
        )
        obj = extract_json(content)
        conf = float(obj.get("confidence", 0.0) or 0.0)
        prof = ProfessionProfile(
            name=obj.get("name") or "unknown",
            display_name=obj.get("display_name") or "Bilinmiyor",
            keywords=obj.get("keywords") or [],
            technologies=obj.get("technologies") or [],
            description=obj.get("description") or "Meslek tespit edilemedi"
        )
        app.logger.info(f"[ProfessionDetector] {prof.display_name} (conf={conf:.2f})")
        return prof, conf
