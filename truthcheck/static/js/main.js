/* ═══════════════════════════════════════════════════════════════════════════
   TruthCheck — Main JavaScript
   ═══════════════════════════════════════════════════════════════════════════ */

'use strict';

// ── Theme ──────────────────────────────────────────────────────────────────
const Theme = {
  key: 'tc-theme',
  current: () => localStorage.getItem(Theme.key) || 'dark',
  set(t) {
    document.documentElement.setAttribute('data-theme', t);
    localStorage.setItem(Theme.key, t);
    const icon = document.querySelector('.theme-icon');
    if (icon) icon.textContent = t === 'dark' ? '☀️' : '🌙';
  },
  toggle() { Theme.set(Theme.current() === 'dark' ? 'light' : 'dark'); },
  init() { Theme.set(Theme.current()); }
};

// ── Auth tokens ────────────────────────────────────────────────────────────
const Auth = {
  getToken:   () => localStorage.getItem('tc_access_token'),
  setToken:   (t) => localStorage.setItem('tc_access_token', t),
  clearToken: () => { localStorage.removeItem('tc_access_token'); localStorage.removeItem('tc_user'); },
  getUser:    () => { try { return JSON.parse(localStorage.getItem('tc_user')); } catch { return null; } },
  setUser:    (u) => localStorage.setItem('tc_user', JSON.stringify(u)),
  isLoggedIn: () => !!Auth.getToken(),

  async check() {
    if (!Auth.getToken()) return null;
    try {
      const res = await API.get('/api/auth/me');
      Auth.setUser(res.user);
      return res.user;
    } catch {
      Auth.clearToken();
      return null;
    }
  },
  logout() {
    Auth.clearToken();
    Toast.show('Logged out successfully', 'info');
    setTimeout(() => window.location.href = '/', 800);
  }
};

// ── API helper ─────────────────────────────────────────────────────────────
const API = {
  async request(method, url, body) {
    const headers = { 'Content-Type': 'application/json' };
    if (Auth.getToken()) headers['Authorization'] = `Bearer ${Auth.getToken()}`;
    const res = await fetch(url, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
    return data;
  },
  get:    (url)       => API.request('GET', url),
  post:   (url, body) => API.request('POST', url, body),
  put:    (url, body) => API.request('PUT', url, body),
  delete: (url)       => API.request('DELETE', url),
};

// ── Toast ──────────────────────────────────────────────────────────────────
const Toast = {
  container: null,
  icons: { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' },
  init() {
    this.container = document.querySelector('.toast-container');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    }
  },
  show(message, type = 'info', duration = 4000) {
    if (!this.container) this.init();
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span class="toast-icon">${this.icons[type]}</span><span>${message}</span>`;
    this.container.appendChild(toast);
    setTimeout(() => {
      toast.classList.add('removing');
      toast.addEventListener('animationend', () => toast.remove(), { once: true });
    }, duration);
  }
};

// ── Particles ──────────────────────────────────────────────────────────────
const Particles = {
  canvas: null, ctx: null, particles: [], running: false,
  init() {
    this.canvas = document.getElementById('particles-canvas');
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.resize();
    window.addEventListener('resize', () => this.resize());
    this.spawn();
    this.running = true;
    this.loop();
  },
  resize() {
    if (!this.canvas) return;
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
  },
  spawn() {
    const count = Math.min(60, Math.floor(window.innerWidth / 25));
    this.particles = Array.from({ length: count }, () => this.newParticle());
  },
  newParticle() {
    return {
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      r: Math.random() * 1.5 + 0.3,
      dx: (Math.random() - 0.5) * 0.4,
      dy: (Math.random() - 0.5) * 0.4,
      opacity: Math.random() * 0.5 + 0.1,
      color: Math.random() > 0.5 ? '0,212,170' : '0,153,255',
    };
  },
  loop() {
    if (!this.running) return;
    const { ctx, canvas, particles } = this;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    particles.forEach(p => {
      p.x += p.dx; p.y += p.dy;
      if (p.x < 0 || p.x > canvas.width) p.dx *= -1;
      if (p.y < 0 || p.y > canvas.height) p.dy *= -1;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${p.color},${p.opacity})`;
      ctx.fill();
    });

    // Draw connections
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 120) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(0,212,170,${0.08 * (1 - dist / 120)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
    requestAnimationFrame(() => this.loop());
  }
};

