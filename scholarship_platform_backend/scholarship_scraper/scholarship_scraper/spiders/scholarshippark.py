import scrapy


class ScholarshipparkSpider(scrapy.Spider):
    name = "scholarshippark"
    allowed_domains = ["scholarshippark.com"]
    start_urls = ["https://scholarshippark.com"]

    def parse(self, response):
        pass
