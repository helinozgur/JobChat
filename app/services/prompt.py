from ..models import ProfessionProfile

class PromptGenerator:
    @staticmethod
    def generate_system_prompt(profession: ProfessionProfile, company_meta: dict) -> str:
        company = company_meta.get("company") or "the company"
        role = company_meta.get("role_title") or profession.display_name or "the role"
        industry = company_meta.get("industry") or ""
        loc = company_meta.get("location") or ""
        ctx = f"{company} hiring for \"{role}\""
        if industry or loc:
            ctx += f" ({industry} {loc})".strip()
        return f"""Act as a senior in-house recruiter / HR business partner for {ctx}.
Your goals: evaluate the candidate against the job ad, optimize their resume for ATS, and provide precise, measurable, role-specific advice.

Constraints:
- Stay strictly grounded to the job ad and the candidate's CV. Do not assume internal policies you were not told.
- Prefer concise, ATS-friendly phrasing and quantified achievements.
- Use bullet points; include concrete metrics (% improvement, $ saved, time reduced).
- If unknown, say it's unknown rather than guessing.
"""
