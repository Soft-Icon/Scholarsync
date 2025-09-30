from flask import Blueprint, request, jsonify, session
from src.models.user import User
from src.database import db

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    print("DEBUG: Signup data received -", data)
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    user = User(
        full_name=data['full_name'],
        email=data['email'],
        state_of_origin=data.get('state_of_origin'),
        gender=data.get('gender'),
        religion=data.get('religion'),
        level_of_study=data.get('level_of_study'),
        institution=data.get('institution'),
        course_of_study=data.get('course_of_study'),
        academic_performance=data.get('academic_performance'),
        skills_interests=data.get('skills_interests')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    print(f"DEBUG: New user created with ID {user.id}")
    
    # 🔑 automatically log in the new user
    session['user_id'] = user.id
    print(f"DEBUG: signup - set session user_id: {session['user_id']}")
    session['is_admin'] = user.is_admin


    return jsonify({
        'message': 'User created successfully',
        'user': {
            'id': user.id,
            'full_name': user.full_name,
            'email': user.email
        }
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and user.check_password(data['password']):
        session['user_id'] = user.id
        session['is_admin'] = user.is_admin
        print(f"DEBUG: Session after login - user_id: {session.get('user_id')}, is_admin: {session.get('is_admin')}")
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email,
                'is_admin': user.is_admin
            }
        }), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    if 'user_id' not in session:
        print("DEBUG: get_current_user - user_id not in session")
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    print(f"DEBUG: get_current_user - session user_id: {session.get('user_id')}")
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
        'skills_interests': user.skills_interests,
        'is_admin': user.is_admin
    }), 200

