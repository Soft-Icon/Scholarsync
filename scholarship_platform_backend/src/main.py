import os
import sys
from flask import Flask
from flask_cors import CORS

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.database import init_db
from src.routes.auth import auth_bp
from src.routes.scholarships import scholarships_bp
from src.routes.applications import applications_bp
from src.routes.profile import profile_bp
from src.routes.ai_assistant import ai_assistant_bp
from src.services.scraper_service import ScraperService
from src.models.scholarship import Scholarship

def create_app():
    app = Flask(__name__)
    
    # --- Flask Configuration ---
    app.config['SECRET_KEY'] = 'jamiu9@youcanchangeit'
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'   # not 'None'
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = False
    app.config['SESSION_PERMANENT'] = True

    # --- Enable CORS ---
    CORS(
        app,
        supports_credentials=True,
        origins=["http://localhost:5173"]  # ✅ Your React frontend origin
    )

    # --- Register Blueprints ---
    app.register_blueprint(auth_bp)
    app.register_blueprint(scholarships_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(ai_assistant_bp)

    # --- Initialize Database ---
    init_db(app)

    # --- Initial Scrape ---
    with app.app_context():
        if Scholarship.query.count() == 0:
            print("No scholarships found in database. Initiating initial scrape...")
            scraper = ScraperService()
            scraper.run_spider()
            print("Initial scrape completed.")
        else:
            print(f"{Scholarship.query.count()} scholarships already in database.")

    return app

# --- App Entry Point ---
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
