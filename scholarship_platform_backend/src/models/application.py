from src.database import db
from datetime import datetime

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scholarship_id = db.Column(db.Integer, db.ForeignKey('scholarship.id'), nullable=False)
    status = db.Column(db.String(50), default='Draft')  # Draft, Submitted, Under Review, Awaiting Result, etc.
    applied_date = db.Column(db.DateTime)
    match_percentage = db.Column(db.Float)  # AI-calculated match percentage
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Application {self.user_id} -> {self.scholarship_id}>'

