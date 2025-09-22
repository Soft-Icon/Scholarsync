from flask import Blueprint, request, jsonify, session
from src.models.user import User
from src.models.scholarship import Scholarship
from src.models.application import Application
from src.services.ai_service import AIService
from src.database import db
import datetime

ai_assistant_bp = Blueprint('ai_assistant', __name__, url_prefix='/api/ai')

ai_service = AIService()

@ai_assistant_bp.route('/chat', methods=['POST'])
def chat():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Get user profile for context
    user = User.query.get(session['user_id'])
    user_profile = {
        'full_name': user.full_name,
        'level_of_study': user.level_of_study,
        'course_of_study': user.course_of_study,
        'institution': user.institution,
        'academic_performance': user.academic_performance,
        'skills_interests': user.skills_interests
    } if user else {}
    
    try:
        ai_response = ai_service.generate_ai_response(user_message, user_profile)
        
        return jsonify({
            'response': ai_response,
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred: ' + str(e)}), 500

@ai_assistant_bp.route('/personal-statement-tips', methods=['POST'])
def personal_statement_tips():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    scholarship_id = data.get('scholarship_id')
    
    # Get user profile
    user = User.query.get(session['user_id'])
    user_profile = {
        'course_of_study': user.course_of_study,
        'level_of_study': user.level_of_study,
        'academic_performance': user.academic_performance,
        'skills_interests': user.skills_interests
    } if user else {}
    
    # Get scholarship info if provided
    scholarship_info = None
    if scholarship_id:
        scholarship = Scholarship.query.get(scholarship_id)
        if scholarship:
            scholarship_info = {
                'title': scholarship.title,
                'field_of_study': scholarship.field_of_study,
                'eligibility': scholarship.eligibility
            }
    
    try:
        tips = ai_service.generate_personal_statement_tips(user_profile, scholarship_info)
        
        return jsonify({
            'tips': tips
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred: ' + str(e)}), 500

@ai_assistant_bp.route('/match-scholarships', methods=['POST'])
def match_scholarships():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get user profile
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user_profile = {
        'level_of_study': user.level_of_study,
        'course_of_study': user.course_of_study,
        'institution': user.institution,
        'academic_performance': user.academic_performance,
        'state_of_origin': user.state_of_origin,
        'gender': user.gender,
        'religion': user.religion,
        'skills_interests': user.skills_interests
    }
    
    # Get all scholarships
    scholarships = Scholarship.query.all()
    
    scholarship_data = []
    for s in scholarships:
        scholarship_data.append({
            'id': s.id,
            'title': s.title,
            'level_of_study': s.level_of_study,
            'field_of_study': s.field_of_study,
            'country': s.country,
            'eligibility': s.eligibility,
            'deadline': s.deadline,
            'amount_benefits': s.amount_benefits,
            'application_link': s.application_link
        })
    
    try:
        recommendations = ai_service.get_scholarship_recommendations(user_profile, scholarship_data)
        
        # Update user's applications with match percentages
        for rec in recommendations:
            # Check if application exists
            existing_app = Application.query.filter_by(
                user_id=user.id,
                scholarship_id=rec['id']
            ).first()
            
            if existing_app:
                existing_app.match_percentage = rec['match_percentage']
            else:
                # Create new application with match percentage
                new_app = Application(
                    user_id=user.id,
                    scholarship_id=rec['id'],
                    match_percentage=rec['match_percentage'],
                    status='Draft'
                )
                db.session.add(new_app)
        
        db.session.commit()
        
        return jsonify({
            'recommendations': recommendations
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to generate recommendations or update applications: ' + str(e)}), 500

