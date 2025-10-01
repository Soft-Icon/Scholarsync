from flask import Blueprint, request, jsonify, session
from src.models.scholarship import Scholarship, SuggestedScholarship
from src.models.application import Application
from src.models.user import User
from src.services.scraper_service import ScraperService
from src.database import db
import json
from datetime import datetime

# Ensure the path for ai_service is correct if it's not a direct sibling of pipelines.py
# For debugging, we'll use a direct import, but consider a more robust import strategy if issues persist.
try:
    from src.services.ai_service import AIService as BackendAIService
except ImportError:
    BackendAIService = None # Fallback if not found


scholarships_bp = Blueprint('scholarships', __name__, url_prefix='/api/scholarships')

@scholarships_bp.route('/', methods=['GET'])
def get_scholarships():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Filters
    country_info = request.args.get('country_info')
    level = request.args.get('level')
    field = request.args.get('field')
    deadline = request.args.get('deadline')
    
    query = Scholarship.query
    
    if country_info:
        query = query.filter(Scholarship.country_info.ilike(f'%{country_info}%'))
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
            'description': s.description,
            'provider_organization': s.provider_organization,
            'deadline': s.deadline,
            'country_info': s.country_info,
            'level_of_study': s.level_of_study,
            'field_of_study': s.field_of_study,
            'eligibility': s.eligibility,
            'academic_requirements': s.academic_requirements,
            'cgpa_requirements': s.cgpa_requirements,
            'amount_benefits': s.amount_benefits,
            'application_link': s.application_link,
            'contact_email': s.contact_email,
            'keywords': json.loads(s.keywords) if s.keywords else [],
            'source_url': s.source_url,
            'source_website': s.source_website,
            'extracted_date': s.extracted_date,
            'created_at': s.created_at.isoformat() if s.created_at else None,
            'updated_at': s.updated_at.isoformat() if s.updated_at else None
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
        'description': scholarship.description,
        'provider_organization': scholarship.provider_organization,
        'deadline': scholarship.deadline,
        'country_info': scholarship.country_info,
        'level_of_study': scholarship.level_of_study,
        'field_of_study': scholarship.field_of_study,
        'eligibility': scholarship.eligibility,
        'academic_requirements': scholarship.academic_requirements,
        'cgpa_requirements': scholarship.cgpa_requirements,
        'amount_benefits': scholarship.amount_benefits,
        'application_link': scholarship.application_link,
        'contact_email': scholarship.contact_email,
        'keywords': json.loads(scholarship.keywords) if scholarship.keywords else [],
        'source_url': scholarship.source_url,
        'source_website': scholarship.source_website,
        'extracted_date': scholarship.extracted_date,
        'created_at': scholarship.created_at.isoformat() if scholarship.created_at else None,
        'updated_at': scholarship.updated_at.isoformat() if scholarship.updated_at else None
    }), 200

@scholarships_bp.route('/', methods=['POST'])
def create_scholarship():
    # Admin only
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.get_json()
    
    scholarship = Scholarship(
        title=data['title'],
        description=data.get('description', ''),
        provider_organization=data.get('provider_organization', ''),
        deadline=data.get('deadline', ''),
        country_info=data.get('country_info', ''),
        level_of_study=data.get('level_of_study', ''),
        field_of_study=data.get('field_of_study', ''),
        eligibility=data.get('eligibility', ''),
        academic_requirements=data.get('academic_requirements', ''),
        cgpa_requirements=data.get('cgpa_requirements', ''),
        amount_benefits=data.get('amount_benefits', ''),
        application_link=data.get('application_link', ''),
        contact_email=data.get('contact_email', ''),
        keywords=json.dumps(data.get('keywords', [])) if data.get('keywords') else '',
        source_url=data.get('source_url', ''),
        source_website=data.get('source_website', ''),
        extracted_date=data.get('extracted_date', datetime.now().isoformat())
    )
    
    db.session.add(scholarship)
    db.session.commit()
    
    return jsonify({'message': 'Scholarship created successfully', 'id': scholarship.id}), 201

