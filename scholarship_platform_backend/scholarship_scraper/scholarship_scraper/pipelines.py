# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import sqlite3
import os
from datetime import datetime
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem 
from .ai_service import AIService
import json

# Ensure the path for ai_service is correct if it's not a direct sibling of pipelines.py
# For debugging, we'll use a direct import, but consider a more robust import strategy if issues persist.
try:
    from src.services.ai_service import AIService as BackendAIService
except ImportError:
    BackendAIService = None # Fallback if not found

class ScholarshipDatabasePipeline:
    def __init__(self):
        # Path to app.db
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.db')
        self.connection = None
        self.cursor = None
        self.ai_service = AIService()

    def open_spider(self, spider):
        """Open database connection when spider starts"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            
            # Create table if it doesn't exist
            self.create_table()
            spider.logger.info(f"Connected to database: {self.db_path}")
            
        except Exception as e:
            spider.logger.error(f"Error connecting to database: {e}")
            raise

    def close_spider(self, spider):
        """Close database connection when spider finishes"""
        if self.connection:
            self.connection.close()
            spider.logger.info("Database connection closed")

    def create_table(self):
        """Create scholarships table if it doesn't exist"""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS scholarships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            provider_organization TEXT,
            deadline TEXT,
            country_info TEXT,
            level_of_study TEXT,
            field_of_study TEXT,
            eligibility TEXT,
            academic_requirements TEXT,
            cgpa_requirements TEXT,
            amount_benefits TEXT,
            application_link TEXT,
            contact_email TEXT,
            keywords TEXT,
            source_url TEXT UNIQUE,
            source_website TEXT,
            extracted_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        self.cursor.execute(create_table_query)
        self.connection.commit()

    def process_item(self, item, spider):
        """Process each scraped item, clean with AI and save to database"""
        adapter = ItemAdapter(item)
        source_url = adapter.get('url') # Use 'url' as source_url from spider output
        
        if not source_url:
            spider.logger.warning("Item missing URL, cannot process.")
            raise DropItem("Item missing URL, cannot process.")

        spider.logger.info(f"Processing item: {adapter.get('title')} from {source_url}")

        cleaned_data = None
        if BackendAIService:
            try:
                ai_service_instance = BackendAIService()
                spider.logger.info(f"Calling AI Service to clean data for: {adapter.get('title')}")
                cleaned_data = ai_service_instance.clean_scholarship_data(dict(item))
                spider.logger.info(f"AI Service cleaned data successfully for: {adapter.get('title')}")
            except Exception as e:
                spider.logger.error(f"AI Service cleaning failed for {adapter.get('title')}: {e}")
                cleaned_data = dict(item) # Fallback to raw item if AI cleaning fails
        else:
            spider.logger.warning("Backend AIService not available. Storing raw data.")
            cleaned_data = dict(item)

        if not cleaned_data: # Should not happen if fallback is implemented, but for safety
            spider.logger.error(f"Cleaned data is empty for: {adapter.get('title')}. Dropping item.")
            raise DropItem(f"Cleaned data is empty for: {adapter.get('title')}")

        # Check if scholarship already exists (avoid duplicates)
        check_query = "SELECT id FROM scholarships WHERE source_url = ?"
        self.cursor.execute(check_query, (source_url,))
        existing = self.cursor.fetchone()

        try:
            if existing:
                self.update_scholarship(cleaned_data, source_url, existing[0], spider)
            else:
                self.insert_scholarship(cleaned_data, source_url, spider)
            return item
        except sqlite3.Error as e:
            spider.logger.error(f"Database operation failed for {adapter.get('title')}: {e}")
            self.connection.rollback()
            raise DropItem(f"Database error: {e}")
        except Exception as e:
            spider.logger.error(f"Unexpected error in process_item for {adapter.get('title')}: {e}")
            raise DropItem(f"Unexpected error: {e}")
          
    def insert_scholarship(self, cleaned_data, source_url, spider):
        """Insert new scholarship record using cleaned data"""
        insert_query = """
        INSERT INTO scholarships (
            title, description, provider_organization, deadline, country_info, level_of_study,
            field_of_study, eligibility, academic_requirements, cgpa_requirements, amount_benefits, 
            application_link, contact_email, keywords, source_url, source_website, extracted_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        values = (
            cleaned_data.get('title'),
            cleaned_data.get('description', ''), # Ensure description is handled
            cleaned_data.get('provider_organization', ''),
            cleaned_data.get('deadline', ''),
            cleaned_data.get('country_info', ''),
            cleaned_data.get('level_of_study', ''),
            cleaned_data.get('field_of_study', ''),
            cleaned_data.get('eligibility', ''),
            cleaned_data.get('academic_requirements', ''),
            cleaned_data.get('cgpa_requirements', ''),
            cleaned_data.get('amount_benefits', ''),
            cleaned_data.get('application_link', ''),
            cleaned_data.get('contact_email', ''),
            json.dumps(cleaned_data.get('keywords', [])) if cleaned_data.get('keywords') else '', # Store keywords as JSON string
            source_url,
            ItemAdapter(cleaned_data).get('source_website', ''),
            datetime.now().isoformat()
        )
        

        self.cursor.execute(insert_query, values)
        self.connection.commit()
        spider.logger.info(f"Inserted new scholarship: {cleaned_data.get('title')}")

    def update_scholarship(self, cleaned_data, source_url, scholarship_id, spider):
        """Update existing scholarship record"""
        update_query = """
        UPDATE scholarships SET
            title = ?, description = ?, provider_organization = ?, deadline = ?, country_info = ?,
            level_of_study = ?, field_of_study = ?, eligibility = ?, academic_requirements = ?,
            cgpa_requirements = ?, amount_benefits = ?, application_link = ?, contact_email = ?,
            keywords = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        
        values = (
            cleaned_data.get('title'),
            cleaned_data.get('description', ''),
            cleaned_data.get('provider_organization', ''),
            cleaned_data.get('deadline', ''),
            cleaned_data.get('country_info', ''),
            cleaned_data.get('level_of_study', ''),
            cleaned_data.get('field_of_study', ''),
            cleaned_data.get('eligibility', ''),
            cleaned_data.get('academic_requirements', ''),
            cleaned_data.get('cgpa_requirements', ''),
            cleaned_data.get('amount_benefits', ''),
            cleaned_data.get('application_link', ''),
            cleaned_data.get('contact_email', ''),
            json.dumps(cleaned_data.get('keywords', [])) if cleaned_data.get('keywords') else '',
            scholarship_id
        )
        
        self.cursor.execute(update_query, values)
        self.connection.commit()
        spider.logger.info(f"Updated existing scholarship: {cleaned_data.get('title')}")
        
        # update the source_website and extracted_date if needed
        # update_source_query = """
        # UPDATE scholarships SET
        #     source_website = ?, extracted_date = ?
        # WHERE id = ?
        # """
        # update_values = (
        #     ItemAdapter(cleaned_data).get('source_website', ''), # Get from original item if not in AI output
        #     datetime.now().isoformat(), # Use current time for extracted_date
        #     scholarship_id
        # )

