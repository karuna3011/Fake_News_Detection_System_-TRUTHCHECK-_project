from database.db import db
from datetime import datetime

class Prediction(db.Model):
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    text = db.Column(db.Text, nullable=False)
    source_url = db.Column(db.String(500), nullable=True)
    result = db.Column(db.String(10), nullable=False)  # 'FAKE' or 'REAL'
    confidence = db.Column(db.Float, nullable=False)
    fake_probability = db.Column(db.Float, nullable=False)
    real_probability = db.Column(db.Float, nullable=False)
    explanation = db.Column(db.Text, nullable=True)
    top_features = db.Column(db.Text, nullable=True)  # JSON string
    language = db.Column(db.String(10), default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'user_id': self.user_id,
            'text': self.text[:200] + '...' if len(self.text) > 200 else self.text,
            'source_url': self.source_url,
            'result': self.result,
            'confidence': self.confidence,
            'fake_probability': self.fake_probability,
            'real_probability': self.real_probability,
            'explanation': self.explanation,
            'top_features': json.loads(self.top_features) if self.top_features else [],
            'language': self.language,
            'created_at': self.created_at.isoformat()
        }
