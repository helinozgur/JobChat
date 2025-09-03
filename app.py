
import re
import json
import requests
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from flask import Flask, request, render_template, session, Response, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ============================================================================
# CONFIGURATION & SETUP
# ============================================================================

app = Flask(__name__)
app.secret_key = "ats-career-coach-v2-senior"
CORS(app)

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ollama configuration
OLLAMA_CONFIG = {
    "url": "http://localhost:11434/api/chat",
    "model": "qwen2.5:7b-instruct",
    "timeout": 60
}

# ============================================================================
# DATA MODELS & CONSTANTS
# ============================================================================

@dataclass
class AnalysisResult:
    """CV Analiz Sonucu Modeli"""
    similarity: float
    coverage: float
    score: float
    issues: List[str]
    missing: List[str]
    suggestions: List[str]
    sections: Dict[str, bool]

@dataclass
class ProfessionProfile:
    """Meslek Profil Modeli"""
    name: str
    display_name: str
    keywords: List[str]
    technologies: List[str]
    description: str

# Kapsamlı meslek profilleri
PROFESSION_PROFILES = {
    # Teknoloji Meslekleri
    "software_engineer": ProfessionProfile(
        name="software_engineer",
        display_name="Yazılım Mühendisi",
        keywords=["software engineer", "yazılım mühendisi", "software developer", "yazılım geliştirici"],
        technologies=[".net", "c#", "java", "python", "javascript", "react", "vue", "angular"],
        description="Yazılım geliştirme ve sistem tasarımı"
    ),
    
    "data_scientist": ProfessionProfile(
        name="data_scientist",
        display_name="Veri Bilimci",
        keywords=["data scientist", "veri bilimci", "machine learning", "data analyst", "ml engineer"],
        technologies=["python", "r", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn"],
        description="Veri analizi ve makine öğrenmesi"
    ),
    
    "devops_engineer": ProfessionProfile(
        name="devops_engineer",
        display_name="DevOps Mühendisi",
        keywords=["devops", "infrastructure", "cloud engineer", "site reliability", "platform engineer"],
        technologies=["docker", "kubernetes", "aws", "azure", "terraform", "jenkins", "git"],
        description="Altyapı ve deployment otomasyonu"
    ),
    
    "mobile_developer": ProfessionProfile(
        name="mobile_developer",
        display_name="Mobil Geliştirici",
        keywords=["mobile developer", "ios developer", "android developer", "flutter", "react native"],
        technologies=["swift", "kotlin", "flutter", "react native", "xamarin", "ionic"],
        description="Mobil uygulama geliştirme"
    ),
    
    "frontend_developer": ProfessionProfile(
        name="frontend_developer",
        display_name="Frontend Geliştirici",
        keywords=["frontend", "front-end", "ui developer", "react developer", "vue developer"],
        technologies=["html", "css", "javascript", "react", "vue", "angular", "typescript"],
        description="Kullanıcı arayüzü geliştirme"
    ),
    
    "backend_developer": ProfessionProfile(
        name="backend_developer",
        display_name="Backend Geliştirici",
        keywords=["backend", "back-end", "api developer", "server developer"],
        technologies=["node.js", ".net", "java", "python", "go", "rust", "postgresql", "mongodb"],
        description="Sunucu tarafı geliştirme"
    ),
    
    # İş ve Yönetim Meslekleri
    "project_manager": ProfessionProfile(
        name="project_manager",
        display_name="Proje Yöneticisi",
        keywords=["project manager", "proje yöneticisi", "scrum master", "product manager", "program manager"],
        technologies=["jira", "confluence", "ms project", "agile", "scrum", "kanban"],
        description="Proje planlama ve yönetim"
    ),
    
    "business_analyst": ProfessionProfile(
        name="business_analyst",
        display_name="İş Analisti",
        keywords=["business analyst", "iş analisti", "system analyst", "requirements analyst"],
        technologies=["sql", "excel", "power bi", "tableau", "visio", "sharepoint"],
        description="İş süreçleri analizi ve optimizasyon"
    ),
    
    "product_manager": ProfessionProfile(
        name="product_manager",
        display_name="Ürün Yöneticisi",
        keywords=["product manager", "ürün yöneticisi", "product owner", "ürün sahibi"],
        technologies=["analytics", "a/b testing", "figma", "miro", "mixpanel", "amplitude"],
        description="Ürün stratejisi ve geliştirme"
    ),
    
    # Tasarım Meslekleri
    "ui_ux_designer": ProfessionProfile(
        name="ui_ux_designer",
        display_name="UI/UX Tasarımcı",
        keywords=["ui designer", "ux designer", "product designer", "interaction designer"],
        technologies=["figma", "sketch", "adobe xd", "principle", "framer", "invision"],
        description="Kullanıcı deneyimi ve arayüz tasarımı"
    ),
    
    "graphic_designer": ProfessionProfile(
        name="graphic_designer",
        display_name="Grafik Tasarımcı",
        keywords=["graphic designer", "grafik tasarımcı", "visual designer", "brand designer"],
        technologies=["photoshop", "illustrator", "indesign", "after effects", "figma"],
        description="Görsel tasarım ve marka kimliği"
    ),
    
    # Pazarlama ve Satış
    "digital_marketer": ProfessionProfile(
        name="digital_marketer",
        display_name="Dijital Pazarlamacı",
        keywords=["digital marketing", "dijital pazarlama", "marketing specialist", "growth hacker"],
        technologies=["google ads", "facebook ads", "google analytics", "hubspot", "mailchimp"],
        description="Dijital pazarlama stratejileri"
    ),
    
    "sales_manager": ProfessionProfile(
        name="sales_manager",
        display_name="Satış Yöneticisi",
        keywords=["sales manager", "satış yöneticisi", "account manager", "business development"],
        technologies=["crm", "salesforce", "hubspot", "pipedrive", "excel"],
        description="Satış süreçleri ve müşteri ilişkileri"
    ),
    
    # Finans ve Muhasebe
    "financial_analyst": ProfessionProfile(
        name="financial_analyst",
        display_name="Finansal Analist",
        keywords=["financial analyst", "finansal analist", "finance manager", "investment analyst"],
        technologies=["excel", "bloomberg", "sap", "quickbooks", "tableau", "power bi"],
        description="Finansal analiz ve raporlama"
    ),
    
    "accountant": ProfessionProfile(
        name="accountant",
        display_name="Muhasebeci",
        keywords=["accountant", "muhasebeci", "bookkeeper", "mali müşavir"],
        technologies=["excel", "quickbooks", "sap", "logo", "eta", "nebim"],
        description="Muhasebe ve finansal kayıtlar"
    ),
    
    # İnsan Kaynakları
    "hr_specialist": ProfessionProfile(
        name="hr_specialist",
        display_name="İK Uzmanı",
        keywords=["hr specialist", "ik uzmanı", "human resources", "recruiter", "talent acquisition"],
        technologies=["workday", "bamboohr", "linkedin recruiter", "applicant tracking"],
        description="İnsan kaynakları ve yetenek yönetimi"
    ),
    
    # Genel/Diğer
    "consultant": ProfessionProfile(
        name="consultant",
        display_name="Danışman",
        keywords=["consultant", "danışman", "advisor", "specialist"],
        technologies=["excel", "powerpoint", "tableau", "sql"],
        description="Uzman danışmanlık hizmetleri"
    )
}

# Kapsamlı teknoloji ve yetenek listesi
TECHNOLOGY_SKILLS = {
    # Programming Languages
    "languages": [
        "C#", ".NET", "Java", "Python", "JavaScript", "TypeScript", "Go", "Rust",
        "PHP", "Ruby", "Swift", "Kotlin", "Dart", "C++", "C", "Scala", "R"
    ],
    
    # Web Technologies
    "web": [
        "React", "Vue.js", "Angular", "Node.js", "Express.js", "Next.js", "Nuxt.js",
        "ASP.NET Core", "ASP.NET MVC", "Spring Boot", "Django", "Flask", "FastAPI",
        "HTML5", "CSS3", "SASS", "LESS", "Bootstrap", "Tailwind CSS"
    ],
    
    # Mobile Technologies
    "mobile": [
        "Flutter", "React Native", "Xamarin", "Ionic", "Swift", "Kotlin",
        "Android Studio", "Xcode", "Firebase"
    ],
    
    # Databases
    "databases": [
        "SQL Server", "PostgreSQL", "MySQL", "MongoDB", "Redis", "ElasticSearch",
        "Oracle", "SQLite", "DynamoDB", "CosmosDB", "Neo4j", "Cassandra"
    ],
    
    # Cloud & Infrastructure
    "cloud": [
        "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Terraform",
        "Jenkins", "GitLab CI", "GitHub Actions", "Ansible", "Vagrant"
    ],
    
    # Data Science & AI
    "data_ai": [
        "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-learn", "Keras",
        "Apache Spark", "Hadoop", "Tableau", "Power BI", "Jupyter"
    ],
    
    # Tools & Others
    "tools": [
        "Git", "Jira", "Confluence", "Figma", "Adobe Creative Suite",
        "Visual Studio", "VS Code", "IntelliJ IDEA", "Postman", "Swagger"
    ]
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

class WebScraper:
    """Web scraping utilities"""
    
    @staticmethod
    def fetch_job_description(url: str) -> str:
        """İş ilanı içeriğini çeker"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, timeout=15, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Farklı site yapıları için selector'lar
            selectors = [
                "article", "main", "[role=main]", 
                ".job-description", ".jobsearch-JobComponent",
                ".content", "#job-description", ".job-detail"
            ]
            
            for selector in selectors:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(" ", strip=True)
                    if len(text) > 500:  # Minimum içerik kontrolü
                        return re.sub(r"\s+", " ", text)
            
            # Fallback: tüm sayfa içeriği
            return re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
            
        except Exception as e:
            logger.error(f"Web scraping error for {url}: {str(e)}")
            raise Exception(f"İş ilanı alınamadı: {str(e)}")

class PDFProcessor:
    """PDF işleme utilities"""
    
    @staticmethod
    def extract_text(file_bytes: bytes) -> str:
        """PDF'den metin çıkarır"""
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            texts = []
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text = page.get_text("text")
                if text.strip():
                    texts.append(text)
            
            doc.close()
            
            full_text = " ".join(texts)
            return re.sub(r"\s+", " ", full_text).strip()
            
        except Exception as e:
            logger.error(f"PDF processing error: {str(e)}")
            raise Exception(f"PDF işlenemedi: {str(e)}")

class ProfessionDetector:
    """Meslek tespit sistemi"""
    
    @staticmethod
    def detect_profession(cv_text: str) -> ProfessionProfile:
        """CV'den mesleği tespit eder"""
        cv_lower = cv_text.lower()
        
        # Skorlama sistemi
        profession_scores = {}
        
        for prof_key, profile in PROFESSION_PROFILES.items():
            score = 0
            
            # Keyword matching
            for keyword in profile.keywords:
                if keyword.lower() in cv_lower:
                    score += 10
            
            # Technology matching  
            for tech in profile.technologies:
                if tech.lower() in cv_lower:
                    score += 5
            
            # Title/header matching (higher weight)
            for keyword in profile.keywords:
                if re.search(rf'\b{re.escape(keyword.title())}\b', cv_text):
                    score += 15
            
            profession_scores[prof_key] = score
        
        # En yüksek skoru alan meslek
        if profession_scores:
            best_profession = max(profession_scores, key=profession_scores.get)
            if profession_scores[best_profession] > 0:
                return PROFESSION_PROFILES[best_profession]
        
        # Varsayılan: consultant (genel)
        return PROFESSION_PROFILES["consultant"]

class SkillExtractor:
    """Yetenek çıkarma sistemi"""
    
    @staticmethod
    def extract_skills(text: str) -> List[str]:
        """Metinden yetenekleri çıkarır"""
        text_lower = text.lower()
        found_skills = set()
        
        # Tüm kategorilerdeki yetenekleri kontrol et
        for category, skills in TECHNOLOGY_SKILLS.items():
            for skill in skills:
                if skill.lower() in text_lower:
                    found_skills.add(skill)
        
        # Özel pattern'ler için regex kontrolü
        special_patterns = {
            r"\.net\s*(\d+\.?\d*)?": ".NET",
            r"asp\.net\s*core": "ASP.NET Core", 
            r"entity\s*framework": "Entity Framework",
            r"sql\s*server": "SQL Server",
            r"visual\s*studio": "Visual Studio",
            r"react\s*native": "React Native",
            r"node\.?js": "Node.js",
            r"vue\.?js": "Vue.js"
        }
        
        for pattern, skill in special_patterns.items():
            if re.search(pattern, text_lower):
                found_skills.add(skill)
        
        return sorted(list(found_skills))

class CVAnalyzer:
    """CV analiz sistemi"""
    
    @staticmethod
    def check_sections(cv_text: str) -> Dict[str, bool]:
        """CV bölümlerini kontrol eder"""
        sections = {
            "Kişisel Bilgiler": bool(re.search(r"\b(kişisel|personal|contact|iletişim)\b", cv_text, re.I)),
            "Özet/Profil": bool(re.search(r"\b(özet|summary|profile|hakkında|about)\b", cv_text, re.I)),
            "Deneyim": bool(re.search(r"\b(deneyim|experience|work|career|iş)\b", cv_text, re.I)),
            "Eğitim": bool(re.search(r"\b(eğitim|education|university|üniversite|okul)\b", cv_text, re.I)),
            "Yetenekler": bool(re.search(r"\b(yetenekler|skills|teknoloji|competenc)\b", cv_text, re.I)),
            "Sertifikalar": bool(re.search(r"\b(sertifika|certificate|certification)\b", cv_text, re.I))
        }
        return sections
    
    @staticmethod
    def check_contact_info(cv_text: str) -> Tuple[bool, bool]:
        """İletişim bilgilerini kontrol eder"""
        phone_pattern = r"(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4,}"
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        
        has_phone = bool(re.search(phone_pattern, cv_text))
        has_email = bool(re.search(email_pattern, cv_text))
        
        return has_phone, has_email
    
    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """İki metin arasındaki benzerliği hesaplar"""
        try:
            vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2),
                lowercase=True
            )
            
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0, 0]
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Similarity calculation error: {str(e)}")
            return 0.0
    
    @classmethod
    def analyze_ats_score(cls, job_description: str, cv_text: str, job_skills: List[str]) -> AnalysisResult:
        """Comprehensive ATS analysis"""
        
        # Similarity calculation
        similarity = cls.calculate_similarity(job_description, cv_text)
        
        # Skill coverage calculation
        coverage = 0.0
        missing_skills = []
        if job_skills:
            cv_lower = cv_text.lower()
            matched_skills = [skill for skill in job_skills if skill.lower() in cv_lower]
            coverage = len(matched_skills) / len(job_skills)
            missing_skills = [skill for skill in job_skills if skill not in matched_skills]
        
        # Section completeness
        sections = cls.check_sections(cv_text)
        section_score = sum(sections.values()) / len(sections)
        
        # Contact information
        has_phone, has_email = cls.check_contact_info(cv_text)
        contact_score = (int(has_phone) + int(has_email)) / 2
        
        # Final ATS score calculation (weighted)
        ats_score = (
            0.40 * similarity +      # İçerik benzerliği
            0.35 * coverage +        # Yetenek kapsamı  
            0.15 * section_score +   # Bölüm tamamlığı
            0.10 * contact_score     # İletişim bilgileri
        ) * 100
        
        ats_score = max(0, min(100, round(ats_score, 1)))
        
        # Issue detection
        issues = []
        if not has_phone:
            issues.append("📞 Telefon numarası eksik")
        if not has_email:
            issues.append("📧 E-posta adresi eksik")
        
        missing_sections = [section for section, exists in sections.items() if not exists]
        if missing_sections:
            issues.append(f"📋 Eksik bölümler: {', '.join(missing_sections)}")
        
        cv_length = len(cv_text)
        if cv_length < 1000:
            issues.append("📄 CV çok kısa - detaylandırılması öneriliyor")
        elif cv_length > 8000:
            issues.append("📄 CV çok uzun - 2 sayfaya sıkıştırılması öneriliyor")
        
        # Suggestions
        suggestions = []
        if missing_skills:
            suggestions.append(f"🎯 Eksik yetenekleri CV'ye ekleyin: {', '.join(missing_skills[:5])}")
        
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

