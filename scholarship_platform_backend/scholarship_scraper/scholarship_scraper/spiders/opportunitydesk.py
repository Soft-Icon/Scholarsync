import scrapy
from datetime import datetime
from scholarship_scraper.items import ScholarshipItem
from urllib.parse import urljoin, urlparse
import re
import json

class OpportunitydeskSpider(scrapy.Spider):
    name = "opportunitydesk"
    allowed_domains = ["opportunitydesk.org"]
    start_urls = ["https://opportunitydesk.org"]
 
    # Add custom settings to handle potential blocking
    custom_settings = {
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'ROBOTSTXT_OBEY': True,
    }
    
    def parse(self, response):
        """
        Parse the scholarship listing page and follow links to detail pages.
        Also handles pagination.
        """
        # Check if the response is valid
        if response.status != 200:
            self.logger.error(f"Failed to load page: {response.url} - Status: {response.status}")
            return
        
        # Debug: Print page title to confirm we're on the right page
        page_title = response.css('title::text').get()
        if page_title:
            self.logger.info(f"Parsing page: {page_title}")
        else:
            self.logger.warning(f"No title found for page: {response.url}")
        
        # Try multiple selectors for scholarship links based on actual page structure
        scholarship_links = []
        
        # Method 1: Look for links in article titles
        scholarship_links.extend(response.css('article h2 a::attr(href)').getall())
        scholarship_links.extend(response.css('article h3 a::attr(href)').getall())
        scholarship_links.extend(response.css('.entry-title a::attr(href)').getall())
        
        # Method 2: Look for links in post content
        scholarship_links.extend(response.css('.post-title a::attr(href)').getall())
        scholarship_links.extend(response.css('.entry-header a::attr(href)').getall())
        
        # Method 3: WordPress specific selectors
        scholarship_links.extend(response.css('h2.entry-title a::attr(href)').getall())
        scholarship_links.extend(response.css('h1.entry-title a::attr(href)').getall())
        scholarship_links.extend(response.css('.post h2 a::attr(href)').getall())
        
        # Method 4: Generic approach - find all links that might be scholarship posts
        all_links = response.css('a::attr(href)').getall()
        for link in all_links:
            if link and self._is_scholarship_link(link):
                scholarship_links.append(link)
        
        # Remove duplicates while preserving order and validate URLs
        scholarship_links = list(dict.fromkeys(scholarship_links))
        valid_links = []
        
        for link in scholarship_links:
            if link and self._is_valid_url(link, response.url):
                valid_links.append(link)
        
        self.logger.info(f"Found {len(valid_links)} valid scholarship links")
        
        # Follow each scholarship link
        for link in valid_links[:10]:  # Limit to first 10 for testing
            yield response.follow(link, callback=self.parse_scholarship, 
                                errback=self.handle_error)
        
        # Follow pagination - try multiple pagination selectors
        next_page = self._find_next_page(response)
        
        if next_page:
            self.logger.info(f"Following pagination: {next_page}")
            yield response.follow(next_page, callback=self.parse,
                                errback=self.handle_error)
    
    def _is_scholarship_link(self, link):
        """Check if a link is likely to be a scholarship post"""
        if not link:
            return False
        
        link_lower = link.lower()
        scholarship_indicators = [
            'scholarship', 'fellowship', 'grant', 'bursary', 
            'funding', 'award', 'financial-aid'
        ]
        
        # Check if link contains scholarship-related terms
        for indicator in scholarship_indicators:
            if indicator in link_lower:
                return True
        
        # Check if it's a date-based URL (common for blog posts)
        if re.search(r'/20\d{2}/', link):
            return True
        
        return False
    
    def _is_valid_url(self, url, base_url):
        """Validate URL format and domain"""
        try:
            if url.startswith('/'):
                url = urljoin(base_url, url)
            
            parsed = urlparse(url)
            return (parsed.scheme in ['http', 'https'] and 
                   'opportunitydesk.org' in parsed.netloc)
        except Exception:
            return False
    
    def _find_next_page(self, response):
        """Find next page link using multiple selectors"""
        pagination_selectors = [
            '.pagination a.next::attr(href)',
            '.pagination .next::attr(href)', 
            '.nav-links .next::attr(href)',
            '.page-numbers.next::attr(href)',
            'a:contains("Next")::attr(href)',
            'a:contains("›")::attr(href)',
            'a[rel="next"]::attr(href)'
        ]
        
        for selector in pagination_selectors:
            next_page = response.css(selector).get()
            if next_page:
                return next_page
        
        return None
    
    def parse_scholarship(self, response):
        """
        Parse the scholarship detail page and extract required information.
        """
        if response.status != 200:
            self.logger.error(f"Failed to load scholarship page: {response.url} - Status: {response.status}")
            return
        
        self.logger.info(f"Parsing scholarship page: {response.url}")
        
        # Extract title with multiple fallbacks
        title_selectors = [
            'h1.entry-title::text',
            'h1.post-title::text', 
            'h1::text',
            '.entry-title::text',
            '.post-title::text',
            'title::text'
        ]
        
        title_element = None
        for selector in title_selectors:
            title_element = response.css(selector).get()
            if title_element:
                break
        
        if not title_element:
            self.logger.warning(f"No title found for URL: {response.url}")
            return
        
        title_element = title_element.strip()
        
        # Get content for keyword checking
        content_text = self._extract_content_text(response)
        title_text = title_element.lower()
        
        # Skip if not a scholarship
        scholarship_keywords = ['scholarship', 'grant', 'fellowship', 'financial aid', 'bursary', 'funding']
        if not any(keyword in content_text.lower() or keyword in title_text for keyword in scholarship_keywords):
            self.logger.info(f"Skipping non-scholarship content: {response.url}")
            return
        
        # Create item
        item = ScholarshipItem()
        
        # Core fields
        item['name'] = title_element
        item['source_url'] = response.url
        item['source_website'] = 'opportunitydesk.org'
        item['extracted_date'] = datetime.now().strftime('%Y-%m-%d')
        
        # Extract structured content
        full_content = self._extract_full_content(response)
        item['description'] = full_content
        
        # Extract specific fields
        item['provider'] = self._extract_provider(title_element, full_content)
        item['deadline'] = self._extract_deadline(full_content)
        item['country'] = self._extract_country(title_element, full_content)
        item['level_of_study'] = self._extract_level_of_study(response.url, title_element, full_content)
        item['field_of_study'] = self._extract_field_of_study(full_content)
        item['eligibility'] = self._extract_structured_section(response, full_content, 'eligibility')
        item['benefits'] = self._extract_structured_section(response, full_content, 'benefits')
        item['application_link'] = self._extract_application_link(response, full_content)
        item['contact_email'] = self._extract_email(full_content)
        item['gender_requirements'] = self._extract_gender_requirements(title_element, full_content)
        item['nationality_requirements'] = self._extract_nationality_requirements(full_content)
        item['institution_requirements'] = self._extract_institution_requirements(full_content)
        item['cgpa_requirements'] = self._extract_cgpa_requirements(full_content)
        
        return item
    
    def _extract_content_text(self, response):
        """Extract plain text content for keyword checking"""
        content_selectors = [
            '.entry-content *::text',
            '.post-content *::text',
            '.content *::text',
            'article *::text'
        ]
        
        for selector in content_selectors:
            content_parts = response.css(selector).getall()
            if content_parts:
                return ' '.join(content_parts)
        
        # Fallback
        return ' '.join(response.css('p::text, li::text').getall())
    
    def _extract_full_content(self, response):
        """Extract full structured content"""
        content_selectors = [
            '.entry-content',
            '.post-content',
            '.content',
            'article'
        ]
        
        for selector in content_selectors:
            content_element = response.css(selector).get()
            if content_element:
                # Extract text while preserving some structure
                text_parts = response.css(f'{selector} p::text, {selector} li::text, {selector} h2::text, {selector} h3::text').getall()
                return ' '.join(text_parts) if text_parts else content_element
        
        # Fallback
        return ' '.join(response.css('p::text, li::text, h2::text, h3::text').getall())
    
    def _extract_provider(self, title, content):
        """Extract scholarship provider"""
        # Try pattern matching first
        provider_patterns = [
            r'(?:offered by|provided by|sponsored by|from)\s+([^,.]+)',
            r'(?:by)\s+([A-Z][^,.]{3,50})',
        ]
        
        for pattern in provider_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Try to extract from title
        if ' at ' in title:
            parts = title.split(' at ')
            if len(parts) > 1:
                return parts[1].strip()
        
        return ''
    
    def _extract_deadline(self, content):
        """Extract application deadline"""
        deadline_patterns = [
            r'(?:deadline|closing date|application deadline)[:\s]+([^\n.,]+)',
            r'(?:applications close|submissions close)[:\s]+([^\n.,]+)',
            r'(?:due date|last date)[:\s]+([^\n.,]+)'
        ]
        
        for pattern in deadline_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ''
    
    def _extract_country(self, title, content):
        """Extract country information"""
        # Common countries in scholarships
        countries = [
            'Nigeria', 'USA', 'United States', 'UK', 'United Kingdom', 
            'Canada', 'Australia', 'Germany', 'France', 'Netherlands',
            'Sweden', 'Norway', 'Denmark', 'Switzerland', 'Belgium'
        ]
        
        # Check title first
        for country in countries:
            if country.lower() in title.lower():
                return country
        
        # Check content
        for country in countries:
            if country.lower() in content.lower():
                return country
        
        # Pattern matching
        country_patterns = [
            r'(?:country|location|host country)[:\s]+([^\n.,]+)',
            r'(?:study in|based in|located in)[:\s]+([^\n.,]+)'
        ]
        
        for pattern in country_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ''
    
    def _extract_level_of_study(self, url, title, content):
        """Extract level of study"""
        level_keywords = {
            'undergraduate': 'Undergraduate',
            'bachelor': 'Undergraduate',
            'postgraduate': 'Postgraduate',
            'masters': 'Masters',
            'phd': 'PhD',
            'doctorate': 'PhD',
            'doctoral': 'PhD'
        }
        
        # Check URL first
        for keyword, level in level_keywords.items():
            if keyword in url.lower():
                return level
        
        # Check title and content
        combined_text = (title + ' ' + content).lower()
        for keyword, level in level_keywords.items():
            if keyword in combined_text:
                return level
        
        return ''
    
    def _extract_field_of_study(self, content):
        """Extract field of study"""
        field_patterns = [
            r'(?:field of study|discipline|subject|major)[:\s]+([^\n.,]+)',
            r'(?:available for|open to)\s+([^.,]*(?:engineering|science|arts|humanities|business|medicine|law|computer|technology)[^.,]*)'
        ]
        
        for pattern in field_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ''
    
    def _extract_structured_section(self, response, content, section_type):
        """Extract structured sections like eligibility or benefits"""
        if section_type == 'eligibility':
            headers = ['eligibility', 'requirements', 'who can apply']
        elif section_type == 'benefits':
            headers = ['benefits', 'value', 'award', 'coverage']
        else:
            return ''
        
        # Try to find section headers
        for header in headers:
            header_selectors = [
                f'h2:contains("{header.title()}")',
                f'h3:contains("{header.title()}")',
                f'h4:contains("{header.title()}")',
                f'strong:contains("{header.title()}")'
            ]
            
            for selector in header_selectors:
                header_element = response.css(selector).get()
                if header_element:
                    # Extract content following this header
                    section_content = self._extract_section_content(response, selector)
                    if section_content:
                        return section_content
        
        # Fallback to regex patterns
        if section_type == 'eligibility':
            patterns = [
                r'(?:eligibility|requirements|who can apply)(?:[:\s]+)([^#]+?)(?:benefits|value|award|how to apply|application process)',
                r'(?:eligible candidates|eligible applicants)(?:[:\s]+)([^#]+?)(?:how to apply|application|documents)'
            ]
        else:  # benefits
            patterns = [
                r'(?:benefits|value|award|scholarship value)(?:[:\s]+)([^#]+?)(?:how to apply|application process|eligibility)'
            ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()
        
        return ''
    
    def _extract_section_content(self, response, header_selector):
        """Extract content following a header"""
        try:
            header = response.css(header_selector)[0]
            content_parts = []
            
            for element in header.xpath('following-sibling::*'):
                if element.root.tag in ['h2', 'h3', 'h4']:
                    break
                element_text = ' '.join(element.css('::text').getall())
                if element_text.strip():
                    content_parts.append(element_text)
            
            return ' '.join(content_parts).strip()
        except (IndexError, AttributeError):
            return ''
    
    def _extract_application_link(self, response, content):
        """Extract application link"""
        # Try to find application sections first
        apply_headers = ['apply', 'application', 'how to apply']
        
        for header in apply_headers:
            header_selectors = [
                f'h2:contains("{header.title()}")',
                f'h3:contains("{header.title()}")',
                f'h4:contains("{header.title()}")'
            ]
            
            for selector in header_selectors:
                if response.css(selector):
                    # Look for links in this section
                    links = response.css(f'{selector} ~ * a::attr(href)').getall()
                    if links:
                        return links[0]
        
        # Try direct link selectors
        apply_link_selectors = [
            'a:contains("Apply")::attr(href)',
            'a:contains("Application")::attr(href)',
            'a[href*="apply"]::attr(href)',
            'a[href*="application"]::attr(href)'
        ]
        
        for selector in apply_link_selectors:
            link = response.css(selector).get()
            if link:
                return link
        
        # Regex pattern in content
        link_pattern = r'(?:apply here|application link)[:\s]+(https?://[^\s]+)'
        match = re.search(link_pattern, content, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return ''
    
    def _extract_email(self, content):
        """Extract contact email"""
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        match = re.search(email_pattern, content)
        return match.group(0) if match else ''
    
    def _extract_gender_requirements(self, title, content):
        """Extract gender requirements"""
        # Check title first
        title_lower = title.lower()
        if 'women' in title_lower or 'female' in title_lower:
            return 'Female'
        elif 'men' in title_lower or 'male' in title_lower:
            return 'Male'
        
        # Pattern matching in content
        gender_pattern = r'(?:gender|women only|female only|male only)[:\s]+([^\n.,]+)'
        match = re.search(gender_pattern, content, re.IGNORECASE)
        return match.group(1).strip() if match else ''
    
    def _extract_nationality_requirements(self, content):
        """Extract nationality requirements"""
        nationality_pattern = r'(?:nationality|citizen|citizenship)[:\s]+([^\n.,]+)'
        match = re.search(nationality_pattern, content, re.IGNORECASE)
        return match.group(1).strip() if match else ''
    
    def _extract_institution_requirements(self, content):
        """Extract institution requirements"""
        institution_pattern = r'(?:institution|university|college)[:\s]+([^\n.,]+)'
        match = re.search(institution_pattern, content, re.IGNORECASE)
        return match.group(1).strip() if match else ''
    
    def _extract_cgpa_requirements(self, content):
        """Extract CGPA requirements"""
        cgpa_pattern = r'(?:cgpa|gpa|grade)[:\s]+([^\n.,]+)'
        match = re.search(cgpa_pattern, content, re.IGNORECASE)
        return match.group(1).strip() if match else ''
    
    def handle_error(self, failure):
        """Handle request errors"""
        self.logger.error(f"Request failed: {failure.request.url} - {failure.value}")
