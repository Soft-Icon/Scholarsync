from flask import Blueprint, request, jsonify, session
from src.models.user import User
from src.database import db

profile_bp = Blueprint('profile', __name__, url_prefix='/api/profile')

@profile_bp.route('/', methods=['GET'])
def get_profile():
    if 'user_id' not in session:
        print("DEBUG: Unauthorized access attempt to get_profile, no user_id in session and can't retrieve user")
        return jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'full_name': user.full_name,
        'email': user.email,
        'state_of_origin': user.state_of_origin,
        'gender': user.gender,
        'religion': user.religion,
        'level_of_study': user.level_of_study,
        'institution': user.institution,
        'course_of_study': user.course_of_study,
        'academic_performance': user.academic_performance,
        'skills_interests': user.skills_interests
    }), 200

@profile_bp.route('/', methods=['PUT'])
def update_profile():
    if 'user_id' not in session:
        print("DEBUG: Unauthorized access attempt to update_profile, no user_id in session and can't update user")
        return jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    user.full_name = data.get('full_name', user.full_name)
    user.state_of_origin = data.get('state_of_origin', user.state_of_origin)
    user.gender = data.get('gender', user.gender)
    user.religion = data.get('religion', user.religion)
    user.level_of_study = data.get('level_of_study', user.level_of_study)
    user.institution = data.get('institution', user.institution)
    user.course_of_study = data.get('course_of_study', user.course_of_study)
    user.academic_performance = data.get('academic_performance', user.academic_performance)
    user.skills_interests = data.get('skills_interests', user.skills_interests)
    
    db.session.commit()
    
    return jsonify({'message': 'Profile updated successfully'}), 200

@profile_bp.route('/completion', methods=['GET'])
def get_profile_completion():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Calculate profile completion percentage
    fields = [
        user.full_name, user.email, user.state_of_origin, user.gender,
        user.religion, user.level_of_study, user.institution,
        user.course_of_study, user.academic_performance, user.skills_interests
    ]
    
    completed_fields = sum(1 for field in fields if field and field.strip())
    completion_percentage = (completed_fields / len(fields)) * 100
    
    return jsonify({
        'completion_percentage': round(completion_percentage),
        'completed_fields': completed_fields,
        'total_fields': len(fields)
    }), 200

