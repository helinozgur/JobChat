let analysisData=null, eventSource=null, chatStartTime=null;

// ----------- helpers ----------
function showAlert(type, message){
  document.getElementById('errorAlert').style.display='none';
  document.getElementById('successAlert').style.display='none';
  const id = type==='error' ? 'errorAlert' : 'successAlert';
  const el = document.getElementById(id);
  el.textContent = message;
  el.style.display = 'block';
  if(type!=='error'){ setTimeout(()=>{ el.style.display='none'; }, 5000); }
}
function setAnalyzeButtonState(disabled, text, loading){
  const btn=document.getElementById('analyzeBtn');
  const txt=document.getElementById('analyzeBtnText');
  const spn=document.getElementById('analyzeLoading');
  btn.disabled=disabled; txt.textContent=text; spn.style.display=loading?'inline-block':'none';
}
function setChatButtonState(disabled, text, loading){
  const btn=document.getElementById('chatBtn');
  const txt=document.getElementById('chatBtnText');
  const spn=document.getElementById('chatLoading');
  btn.disabled=disabled; txt.textContent=text; spn.style.display=loading?'inline-block':'none';
}
function isValidUrl(s){ try{ new URL(s); return s.startsWith('http://')||s.startsWith('https://'); }catch(_){ return false; } }

// ----------- init ----------
document.addEventListener('DOMContentLoaded',()=>{
  document.getElementById('chatQuestion').placeholder = i18n('ph.chat');
  const form=document.getElementById('analyzeForm');
  if(form) form.addEventListener('submit', handleAnalysis);

  // status ping
  fetch('/api/status').then(r=>r.json()).then(d=>{
    console.log('Status', d);
  }).catch(()=>{});
});

// ----------- analysis ----------
async function handleAnalysis(e){
  e.preventDefault();

  const jobUrl=document.getElementById('jobUrl').value.trim();
  const fileInput=document.getElementById('cvFile');

  if(!jobUrl){ showAlert('error', i18n('err.url.required')); return; }
  if(!isValidUrl(jobUrl)){ showAlert('error', i18n('err.url.invalid')); return; }
  if(!fileInput.files[0]){ showAlert('error', i18n('err.cv.required')); return; }

  const file=fileInput.files[0];
  if(!file.name.toLowerCase().endsWith('.pdf')){ showAlert('error', i18n('err.cv.type')); return; }
  if(file.size > 10*1024*1024){ showAlert('error', i18n('err.cv.size')); return; }

  setAnalyzeButtonState(true, i18n('btn.analyzing'), true);

  const fd=new FormData();
  fd.append('job_url', jobUrl);
  fd.append('cv', file);

  try{
    const res = await fetch('/api/analyze', { method:'POST', body: fd });
    const data = await res.json();

    if(data.success){
      analysisData=data;
      displayAnalysisResults(data);
      showAlert('success', i18n('ok.analysis')(data.profession.display_name));
      updateCoachBadge(data);
    }else{
      showAlert('error', data.error || i18n('err.analysis.fail'));
    }
  }catch(err){
    showAlert('error', i18n('err.conn')(err.message));
  }finally{
    setAnalyzeButtonState(false, i18n('btn.analyze'), false);
  }
}

