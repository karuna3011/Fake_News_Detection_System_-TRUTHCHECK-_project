"""
TruthCheck — AI-Powered Fake News Detection Platform
Flask Application Entry Point
"""

import os
import sys
import logging
from datetime import timedelta
from flask import Flask, render_template, jsonify, send_from_directory
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# ── ensure project root is on sys.path ───────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from database.db import db, init_db
from routes.auth import auth_bp
from routes.predict import predict_bp
from routes.admin import admin_bp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger(__name__)

# ── factory ───────────────────────────────────────────────────────────────────

def create_app(config: dict | None = None) -> Flask:
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static',
    )

    # ── Config ────────────────────────────────────────────────────────────────
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'truthcheck-super-secret-key-2025'),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'DATABASE_URL', f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'truthcheck.db')}"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-truthcheck-2025'),
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=24),
        JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=30),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16 MB max upload
    )
    if config:
        app.config.update(config)

    # ── Extensions ────────────────────────────────────────────────────────────
    CORS(app, origins=['*'])
    JWTManager(app)

    # ── Database ──────────────────────────────────────────────────────────────
    init_db(app)

    # ── Blueprints ────────────────────────────────────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(admin_bp)

    # ── Page routes ───────────────────────────────────────────────────────────
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/detect')
    def detect():
        return render_template('detect.html')

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/admin')
    def admin_panel():
        return render_template('admin.html')

    @app.route('/login')
    def login_page():
        return render_template('auth.html', mode='login')

    @app.route('/register')
    def register_page():
        return render_template('auth.html', mode='register')

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/pricing')
    def pricing():
        return render_template('pricing.html')

    @app.route('/contact')
    def contact():
        return render_template('contact.html')

    # ── Health ────────────────────────────────────────────────────────────────
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok', 'service': 'TruthCheck API', 'version': '1.0.0'})

    # ── Error handlers ────────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        if '/api/' in str(e):
            return jsonify({'error': 'Endpoint not found'}), 404
        return render_template('index.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"500 error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    logger.info(f"🚀 TruthCheck running on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