// ── Scroll reveal ──────────────────────────────────────────────────────────
const Reveal = {
  observer: null,
  init() {
    const options = { threshold: 0.1, rootMargin: '0px 0px -40px 0px' };
    this.observer = new IntersectionObserver(entries => {
      entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); } });
    }, options);
    document.querySelectorAll('.reveal').forEach(el => this.observer.observe(el));
  }
};

// ── Navbar ─────────────────────────────────────────────────────────────────
const Navbar = {
  init() {
    const nav = document.querySelector('.navbar');
    if (!nav) return;

    // Scroll effect
    window.addEventListener('scroll', () => {
      nav.classList.toggle('scrolled', window.scrollY > 20);
    }, { passive: true });

    // Hamburger
    const hamburger = nav.querySelector('.nav-hamburger');
    const links = nav.querySelector('.nav-links');
    hamburger?.addEventListener('click', () => links?.classList.toggle('open'));

    // Active link
    const current = location.pathname;
    nav.querySelectorAll('.nav-links a').forEach(a => {
      if (a.getAttribute('href') === current) a.classList.add('active');
    });

    // Auth-aware nav
    this.updateAuthNav();
  },
  updateAuthNav() {
    const user = Auth.getUser();
    const authSection = document.querySelector('.nav-auth');
    if (!authSection) return;
    if (user) {
      authSection.innerHTML = `
        <a href="/dashboard" class="btn btn-ghost btn-sm">Dashboard</a>
        <button onclick="Auth.logout()" class="btn btn-outline btn-sm">Logout</button>
      `;
    } else {
      authSection.innerHTML = `
        <a href="/login" class="btn btn-ghost btn-sm">Login</a>
        <a href="/register" class="btn btn-primary btn-sm">Get Started</a>
      `;
    }
  }
};

// ── Counter animation ──────────────────────────────────────────────────────
function animateCounter(el, target, suffix = '') {
  const duration = 1800;
  const start = performance.now();
  const update = (now) => {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.floor(ease * target).toLocaleString() + suffix;
    if (progress < 1) requestAnimationFrame(update);
  };
  requestAnimationFrame(update);
}

