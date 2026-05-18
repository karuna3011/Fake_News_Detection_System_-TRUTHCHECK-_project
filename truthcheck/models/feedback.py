from database.db import db
from datetime import datetime

class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    prediction_id = db.Column(db.Integer, db.ForeignKey('predictions.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    rating = db.Column(db.Integer, nullable=True)  # 1-5
    comment = db.Column(db.Text, nullable=True)
    is_correct = db.Column(db.Boolean, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
