import os
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
# from scholarship_scraper.scholarship_scraper.spiders.opportunitydesk import ScholarshipSpider # This will be loaded by Scrapy's SpiderLoader

class ScraperService:
    def __init__(self):
        # Add the directory containing the 'scholarship_scraper' project to sys.path
        # This allows Python to find 'scholarship_scraper' as a top-level package
        project_root = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir) # points to scholarship_platform_backend
        if project_root not in sys.path:
            sys.path.insert(0, project_root) # Insert at the beginning to prioritize

        # Set the SCRAPY_SETTINGS_MODULE environment variable
        os.environ['SCRAPY_SETTINGS_MODULE'] = 'scholarship_scraper.scholarship_scraper.settings'
        
        self.settings = get_project_settings()
        self.process = CrawlerProcess(self.settings)

    def run_spider(self):
        # Check if spider is already running to avoid multiple instances
        # Scrapy will automatically discover and load spiders from SPIDER_MODULES defined in settings.py
        if not self.process.crawlers:
            self.process.crawl('opportunitydesk_scholarships') # Pass spider name, not the class directly
            self.process.start(stop_after_crawl=True) # The script will block here until the crawling is finished
        else:
            print("Scrapy spider is already running or has been run.")

# This part is for testing the scraper service directly
if __name__ == '__main__':
    scraper = ScraperService()
    print("Starting Scrapy crawl...")
    scraper.run_spider()
    print("Scrapy crawl finished.")
