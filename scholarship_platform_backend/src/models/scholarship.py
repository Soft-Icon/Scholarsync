from src.database import db

class Scholarship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255), nullable=False, unique=True)
    deadline = db.Column(db.String(255))
    eligibility = db.Column(db.Text)
    country = db.Column(db.String(100))
    source = db.Column(db.String(100))
    provider_organization = db.Column(db.String(255))
    level_of_study = db.Column(db.String(100))
    field_of_study = db.Column(db.String(255))
    amount_benefits = db.Column(db.Text)
    application_link = db.Column(db.String(255))
    contact_email = db.Column(db.String(255))
    supporting_files = db.Column(db.Text)  # JSON or comma-separated list
    
    # Relationships
    applications = db.relationship('Application', backref='scholarship', lazy=True)

    def __repr__(self):
        return f'<Scholarship {self.title}>'


