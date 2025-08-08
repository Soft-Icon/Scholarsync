from src.database import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    state_of_origin = db.Column(db.String(100))
    gender = db.Column(db.String(20))
    religion = db.Column(db.String(100))
    level_of_study = db.Column(db.String(100))
    institution = db.Column(db.String(255))
    course_of_study = db.Column(db.String(255))
    academic_performance = db.Column(db.String(100))  # e.g., CGPA, Grade
    skills_interests = db.Column(db.Text)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('Application', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

