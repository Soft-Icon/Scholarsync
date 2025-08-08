import os
import google.generativeai as genai # type: ignore
from typing import List, Dict, Any
import json
import re
from dotenv import load_dotenv # type: ignore
load_dotenv()


class AIService:
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def clean_scholarship_data(self, raw_scholarship_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and standardize scholarship data using Gemini AI
        """
        prompt = f"""
        Clean and standardize the following scholarship data. Extract and format the information properly:

        Raw Data:
        {json.dumps(raw_scholarship_data, indent=2)}

        Please return a JSON object with the following standardized fields:
        - title: Clean scholarship title
        - provider_organization: Organization providing the scholarship
        - deadline: Application deadline (format: YYYY-MM-DD if possible)
        - country: Country where scholarship is offered
        - level_of_study: undergraduate/masters/phd/all
        - field_of_study: Field or subject area
        - eligibility: Clean eligibility criteria
        - amount_benefits: Scholarship amount or benefits
        - application_link: Application URL
        - contact_email: Contact email if available

        Return only the JSON object, no additional text.
        """

        try:
            response = self.model.generate_content(prompt)
            cleaned_text = response.text.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', cleaned_text, re.DOTALL)
            if json_match:
                cleaned_data = json.loads(json_match.group())
                return cleaned_data
            
            return raw_scholarship_data
        except Exception as e:
            print(f"Error cleaning scholarship data: {e}")
            return raw_scholarship_data

    def calculate_match_percentage(self, user_profile: Dict[str, Any], scholarship: Dict[str, Any]) -> int:
        """
        Calculate how well a scholarship matches a user's profile using Gemini AI
        """
        prompt = f"""
        Calculate a match percentage (0-100) between this user profile and scholarship opportunity.

        User Profile:
        - Level of Study: {user_profile.get('level_of_study', 'N/A')}
        - Field of Study: {user_profile.get('course_of_study', 'N/A')}
        - Institution: {user_profile.get('institution', 'N/A')}
        - Academic Performance: {user_profile.get('academic_performance', 'N/A')}
        - State of Origin: {user_profile.get('state_of_origin', 'N/A')}
        - Gender: {user_profile.get('gender', 'N/A')}
        - Religion: {user_profile.get('religion', 'N/A')}
        - Skills & Interests: {user_profile.get('skills_interests', 'N/A')}

        Scholarship:
        - Title: {scholarship.get('title', 'N/A')}
        - Level Required: {scholarship.get('level_of_study', 'N/A')}
        - Field: {scholarship.get('field_of_study', 'N/A')}
        - Country: {scholarship.get('country', 'N/A')}
        - Eligibility: {scholarship.get('eligibility', 'N/A')}

        Consider these factors:
        1. Level of study match (30%)
        2. Field of study relevance (25%)
        3. Eligibility criteria alignment (20%)
        4. Geographic relevance (15%)
        5. Skills/interests alignment (10%)

        Return only a number between 0-100 representing the match percentage.
        """

        try:
            response = self.model.generate_content(prompt)
            match_text = response.text.strip()
            
            # Extract number from response
            match_number = re.findall(r'\d+', match_text)
            if match_number:
                return min(100, max(0, int(match_number[0])))
            return 0
        except Exception as e:
            print(f"Error calculating match percentage: {e}")
            return 0

    def get_scholarship_recommendations(self, user_profile: Dict[str, Any], scholarships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get personalized scholarship recommendations for a user
        """
        recommendations = []
        
        for scholarship in scholarships:
            match_percentage = self.calculate_match_percentage(user_profile, scholarship)
            
            if match_percentage > 30:  # Only recommend if match is above 30%
                recommendation = {
                    **scholarship,
                    'match_percentage': match_percentage
                }
                recommendations.append(recommendation)
        
        # Sort by match percentage (highest first)
        recommendations.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return recommendations[:10]  # Return top 10 recommendations

    def generate_ai_response(self, user_message: str, user_profile: Dict[str, Any] = None) -> str:
        """
        Generate AI assistant response for scholarship-related queries using Gemini
        """
        context = ""
        if user_profile:
            context = f"""
            User Context:
            - Name: {user_profile.get('full_name', 'N/A')}
            - Level: {user_profile.get('level_of_study', 'N/A')}
            - Field: {user_profile.get('course_of_study', 'N/A')}
            - Institution: {user_profile.get('institution', 'N/A')}
            """

        prompt = f"""
        You are a helpful scholarship assistant for Nigerian students. Provide helpful, accurate, and encouraging responses about scholarships, applications, and academic opportunities.

        {context}

        User Question: {user_message}

        Guidelines:
        - Be encouraging and supportive
        - Provide specific, actionable advice
        - Focus on scholarship-related topics
        - If asked about specific scholarships, provide general guidance
        - Keep responses concise but informative
        - Use a friendly, professional tone
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return "I'm sorry, I'm having trouble processing your request right now. Please try again later or contact support for assistance."

    def generate_personal_statement_tips(self, user_profile: Dict[str, Any], scholarship_info: Dict[str, Any] = None) -> str:
        """
        Generate personalized tips for writing a personal statement using Gemini AI
        """
        prompt = f"""
        Generate personalized tips for writing a scholarship personal statement.

        User Profile:
        - Field of Study: {user_profile.get('course_of_study', 'N/A')}
        - Level: {user_profile.get('level_of_study', 'N/A')}
        - Academic Performance: {user_profile.get('academic_performance', 'N/A')}
        - Skills & Interests: {user_profile.get('skills_interests', 'N/A')}

        {"Scholarship: " + scholarship_info.get('title', 'General scholarship') if scholarship_info else ""}

        Provide 5-7 specific, actionable tips tailored to this student's background.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating personal statement tips: {e}")
            return "Here are some general tips for writing a strong personal statement: 1) Start with a compelling hook, 2) Show don't tell with specific examples, 3) Connect your goals to the scholarship, 4) Be authentic and genuine, 5) Proofread carefully."