// ── Detection tool ─────────────────────────────────────────────────────────
const Detector = {
  currentTab: 'text',
  init() {
    const tabs = document.querySelectorAll('.detect-tab');
    const textArea = document.getElementById('detect-text');
    const urlArea = document.getElementById('detect-url-section');
    const charCount = document.getElementById('char-count');
    const textarea = document.getElementById('news-text');
    const analyzeBtn = document.getElementById('analyze-btn');

    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        this.currentTab = tab.dataset.tab;
        textArea?.classList.toggle('hidden', this.currentTab !== 'text');
        urlArea?.classList.toggle('hidden', this.currentTab !== 'url');
      });
    });

    textarea?.addEventListener('input', () => {
      const len = textarea.value.length;
      if (charCount) charCount.textContent = `${len.toLocaleString()} / 50,000`;
      if (len > 50000) charCount.style.color = 'var(--c-red)';
      else charCount.style.color = '';
    });

    analyzeBtn?.addEventListener('click', () => this.analyze());

    // Allow Enter in URL input
    document.getElementById('url-input')?.addEventListener('keydown', e => {
      if (e.key === 'Enter') this.analyze();
    });
  },

  async analyze() {
    const textarea = document.getElementById('news-text');
    const urlInput = document.getElementById('url-input');
    const btn = document.getElementById('analyze-btn');
    const overlay = document.getElementById('analyzing-overlay');
    const resultSection = document.getElementById('result-section');

    const text = textarea?.value.trim();
    const url = urlInput?.value.trim();

    if (this.currentTab === 'text' && !text) {
      Toast.show('Please paste some article text to analyze', 'warning');
      textarea?.focus();
      return;
    }
    if (this.currentTab === 'url' && !url) {
      Toast.show('Please enter a URL to analyze', 'warning');
      return;
    }

    // Show loading
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Analyzing…';
    resultSection?.classList.add('hidden');
    overlay?.classList.add('active');

    // Simulate realistic thinking time
    await new Promise(r => setTimeout(r, 800));

    try {
      const body = this.currentTab === 'url' ? { url } : { text };
      const result = await API.post('/api/predict', body);
      this.showResult(result);
      Toast.show(`Analysis complete: ${result.result}`, result.result === 'FAKE' ? 'error' : 'success');
    } catch (err) {
      Toast.show(err.message || 'Analysis failed. Please try again.', 'error');
    } finally {
      btn.disabled = false;
      btn.innerHTML = '🔍 Analyze';
      overlay?.classList.remove('active');
    }
  },

  showResult(data) {
    const section = document.getElementById('result-section');
    if (!section) return;

    const isFake = data.result === 'FAKE';
    const emoji = isFake ? '🚨' : '✅';
    const color = isFake ? 'var(--c-red)' : 'var(--c-green)';

    section.innerHTML = `
      <div class="card result-card card-glow">
        <div class="result-verdict">
          <div class="result-badge ${data.result.toLowerCase()}">${emoji} ${data.result}</div>
          <div class="result-confidence">
            Confidence: <strong style="color:${color}">${data.confidence}%</strong>
          </div>
          <div style="margin-left:auto;font-size:0.8rem;color:var(--text-muted)">
            Credibility Score: <span style="color:${color};font-weight:700">${data.credibility_score}/100</span>
          </div>
        </div>

        <div class="probability-bars">
          <div class="prob-bar-row">
            <div class="prob-bar-label">
              <span>🚨 Fake</span>
              <span style="color:var(--c-red);font-weight:700">${data.fake_probability}%</span>
            </div>
            <div class="prob-bar-track">
              <div class="prob-bar-fill fake" data-width="${data.fake_probability}"></div>
            </div>
          </div>
          <div class="prob-bar-row">
            <div class="prob-bar-label">
              <span>✅ Real</span>
              <span style="color:var(--c-green);font-weight:700">${data.real_probability}%</span>
            </div>
            <div class="prob-bar-track">
              <div class="prob-bar-fill real" data-width="${data.real_probability}"></div>
            </div>
          </div>
        </div>

        <div class="divider"></div>

        <h4 style="font-size:0.9rem;color:var(--text-secondary);margin-bottom:0.75rem;font-family:var(--font-display)">AI EXPLANATION</h4>
        <p style="font-size:0.9rem;color:var(--text-secondary);line-height:1.7">${data.explanation}</p>

        ${data.top_features?.length ? `
        <div style="margin-top:1.25rem">
          <h4 style="font-size:0.9rem;color:var(--text-secondary);margin-bottom:0.75rem;font-family:var(--font-display)">KEY SIGNAL WORDS</h4>
          <div class="features-tags">
            ${data.top_features.map(f => `<span class="feature-tag">${f.word}</span>`).join('')}
          </div>
        </div>` : ''}

        <div style="display:flex;gap:0.75rem;margin-top:1.5rem;flex-wrap:wrap">
          <button onclick="Detector.shareResult('${data.result}', ${data.confidence})" class="btn btn-ghost btn-sm">📤 Share</button>
          <button onclick="Detector.reset()" class="btn btn-ghost btn-sm">🔄 Analyze Another</button>
        </div>
      </div>
    `;

    section.classList.remove('hidden');
    section.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    // Animate bars
    setTimeout(() => {
      section.querySelectorAll('.prob-bar-fill').forEach(bar => {
        bar.style.width = bar.dataset.width + '%';
      });
    }, 100);
  },

  reset() {
    document.getElementById('news-text').value = '';
    document.getElementById('result-section').classList.add('hidden');
    document.getElementById('result-section').innerHTML = '';
    document.getElementById('char-count').textContent = '0 / 50,000';
    document.getElementById('news-text').focus();
  },

  shareResult(result, confidence) {
    const text = `I just analyzed an article with TruthCheck AI — verdict: ${result} (${confidence}% confidence)\nCheck it out: ${window.location.href}`;
    if (navigator.share) {
      navigator.share({ title: 'TruthCheck Result', text });
    } else {
      navigator.clipboard.writeText(text);
      Toast.show('Result copied to clipboard!', 'success');
    }
  }
};