function displayAnalysisResults(data){
  const { analysis, profession, skills, cv_preview } = data;

  // score
  const scoreEl=document.getElementById('scoreValue');
  scoreEl.textContent = Math.round(analysis.score);
  scoreEl.className='status-value ' + (analysis.score>=80?'ok':analysis.score>=60?'warnc':'err');

  document.getElementById('professionValue').textContent = profession.display_name;
  document.getElementById('similarityBar').style.width = Math.round(analysis.similarity*100)+'%';
  document.getElementById('coverageBar').style.width = Math.round(analysis.coverage*100)+'%';

  // skills
  // CV skills
  const cvSkills = skills.cv_skills || [];
  document.getElementById('cvSkills').innerHTML =
    (cvSkills.length? cvSkills.slice(0,8).map(s=>`<span class="chip">${s}</span>`).join('') :
     `<span class="muted">${getLang()==='tr'?'Yetenek bulunamadı':'No skills detected'}</span>`);

  // Matched
  const matched = skills.matched_skills || [];
  document.getElementById('matchedSkills').innerHTML =
    (matched.length? matched.slice(0,6).map(s=>`<span class="chip">${s}</span>`).join('') :
     `<span class="muted">${getLang()==='tr'?'Doğrudan eşleşme yok':'No direct matches'}</span>`);

  // Missing
  const missing = analysis.missing || [];
  document.getElementById('missingKeywords').innerHTML =
    (missing.length? missing.slice(0,8).map(s=>`<span class="chip">${s}</span>`).join('') :
     `<span class="chip" style="background:var(--ok);color:#fff">✅ ${getLang()==='tr'?'Kritik boşluk yok':'No critical gaps'}</span>`);

  // Job reqs
  const jobList = skills.job_skills || [];
  document.getElementById('jobSkills').textContent = jobList.length ? jobList.join(', ') : (getLang()==='tr'?'Belirgin yok':'No specific skills');

  // Report
  renderReport(analysis, profession);

  // Preview
  document.getElementById('cvPreview').textContent = cv_preview;

  // Show
  document.getElementById('resultsSection').style.display='block';
  setTimeout(()=>{ document.getElementById('resultsSection').scrollIntoView({behavior:'smooth'}); }, 200);
}

function renderReport(analysis, profession){
  const c=document.getElementById('optimizationReport');
  const sections=analysis.sections||{};
  const done=Object.values(sections).filter(Boolean).length;
  const total=Object.keys(sections).length;

  const issues = (analysis.issues||[]).map(i=>`<li>${i}</li>`).join('');
  const suggs  = (analysis.suggestions||[]).map(i=>`<li>${i}</li>`).join('');
  const rows   = Object.entries(sections).map(([k,v])=>`
    <div class="chip" style="display:flex;gap:8px;align-items:center;">
      <span>${v?'✅':'❌'}</span><span>${k}</span>
    </div>`).join('');

  c.innerHTML = `
    ${issues?`
      <div style="margin-bottom:16px">
        <h3 class="sub warn">⚠️ ${getLang()==='tr'?'Kritik Eksikler':'Critical Issues'}</h3>
        <ul style="margin:0 0 0 20px">${issues}</ul>
      </div>`:''}
    ${suggs?`
      <div style="margin-bottom:16px">
        <h3 class="sub">💡 ${getLang()==='tr'?'Profesyonel Öneriler':'Professional Recommendations'}</h3>
        <ul style="margin:0 0 0 20px">${suggs}</ul>
      </div>`:''}
    <div style="margin-bottom:16px">
      <h3 class="sub">📋 ${getLang()==='tr'?'CV Yapısı Analizi':'Resume Structure Analysis'} (${done}/${total})</h3>
      <div class="chips">${rows}</div>
    </div>
    <div class="badge" style="margin-top:8px">
      <div class="emoji">🎯</div>
      <div>
        <div class="badge-title">${profession.display_name}</div>
        <div class="badge-desc">${profession.description}</div>
      </div>
    </div>
  `;
}

function updateCoachBadge(data){
  const {profession}=data;
  document.getElementById('detectedProfession').textContent=profession.display_name;
  document.getElementById('professionDescription').textContent=profession.description;
  document.getElementById('professionBadge').style.display='block';

  const out=document.getElementById('chatOutput');
  const title = DICT[getLang()]['coach.ready'](profession.display_name);
  out.innerHTML = `
    <div class="empty-chat">
      <div class="big-emoji">👨‍💼</div>
      <div class="title">${title}</div>
      <div class="muted small">${i18n('coach.lead')}</div>
    </div>`;
}

