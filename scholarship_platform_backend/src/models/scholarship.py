from src.database import db

class Scholarship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    provider_organization = db.Column(db.String(255))
    deadline = db.Column(db.String(255))
    country_info = db.Column(db.String(100))
    level_of_study = db.Column(db.String(100))
    field_of_study = db.Column(db.String(255))
    eligibility = db.Column(db.Text)
    academic_requirements = db.Column(db.Text)
    cgpa_requirements = db.Column(db.Text)
    amount_benefits = db.Column(db.Text)
    application_link = db.Column(db.String(255))
    contact_email = db.Column(db.String(255))
    keywords = db.Column(db.Text)  # Store as JSON string
    source_url = db.Column(db.String(255), nullable=False, unique=True)
    source_website = db.Column(db.String(100))
    extracted_date = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Relationships
    applications = db.relationship('Application', backref='scholarship', lazy=True)

    def __repr__(self):
        return f'<Scholarship {self.title}>'


