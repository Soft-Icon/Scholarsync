import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Initialize database with Flask app"""
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # Import all models to ensure they are registered
        from src.models.user import User
        from src.models.scholarship import Scholarship
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

