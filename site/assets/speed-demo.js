/* White Lightning Motors — Video-Driven Speed Demo
   Plays time-travel.mp4 (21.5s) with HUD overlay synced to video.currentTime.
   Lead capture on completion. Single-file, no deps. */

(() => {
  if (window.__WLM_SPEED__) return;
  window.__WLM_SPEED__ = true;

  // ----- Timeline config (in seconds, tuned to your video) -----
  const T = {
    STOCK_START:   0.0,
    STOCK_CAP:     7.5,   // speedo locks at 11
    SWAP:          7.7,   // flash + thunderclap, status flip
    APEX:         14.4,   // speedo locks at 41
    TIMETRAVEL:   17.0,   // status flips to "1946"
    LEADFORM:     21.0,   // form slides up
  };
  const STOCK_TOP = 11;
  const UNLEASHED_TOP = 41;
  const STORE_KEY = 'wlm-speed-demo-seen';
  const VIDEO_SRC = '/assets/videos/time-travel.mp4';

  // ----- Side widget -----
  const widget = document.createElement('button');
  widget.className = 'wlm-speed-widget';
  widget.setAttribute('aria-label', 'Feel the speed — interactive demo');
  widget.innerHTML = `
    <span class="wlm-speed-widget-inner">
      <span class="wlm-bolt">⚡</span>
      <span class="wlm-w-text">FEEL&nbsp;THE&nbsp;SPEED</span>
      <span class="wlm-w-sub">▶ 21 sec demo</span>
    </span>`;
  document.body.appendChild(widget);

  // ----- Overlay (built on first open) -----
  let overlay, els, raf, audioCtx, thunderTriggered = false;

  function buildOverlay() {
    overlay = document.createElement('div');
    overlay.className = 'wlm-speed-overlay';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.innerHTML = `
      <div class="wlm-stage" id="wlm-stage">
        <video class="wlm-video" id="wlm-video" preload="auto" playsinline crossorigin="anonymous">
          <source src="${VIDEO_SRC}" type="video/mp4">
        </video>
        <div class="wlm-vignette"></div>
        <div class="wlm-flash" id="wlm-flash"></div>
        <div class="wlm-dash">
          <div class="wlm-dash-frame">
            <svg class="wlm-gauge" viewBox="0 0 320 200" aria-hidden="true">
              <defs>
                <linearGradient id="wlmGaugeArc" x1="0" x2="1">
                  <stop offset="0" stop-color="#22c55e"/>
                  <stop offset=".4" stop-color="#facc15"/>
                  <stop offset=".7" stop-color="#f97316"/>
                  <stop offset="1" stop-color="#ef4444"/>
                </linearGradient>
              </defs>
              <path d="M40 170 A 120 120 0 0 1 280 170" fill="none" stroke="rgba(0,0,0,.5)" stroke-width="18" stroke-linecap="round"/>
              <path d="M40 170 A 120 120 0 0 1 280 170" fill="none" stroke="#1a1a22" stroke-width="14" stroke-linecap="round"/>
              <path id="wlm-arc" d="M40 170 A 120 120 0 0 1 280 170" fill="none" stroke="url(#wlmGaugeArc)" stroke-width="12" stroke-linecap="round" stroke-dasharray="377" stroke-dashoffset="377"/>
              <g stroke="#3a3f4d" stroke-width="2">
                ${Array.from({length:9},(_,i)=>{const a=Math.PI*(1-i/8),r1=110,r2=128,x1=160+Math.cos(a)*r1,y1=170-Math.sin(a)*r1,x2=160+Math.cos(a)*r2,y2=170-Math.sin(a)*r2;return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/>`}).join('')}
              </g>
              <g id="wlm-needle" transform="rotate(-90 160 170)">
                <line x1="160" y1="170" x2="160" y2="50" stroke="#fff" stroke-width="3"/>
                <circle cx="160" cy="170" r="8" fill="#00c2ff" stroke="#fff" stroke-width="2"/>
              </g>
            </svg>
            <div class="wlm-mph"><span id="wlm-mph">0</span><small>MPH</small></div>
            <div class="wlm-status" id="wlm-status">READY</div>
          </div>
        </div>
        <div class="wlm-hud-top">
          <div class="wlm-brand-strip"><span class="wlm-bolt">⚡</span> WHITE LIGHTNING MOTORS</div>
          <button class="wlm-close" id="wlm-close" aria-label="Close demo">✕</button>
        </div>
        <div class="wlm-startgate" id="wlm-startgate">
          <div class="wlm-startgate-inner">
            <div class="wlm-bolt-huge">⚡</div>
            <h2>Feel what <span class="wlm-blue">11 → 41 mph</span> does to your golf cart.</h2>
            <p>Sound up. 21 seconds. POV from the driver's seat — with a surprise at the end.</p>
            <button class="wlm-start-btn" id="wlm-start">▶ TAP TO DRIVE</button>
            <small>Headphones recommended · Tap close to exit anytime</small>
          </div>
        </div>
        <div class="wlm-leadform" id="wlm-leadform">
          <div class="wlm-leadform-inner">
            <span class="wlm-confetti" id="wlm-confetti"></span>
            <div id="wlm-form-wrap">
              <h2>Want THIS in your cart?</h2>
              <p class="wlm-leadform-sub">Charlie will text you a real quote in under 5 minutes.</p>
              <form id="wlm-form">
                <input type="text" name="name" placeholder="Your name" required>
                <input type="tel" name="phone" placeholder="Phone (texts welcome)" required>
                <input type="email" name="email" placeholder="Email" required>
                <input type="text" name="cart" placeholder="Cart make / model / year (optional)">
                <button type="submit" class="wlm-submit">⚡ Send me a quote</button>
                <small>Or call now: <a href="tel:8328321993">832-832-1993</a></small>
              </form>
            </div>
            <div class="wlm-thanks" id="wlm-thanks">
              <div class="wlm-bolt-huge">⚡</div>
              <h2>You're in. Charlie will call within 5 minutes.</h2>
              <p>Keep an eye on your phone — 832-832-1993.</p>
              <button class="wlm-start-btn" id="wlm-replay">↺ Run it again</button>
            </div>
          </div>
        </div>
      </div>`;
    document.body.appendChild(overlay);

    els = {
      stage: overlay.querySelector('#wlm-stage'),
      video: overlay.querySelector('#wlm-video'),
      arc: overlay.querySelector('#wlm-arc'),
      needle: overlay.querySelector('#wlm-needle'),
      mph: overlay.querySelector('#wlm-mph'),
      status: overlay.querySelector('#wlm-status'),
      flash: overlay.querySelector('#wlm-flash'),
      startgate: overlay.querySelector('#wlm-startgate'),
      leadform: overlay.querySelector('#wlm-leadform'),
      thanks: overlay.querySelector('#wlm-thanks'),
      formWrap: overlay.querySelector('#wlm-form-wrap'),
      form: overlay.querySelector('#wlm-form'),
      confetti: overlay.querySelector('#wlm-confetti'),
      dash: overlay.querySelector('.wlm-dash'),
    };

    overlay.querySelector('#wlm-close').addEventListener('click', close);
    overlay.querySelector('#wlm-start').addEventListener('click', start);
    overlay.querySelector('#wlm-replay').addEventListener('click', replay);
    els.form.addEventListener('submit', onSubmit);
    els.video.addEventListener('ended', () => showLeadForm());
    // Drive HUD from the video clock — works even when tab is backgrounded
    els.video.addEventListener('timeupdate', updateHUDFromVideo);
    els.video.addEventListener('play', () => { raf = requestAnimationFrame(updateHUD); });
  }

  function updateHUDFromVideo() {
    if (!els.video) return;
    paintHUD(els.video.currentTime);
  }

  function paintHUD(t) {
    const speed = speedAt(t);
    els.mph.textContent = Math.round(speed);
    setArc(speed / UNLEASHED_TOP);
    setNeedle(speed, t);
    const status = statusAt(t);
    if (status !== els.status.textContent) els.status.textContent = status;

    if (!thunderTriggered && t >= T.STOCK_CAP && t < T.SWAP + 0.4) {
      thunderTriggered = true;
      els.flash.classList.add('go');
      thunderclap();
      setTimeout(() => els.flash.classList.remove('go'), 900);
    }
    const shake = (t > T.SWAP && t < T.APEX) ? Math.min(6, (t - T.SWAP) * 1.4) : 0;
    if (shake > 0.1) {
      const x = (Math.random()-0.5) * shake;
      const y = (Math.random()-0.5) * shake;
      els.stage.style.transform = `translate(${x}px, ${y}px)`;
    } else {
      els.stage.style.transform = '';
    }
    if (t >= T.TIMETRAVEL) els.dash.classList.add('wlm-tt');
    else els.dash.classList.remove('wlm-tt');
    if (t >= T.LEADFORM && !els.leadform.classList.contains('on')) showLeadForm();
  }

  // ----- Audio: thunderclap synth (video has its own audio; this layers a punch) -----
  function thunderclap() {
    try {
      if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      if (audioCtx.state === 'suspended') audioCtx.resume();
      const dur = 1.0;
      const buf = audioCtx.createBuffer(1, audioCtx.sampleRate * dur, audioCtx.sampleRate);
      const d = buf.getChannelData(0);
      for (let i = 0; i < d.length; i++) d[i] = (Math.random()*2-1) * Math.pow(1 - i/d.length, 1.8);
      const src = audioCtx.createBufferSource(); src.buffer = buf;
      const filt = audioCtx.createBiquadFilter(); filt.type='lowpass'; filt.frequency.value=500;
      const g = audioCtx.createGain(); g.gain.value = 0.5;
      g.gain.setTargetAtTime(0, audioCtx.currentTime + 0.05, 0.4);
      src.connect(filt).connect(g).connect(audioCtx.destination);
      src.start();
    } catch(e){}
  }

  // ----- HUD math -----
  function speedAt(t) {
    if (t <= T.STOCK_START) return 0;
    if (t <= T.STOCK_CAP)   return STOCK_TOP * (t / T.STOCK_CAP);
    if (t <= T.SWAP)        return STOCK_TOP;
    if (t <= T.APEX) {
      const r = (t - T.SWAP) / (T.APEX - T.SWAP);
      return STOCK_TOP + (UNLEASHED_TOP - STOCK_TOP) * easeOutCubic(r);
    }
    if (t <= T.TIMETRAVEL)  return UNLEASHED_TOP;
    // Time travel — speedometer scrambles
    return UNLEASHED_TOP;
  }
  function easeOutCubic(x){return 1 - Math.pow(1-x, 3)}

  function statusAt(t) {
    if (t < T.STOCK_CAP)    return 'STOCK MOTOR';
    if (t < T.SWAP)         return 'STOCK CEILING · 11 MPH';
    if (t < T.APEX)         return '⚡ WHITE LIGHTNING ⚡';
    if (t < T.TIMETRAVEL)   return 'UNLEASHED · 41 MPH';
    if (t < T.LEADFORM)     return '1946 · YEAH, IT\'S THAT FAST';
    return '';
  }

  function setNeedle(speed, t) {
    let deg;
    if (t < T.TIMETRAVEL) {
      const top = t < T.SWAP ? STOCK_TOP * 1.3 : UNLEASHED_TOP;
      const ratio = Math.min(1, speed / top);
      deg = -90 + ratio * 180;
    } else {
      // Time-travel scramble: spin needle
      deg = -90 + (((t - T.TIMETRAVEL) * 720) % 360);
    }
    els.needle.setAttribute('transform', `rotate(${deg} 160 170)`);
  }

  function setArc(pct) {
    const total = 377;
    els.arc.style.strokeDashoffset = total - total * Math.min(1, pct);
  }

  function updateHUD() {
    if (!els.video || els.video.ended) return;
    if (!els.video.paused) paintHUD(els.video.currentTime);
    raf = requestAnimationFrame(updateHUD);
  }

  // ----- Demo control -----
  function open() {
    if (!overlay) buildOverlay();
    document.body.style.overflow = 'hidden';
    overlay.classList.add('on');
    requestAnimationFrame(() => overlay.classList.add('ready'));
    els.startgate.classList.add('on');
    els.leadform.classList.remove('on');
    els.thanks.classList.remove('on');
    els.formWrap.style.display = '';
    // Reset HUD
    els.mph.textContent = '0';
    setArc(0);
    setNeedle(0, 0);
    els.status.textContent = 'READY';
    thunderTriggered = false;
    // Pre-load
    els.video.load();
  }

  function close() {
    overlay.classList.remove('on','ready');
    document.body.style.overflow = '';
    cancelAnimationFrame(raf);
    els.video.pause();
    els.video.currentTime = 0;
    els.leadform.classList.remove('on');
    els.thanks.classList.remove('on');
    els.startgate.classList.add('on');
  }

  function start() {
    els.startgate.classList.remove('on');
    thunderTriggered = false;
    els.video.currentTime = 0;
    els.video.muted = false;
    const playPromise = els.video.play();
    if (playPromise) {
      playPromise.catch(() => {
        // Autoplay with sound may fail — try muted, surface a prompt
        els.video.muted = true;
        els.video.play().catch(() => {});
      });
    }
    raf = requestAnimationFrame(updateHUD);
  }

  function replay() {
    els.thanks.classList.remove('on');
    els.leadform.classList.remove('on');
    els.formWrap.style.display = '';
    els.startgate.classList.add('on');
    els.mph.textContent = '0';
    setArc(0); setNeedle(0, 0);
    els.status.textContent = 'READY';
    thunderTriggered = false;
  }

  function showLeadForm() {
    if (els.leadform.classList.contains('on')) return;
    els.leadform.classList.add('on');
    burstConfetti();
  }

  function burstConfetti() {
    const c = els.confetti;
    c.innerHTML = '';
    for (let i = 0; i < 60; i++) {
      const b = document.createElement('span');
      b.textContent = '⚡';
      b.style.left = (40 + Math.random() * 20) + '%';
      b.style.top = '50%';
      b.style.setProperty('--dx', ((Math.random() - 0.5) * 900) + 'px');
      b.style.setProperty('--dy', (-300 - Math.random() * 500) + 'px');
      b.style.setProperty('--rot', (Math.random() * 720 - 360) + 'deg');
      b.style.animationDelay = (Math.random() * 0.3) + 's';
      c.appendChild(b);
    }
    setTimeout(() => c.innerHTML = '', 2500);
  }

  function onSubmit(e) {
    e.preventDefault();
    const fd = new FormData(els.form);
    const body =
      `New WLM lead from the speed demo:%0A%0A` +
      `Name: ${encodeURIComponent(fd.get('name'))}%0A` +
      `Phone: ${encodeURIComponent(fd.get('phone'))}%0A` +
      `Email: ${encodeURIComponent(fd.get('email'))}%0A` +
      `Cart: ${encodeURIComponent(fd.get('cart') || '(not provided)')}%0A%0A` +
      `Sent from: ${encodeURIComponent(location.pathname)}`;
    const a = document.createElement('a');
    a.href = `mailto:sales@whitelightningmotors.com?subject=Speed%20Demo%20Lead&body=${body}`;
    a.click();
    els.formWrap.style.display = 'none';
    els.thanks.classList.add('on');
    burstConfetti();
    try { localStorage.setItem(STORE_KEY, '1'); } catch(e){}
  }

  widget.addEventListener('click', open);
  try { if (localStorage.getItem(STORE_KEY)) widget.classList.add('seen'); } catch(e){}
})();
