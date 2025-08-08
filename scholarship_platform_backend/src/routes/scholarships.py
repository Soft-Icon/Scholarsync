from flask import Blueprint, request, jsonify, session
from src.models.scholarship import Scholarship
from src.models.application import Application
from src.database import db

scholarships_bp = Blueprint('scholarships', __name__, url_prefix='/api/scholarships')

@scholarships_bp.route('/', methods=['GET'])
def get_scholarships():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Filters
    country = request.args.get('country')
    level = request.args.get('level')
    field = request.args.get('field')
    deadline = request.args.get('deadline')
    
    query = Scholarship.query
    
    if country:
        query = query.filter(Scholarship.country.ilike(f'%{country}%'))
    if level:
        query = query.filter(Scholarship.level_of_study.ilike(f'%{level}%'))
    if field:
        query = query.filter(Scholarship.field_of_study.ilike(f'%{field}%'))
    if deadline:
        query = query.filter(Scholarship.deadline.ilike(f'%{deadline}%'))
    
    scholarships = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'scholarships': [{
            'id': s.id,
            'title': s.title,
            'link': s.link,
            'deadline': s.deadline,
            'eligibility': s.eligibility,
            'country': s.country,
            'provider_organization': s.provider_organization,
            'level_of_study': s.level_of_study,
            'field_of_study': s.field_of_study,
            'amount_benefits': s.amount_benefits,
            'application_link': s.application_link
        } for s in scholarships.items],
        'total': scholarships.total,
        'pages': scholarships.pages,
        'current_page': page
    }), 200

@scholarships_bp.route('/<int:scholarship_id>', methods=['GET'])
def get_scholarship(scholarship_id):
    scholarship = Scholarship.query.get_or_404(scholarship_id)
    
    return jsonify({
        'id': scholarship.id,
        'title': scholarship.title,
        'link': scholarship.link,
        'deadline': scholarship.deadline,
        'eligibility': scholarship.eligibility,
        'country': scholarship.country,
        'provider_organization': scholarship.provider_organization,
        'level_of_study': scholarship.level_of_study,
        'field_of_study': scholarship.field_of_study,
        'amount_benefits': scholarship.amount_benefits,
        'application_link': scholarship.application_link,
        'contact_email': scholarship.contact_email,
        'supporting_files': scholarship.supporting_files
    }), 200

@scholarships_bp.route('/', methods=['POST'])
def create_scholarship():
    # Admin only
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    scholarship = Scholarship(
        title=data['title'],
        link=data.get('link', ''),
        deadline=data.get('deadline'),
        eligibility=data.get('eligibility'),
        country=data.get('country'),
        provider_organization=data.get('provider_organization'),
        level_of_study=data.get('level_of_study'),
        field_of_study=data.get('field_of_study'),
        amount_benefits=data.get('amount_benefits'),
        application_link=data.get('application_link'),
        contact_email=data.get('contact_email'),
        supporting_files=data.get('supporting_files'),
        source='manual'
    )
    
    db.session.add(scholarship)
    db.session.commit()
    
    return jsonify({'message': 'Scholarship created successfully', 'id': scholarship.id}), 201

@scholarships_bp.route('/suggested', methods=['GET'])
def get_suggested_scholarships():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    # Get user's applications with match percentages
    applications = db.session.query(Application, Scholarship).join(
        Scholarship, Application.scholarship_id == Scholarship.id
    ).filter(Application.user_id == user_id).all()
    
    suggested = []
    for app, scholarship in applications:
        suggested.append({
            'id': scholarship.id,
            'title': scholarship.title,
            'country': scholarship.country,
            'deadline': scholarship.deadline,
            'level_of_study': scholarship.level_of_study,
            'field_of_study': scholarship.field_of_study,
            'match_percentage': app.match_percentage or 0,
            'application_status': app.status,
            'applied_date': app.applied_date.isoformat() if app.applied_date else None
        })
    
    # Sort by match percentage
    suggested.sort(key=lambda x: x['match_percentage'], reverse=True)
    
    return jsonify({'suggested_scholarships': suggested}), 200