class PromptGenerator:
    """AI prompt üretici - Senior seviye"""
    
    @staticmethod
    def generate_system_prompt(profession: ProfessionProfile, cv_skills: List[str], job_skills: List[str]) -> str:
        """Mesleğe özel sistem prompt'u oluşturur"""
        
        # Ana meslek tanımı
        base_prompts = {
            "software_engineer": "Sen senior yazılım mimarisi ve geliştirme uzmanısın.",
            "data_scientist": "Sen senior veri bilimi ve ML engineering uzmanısın.", 
            "devops_engineer": "Sen senior cloud infrastructure ve DevOps uzmanısın.",
            "project_manager": "Sen senior proje yönetimi ve Agile coaching uzmanısın.",
            "ui_ux_designer": "Sen senior product design ve user experience uzmanısın.",
            "business_analyst": "Sen senior business analysis ve process optimization uzmanısın.",
            "digital_marketer": "Sen senior digital marketing ve growth hacking uzmanısın.",
            "financial_analyst": "Sen senior financial modeling ve investment analysis uzmanısın."
        }
        
        profession_prompt = base_prompts.get(
            profession.name, 
            f"Sen senior {profession.display_name} uzmanısın."
        )
        
        # Teknoloji analizi
        tech_focus = "genel teknolojiler"
        if cv_skills:
            if any(skill in cv_skills for skill in [".NET", "C#", "ASP.NET"]):
                tech_focus = "Microsoft .NET ekosistemi"
            elif any(skill in cv_skills for skill in ["Python", "Django", "Flask"]):
                tech_focus = "Python ve veri teknolojileri"
            elif any(skill in cv_skills for skill in ["React", "Vue.js", "Angular"]):
                tech_focus = "Modern frontend teknolojileri"
            elif any(skill in cv_skills for skill in ["AWS", "Azure", "Docker"]):
                tech_focus = "Cloud ve konteyner teknolojileri"
        
        # Kapsamlı sistem prompt'u
        system_prompt = f"""{profession_prompt}

🎯 **Uzmanlık Alanın**: {profession.description}
💻 **Teknoloji Odağı**: {tech_focus}
📊 **Yaklaşımın**: Senior-level, praktik odaklı, ölçülebilir sonuçlar

**Görevin:**
1. Kullanıcının mesleki gelişimi için stratejik öneriler sun
2. CV'sini ATS sistemleri için optimize et  
3. Her öneride somut metrikler ve sonuçlar belirt
4. Industry best practices'leri paylaş
5. Senior-level perspektiften değerlendirmeler yap

**Format Kuralları:**
- Her proje önerisi: 1-2 cümle açıklama + teknoloji stack + 2-3 ölçülebilir başarı metriği
- ATS-friendly keywords kullan
- Action verb'lerle güçlü ifadeler oluştur
- Sayısal değerler ve % oranları ekle
- Senior düzey sorumlulukları vurgula

**Örnek Metrik Formatı:**
• "Performance %40 iyileştirdi"
• "$50K cost reduction sağladı" 
• "Team'de 5 developer'ı mentor'ladı"
• "95% test coverage ulaştı"

Kısa, net ve etkili yanıtlar ver. Her tavsiye actionable olsun."""

        return system_prompt

