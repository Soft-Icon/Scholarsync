import scrapy
import re
from urllib.parse import urljoin, urlparse
from scrapy.http import Request
from ..items import ScholarshipScraperItem


class ScholarshipSpider(scrapy.Spider):
    name = 'opportunitydesk_scholarships'
    allowed_domains = ['opportunitydesk.org']
    start_urls = ['https://opportunitydesk.org/category/fellowships-and-scholarships/undergraduate/']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 2,  # Be respectful to the server
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'ROBOTSTXT_OBEY': True,
    }

    def parse(self, response):
        """Parse the main scholarship listing page"""
        # Extract individual scholarship links
        scholarship_links = response.css('article h2 a::attr(href)').getall()
        
        # Alternative selectors in case the structure is different
        if not scholarship_links:
            scholarship_links = response.css('article .entry-title a::attr(href)').getall()
        
        if not scholarship_links:
            scholarship_links = response.css('a[href*="/20"]::attr(href)').re(r'https://opportunitydesk\.org/\d{4}/\d{2}/\d{2}/[^"]+')
        
        self.logger.info(f"Found {len(scholarship_links)} scholarship links on page")
        
        # Visit each scholarship page
        for link in scholarship_links:
            if link:
                absolute_url = urljoin(response.url, link)
                yield Request(
                    url=absolute_url,
                    callback=self.parse_scholarship,
                    meta={'scholarship_url': absolute_url}
                )
        
        # Handle pagination - but only follow first 2 pages to avoid old scholarships
        current_page = response.meta.get('page_number', 1)
        max_pages = 2  # Limit to first 2 pages to avoid old scholarships
        
        if current_page < max_pages:
            next_page = response.css('.next.page-numbers::attr(href)').get()
            if not next_page:
                next_page = response.css('a.next::attr(href)').get()
            
            if next_page:
                self.logger.info(f"Following next page: {next_page} (Page {current_page + 1})")
                yield Request(
                    url=urljoin(response.url, next_page),
                    callback=self.parse,
                    meta={'page_number': current_page + 1}
                )
        else:
            self.logger.info(f"Reached maximum pages ({max_pages}). Stopping pagination to avoid old scholarships.")

    def is_current_scholarship(self, deadline_text, content):
        """Check if scholarship is current/recent (2025 or late 2024)"""
        if not deadline_text and not content:
            return True  # Include if we can't determine date
            
        # Check for 2025 dates
        if re.search(r'202[5-9]', deadline_text or content or ''):
            return True
            
        # Check for late 2024 dates (November, December 2024)
        if re.search(r'(?:November|December|Nov|Dec)[^0-9]*202[4]', deadline_text or content or '', re.IGNORECASE):
            return True
            
        # If contains 2023 or early 2024, likely old
        if re.search(r'202[0-3]', deadline_text or content or ''):
            return False
            
        return True  # Default to include if uncertain

    def parse_scholarship(self, response):
        """Parse individual scholarship page"""
        scholarship_url = response.meta.get('scholarship_url', response.url)
        
        # Extract title
        title = response.css('h1.entry-title::text').get()
        if not title:
            title = response.css('title::text').get()
        
        # Extract deadline
        deadline = self.extract_deadline(response)
        
        # Extract main content
        content_selectors = [
            '.entry-content',
            '.post-content', 
            'article .content',
            '.single-post-content'
        ]
        
        content = None
        for selector in content_selectors:
            content = response.css(selector).get()
            if content:
                break
        
        if not content:
            # Fallback to get all text content
            content = ' '.join(response.css('article *::text').getall())
        
        # Filter out old scholarships
        if not self.is_current_scholarship(deadline, content):
            self.logger.info(f"Skipping old scholarship: {title}")
            return
        
        # Extract structured information
        description = self.extract_description(response, content)
        eligibility = self.extract_eligibility(response, content)
        application_urls = self.extract_application_urls(response, content)
        
        # Extract key academic requirements
        cgpa_requirements = self.extract_cgpa_requirements(content)
        academic_requirements = self.extract_academic_requirements(content)
        
        # Extract additional metadata for TF-IDF
        keywords = self.extract_keywords(content)
        field_of_study = self.extract_field_of_study(content)
        country_info = self.extract_country_info(content)
        
        scholarship = ScholarshipScraperItem()
        scholarship['title'] = self.clean_text(title)
        scholarship['url'] = scholarship_url
        scholarship['deadline'] = deadline
        scholarship['description'] = self.clean_text(description)
        scholarship['eligibility'] = self.clean_text(eligibility)
        scholarship['application_urls'] = application_urls
        scholarship['cgpa_requirements'] = cgpa_requirements
        scholarship['academic_requirements'] = academic_requirements
        scholarship['keywords'] = keywords
        scholarship['field_of_study'] = field_of_study
        scholarship['country_info'] = country_info
        scholarship['content_length'] = len(content) if content else 0
        scholarship['scraped_at'] = response.meta.get('download_timestamp')
        
        yield scholarship

    def extract_deadline(self, response):
        """Extract deadline information"""
        # Look for deadline patterns
        deadline_patterns = [
            r'Deadline:\s*([^<\n]+)',
            r'Application [Dd]eadline:\s*([^<\n]+)',
            r'Due [Dd]ate:\s*([^<\n]+)',
            r'Closes?:\s*([^<\n]+)',
        ]
        
        text_content = response.text
        for pattern in deadline_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None

    def extract_description(self, response, content):
        """Extract scholarship description"""
        if not content:
            return None
            
        # Look for description sections
        description_sections = []
        
        # Try to find structured description
        desc_selectors = [
            '.entry-content p:first-of-type',
            '.post-content p:first-of-type',
            'article p:first-of-type'
        ]
        
        for selector in desc_selectors:
            desc = response.css(selector + '::text').getall()
            if desc:
                description_sections.extend(desc)
                break
        
        # If no structured description, extract from content
        if not description_sections and content:
            # Get first few paragraphs as description
            soup_text = re.sub(r'<[^>]+>', ' ', content)
            paragraphs = soup_text.split('\n')
            description_sections = [p.strip() for p in paragraphs[:3] if p.strip()]
        
        return ' '.join(description_sections) if description_sections else None

    def extract_eligibility(self, response, content):
        """Extract eligibility information"""
        if not content:
            return None
            
        # Look for eligibility sections
        eligibility_patterns = [
            r'Eligibility[^:]*:?\s*(.+?)(?=\n\n|Application|Requirements:|Scholarship|How to Apply|$)',
            r'Eligible[^:]*:?\s*(.+?)(?=\n\n|Application|Requirements:|Scholarship|How to Apply|$)',
            r'Who can apply[^:]*:?\s*(.+?)(?=\n\n|Application|Requirements:|Scholarship|How to Apply|$)',
            r'Requirements[^:]*:?\s*(.+?)(?=\n\n|Application|Eligibility|Scholarship|How to Apply|$)'
        ]
        
        text_content = re.sub(r'<[^>]+>', ' ', content)
        
        for pattern in eligibility_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return None

    def extract_application_urls(self, response, content):
        """Extract application URLs"""
        application_urls = []
        
        # Look for application links
        app_link_patterns = [
            r'href="([^"]*apply[^"]*)"',
            r'href="([^"]*application[^"]*)"',
            r'href="([^"]*register[^"]*)"',
            r'href="([^"]*form[^"]*)"'
        ]
        
        for pattern in app_link_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            application_urls.extend(matches)
        
        # Also check for specific application text patterns
        app_text_patterns = [
            r'Apply (?:here|now|at):\s*(?:<[^>]*>)*\s*([^<\s]+)',
            r'Application (?:link|form):\s*(?:<[^>]*>)*\s*([^<\s]+)',
            r'Visit:\s*(?:<[^>]*>)*\s*([^<\s]+)'
        ]
        
        text_content = re.sub(r'<[^>]+>', ' ', content)
        for pattern in app_text_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            application_urls.extend(matches)
        
        # Clean and validate URLs
        clean_urls = []
        for url in application_urls:
            url = url.strip()
            if url and ('http' in url or '.' in url):
                if not url.startswith('http'):
                    url = 'https://' + url
                clean_urls.append(url)
        
        return list(set(clean_urls))  # Remove duplicates

    def extract_cgpa_requirements(self, content):
        """Extract CGPA/GPA requirements"""
        if not content:
            return []
            
        cgpa_patterns = [
            r'CGPA[^0-9]*([0-9]+\.?[0-9]*)',
            r'GPA[^0-9]*([0-9]+\.?[0-9]*)',
            r'Grade Point Average[^0-9]*([0-9]+\.?[0-9]*)',
            r'minimum.*?([0-9]+\.?[0-9]*)\s*(?:CGPA|GPA)',
            r'([0-9]+\.?[0-9]*)\s*(?:CGPA|GPA|grade point)',
            r'academic.*?([0-9]+\.?[0-9]*)\s*(?:out of|/)\s*([0-9]+\.?[0-9]*)'
        ]
        
        text_content = re.sub(r'<[^>]+>', ' ', content)
        requirements = []
        
        for pattern in cgpa_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    requirements.append('/'.join(match))
                else:
                    requirements.append(match)
        
        return list(set(requirements))

    def extract_academic_requirements(self, content):
        """Extract other academic requirements"""
        if not content:
            return []
            
        academic_patterns = [
            r'Bachelor[^.]*degree',
            r'Master[^.]*degree',
            r'PhD|Doctorate',
            r'First Class|Second Class|Third Class',
            r'Honours?|Honor',
            r'[0-9]+\s*years?\s*(?:of\s*)?(?:experience|study)',
            r'minimum.*?qualifications?',
            r'academic.*?performance',
            r'transcripts?',
            r'certificates?'
        ]
        
        text_content = re.sub(r'<[^>]+>', ' ', content)
        requirements = []
        
        for pattern in academic_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            requirements.extend(matches)
        
        return list(set(requirements))

    def extract_keywords(self, content):
        """Extract keywords for TF-IDF analysis"""
        if not content:
            return []
            
        # Keywords relevant for scholarship matching
        keyword_patterns = [
            r'\b(?:undergraduate|postgraduate|graduate|masters?|phd|doctorate)\b',
            r'\b(?:engineering|medicine|law|business|science|arts|computer|technology)\b',
            r'\b(?:scholarship|fellowship|grant|funding|award)\b',
            r'\b(?:international|domestic|local|global)\b',
            r'\b(?:women|female|minorities|disabled|refugee)\b',
            r'\b(?:african|asian|european|american)\b',
            r'\b(?:stem|research|leadership|community)\b'
        ]
        
        text_content = re.sub(r'<[^>]+>', ' ', content).lower()
        keywords = []
        
        for pattern in keyword_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            keywords.extend(matches)
        
        return list(set(keywords))

    def extract_field_of_study(self, content):
        """Extract field of study information"""
        if not content:
            return []
            
        field_patterns = [
            r'\b(?:engineering|computer science|medicine|law|business|economics|mathematics|physics|chemistry|biology|psychology|sociology|anthropology|history|literature|arts|design|architecture|agriculture|environmental|education|journalism|communications?)\b'
        ]
        
        text_content = re.sub(r'<[^>]+>', ' ', content).lower()
        fields = []
        
        for pattern in field_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            fields.extend(matches)
        
        return list(set(fields))

    def extract_country_info(self, content):
        """Extract country/region information"""
        if not content:
            return []
            
        # Common countries and regions mentioned in scholarships
        country_patterns = [
            r'\b(?:USA|United States|America|UK|United Kingdom|Britain|Canada|Australia|Germany|France|Netherlands|Sweden|Norway|Denmark|Switzerland|Japan|South Korea|Singapore|China|India|South Africa|Kenya|Nigeria|Ghana|Rwanda|Uganda|Tanzania|Ethiopia)\b'
        ]
        
        text_content = re.sub(r'<[^>]+>', ' ', content)
        countries = []
        
        for pattern in country_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            countries.extend(matches)
        
        return list(set(countries))

    def clean_text(self, text):
        """Clean and normalize text"""
        if not text:
            return None
            
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.,;:!?()-]', ' ', text)
        
        return text.strip()

# additional utility functions
def save_to_json(data, filename='scholarships.json'):
    """Save scraped data to JSON file"""
    import json
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def run_spider():
    """Run the spider programmatically"""
    from scrapy.crawler import CrawlerProcess
    
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'FEEDS': {
            'scholarships.json': {'format': 'json'},
            'scholarships.csv': {'format': 'csv'},
        }
    })
    
    process.crawl(ScholarshipSpider)
    process.start()

if __name__ == '__main__':
    run_spider()