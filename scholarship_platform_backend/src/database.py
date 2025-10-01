import os
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.orm import sessionmaker
from .models import Scholarship

db = SQLAlchemy()

def init_db(app):
    """Initialize database with Flask app"""
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # Import all models to ensure they are registered
        from src.models.user import User
        from src.models.scholarship import Scholarship, SuggestedScholarship
        from src.models.application import Application
        
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin_user = User.query.filter_by(email='admin@scholarsync.com').first()
        if not admin_user:
            admin_user = User(
                full_name='Admin User',
                email='admin@scholarsync.com',
                is_admin=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created: admin@scholarsync.com / admin123")



def sync_from_scraper_db():
    """
    Copy all rows from scraper DB’s scholarships table into Flask DB.
    """
    # Get scraper DB URL (you might store in config)
    scraper_db_url = current_app.config.get("SCRAPER_DATABASE_URI")
    if not scraper_db_url:
        current_app.logger.warning("No SCRAPER_DATABASE_URI configured, skipping sync")
        return

    # Set up a SQLAlchemy engine & metadata for scraper DB
    engine = create_engine(scraper_db_url)
    metadata = MetaData(bind=engine)
    # reflect the scraper table
    scraper_table = Table("scholarships", metadata, autoload_with=engine)

    # set up a session for scraper DB
    ScraperSession = sessionmaker(bind=engine)
    scr_session = ScraperSession()

    # Use Flask app’s session for target
    # db.session is the SQLAlchemy session for Flask DB
    try:
        # read all rows
        rows = scr_session.execute(select(scraper_table)).all()
        for row in rows:
            # row is a Row mapping (depending on version)
            data = dict(row._mapping) if hasattr(row, "_mapping") else dict(row)

            # Check for existing by source_url (or some unique field)
            existing = Scholarship.query.filter_by(source_url=data.get("source_url")).first()
            if existing:
                # maybe update fields
                # e.g. existing.title = data.get("title")
                continue

            # Create new Scholarship instance
            sch = Scholarship(
                title=data.get("title") or "",
                description=data.get("description"),
                provider_organization=data.get("provider_organization"),
                deadline=data.get("deadline"),
                country_info=data.get("country_info"),
                level_of_study=data.get("level_of_study"),
                field_of_study=data.get("field_of_study"),
                eligibility=data.get("eligibility"),
                academic_requirements=data.get("academic_requirements"),
                cgpa_requirements=data.get("cgpa_requirements"),
                amount_benefits=data.get("amount_benefits"),
                application_link=data.get("application_link"),
                contact_email=data.get("contact_email"),
                keywords=data.get("keywords"),
                source_url=data.get("source_url"),
                source_website=data.get("source_website"),
                extracted_date=data.get("extracted_date"),
            )
            db.session.add(sch)

        # commit all at once
        db.session.commit()

    except Exception as e:
        current_app.logger.error("Error syncing from scraper DB: %s", e)
        db.session.rollback()
    finally:
        scr_session.close()
