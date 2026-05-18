from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from database.db import db
from models.prediction import Prediction
from ai_model.detector import get_detector
import json, logging, re

predict_bp = Blueprint('predict', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

def _scrape_url(url: str) -> str:
    """Attempt to scrape article text from a URL."""
    try:
        import requests
        from bs4 import BeautifulSoup
        headers = {'User-Agent': 'Mozilla/5.0 (TruthCheck/1.0)'}
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        paragraphs = soup.find_all('p')
        text = ' '.join(p.get_text(strip=True) for p in paragraphs)
        return text[:5000]
    except Exception as e:
        logger.warning(f"URL scrape failed: {e}")
        return ''

@predict_bp.route('/predict', methods=['POST'])
def predict():
    user_id = None
    try:
        verify_jwt_in_request(optional=True)
        uid = get_jwt_identity()
        user_id = int(uid) if uid else None
    except Exception:
        pass

    data = request.get_json() or {}
    text = data.get('text', '').strip()
    url = data.get('url', '').strip()

    if url and not text:
        scraped = _scrape_url(url)
        if scraped:
            text = scraped
        else:
            return jsonify({'error': 'Could not extract text from URL'}), 422

    if not text:
        return jsonify({'error': 'Text or URL is required'}), 400
    if len(text) < 20:
        return jsonify({'error': 'Text too short for analysis (minimum 20 characters)'}), 400
    if len(text) > 50000:
        return jsonify({'error': 'Text too long (maximum 50,000 characters)'}), 400

    detector = get_detector()
    result = detector.predict(text)

    prediction = Prediction(
        user_id=user_id,
        text=text,
        source_url=url or None,
        result=result['result'],
        confidence=result['confidence'],
        fake_probability=result['fake_probability'],
        real_probability=result['real_probability'],
        explanation=result['explanation'],
        top_features=json.dumps(result['top_features']),
        ip_address=request.remote_addr,
    )
    db.session.add(prediction)
    db.session.commit()

    return jsonify({
        'id': prediction.id,
        **result
    })

@predict_bp.route('/history', methods=['GET'])
@jwt_required()
def history():
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '').strip()
    filter_result = request.args.get('result', '').upper()

    query = Prediction.query.filter_by(user_id=user_id)
    if search:
        query = query.filter(Prediction.text.ilike(f'%{search}%'))
    if filter_result in ('FAKE', 'REAL'):
        query = query.filter_by(result=filter_result)

    paginated = query.order_by(Prediction.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'predictions': [p.to_dict() for p in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': paginated.page,
    })

@predict_bp.route('/stats', methods=['GET'])
@jwt_required()
def stats():
    user_id = int(get_jwt_identity())
    predictions = Prediction.query.filter_by(user_id=user_id).all()

    total = len(predictions)
    fake_count = sum(1 for p in predictions if p.result == 'FAKE')
    real_count = total - fake_count
    avg_conf = round(sum(p.confidence for p in predictions) / total, 1) if total else 0

    return jsonify({
        'total': total,
        'fake_count': fake_count,
        'real_count': real_count,
        'avg_confidence': avg_conf,
        'fake_percentage': round((fake_count / total * 100), 1) if total else 0,
    })