# ============================================================================
# API ROUTES
# ============================================================================

@app.route("/")
def index():
    """Ana sayfa"""
    return render_template("index.html")

@app.route("/api/analyze", methods=["POST"])
def analyze_cv():
    """CV ve iş ilanı analizi - Senior-level implementation"""
    try:
        # Input validation
        job_url = request.form.get("job_url", "").strip()
        file = request.files.get("cv")
        
        if not job_url:
            return jsonify({"error": "İş ilanı URL'si gerekli"}), 400
            
        if not file or not file.filename.lower().endswith(".pdf"):
            return jsonify({"error": "Geçerli bir PDF CV dosyası gerekli"}), 400

        logger.info(f"Analysis started for URL: {job_url}")
        
        # Web scraping
        try:
            job_description = WebScraper.fetch_job_description(job_url)
            logger.info(f"Job description fetched: {len(job_description)} characters")
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        
        # PDF processing
        try:
            cv_content = PDFProcessor.extract_text(file.read())
            logger.info(f"CV processed: {len(cv_content)} characters")
            
            if not cv_content.strip():
                return jsonify({"error": "CV'den metin çıkarılamadı. PDF'in düzgün formatlandığından emin olun."}), 400
                
        except Exception as e:
            return jsonify({"error": str(e)}), 400
        
        # Analysis pipeline
        profession = ProfessionDetector.detect_profession(cv_content)
        job_skills = SkillExtractor.extract_skills(job_description)
        cv_skills = SkillExtractor.extract_skills(cv_content)
        analysis_result = CVAnalyzer.analyze_ats_score(job_description, cv_content, job_skills)
        
        # Session storage for chat
        session.update({
            "job_description": job_description[:4000],
            "cv_content": cv_content[:4000], 
            "profession": profession.name,
            "profession_display": profession.display_name,
            "cv_skills": cv_skills[:25],
            "job_skills": job_skills[:25]
        })
        
        logger.info(f"Analysis completed - Profession: {profession.display_name}, Score: {analysis_result.score}")
        
        # Response
        return jsonify({
            "success": True,
            "analysis": {
                "score": analysis_result.score,
                "similarity": round(analysis_result.similarity, 3),
                "coverage": round(analysis_result.coverage, 3),
                "missing": analysis_result.missing[:10],  # İlk 10 eksik yetenek
                "issues": analysis_result.issues,
                "suggestions": analysis_result.suggestions,
                "sections": analysis_result.sections
            },
            "profession": {
                "name": profession.name,
                "display_name": profession.display_name,
                "description": profession.description
            },
            "skills": {
                "job_skills": job_skills[:15],
                "cv_skills": cv_skills[:15],
                "matched_skills": list(set(job_skills) & set(cv_skills))
            },
            "cv_preview": cv_content[:800]
        })
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({"error": f"Analiz hatası: {str(e)}"}), 500

