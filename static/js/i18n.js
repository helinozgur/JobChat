// static/js/i18n.js
(() => {
  const dict = {
    tr: {
      "title.app": "ATS Kontrol + AI Kariyer Koçu",
      "label.language": "Dil",
      "lead.text": "CV'nizi iş ilanlarına göre optimize edin ve AI koçunuzdan kişiselleştirilmiş kariyer tavsiyeleri alın.",
      "label.jobUrl": "İş İlanı URL'si",
      "form.jobUrl_ph": "https://...",
      "hint.pasteLink": "LinkedIn, Kariyer.net, Indeed vb. ilan linkini yapıştırın",
      "label.cvFile": "CV Dosyası (PDF)",
      "btn.analyze": "📊 Analiz Et",

      "section.ats": "📈 ATS Skoru",
      "score.overall": "Genel Skor",
      "score.detected": "Tespit Edilen Meslek",
      "score.similarity": "Benzerlik",
      "score.coverage": "Kapsama",

      "section.skills": "🎯 Yetenek Boşluk Analizi",
      "skills.yours": "✅ CV'deki Yetenekler",
      "skills.matched": "🎯 Eşleşen Yetenekler",
      "skills.missing": "❌ Eksik Yetenekler (Öncelikli)",
      "skills.jobReq": "İlanın İstediği Yetenekler:",

      "section.report": "⚡ Profesyonel Optimizasyon Raporu",
      "resume.preview": "📋 CV Önizleme (İlk 800 karakter)",

      "section.coach": "🤖 AI Kariyer Koçu",
      "coach.lead": "Kişiselleştirilmiş kariyer önerileri. Mesleğiniz CV'nizden otomatik algılanır ve öneriler buna göre özelleştirilir.",
      "coach.examples.project": "Proje Fikirleri",
      "coach.examples.optimize": "CV Optimizasyonu",
      "coach.examples.skills": "Beceri Geliştirme",
      "coach.examples.interview": "Mülakat Hazırlığı",
      "coach.examples.path": "Kariyer Yolu",
      "coach.examples.projectQ": "Bu role uygun CV'me hangi projeleri eklemeliyim?",
      "coach.examples.optimizeQ": "Bu ilana göre CV'mi nasıl optimize edebilirim?",
      "coach.examples.skillsQ": "Kariyerimde ilerlemek için hangi becerileri geliştirmeliyim?",
      "coach.examples.interviewQ": "Bu pozisyon için mülakata nasıl hazırlanmalıyım?",
      "coach.examples.pathQ": "Bu alanda kariyer ilerleme yolları neler?",
      "coach.ready": "AI Koçu Hazır",
      "coach.ready_hint": "Önce CV'nizi yükleyin, ardından mesleğinize özel öneriler alın.",

      "btn.ask": "💬 Koça Sor",
      "btn.clear": "🗑️ Temizle",
      "chat.typing": "Koç düşünüyor…",

      "ph.chat": "Koçunuza bir şey sorun… Örn: 'Bu rol için öne çıkarabileceğim projeler neler?'",


      "btn.asking": "Soruluyor...", // bu da olsun ihtimale karşı
      
      // Profession badge için:
      "profession.softwareEngineer": "Yazılım Mühendisi",
      "profession.description.softwareEngineer": "Yazılım sistemleri geliştirir ve sürdürür, makine öğrenmesi, görüntü işleme ve bulut dağıtımına odaklanır.",
      
      // Status messages:
      "status.thinking": "Koç düşünüyor...",
      "status.ready": "Hazır",
      
      // Analysis results:
      "analysis.complete": "Analiz tamamlandı",
      "analysis.score": "Skor",
      "analysis.detected": "Tespit edilen",

      // Eksik anahtarlar eklendi:
      "btn.analyzing": "Analiz Ediliyor...",
      "err.url.required": "İş ilanı URL'si gerekli",
      "err.url.invalid": "Geçersiz URL formatı",
      "err.cv.required": "CV dosyası gerekli",
      "err.cv.type": "Sadece PDF dosyaları kabul edilir",
      "err.cv.size": "Dosya boyutu 10MB'dan küçük olmalı",
      "err.analysis.fail": "Analiz başarısız oldu",
      "err.conn": (msg) => `Bağlantı hatası: ${msg}`,
      "ok.analysis": (profession) => `Analiz tamamlandı! Meslek: ${profession}`,
      "chat.enterQ": "Lütfen bir soru girin",
      "chat.needAnalysis": "Önce CV analizini yapın",
      "chat.you": "Siz",
      "chat.coach": "AI Koç",
      "chat.error": "Hata:",
      "chat.more": "Başka sorularınız varsa sorabilirsiniz...",
      "chat.conn.lost": "Bağlantı kesildi",
      "coach.readyGeneric": "AI Koç Hazır",
      "coach.ready": (profession) => `${profession} için AI Koç Hazır`
    },

    en: {
      "title.app": "ATS Check + AI Career Coach",
      "label.language": "Language",
      "lead.text": "Optimize your resume against job postings and get personalized career advice from your AI coach.",
      "label.jobUrl": "Job Posting URL",
      "form.jobUrl_ph": "https://...",
      "hint.pasteLink": "Paste a link from LinkedIn, Indeed, etc.",
      "label.cvFile": "Resume (PDF)",
      "btn.analyze": "📊 Analyze",

      "section.ats": "📈 ATS Score",
      "score.overall": "Overall Score",
      "score.detected": "Detected Profession",
      "score.similarity": "Similarity",
      "score.coverage": "Coverage",

      "section.skills": "🎯 Skills Gap Analysis",
      "skills.yours": "✅ Your Skills",
      "skills.matched": "🎯 Matched Skills",
      "skills.missing": "❌ Missing Skills (High Priority)",
      "skills.jobReq": "Job Requirements:",

      "section.report": "⚡ Professional Optimization Report",
      "resume.preview": "📋 Resume Preview (First 800 characters)",

      "section.coach": "🤖 AI Career Coach",
      "coach.lead": "Get personalized, career advice. Your profession is auto-detected from your resume for tailored recommendations.",
      "coach.examples.project": "Project Ideas",
      "coach.examples.optimize": "Resume Optimization",
      "coach.examples.skills": "Skill Development",
      "coach.examples.interview": "Interview Prep",
      "coach.examples.path": "Career Path",
      "coach.examples.projectQ": "What projects should I add to my resume for this role?",
      "coach.examples.optimizeQ": "How can I optimize my resume for this specific job?",
      "coach.examples.skillsQ": "What skills should I develop to advance my career?",
      "coach.examples.interviewQ": "How should I prepare for interviews for this position?",
      "coach.examples.pathQ": "What are the typical career paths in this field?",
      "coach.ready": "AI Coach Ready",
      "coach.ready_hint": "Upload your resume first, then get profession-specific advice.",

      "btn.ask": "💬 Ask Coach",
      "btn.clear": "🗑️ Clear",
      "chat.typing": "AI is thinking…",

      "ph.chat": "Ask your AI career coach… e.g., 'Which projects will impress for this role?'",

      "btn.asking": "Asking...",
      
      "profession.softwareEngineer": "Software Engineer",
      "profession.description.softwareEngineer": "Develops and maintains software systems, focusing on machine learning, image processing, and cloud deployment.",
      
      "status.thinking": "AI is thinking...",
      "status.ready": "Ready",
      
      "analysis.complete": "Analysis complete", 
      "analysis.score": "Score",
      "analysis.detected": "Detected",

      // Eksik anahtarlar eklendi:
      "btn.analyzing": "Analyzing...",
      "err.url.required": "Job URL is required",
      "err.url.invalid": "Invalid URL format",
      "err.cv.required": "CV file is required",
      "err.cv.type": "Only PDF files are accepted",
      "err.cv.size": "File size must be under 10MB",
      "err.analysis.fail": "Analysis failed",
      "err.conn": (msg) => `Connection error: ${msg}`,
      "ok.analysis": (profession) => `Analysis completed! Profession: ${profession}`,
      "chat.enterQ": "Please enter a question",
      "chat.needAnalysis": "Please run CV analysis first",
      "chat.you": "You",
      "chat.coach": "AI Coach",
      "chat.error": "Error:",
      "chat.more": "Feel free to ask more questions...",
      "chat.conn.lost": "Connection lost",
      "coach.readyGeneric": "AI Coach Ready",
      "coach.ready": (profession) => `AI Coach Ready for ${profession}`
    }
  };

  const LS_KEY = "ui_lang";

  function setPlaceholder(el, key) {
    const phKey = el.getAttribute("data-i18n-ph");
    if (!phKey) return;
    const lang = current();
    const val = dict[lang][phKey] ?? "";
    el.setAttribute("placeholder", val);
  }

  function applyTranslations() {
    const lang = current();
    document.documentElement.setAttribute("lang", lang);

    // normal metinler
    document.querySelectorAll("[data-i18n]").forEach(el => {
      const k = el.getAttribute("data-i18n");
      const val = dict[lang][k] ?? k;
      el.textContent = val;
    });

    // placeholder'lar
    document.querySelectorAll("[data-i18n-ph]").forEach(el => setPlaceholder(el));

    // select kutusunu seçili dile getir
    const sel = document.getElementById("langSelect");
    if (sel && sel.value !== lang) sel.value = lang;
  }

  function current() {
    return localStorage.getItem(LS_KEY) || "tr";
  }

  function setLang(lang) {
    if (!dict[lang]) return;
    localStorage.setItem(LS_KEY, lang);
    applyTranslations();
  }

  // Global fonksiyonları export et
  window.getLang = current;
  window.DICT = dict;
  
  // i18n fonksiyonunu export et
  window.i18n = (key) => {
    const value = dict[current()][key];
    if (typeof value === 'function') {
      return value;
    }
    return value ?? key;
  };

  // global yardımcı (app.js'de kullanılıyor)
  window.t = (key) => (dict[current()][key] ?? key);

  window.addEventListener("DOMContentLoaded", () => {
    // dil seçiciyi bağla
    const sel = document.getElementById("langSelect");
    if (sel) {
      sel.value = current();
      sel.addEventListener("change", e => setLang(e.target.value));
    }
    applyTranslations();
  });

  console.log('i18n loaded successfully');
})();