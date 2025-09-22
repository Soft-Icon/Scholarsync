# ScholarSync - Scholarship Recommendation Platform

A comprehensive scholarship recommendation platform for Nigerian students that uses web scraping, AI-powered matching, and provides a complete user interface for scholarship discovery and application management.

## Features

### Core Features
- **User Authentication**: Secure signup and login system
- **Profile Management**: Comprehensive student profile with academic details
- **Scholarship Discovery**: AI-powered scholarship recommendations based on user profile
- **Manual Search**: Advanced filtering and search capabilities
- **Application Tracking**: Track scholarship application status and progress
- **Admin Panel**: Administrative interface for manual scholarship entry
- **AI Assistant**: Chat-based AI assistant for scholarship guidance and tips

### Technical Features
- **Web Scraping**: Automated data collection from scholarship websites
- **AI Integration**: Google Gemini-powered matching and recommendation system
- **Responsive Design**: Mobile-friendly interface
- **Real-time Updates**: Dynamic content updates and notifications

## Technology Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **AI Integration**: Google Gemini API for matching and chat assistance
- **Web Scraping**: Scrapy framework
- **Authentication**: Session-based authentication
- **CORS**: Flask-CORS for cross-origin requests

### Frontend
- **Framework**: React with Vite
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Icons**: Lucide React
- **Routing**: React Router DOM
- **State Management**: React Hooks

## Project Structure

```
scholarship_platform/
├── scholarship_platform_backend/
│   ├── src/
│   │   ├── models/           # Database models
│   │   ├── routes/           # API endpoints
│   │   ├── services/         # Business logic and AI services
│   │   ├── database.py       # Database configuration
│   │   └── main.py          # Flask application entry point
│   ├── scholarship_scraper/  # Scrapy project
│   │   ├── spiders/         # Web scrapers
│   │   ├── items.py         # Data models
│   │   └── pipelines.py     # Data processing
│   └── venv/                # Python virtual environment
├── scholarship_platform_frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── assets/          # Static assets
│   │   └── App.jsx         # Main application component
│   └── public/             # Public assets
└── README.md
```

## Installation and Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- pnpm package manager

### User Registration
1. Visit the signup page
2. Fill in personal and academic information
3. Complete profile for better scholarship matching

### Scholarship Management (Admin)
1. Login as admin
2. Navigate to Admin Panel
3. Add scholarships manually with detailed information

### AI-Powered Recommendations
1. Complete your profile with academic details
2. Visit the dashboard to see personalized recommendations
3. Use the AI Assistant for guidance and tips

### Web Scraping
Run the scrapers to collect scholarship data:
```bash
cd scholarship_platform_backend/scholarship_scraper
scrapy crawl opportunitydesk
scrapy crawl myschoolgist
scrapy crawl scholarshippark
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user

### Scholarships
- `GET /api/scholarships/` - Get scholarships with filtering
- `POST /api/scholarships/` - Create scholarship (admin only)
- `GET /api/scholarships/suggested` - Get AI-recommended scholarships

### Applications
- `GET /api/applications/` - Get user applications
- `POST /api/applications/` - Create application
- `POST /api/applications/<id>/submit` - Submit application

### Profile
- `GET /api/profile/` - Get user profile
- `PUT /api/profile/` - Update user profile
- `GET /api/profile/completion` - Get profile completion percentage

### AI Assistant
- `POST /api/ai/chat` - Chat with AI assistant
- `POST /api/ai/match-scholarships` - Trigger AI matching
- `POST /api/ai/personal-statement-tips` - Get personalized tips

## Database Schema

### Users Table
- Personal information (name, email, state, gender, religion)
- Academic details (level, institution, course, performance)
- Skills and interests
- Admin flag

### Scholarships Table
- Title and provider organization
- Deadline and country
- Level and field of study
- Eligibility criteria
- Amount/benefits and application link
- Source (scraped or manual)

### Applications Table
- User and scholarship relationship
- Application status and dates
- AI-calculated match percentage

## AI Integration

The platform uses Google's Gemini API for:

1. **Scholarship Matching**: Calculates compatibility scores between user profiles and scholarships
2. **Data Cleaning**: Standardizes scraped scholarship data
3. **Chat Assistant**: Provides personalized guidance and tips
4. **Personal Statement Help**: Generates tailored writing advice

## Web Scraping

Automated scrapers collect data from:
- opportunitydesk.org (working)
- myschoolgist.com (not working at the moment)
- scholarshippark.com (not working at the moment)

Scrapers extract:
- Scholarship titles and descriptions
- Deadlines and eligibility criteria
- Application links and contact information

## Security Features

- Password hashing with Werkzeug
- Session-based authentication
- CORS protection
- Input validation and sanitization
- Admin-only routes protection

## Future Enhancements

1. **Email Notifications**: Deadline reminders and status updates
2. **Document Upload**: Support for application documents
3. **Advanced Analytics**: Application success tracking
4. **Mobile App**: Native mobile application
5. **Payment Integration**: Premium features and services
6. **Social Features**: User communities and forums

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For support and questions, please contact the development team or create an issue in the repository.

