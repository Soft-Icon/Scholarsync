from flask import Blueprint, request, jsonify, session
from src.models.application import Application
from src.models.scholarship import Scholarship
from src.database import db
from datetime import datetime

applications_bp = Blueprint('applications', __name__, url_prefix='/api/applications')

@applications_bp.route('/', methods=['GET'])
def get_user_applications():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    applications = db.session.query(Application, Scholarship).join(
        Scholarship, Application.scholarship_id == Scholarship.id
    ).filter(Application.user_id == user_id).all()
    
    result = []
    for app, scholarship in applications:
        result.append({
            'id': app.id,
            'scholarship_title': scholarship.title,
            'status': app.status,
            'applied_date': app.applied_date.isoformat() if app.applied_date else None,
            'match_percentage': app.match_percentage,
            'scholarship_deadline': scholarship.deadline,
            'scholarship_country': scholarship.country
        })
    
    return jsonify({'applications': result}), 200

@applications_bp.route('/', methods=['POST'])
def create_application():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    user_id = session['user_id']
    scholarship_id = data['scholarship_id']
    
    # Check if application already exists
    existing = Application.query.filter_by(
        user_id=user_id, 
        scholarship_id=scholarship_id
    ).first()
    
    if existing:
        return jsonify({'error': 'Application already exists'}), 400
    
    application = Application(
        user_id=user_id,
        scholarship_id=scholarship_id,
        status='Draft'
    )
    
    db.session.add(application)
    db.session.commit()
    
    return jsonify({'message': 'Application created successfully', 'id': application.id}), 201

@applications_bp.route('/<int:application_id>/submit', methods=['POST'])
def submit_application(application_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    application = Application.query.filter_by(
        id=application_id, 
        user_id=session['user_id']
    ).first_or_404()
    
    application.status = 'Submitted'
    application.applied_date = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': 'Application submitted successfully'}), 200

@applications_bp.route('/<int:application_id>', methods=['PUT'])
def update_application_status(application_id):
    # Admin only for status updates
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    application = Application.query.get_or_404(application_id)
    
    application.status = data.get('status', application.status)
    
    db.session.commit()
    
    return jsonify({'message': 'Application status updated successfully'}), 200

