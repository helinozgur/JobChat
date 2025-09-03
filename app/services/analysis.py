import re
from typing import Dict, List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ..models import AnalysisResult

class CVAnalyzer:
    @staticmethod
    def check_sections(cv_text: str) -> Dict[str, bool]:
        return {
            "Kişisel Bilgiler": bool(re.search(r"\b(kişisel|personal|contact|iletişim)\b", cv_text, re.I)),
            "Özet/Profil":     bool(re.search(r"\b(özet|summary|profile|hakkında|about)\b", cv_text, re.I)),
            "Deneyim":         bool(re.search(r"\b(deneyim|experience|work|career|iş)\b", cv_text, re.I)),
            "Eğitim":          bool(re.search(r"\b(eğitim|education|university|üniversite|okul)\b", cv_text, re.I)),
            "Yetenekler":      bool(re.search(r"\b(yetenekler|skills|teknoloji|competenc)\b", cv_text, re.I)),
            "Sertifikalar":    bool(re.search(r"\b(sertifika|certificate|certification)\b", cv_text, re.I))
        }

    @staticmethod
    def check_contact_info(cv_text: str) -> Tuple[bool, bool]:
        phone_pattern = r"(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4,}"
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        return bool(re.search(phone_pattern, cv_text)), bool(re.search(email_pattern, cv_text))

    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        try:
            vec = TfidfVectorizer(max_features=20000, ngram_range=(1,2), lowercase=True)
            tfidf = vec.fit_transform([text1, text2])
            return float(cosine_similarity(tfidf[0:1], tfidf[1:2])[0, 0])
        except Exception:
            return 0.0

    @classmethod
    def analyze_ats_score(
        cls,
        job_description: str,
        cv_text: str,
        job_skills: List[str],
        matched_skills: Optional[List[str]] = None,
        missing_skills_input: Optional[List[str]] = None
    ) -> AnalysisResult:
        similarity = cls.calculate_similarity(job_description, cv_text)

        if matched_skills is not None and missing_skills_input is not None and job_skills:
            coverage = len(matched_skills) / max(1, len(job_skills))
            missing_skills = missing_skills_input
        else:
            # naive fallback
            coverage = 0.0
            missing_skills = []
            if job_skills:
                cv_lower = cv_text.lower()
                matched = [s for s in job_skills if s.lower() in cv_lower]
                coverage = len(matched) / len(job_skills)
                missing_skills = [s for s in job_skills if s not in matched]

        sections = cls.check_sections(cv_text)
        section_score = sum(sections.values()) / len(sections)
        has_phone, has_email = cls.check_contact_info(cv_text)
        contact_score = (int(has_phone) + int(has_email)) / 2

        ats_score = (0.40*similarity + 0.35*coverage + 0.15*section_score + 0.10*contact_score) * 100
        ats_score = max(0, min(100, round(ats_score, 1)))

        issues = []
        if not has_phone: issues.append("📞 Telefon numarası eksik")
        if not has_email: issues.append("📧 E-posta adresi eksik")
        missing_sections = [k for k,v in sections.items() if not v]
        if missing_sections: issues.append(f"📋 Eksik bölümler: {', '.join(missing_sections)}")

        cv_length = len(cv_text)
        if cv_length < 1000: issues.append("📄 CV çok kısa - detaylandırılması öneriliyor")
        elif cv_length > 8000: issues.append("📄 CV çok uzun - 2 sayfaya sıkıştırılması öneriliyor")

        suggestions = []
        if missing_skills: suggestions.append(f"🎯 Eksik yetenekleri CV'ye ekleyin: {', '.join(missing_skills[:5])}")
        suggestions.extend([
            "📊 Başarıları rakamlarla destekleyin (% artış, $ tasarruf, proje sayısı)",
            "🔧 Action verb'lerle başlayan güçlü cümleler kullanın",
            "📈 Son 10 yıllık deneyime odaklanın",
            "🎯 Her pozisyon için CV'yi özelleştirin"
        ])

        return AnalysisResult(
            similarity=similarity,
            coverage=coverage,
            score=ats_score,
            issues=issues,
            missing=missing_skills,
            suggestions=suggestions,
            sections=sections
        )