// ── Auth forms ─────────────────────────────────────────────────────────────
const AuthForms = {
  init() {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');

    loginForm?.addEventListener('submit', async (e) => {
      e.preventDefault();
      await this.handleLogin(loginForm);
    });

    registerForm?.addEventListener('submit', async (e) => {
      e.preventDefault();
      await this.handleRegister(registerForm);
    });

    // Password toggles
    document.querySelectorAll('.input-toggle').forEach(toggle => {
      toggle.addEventListener('click', () => {
        const input = toggle.previousElementSibling;
        if (input.type === 'password') {
          input.type = 'text';
          toggle.textContent = '🙈';
        } else {
          input.type = 'password';
          toggle.textContent = '👁';
        }
      });
    });
  },

  async handleLogin(form) {
    const btn = form.querySelector('[type=submit]');
    const email = form.querySelector('[name=email]').value;
    const password = form.querySelector('[name=password]').value;

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Logging in…';

    try {
      const data = await API.post('/api/auth/login', { email, password });
      Auth.setToken(data.access_token);
      Auth.setUser(data.user);
      Toast.show(`Welcome back, ${data.user.username}! 👋`, 'success');
      setTimeout(() => window.location.href = '/dashboard', 1000);
    } catch (err) {
      Toast.show(err.message, 'error');
      btn.disabled = false;
      btn.textContent = 'Login';
    }
  },

  async handleRegister(form) {
    const btn = form.querySelector('[type=submit]');
    const username = form.querySelector('[name=username]').value;
    const email = form.querySelector('[name=email]').value;
    const password = form.querySelector('[name=password]').value;
    const confirm = form.querySelector('[name=confirm_password]')?.value;

    if (confirm !== undefined && password !== confirm) {
      Toast.show('Passwords do not match', 'error');
      return;
    }

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Creating account…';

    try {
      const data = await API.post('/api/auth/register', { username, email, password });
      Auth.setToken(data.access_token);
      Auth.setUser(data.user);
      Toast.show('Account created successfully! 🎉', 'success');
      setTimeout(() => window.location.href = '/dashboard', 1000);
    } catch (err) {
      Toast.show(err.message, 'error');
      btn.disabled = false;
      btn.textContent = 'Create Account';
    }
  }
};

// ── Dashboard ──────────────────────────────────────────────────────────────
const Dashboard = {
  async init() {
    const user = await Auth.check();
    if (!user) {
      Toast.show('Please login to view your dashboard', 'info');
      setTimeout(() => window.location.href = '/login', 1000);
      return;
    }

    document.querySelectorAll('.user-name').forEach(el => el.textContent = user.username);
    document.querySelectorAll('.user-email').forEach(el => el.textContent = user.email);

    await this.loadStats();
    await this.loadHistory();
    this.initChart();
  },

  async loadStats() {
    try {
      const stats = await API.get('/api/stats');
      document.getElementById('stat-total').textContent = stats.total;
      document.getElementById('stat-fake').textContent = stats.fake_count;
      document.getElementById('stat-real').textContent = stats.real_count;
      document.getElementById('stat-confidence').textContent = `${stats.avg_confidence}%`;
    } catch { /* no history yet */ }
  },

  async loadHistory(page = 1, search = '', filter = '') {
    const tbody = document.getElementById('history-tbody');
    if (!tbody) return;

    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:2rem;color:var(--text-muted)">
      <span class="spinner"></span> Loading history…
    </td></tr>`;

    try {
      const params = new URLSearchParams({ page, per_page: 10 });
      if (search) params.set('search', search);
      if (filter) params.set('result', filter);
      const data = await API.get(`/api/history?${params}`);

      if (!data.predictions.length) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:3rem;color:var(--text-muted)">
          No analysis history yet. <a href="/detect" style="color:var(--c-teal)">Analyze your first article →</a>
        </td></tr>`;
        return;
      }

      tbody.innerHTML = data.predictions.map(p => `
        <tr>
          <td style="max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${p.text}</td>
          <td><span class="badge ${p.result.toLowerCase()}">${p.result === 'FAKE' ? '🚨' : '✅'} ${p.result}</span></td>
          <td><span style="font-family:var(--font-mono);font-weight:700">${p.confidence}%</span></td>
          <td style="font-family:var(--font-mono);font-size:0.8rem">${p.credibility_score ?? '-'}</td>
          <td style="font-size:0.8rem;color:var(--text-muted)">${new Date(p.created_at).toLocaleDateString()}</td>
          <td><button class="btn btn-ghost btn-sm" onclick="Dashboard.showDetail(${p.id})">View</button></td>
        </tr>
      `).join('');
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--c-red);padding:2rem">${err.message}</td></tr>`;
    }
  },

  initChart() {
    const canvas = document.getElementById('stats-chart');
    if (!canvas || typeof Chart === 'undefined') return;
    const fake = parseInt(document.getElementById('stat-fake')?.textContent) || 0;
    const real = parseInt(document.getElementById('stat-real')?.textContent) || 0;
    new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels: ['Fake', 'Real'],
        datasets: [{
          data: [fake, real],
          backgroundColor: ['rgba(255,59,92,0.8)', 'rgba(16,185,129,0.8)'],
          borderColor: ['rgba(255,59,92,1)', 'rgba(16,185,129,1)'],
          borderWidth: 2,
          borderRadius: 4,
        }]
      },
      options: {
        responsive: true,
        cutout: '72%',
        plugins: {
          legend: {
            labels: { color: 'rgba(255,255,255,0.6)', font: { family: 'DM Sans', size: 12 } }
          }
        }
      }
    });
  }
};

