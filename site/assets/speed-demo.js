/* White Lightning Motors — POV Speed Demo
   Single self-contained widget: side trigger + full-screen experience + lead capture.
   No dependencies. Pure JS + Web Audio API. */

(() => {
  if (window.__WLM_SPEED__) return;
  window.__WLM_SPEED__ = true;

  const STOCK_TOP = 11;
  const UNLEASHED_TOP = 41;
  const STORE_KEY = 'wlm-speed-demo-seen';

  // ---------- Side widget ----------
  const widget = document.createElement('button');
  widget.className = 'wlm-speed-widget';
  widget.setAttribute('aria-label', 'Feel the speed — interactive demo');
  widget.innerHTML = `
    <span class="wlm-speed-widget-inner">
      <span class="wlm-bolt">⚡</span>
      <span class="wlm-w-text">FEEL&nbsp;THE&nbsp;SPEED</span>
      <span class="wlm-w-sub">▶ 18 sec demo</span>
    </span>`;
  document.body.appendChild(widget);

  // ---------- Demo overlay (built on first open) ----------
  let overlay, els, audio, raf, audioCtx, engineOsc, engineGain, lpfilter;
  let phase = 'idle', startTime = 0, speed = 0, particles = [], canvas, ctx;
  let cameraShake = 0, scenery = [];

  function buildOverlay() {
    overlay = document.createElement('div');
    overlay.className = 'wlm-speed-overlay';
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.innerHTML = `
      <div class="wlm-stage" id="wlm-stage">
        <div class="wlm-sky"></div>
        <div class="wlm-sun"></div>
        <div class="wlm-mountains"></div>
        <div class="wlm-scenery" id="wlm-scenery"></div>
        <div class="wlm-road-wrap">
          <div class="wlm-road">
            <div class="wlm-road-lines"></div>
          </div>
        </div>
        <canvas class="wlm-particles" id="wlm-particles"></canvas>
        <div class="wlm-speedlines"></div>
        <div class="wlm-vignette"></div>
        <div class="wlm-flash" id="wlm-flash"></div>
        <div class="wlm-cabin">
          <svg class="wlm-wheel" viewBox="0 0 200 200" aria-hidden="true">
            <defs>
              <radialGradient id="wlmWheel" cx=".5" cy=".5" r=".5">
                <stop offset="0" stop-color="#1a1a22"/>
                <stop offset="1" stop-color="#000"/>
              </radialGradient>
            </defs>
            <circle cx="100" cy="100" r="90" fill="url(#wlmWheel)" stroke="#252830" stroke-width="2"/>
            <circle cx="100" cy="100" r="35" fill="#0a0a0d" stroke="#252830" stroke-width="2"/>
            <path d="M100 65 L92 78 L108 78 Z" fill="#00c2ff"/>
            <text x="100" y="110" text-anchor="middle" fill="#fff" font-family="Arial" font-size="10" font-weight="900" letter-spacing="2">WLM</text>
            <rect x="98" y="20" width="4" height="50" fill="#1a1a22"/>
            <rect x="98" y="130" width="4" height="50" fill="#1a1a22"/>
            <rect x="20" y="98" width="50" height="4" fill="#1a1a22"/>
            <rect x="130" y="98" width="50" height="4" fill="#1a1a22"/>
          </svg>
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
                  <linearGradient id="wlmGaugeArc2" x1="0" x2="1">
                    <stop offset="0" stop-color="#00c2ff"/>
                    <stop offset="1" stop-color="#fff"/>
                  </linearGradient>
                </defs>
                <!-- gauge arc background -->
                <path d="M40 170 A 120 120 0 0 1 280 170" fill="none" stroke="#1a1a22" stroke-width="16" stroke-linecap="round"/>
                <!-- speed arc (will be styled by JS) -->
                <path id="wlm-arc" d="M40 170 A 120 120 0 0 1 280 170" fill="none" stroke="url(#wlmGaugeArc)" stroke-width="14" stroke-linecap="round" stroke-dasharray="377" stroke-dashoffset="377"/>
                <!-- tick marks -->
                <g stroke="#3a3f4d" stroke-width="2">
                  ${Array.from({length:9},(_,i)=>{const a=Math.PI*(1-i/8),r1=110,r2=128,x1=160+Math.cos(a)*r1,y1=170-Math.sin(a)*r1,x2=160+Math.cos(a)*r2,y2=170-Math.sin(a)*r2;return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/>`}).join('')}
                </g>
                <!-- needle -->
                <g id="wlm-needle" transform="rotate(-90 160 170)">
                  <line x1="160" y1="170" x2="160" y2="50" stroke="#fff" stroke-width="3"/>
                  <circle cx="160" cy="170" r="8" fill="#00c2ff" stroke="#fff" stroke-width="2"/>
                </g>
              </svg>
              <div class="wlm-mph"><span id="wlm-mph">0</span><small>MPH</small></div>
              <div class="wlm-status" id="wlm-status">TAP TO START</div>
            </div>
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
            <p>Sound up. 18 seconds. POV from the driver's seat.</p>
            <button class="wlm-start-btn" id="wlm-start">▶ TAP TO DRIVE</button>
            <small>Headphones recommended · Tap close to exit anytime</small>
          </div>
        </div>
        <div class="wlm-leadform" id="wlm-leadform">
          <div class="wlm-leadform-inner">
            <span class="wlm-confetti" id="wlm-confetti"></span>
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
      scenery: overlay.querySelector('#wlm-scenery'),
      arc: overlay.querySelector('#wlm-arc'),
      needle: overlay.querySelector('#wlm-needle'),
      mph: overlay.querySelector('#wlm-mph'),
      status: overlay.querySelector('#wlm-status'),
      flash: overlay.querySelector('#wlm-flash'),
      startgate: overlay.querySelector('#wlm-startgate'),
      leadform: overlay.querySelector('#wlm-leadform'),
      thanks: overlay.querySelector('#wlm-thanks'),
      form: overlay.querySelector('#wlm-form'),
      confetti: overlay.querySelector('#wlm-confetti'),
    };

    canvas = overlay.querySelector('#wlm-particles');
    ctx = canvas.getContext('2d');
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    overlay.querySelector('#wlm-close').addEventListener('click', close);
    overlay.querySelector('#wlm-start').addEventListener('click', start);
    overlay.querySelector('#wlm-replay').addEventListener('click', () => {
      els.thanks.classList.remove('on');
      els.leadform.classList.remove('on');
      els.startgate.classList.add('on');
      els.status.textContent = 'TAP TO START';
      setNeedle(0);
      setArc(0);
      els.mph.textContent = '0';
    });
    els.form.addEventListener('submit', onSubmit);

    // Build scenery
    for (let i = 0; i < 8; i++) {
      const tree = document.createElement('div');
      tree.className = 'wlm-tree ' + (i%2 ? 'right' : 'left');
      tree.style.bottom = (12 + (i*7)%18) + '%';
      scenery.push({el: tree, lane: i%2 ? 1 : -1, z: i*180 + 50, baseSize: 80 + Math.random()*60});
      els.scenery.appendChild(tree);
    }
    for (let i = 0; i < 6; i++) {
      const house = document.createElement('div');
      house.className = 'wlm-house ' + (i%2 ? 'right' : 'left');
      house.style.bottom = (14 + (i*8)%16) + '%';
      scenery.push({el: house, lane: i%2 ? 1 : -1, z: i*240 + 120, baseSize: 110 + Math.random()*40, house: true});
      els.scenery.appendChild(house);
    }
  }

  function resizeCanvas() {
    if (!canvas) return;
    canvas.width  = window.innerWidth;
    canvas.height = window.innerHeight;
  }

  // ---------- Audio synthesis ----------
  function initAudio() {
    try {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      // Engine: sawtooth + sub oscillator through lowpass
      engineOsc = audioCtx.createOscillator();
      engineOsc.type = 'sawtooth';
      engineOsc.frequency.value = 60;

      const sub = audioCtx.createOscillator();
      sub.type = 'square';
      sub.frequency.value = 30;
      const subGain = audioCtx.createGain();
      subGain.gain.value = 0.18;

      lpfilter = audioCtx.createBiquadFilter();
      lpfilter.type = 'lowpass';
      lpfilter.frequency.value = 200;
      lpfilter.Q.value = 4;

      engineGain = audioCtx.createGain();
      engineGain.gain.value = 0;

      engineOsc.connect(lpfilter);
      sub.connect(subGain).connect(lpfilter);
      lpfilter.connect(engineGain).connect(audioCtx.destination);
      engineOsc.start();
      sub.start();
    } catch (e) { /* audio is bonus */ }
  }

  function setEngine(speedNow) {
    if (!engineGain || !engineOsc) return;
    // Map speed 0..41 → freq 60..380 and gain 0..0.18
    const target = 60 + (speedNow / UNLEASHED_TOP) * 320;
    engineOsc.frequency.setTargetAtTime(target, audioCtx.currentTime, 0.05);
    lpfilter.frequency.setTargetAtTime(200 + speedNow * 40, audioCtx.currentTime, 0.05);
    const gain = Math.min(0.18, 0.04 + (speedNow / UNLEASHED_TOP) * 0.16);
    engineGain.gain.setTargetAtTime(gain, audioCtx.currentTime, 0.05);
  }

  function thunderclap() {
    if (!audioCtx) return;
    const dur = 1.2;
    const noiseBuf = audioCtx.createBuffer(1, audioCtx.sampleRate * dur, audioCtx.sampleRate);
    const data = noiseBuf.getChannelData(0);
    for (let i = 0; i < data.length; i++) {
      data[i] = (Math.random() * 2 - 1) * (1 - i/data.length);
    }
    const src = audioCtx.createBufferSource();
    src.buffer = noiseBuf;
    const filt = audioCtx.createBiquadFilter();
    filt.type = 'lowpass';
    filt.frequency.value = 400;
    const g = audioCtx.createGain();
    g.gain.value = 0.55;
    g.gain.setTargetAtTime(0, audioCtx.currentTime + 0.05, 0.5);
    src.connect(filt).connect(g).connect(audioCtx.destination);
    src.start();
  }

  // ---------- Demo control ----------
  function open() {
    if (!overlay) buildOverlay();
    document.body.style.overflow = 'hidden';
    overlay.classList.add('on');
    requestAnimationFrame(() => overlay.classList.add('ready'));
    els.startgate.classList.add('on');
  }

  function close() {
    overlay.classList.remove('on','ready');
    document.body.style.overflow = '';
    cancelAnimationFrame(raf);
    if (engineGain) engineGain.gain.setTargetAtTime(0, audioCtx.currentTime, 0.1);
    phase = 'idle';
    speed = 0;
    particles = [];
    els.leadform.classList.remove('on');
    els.thanks.classList.remove('on');
    els.startgate.classList.add('on');
    setNeedle(0);
    setArc(0);
    els.mph.textContent = '0';
    els.status.textContent = 'TAP TO START';
  }

  function start() {
    if (!audioCtx) initAudio();
    if (audioCtx && audioCtx.state === 'suspended') audioCtx.resume();
    els.startgate.classList.remove('on');
    phase = 'stock';
    startTime = performance.now();
    speed = 0;
    particles = [];
    tick();
  }

  function setArc(pct) {
    // arc length ≈ 377 (semicircle path) — fill from 0 to clamp(pct)
    const total = 377;
    els.arc.style.strokeDashoffset = total - total * Math.min(1, pct);
  }

  function setNeedle(speedNow) {
    // 0 → -90deg, 41 → +90deg (or 27 in stock mode)
    const top = phase === 'stock' ? STOCK_TOP * 1.3 : UNLEASHED_TOP;  // a little headroom past stock cap visually
    const ratio = Math.min(1, speedNow / top);
    const deg = -90 + ratio * 180;
    els.needle.setAttribute('transform', `rotate(${deg} 160 170)`);
  }

  function tick() {
    const now = performance.now();
    const t = (now - startTime) / 1000;
    let prevSpeed = speed;

    if (phase === 'stock') {
      // 0 → STOCK_TOP over ~5s, plateau
      speed = Math.min(STOCK_TOP, ease(t, 5) * STOCK_TOP);
      els.status.textContent = speed >= STOCK_TOP - 0.3 ? 'STOCK CEILING · 11 MPH' : 'STOCK MOTOR';
      if (t > 6) {
        phase = 'swap';
        startTime = now;
        triggerSwap();
      }
    } else if (phase === 'swap') {
      // Brief moment of white-out + thunder, then "UNLEASHED"
      speed = STOCK_TOP;
      els.status.textContent = '⚡ WHITE LIGHTNING ⚡';
      if (t > 1.4) {
        phase = 'unleashed';
        startTime = now;
      }
    } else if (phase === 'unleashed') {
      // STOCK_TOP → UNLEASHED_TOP over ~7s, climactic curve
      const r = Math.min(1, ease(t, 7));
      speed = STOCK_TOP + (UNLEASHED_TOP - STOCK_TOP) * r;
      els.status.textContent = speed >= UNLEASHED_TOP - 0.5 ? 'UNLEASHED · ' + UNLEASHED_TOP + ' MPH' : 'UNLEASHED';
      cameraShake = Math.min(8, 2 + r * 8);
      if (t > 7.4) {
        phase = 'apex';
        startTime = now;
        thunderclap();
      }
    } else if (phase === 'apex') {
      speed = UNLEASHED_TOP;
      cameraShake = Math.max(0, 8 - t * 6);
      if (t > 1.2) {
        phase = 'lead';
        showLeadForm();
      }
    }

    // Update HUD
    setNeedle(speed);
    setArc(speed / UNLEASHED_TOP);
    els.mph.textContent = Math.round(speed);

    // Animate world
    updateScenery(speed);
    drawParticles(speed);
    setEngine(speed);
    applyShake();

    raf = requestAnimationFrame(tick);
  }

  function ease(t, total) {
    const x = Math.min(1, t / total);
    // ease-in-out cubic
    return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
  }

  function triggerSwap() {
    els.flash.classList.add('go');
    thunderclap();
    setTimeout(() => els.flash.classList.remove('go'), 900);
  }

  function updateScenery(speedNow) {
    const dz = 4 + (speedNow / UNLEASHED_TOP) * 60;
    scenery.forEach(s => {
      s.z -= dz;
      if (s.z < 50) s.z += 1500 + Math.random() * 400;
      const scale = Math.max(0.05, 600 / (s.z + 200));
      const xLane = s.lane * (window.innerWidth * 0.35);
      const px = window.innerWidth / 2 + xLane * (s.z < 800 ? 1 : 0.6);
      const sizePx = s.baseSize * scale;
      s.el.style.width = sizePx + 'px';
      s.el.style.height = (s.house ? sizePx * 1.1 : sizePx * 2.2) + 'px';
      s.el.style.left = (px - sizePx/2) + 'px';
      s.el.style.opacity = Math.min(1, (1500 - s.z) / 1200);
      s.el.style.zIndex = Math.floor(1000 - s.z);
    });
  }

  function drawParticles(speedNow) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    // Spawn streak particles
    const spawn = Math.floor(speedNow / 3);
    for (let i = 0; i < spawn; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: canvas.height * 0.4 + Math.random() * canvas.height * 0.5,
        vx: (Math.random() - 0.5) * 20,
        vy: 0,
        life: 1,
        speed: speedNow,
      });
    }
    const accel = speedNow / UNLEASHED_TOP;
    particles = particles.filter(p => {
      const dirX = (p.x - canvas.width/2);
      const dirY = (p.y - canvas.height/2);
      const norm = Math.sqrt(dirX*dirX + dirY*dirY) || 1;
      p.vx += (dirX / norm) * 0.6 * (1 + accel*3);
      p.vy += (dirY / norm) * 0.6 * (1 + accel*3);
      p.x += p.vx;
      p.y += p.vy;
      p.life -= 0.025;
      const streak = Math.min(80, 4 + accel * 60);
      ctx.strokeStyle = `rgba(${180 + accel*70},${220 + accel*30},255,${p.life * 0.7})`;
      ctx.lineWidth = 1 + accel * 1.5;
      ctx.beginPath();
      ctx.moveTo(p.x, p.y);
      ctx.lineTo(p.x - p.vx * streak/14, p.y - p.vy * streak/14);
      ctx.stroke();
      return p.life > 0 && p.x > -100 && p.x < canvas.width + 100 && p.y > -100 && p.y < canvas.height + 100;
    });
  }

  function applyShake() {
    if (!els.stage) return;
    if (cameraShake > 0.05) {
      const x = (Math.random() - 0.5) * cameraShake;
      const y = (Math.random() - 0.5) * cameraShake;
      els.stage.style.transform = `translate(${x}px, ${y}px)`;
    } else {
      els.stage.style.transform = '';
    }
  }

  function showLeadForm() {
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
      b.style.setProperty('--dx', ((Math.random() - 0.5) * 800) + 'px');
      b.style.setProperty('--dy', (-300 - Math.random() * 400) + 'px');
      b.style.setProperty('--rot', (Math.random() * 720 - 360) + 'deg');
      b.style.animationDelay = (Math.random() * 0.3) + 's';
      c.appendChild(b);
    }
    setTimeout(() => c.innerHTML = '', 2500);
  }

  function onSubmit(e) {
    e.preventDefault();
    const fd = new FormData(els.form);
    const body = `New WLM lead from the speed demo:%0A%0A` +
      `Name: ${encodeURIComponent(fd.get('name'))}%0A` +
      `Phone: ${encodeURIComponent(fd.get('phone'))}%0A` +
      `Email: ${encodeURIComponent(fd.get('email'))}%0A` +
      `Cart: ${encodeURIComponent(fd.get('cart') || '(not provided)')}%0A%0A` +
      `Sent from: ${encodeURIComponent(location.pathname)}`;
    // Open mail client (in new tab so we don't lose the page)
    const a = document.createElement('a');
    a.href = `mailto:sales@whitelightningmotors.com?subject=Speed%20Demo%20Lead&body=${body}`;
    a.click();
    els.thanks.classList.add('on');
    burstConfetti();
    try { localStorage.setItem(STORE_KEY, '1'); } catch(e){}
  }

  widget.addEventListener('click', open);

  // Subtle: if visitor already converted, dial down widget pulse
  try {
    if (localStorage.getItem(STORE_KEY)) widget.classList.add('seen');
  } catch(e){}

})();
