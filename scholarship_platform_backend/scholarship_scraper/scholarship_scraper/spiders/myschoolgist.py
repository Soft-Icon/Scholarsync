import scrapy


class MyschoolgistSpider(scrapy.Spider):
    name = "myschoolgist"
    allowed_domains = ["myschoolgist.com"]
    start_urls = ["https://myschoolgist.com"]

    def parse(self, response):
        pass
