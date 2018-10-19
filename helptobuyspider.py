import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re
from decimal import Decimal
from scrapy.http import Request, FormRequest

# usage: scrapy runspider helptobuyspider.py -o result.json -t json

class HelpToBuySpider(scrapy.Spider):
    name = 'help-to-buy-spider'
    start_urls = ['https://www.helptobuynw.org.uk/property-search/?Buying=True&Renting=False']
    rules = (
        Rule(LinkExtractor(allow=('/property-detail/')), callback='parsePropertyDetails')
    )

    def parse(self, response):
        for next_page in response.css('ul.pagination a'):
            result = re.search(r"__doPostBack\('(.*?)'", next_page.css('a::attr(href)').extract_first())
            yield FormRequest(
                self.start_urls[0],
                formdata={
                    '__VIEWSTATE': str(response.css('input#__VIEWSTATE::attr(value)').extract_first()),
                    '__EVENTTARGET': str(result.group(1)),
                    '__EVENTARGUMENT': '',
                    '__LASTFOCUS': ''
                },
                callback=self.parsePropertyListing
            )

    def parsePropertyListing(self, response):
        for property in response.css('ul.property-listing li'):
            yield response.follow(response.urljoin(property.css('a.button::attr(href)').extract_first()), self.parsePropertyDetails)

    def parsePropertyDetails(self, response):
        item = {
            "title": response.css('.top h1 span::text').extract_first(),
            "area": response.css('.top p span::text').extract_first(),
            "bedrooms": response.css('.amenities p.icon-bedroom span::text').extract_first(),
            "bathrooms": response.css('.amenities p.icon-bathroom span::text').extract_first(),
            "availability": response.css('.amenities p.coming-soon::text').extract_first(),
            "scheme": response.css('.tabs #0 h4::text').extract_first(),
            "asking_price": Decimal(re.sub(r'[^\d.]', '', response.css('h5.price span::text').extract_first())),
            "description": response.css('section.icon-asking-price.content-box p span::text').extract_first(),
            "provider": response.css('section.icon-developer.content-box h3 span::text').extract_first(),
            "details_url": response.request.url,
            "images": []
        }
        for image in response.css('.slide img::attr(src)').extract():
                item['images'].append(response.urljoin(image))

        yield item