// ----------- chat ----------
document.getElementById('chatBtn').addEventListener('click', ()=>{
  const q=document.getElementById('chatQuestion').value.trim();
  if(!q){ showAlert('error', i18n('chat.enterQ')); return; }
  if(!analysisData){ showAlert('error', i18n('chat.needAnalysis')); return; }
  startChat(q);
});

document.getElementById('chatQuestion').addEventListener('keydown', (e)=>{
  if(e.key==='Enter' && (e.ctrlKey||e.metaKey)){ e.preventDefault(); document.getElementById('chatBtn').click(); }
});

function setQuestion(q){
  document.getElementById('chatQuestion').value=q;
  document.getElementById('chatQuestion').focus();
}

function clearChat(){
  const out=document.getElementById('chatOutput');
  if(analysisData){
    const p=analysisData.profession.display_name;
    const title=DICT[getLang()]['coach.ready'](p);
    out.innerHTML = `
      <div class="empty-chat">
        <div class="big-emoji">👨‍💼</div>
        <div class="title">${title}</div>
        <div class="muted small">${i18n('coach.lead')}</div>
      </div>`;
  }else{
    out.innerHTML = `
      <div class="empty-chat">
        <div class="big-emoji">🤖</div>
        <div class="title">${i18n('coach.readyGeneric')}</div>
        <div class="muted small">${i18n('coach.readyHint')}</div>
      </div>`;
  }
  document.getElementById('chatQuestion').value='';
  document.getElementById('chatStats').style.display='none';
  if(eventSource) eventSource.close();
}

function startChat(question){
  const out=document.getElementById('chatOutput');
  const typing=document.getElementById('typingIndicator');

  setChatButtonState(true, i18n('btn.asking'), true);
  typing.style.display='flex';

  out.innerHTML = `
    <div style="margin-bottom:12px;padding:12px;background:var(--input-bg);border-left:4px solid var(--acc);border-radius:8px">
      <strong>${i18n('chat.you')}</strong><br><span style="font-style:italic">"${question}"</span>
    </div>
    <div style="margin-bottom:8px"><strong>${i18n('chat.coach')}</strong></div>
    <div id="chatResponse"></div>
  `;

  chatStartTime=Date.now();
  if(eventSource) eventSource.close();

  eventSource=new EventSource(`/api/chat?question=${encodeURIComponent(question)}`);

  eventSource.onmessage=(ev)=>{
    try{
      const data=JSON.parse(ev.data);
      if(data.error){ handleChatError(data.error); return; }
      if(data.done){ handleChatComplete(); return; }
      const chunk=(data.message && data.message.content)?data.message.content:'';
      if(chunk){
        const resp=document.getElementById('chatResponse');
        resp.textContent += chunk;
        out.scrollTop=out.scrollHeight;
      }
    }catch(_){}
  };

  eventSource.onerror=()=>{ handleChatError(i18n('chat.conn.lost')); };
}

function handleChatError(msg){
  const out=document.getElementById('chatOutput');
  out.innerHTML += `
    <div style="color:var(--err);padding:12px;background:rgba(255,107,107,.1);border-radius:8px;margin-top:12px">
      ❌ <strong>${i18n('chat.error')}</strong> ${msg}
    </div>`;
  setChatButtonState(false, i18n('btn.ask'), false);
  document.getElementById('typingIndicator').style.display='none';
  if(eventSource) eventSource.close();
}

function handleChatComplete(){
  const out=document.getElementById('chatOutput');
  out.innerHTML += `
    <div class="muted small" style="margin-top:12px">${i18n('chat.more')}</div>`;
  document.getElementById('responseTime').textContent = (Date.now()-chatStartTime);
  document.getElementById('chatStats').style.display='block';
  setChatButtonState(false, i18n('btn.ask'), false);
  document.getElementById('typingIndicator').style.display='none';
  if(eventSource) eventSource.close();
}