@app.route("/api/chat")
def chat_stream():
    """Senior-level AI coaching with streaming"""
    
    question = request.args.get("question", "").strip()
    if not question:
        return jsonify({"error": "Soru boş olamaz"}), 400
    
    # Session data
    job_description = session.get("job_description", "")
    cv_content = session.get("cv_content", "")
    profession_name = session.get("profession", "consultant")
    cv_skills = session.get("cv_skills", [])
    job_skills = session.get("job_skills", [])
    
    if not cv_content:
        return jsonify({"error": "Önce CV analizini yapın"}), 400
    
    # Profession profile
    profession = PROFESSION_PROFILES.get(profession_name, PROFESSION_PROFILES["consultant"])
    
    # System prompt generation
    system_prompt = PromptGenerator.generate_system_prompt(profession, cv_skills, job_skills)
    
    # Context building
    context = f"""
**KULLANICI PROFİLİ:**
Meslek: {profession.display_name}
CV Yetenekleri: {', '.join(cv_skills[:10])}
İlan Yetenekleri: {', '.join(job_skills[:10])}

**İŞ İLANI ÖZETİ:**
{job_description[:1500]}

**CV ÖZETİ:**  
{cv_content[:1500]}

**KULLANICI SORUSU:**
{question}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": context}
    ]
    
    logger.info(f"Chat request - Question: {question[:50]}..., Profession: {profession.display_name}")
    
    def generate_chat_response():
        """Ollama streaming response generator"""
        try:
            with requests.post(
                OLLAMA_CONFIG["url"],
                json={
                    "model": OLLAMA_CONFIG["model"],
                    "stream": True,
                    "messages": messages,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 2000
                    }
                },
                stream=True,
                timeout=OLLAMA_CONFIG["timeout"]
            ) as response:
                
                response.raise_for_status()
                
                for line in response.iter_lines(decode_unicode=True):
                    if not line.strip():
                        continue
                        
                    try:
                        data = json.loads(line)
                        yield f"data: {line}\n\n"
                        
                        if data.get("done"):
                            break
                            
                    except json.JSONDecodeError:
                        continue
                
                yield f"data: {json.dumps({'done': True})}\n\n"
                
        except requests.exceptions.Timeout:
            error_msg = json.dumps({"error": "AI koç yanıt vermede gecikti, lütfen tekrar deneyin"})
            yield f"data: {error_msg}\n\n"
            
        except requests.exceptions.ConnectionError:
            error_msg = json.dumps({"error": "Ollama bağlantısı kurulamadı. Lütfen Ollama servisinin çalıştığından emin olun"})
            yield f"data: {error_msg}\n\n"
            
        except Exception as e:
            logger.error(f"Chat streaming error: {str(e)}")
            error_msg = json.dumps({"error": f"Beklenmeyen hata: {str(e)}"})
            yield f"data: {error_msg}\n\n"

    return Response(
        generate_chat_response(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Nginx için
        }
    )

@app.route("/api/status")
def get_status():
    """API status and session info"""
    return jsonify({
        "status": "healthy",
        "version": "2.0.0-senior",
        "has_session": bool(session.get("cv_content")),
        "profession": session.get("profession_display", "Belirlenmedi"),
        "ollama_configured": bool(OLLAMA_CONFIG["url"]),
        "supported_professions": len(PROFESSION_PROFILES)
    })

@app.route("/api/professions")
def get_professions():
    """Desteklenen mesleklerin listesi"""
    professions = []
    
    for prof_key, profile in PROFESSION_PROFILES.items():
        professions.append({
            "key": prof_key,
            "name": profile.display_name,
            "description": profile.description,
            "sample_technologies": profile.technologies[:5]
        })
    
    return jsonify({
        "professions": sorted(professions, key=lambda x: x["name"]),
        "total_count": len(professions)
    })

@app.route("/api/skills")
def get_skills():
    """Teknoloji yetenek kategorileri"""
    return jsonify({
        "categories": TECHNOLOGY_SKILLS,
        "total_skills": sum(len(skills) for skills in TECHNOLOGY_SKILLS.values())
    })

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint bulunamadı"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Sunucu hatası"}), 500

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({"error": "Dosya çok büyük. Maksimum 10MB"}), 413

# ============================================================================
# MAIN APPLICATION
# ============================================================================

if __name__ == "__main__":
    # Production-ready configuration
    import os
    
    # Environment variables
    port = int(os.environ.get("PORT", 8001))
    debug = os.environ.get("FLASK_ENV") == "development"
    
    # File upload limits
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB
    
    logger.info("🚀 ATS Career Coach v2.0 - Senior Edition")
    logger.info(f"📊 {len(PROFESSION_PROFILES)} professions supported")
    logger.info(f"🛠️ {sum(len(skills) for skills in TECHNOLOGY_SKILLS.values())} skills in database")
    logger.info(f"🤖 Ollama: {OLLAMA_CONFIG['url']} - Model: {OLLAMA_CONFIG['model']}")
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug,
        threaded=True
    )