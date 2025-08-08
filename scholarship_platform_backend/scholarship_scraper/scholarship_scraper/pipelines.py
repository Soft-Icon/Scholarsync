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

class ScholarshipDatabasePipeline:
    def __init__(self):
        # Path to your app.db - adjust if needed
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.db')
        self.connection = None
        self.cursor = None

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
            name TEXT NOT NULL,
            description TEXT,
            provider TEXT,
            deadline TEXT,
            country TEXT,
            level_of_study TEXT,
            field_of_study TEXT,
            eligibility TEXT,
            benefits TEXT,
            application_link TEXT,
            contact_email TEXT,
            gender_requirements TEXT,
            nationality_requirements TEXT,
            institution_requirements TEXT,
            cgpa_requirements TEXT,
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
        """Process each scraped item and save to database"""
        try:
            adapter = ItemAdapter(item)
            
            # Check if scholarship already exists (avoid duplicates)
            check_query = "SELECT id FROM scholarships WHERE source_url = ?"
            self.cursor.execute(check_query, (adapter.get('source_url'),))
            existing = self.cursor.fetchone()
            
            if existing:
                # Update existing record
                self.update_scholarship(adapter, existing[0], spider)
            else:
                # Insert new record
                self.insert_scholarship(adapter, spider)
                
            return item
            
        except Exception as e:
            spider.logger.error(f"Error processing item: {e}")
            spider.logger.error(f"Item data: {dict(adapter)}")
            # Don't raise exception - continue processing other items
            return item

    def insert_scholarship(self, adapter, spider):
        """Insert new scholarship record"""
        insert_query = """
        INSERT INTO scholarships (
            name, description, provider, deadline, country, level_of_study,
            field_of_study, eligibility, benefits, application_link, contact_email,
            gender_requirements, nationality_requirements, institution_requirements,
            cgpa_requirements, source_url, source_website, extracted_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        values = (
            adapter.get('name', ''),
            adapter.get('description', ''),
            adapter.get('provider', ''),
            adapter.get('deadline', ''),
            adapter.get('country', ''),
            adapter.get('level_of_study', ''),
            adapter.get('field_of_study', ''),
            adapter.get('eligibility', ''),
            adapter.get('benefits', ''),
            adapter.get('application_link', ''),
            adapter.get('contact_email', ''),
            adapter.get('gender_requirements', ''),
            adapter.get('nationality_requirements', ''),
            adapter.get('institution_requirements', ''),
            adapter.get('cgpa_requirements', ''),
            adapter.get('source_url', ''),
            adapter.get('source_website', ''),
            adapter.get('extracted_date', '')
        )
        
        self.cursor.execute(insert_query, values)
        self.connection.commit()
        spider.logger.info(f"Inserted new scholarship: {adapter.get('name')}")

    def update_scholarship(self, adapter, scholarship_id, spider):
        """Update existing scholarship record"""
        update_query = """
        UPDATE scholarships SET
            name = ?, description = ?, provider = ?, deadline = ?, country = ?,
            level_of_study = ?, field_of_study = ?, eligibility = ?, benefits = ?,
            application_link = ?, contact_email = ?, gender_requirements = ?,
            nationality_requirements = ?, institution_requirements = ?, cgpa_requirements = ?,
            source_website = ?, extracted_date = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        
        values = (
            adapter.get('name', ''),
            adapter.get('description', ''),
            adapter.get('provider', ''),
            adapter.get('deadline', ''),
            adapter.get('country', ''),
            adapter.get('level_of_study', ''),
            adapter.get('field_of_study', ''),
            adapter.get('eligibility', ''),
            adapter.get('benefits', ''),
            adapter.get('application_link', ''),
            adapter.get('contact_email', ''),
            adapter.get('gender_requirements', ''),
            adapter.get('nationality_requirements', ''),
            adapter.get('institution_requirements', ''),
            adapter.get('cgpa_requirements', ''),
            adapter.get('source_website', ''),
            adapter.get('extracted_date', ''),
            scholarship_id
        )
        
        self.cursor.execute(update_query, values)
        self.connection.commit()
        spider.logger.info(f"Updated existing scholarship: {adapter.get('name')}")


class DuplicatesPipeline:
    """Pipeline to filter duplicate items based on source URL"""
    
    def __init__(self):
        self.seen_urls = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        url = adapter.get('source_url')
        
        if url in self.seen_urls:
            spider.logger.info(f"Duplicate item found: {url}")
            raise DropItem(f"Duplicate item found: {url}")
        else:
            self.seen_urls.add(url)
            return item


class ValidationPipeline:
    """Pipeline to validate item data before saving"""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Validate required fields
        if not adapter.get('name'):
            spider.logger.warning(f"Item missing name: {adapter.get('source_url')}")
            raise DropItem("Missing scholarship name")
            
        if not adapter.get('source_url'):
            spider.logger.warning("Item missing source URL")
            raise DropItem("Missing source URL")
        
        # Clean and truncate fields if needed
        name = adapter.get('name', '').strip()
        if len(name) > 500:  # Truncate very long names
            adapter['name'] = name[:500] + '...'
            
        # Clean description
        description = adapter.get('description', '').strip()
        if len(description) > 5000:  # Truncate very long descriptions
            adapter['description'] = description[:5000] + '...'
            
        return item
