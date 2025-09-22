# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScholarshipScraperItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    deadline = scrapy.Field()
    description = scrapy.Field()
    eligibility = scrapy.Field()
    application_urls = scrapy.Field()
    cgpa_requirements = scrapy.Field()
    academic_requirements = scrapy.Field()
    keywords = scrapy.Field()
    field_of_study = scrapy.Field()
    country_info = scrapy.Field()
    content_length = scrapy.Field()
    scraped_at = scrapy.Field()