@scholarships_bp.route('/suggested', methods=['GET'])
def get_suggested_scholarships():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = session['user_id']
    
    suggested_scholarships = SuggestedScholarship.query.filter_by(user_id=user_id)
    if not suggested_scholarships.count():
        all_scholarships = Scholarship.query.all()
        user_profile = User.query.get(user_id)
        if not user_profile:
            return jsonify({'error': 'User not found'}), 404
        
        if BackendAIService:
            try:
                ai_service_instance = BackendAIService()
                print("AIService instance created successfully.")
                print("Fetching suggested scholarships using AIService...")
                suggested_scholarships = ai_service_instance.get_suggested_scholarships(
                    user_profile=model_to_dict(user_profile),
                    scholarships=[model_to_dict(s) for s in all_scholarships]
                )
                print(f"Suggested Scholarships: ", suggested_scholarships)
                # Clear existing suggested scholarships
                SuggestedScholarship.query.filter_by(user_id=user_id).delete()
                db.session.commit()

                for sch in suggested_scholarships:
                    print(sch)
                    suggestion = SuggestedScholarship(
                        scholarship_id=sch['id'],
                        user_id=user_id,
                        match=sch.get('match_percentage', 0),
                        title=sch.get('title', '')
                    )
                    db.session.add(suggestion)
                db.session.commit()

            except Exception as e:
                print("Error fetching suggested scholarships:", e)
        else:
            print("AIService not available. Skipping AI-based suggestions.")
    
    suggested_scholarships = SuggestedScholarship.query.filter_by(user_id=user_id)
    if not suggested_scholarships.count():
        return jsonify({'message': 'No suggested scholarships available'}), 200
    else:
        suggested_ids = [s.scholarship_id for s in suggested_scholarships]
        scholarships = Scholarship.query.filter(Scholarship.id.in_(suggested_ids)).all()
        scholarship_map = {s.id: s for s in scholarships}
        
        suggested = []
        for s in suggested_scholarships:
            sch = scholarship_map.get(s.scholarship_id)
            if sch:
                suggested.append({
                    'id': sch.id,
                    'title': sch.title,
                    'country_info': sch.country_info,
                    'deadline': sch.deadline,
                    'level_of_study': sch.level_of_study,
                    'field_of_study': sch.field_of_study,
                    'match_percentage': s.match_p,
                    'description': sch.description,
                    'provider_organization': sch.provider_organization,
                    'eligibility': sch.eligibility,
                    'academic_requirements': sch.academic_requirements,
                    'cgpa_requirements': sch.cgpa_requirements,
                    'amount_benefits': sch.amount_benefits,
                    'application_link': sch.application_link,
                    'contact_email': sch.contact_email,
                    'keywords': json.loads(sch.keywords) if sch.keywords else [],
                    'source_url': sch.source_url,
                    'source_website': sch.source_website,
                    'extracted_date': sch.extracted_date
                })
        
        # Sort by match percentage
        suggested.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return jsonify({'suggested_scholarships': suggested}), 200

    
    

    
    # Get user's applications with match percentages
    applications = db.session.query(Application, Scholarship).join(
        Scholarship, Application.scholarship_id == Scholarship.id
    ).filter(Application.user_id == user_id).all()
    
    suggested = []
    for app, scholarship in applications:
        suggested.append({
            'id': scholarship.id,
            'title': scholarship.title,
            'country_info': scholarship.country_info,
            'deadline': scholarship.deadline,
            'level_of_study': scholarship.level_of_study,
            'field_of_study': scholarship.field_of_study,
            'match_percentage': app.match_percentage or 0,
            'application_status': app.status,
            'applied_date': app.applied_date.isoformat() if app.applied_date else None,
            'description': scholarship.description,
            'provider_organization': scholarship.provider_organization,
            'eligibility': scholarship.eligibility,
            'academic_requirements': scholarship.academic_requirements,
            'cgpa_requirements': scholarship.cgpa_requirements,
            'amount_benefits': scholarship.amount_benefits,
            'application_link': scholarship.application_link,
            'contact_email': scholarship.contact_email,
            'keywords': json.loads(scholarship.keywords) if scholarship.keywords else [],
            'source_url': scholarship.source_url,
            'source_website': scholarship.source_website,
            'extracted_date': scholarship.extracted_date
        })
    
    # Sort by match percentage
    suggested.sort(key=lambda x: x['match_percentage'], reverse=True)
    
    return jsonify({'suggested_scholarships': suggested}), 200

@scholarships_bp.route('/scrape', methods=['POST'])
def trigger_scrape():
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'error': 'Admin access required'}), 403

    try:
        scraper_service = ScraperService()
        scraper_service.run_spider()
        return jsonify({'message': 'Scraping initiated successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to initiate scraping: {e}'}), 500


def model_to_dict(model):
    """Convert SQLAlchemy model instance to dictionary"""
    return {c.name: getattr(model, c.name) for c in model.__table__.columns}