// ── Admin panel ────────────────────────────────────────────────────────────
const AdminPanel = {
  async init() {
    const user = await Auth.check();
    if (!user?.is_admin) {
      Toast.show('Admin access required', 'error');
      setTimeout(() => window.location.href = '/', 1000);
      return;
    }
    await this.loadDashboard();
    await this.loadUsers();
    await this.loadPredictions();
  },

  async loadDashboard() {
    try {
      const data = await API.get('/api/admin/dashboard');
      document.getElementById('admin-total-users').textContent = data.total_users;
      document.getElementById('admin-active-users').textContent = data.active_users;
      document.getElementById('admin-total-preds').textContent = data.total_predictions;
      document.getElementById('admin-fake-preds').textContent = data.fake_predictions;
    } catch (err) { Toast.show(err.message, 'error'); }
  },

  async loadUsers() {
    const tbody = document.getElementById('admin-users-tbody');
    if (!tbody) return;
    try {
      const data = await API.get('/api/admin/users');
      tbody.innerHTML = data.users.map(u => `
        <tr>
          <td>${u.id}</td>
          <td>${u.username}</td>
          <td>${u.email}</td>
          <td><span class="badge ${u.is_admin ? 'real' : 'fake'}">${u.is_admin ? 'Admin' : 'User'}</span></td>
          <td><span class="badge ${u.is_active ? 'real' : 'fake'}">${u.is_active ? 'Active' : 'Inactive'}</span></td>
          <td>${u.prediction_count}</td>
          <td>
            ${!u.is_admin ? `<button class="btn btn-ghost btn-sm" onclick="AdminPanel.toggleUser(${u.id}, this)">${u.is_active ? 'Deactivate' : 'Activate'}</button>` : '—'}
          </td>
        </tr>
      `).join('');
    } catch (err) { Toast.show(err.message, 'error'); }
  },

  async loadPredictions() {
    const tbody = document.getElementById('admin-preds-tbody');
    if (!tbody) return;
    try {
      const data = await API.get('/api/admin/predictions');
      tbody.innerHTML = data.predictions.map(p => `
        <tr>
          <td>${p.id}</td>
          <td>${p.user_id || 'Anonymous'}</td>
          <td style="max-width:250px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${p.text}</td>
          <td><span class="badge ${p.result.toLowerCase()}">${p.result}</span></td>
          <td>${p.confidence}%</td>
          <td style="font-size:0.8rem;color:var(--text-muted)">${new Date(p.created_at).toLocaleDateString()}</td>
        </tr>
      `).join('');
    } catch {}
  },

  async toggleUser(userId, btn) {
    try {
      const data = await API.post(`/api/admin/users/${userId}/toggle`);
      Toast.show(data.message, 'success');
      btn.textContent = data.user.is_active ? 'Deactivate' : 'Activate';
      await this.loadDashboard();
    } catch (err) { Toast.show(err.message, 'error'); }
  }
};

// ── DOM Ready ──────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  Theme.init();
  Toast.init();
  Navbar.init();
  Reveal.init();

  const page = document.body.dataset.page;

  if (page === 'home') {
    Particles.init();
    // Animate counters
    const counterObserver = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          const el = e.target;
          const target = parseInt(el.dataset.target);
          const suffix = el.dataset.suffix || '';
          animateCounter(el, target, suffix);
          counterObserver.unobserve(el);
        }
      });
    }, { threshold: 0.5 });
    document.querySelectorAll('[data-target]').forEach(el => counterObserver.observe(el));
  }

  if (page === 'detect') Detector.init();
  if (page === 'auth') AuthForms.init();
  if (page === 'dashboard') Dashboard.init();
  if (page === 'admin') AdminPanel.init();

  // Theme toggle
  document.querySelectorAll('.theme-toggle').forEach(btn => {
    btn.addEventListener('click', () => Theme.toggle());
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const target = document.querySelector(a.getAttribute('href'));
      if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
    });
  });
});
