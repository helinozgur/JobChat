from typing import Dict
from .llm_client import LLMClient
from ..utils import extract_json

class CompanyExtractor:
    @staticmethod
    def parse(job_text: str) -> Dict[str, str]:
        system = "You extract company metadata from job ads. Respond with JSON only."
        user = f"""
From the job ad text, extract company metadata. If unknown, set null.

Schema:
{{
  "company": "string|null",
  "role_title": "string|null",
  "industry": "string|null",
  "location": "string|null"
}}

TEXT:
{job_text[:4000]}
"""
        content = LLMClient.chat(
            [{"role":"system","content":system},{"role":"user","content":user}],
            options={"temperature":0.0}
        )
        obj = extract_json(content)
        return {
            "company": obj.get("company"),
            "role_title": obj.get("role_title"),
            "industry": obj.get("industry"),
            "location": obj.get("location"),
        }
