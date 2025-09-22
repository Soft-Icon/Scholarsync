import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.database import init_db
from src.routes.auth import auth_bp
from src.routes.scholarships import scholarships_bp
from src.routes.applications import applications_bp
from src.routes.profile import profile_bp
from src.routes.ai_assistant import ai_assistant_bp
from src.services.scraper_service import ScraperService
from src.models.scholarship import Scholarship

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['SESSION_COOKIE_SAMESITE'] = 'None' # Required for cross-site cookies in modern browsers
app.config['SESSION_COOKIE_SECURE'] = False # Set to False for local HTTP development, True for HTTPS in production

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173"], "supports_credentials": True}})

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(scholarships_bp)
app.register_blueprint(applications_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(ai_assistant_bp)

# Initialize database
init_db(app)

# Perform initial scrape if no scholarships exist
with app.app_context():
    if Scholarship.query.count() == 0:
        print("No scholarships found in database. Initiating initial scrape...")
        scraper = ScraperService()
        scraper.run_spider()
        print("Initial scrape completed.")
    else:
        print(f"{Scholarship.query.count()} scholarships already in database.")


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

