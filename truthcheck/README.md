# 🔍 TruthCheck — AI-Powered Fake News Detection Platform

A premium, full-stack SaaS application that uses machine learning to detect fake news in real time. Built with Flask, scikit-learn, SQLite/PostgreSQL, and a beautiful glassmorphism UI.

![TruthCheck Banner](https://via.placeholder.com/1200x400/080b14/00d4aa?text=TruthCheck+AI)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 AI Detection | TF-IDF + Logistic Regression / PassiveAggressiveClassifier |
| 📊 Confidence Scores | Probability breakdown with visual bars |
| 🌐 URL Scraping | Auto-extract article text from any URL |
| 👤 Auth System | JWT authentication with bcrypt password hashing |
| 📋 Dashboard | Personal history, search, filter, charts |
| 🛡 Admin Panel | User management, prediction monitoring |
| 🌙 Dark/Light Mode | Premium glassmorphism UI with theme toggle |
| 📱 Responsive | Mobile-first design across all pages |
| 🔌 REST API | Full API with JWT auth for integrations |
| 🐳 Docker Ready | One-command deployment |

---

## 🗂 Project Structure

```
truthcheck/
├── app.py                  # Flask application factory
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker container config
├── docker-compose.yml      # Docker Compose setup
├── .env.example            # Environment variable template
│
├── models/                 # SQLAlchemy ORM models
│   ├── user.py             # User model
│   ├── prediction.py       # Prediction model
│   └── feedback.py         # Feedback model
│
├── routes/                 # Flask blueprints
│   ├── auth.py             # /api/auth/* endpoints
│   ├── predict.py          # /api/predict, /api/history, /api/stats
│   └── admin.py            # /api/admin/* endpoints
│
├── ai_model/               # Machine learning engine
│   └── detector.py         # FakeNewsDetector class
│
├── database/               # Database layer
│   └── db.py               # SQLAlchemy + seed function
│
├── utils/                  # Shared utilities
│   └── helpers.py          # Text sanitization, validators
│
├── static/
│   ├── css/main.css        # Complete design system
│   └── js/main.js          # All frontend interactions
│
└── templates/              # Jinja2 HTML templates
    ├── base.html           # Base layout with nav/footer
    ├── index.html          # Landing page
    ├── detect.html         # Detection tool
    ├── auth.html           # Login / Register
    ├── dashboard.html      # User dashboard
    ├── admin.html          # Admin panel
    ├── pricing.html        # Pricing page
    ├── about.html          # About page
    └── contact.html        # Contact page
```

---

## 🚀 Quick Start

### Option 1: Local Development

**1. Clone the repository**
```bash
git clone https://github.com/yourname/truthcheck.git
cd truthcheck
```

**2. Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings (defaults work for local dev)
```

**5. Run the application**
```bash
python app.py
```

**6. Open your browser**
```
http://localhost:5000
```

> On first run, the database is created automatically and an admin user is seeded:
> **Email:** admin@truthcheck.ai | **Password:** Admin@123!

---

### Option 2: Docker Deployment

```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 🔌 API Reference

All API endpoints return JSON. Protected routes require an `Authorization: Bearer <token>` header.

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create new account |
| POST | `/api/auth/login` | Login and get JWT token |
| GET | `/api/auth/me` | Get current user info |
| POST | `/api/auth/refresh` | Refresh access token |

**Register example:**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@example.com","password":"MyPass123"}'
```

**Login example:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"MyPass123"}'
```

---

### Prediction

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/predict` | Optional | Analyze text or URL |
| GET | `/api/history` | Required | Get user's prediction history |
| GET | `/api/stats` | Required | Get user statistics |

**Analyze text:**
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "SHOCKING: Scientists hide miracle cure..."}'
```

**Response:**
```json
{
  "id": 42,
  "result": "FAKE",
  "confidence": 87.3,
  "fake_probability": 87.3,
  "real_probability": 12.7,
  "credibility_score": 12.7,
  "explanation": "The AI model classified this as FAKE...",
  "top_features": [
    {"word": "shocking", "score": 0.432},
    {"word": "miracle", "score": 0.387}
  ],
  "word_count": 45
}
```

**Analyze URL:**
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/news-article"}'
```

---

### Admin (Admin JWT required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/dashboard` | System statistics |
| GET | `/api/admin/users` | List all users |
| POST | `/api/admin/users/<id>/toggle` | Activate/deactivate user |
| GET | `/api/admin/predictions` | All predictions |

---

## 🧠 AI Model Details

### Algorithm Pipeline
```
Raw Text
  → Preprocessing (lowercase, URL/email removal, punctuation)
  → TF-IDF Vectorization (10,000 features, n-gram 1–3, sublinear TF)
  → Logistic Regression (C=1.0, balanced class weights)
  → Probability Output → Result + Confidence Score
```

### Model Training
The model auto-trains on a synthetic dataset of 60 articles (30 fake, 30 real) on first run and saves to `ai_model/fake_news_model.pkl`.

**To retrain on your own dataset**, upload a CSV with columns:
- `text` — the article text
- `label` — either `FAKE` or `REAL`

Use the Admin Panel → AI Model → Upload Dataset, or call the internal `train_on_dataframe()` method.

### Recommended Public Datasets
- [Fake and Real News Dataset (Kaggle)](https://www.kaggle.com/clmentbisaillon/fake-and-real-news-dataset)
- [LIAR Dataset](https://paperswithcode.com/dataset/liar)
- [FakeNewsNet](https://github.com/KaiDMML/FakeNewsNet)

---

## 🎨 Frontend Architecture

### Design System
- **Fonts:** Syne (display/headings) + DM Sans (body) + JetBrains Mono (code)
- **Colors:** Teal `#00d4aa` primary, Blue `#0099ff`, Purple `#7c3aed`
- **Theme:** Glassmorphism with `backdrop-filter: blur()` on all cards
- **Animations:** CSS keyframes + IntersectionObserver scroll reveals
- **Charts:** Chart.js 4.x (doughnut + bar charts)

### JavaScript Modules
| Module | Purpose |
|--------|---------|
| `Theme` | Dark/light mode toggle with localStorage |
| `Auth` | JWT token management, login/register |
| `API` | Fetch wrapper with auto auth headers |
| `Toast` | Notification system |
| `Particles` | Canvas-based animated background |
| `Reveal` | IntersectionObserver scroll animations |
| `Detector` | Detection tool logic |
| `Dashboard` | User dashboard data loading |
| `AdminPanel` | Admin panel data management |

---

## 🔧 Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `truthcheck-super-secret-key-2025` | Flask session secret |
| `JWT_SECRET_KEY` | `jwt-secret-key-truthcheck-2025` | JWT signing key |
| `DATABASE_URL` | SQLite in `/database/` | Database connection string |
| `FLASK_DEBUG` | `1` | Debug mode (set to 0 in prod) |
| `PORT` | `5000` | Server port |

> ⚠️ **Always change SECRET_KEY and JWT_SECRET_KEY in production!**

---

## 🚀 Production Deployment

### Heroku
```bash
heroku create truthcheck-app
heroku config:set SECRET_KEY=your-secret JWT_SECRET_KEY=your-jwt-secret
git push heroku main
```

### Railway / Render
Set the start command to:
```
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2
```

### VPS (Ubuntu)
```bash
# Install dependencies
pip install -r requirements.txt gunicorn

# Run with gunicorn + nginx reverse proxy
gunicorn app:app --bind 0.0.0.0:5000 --workers 4 --daemon
```

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

Built with ❤️ and ☕ by the TruthCheck team.
