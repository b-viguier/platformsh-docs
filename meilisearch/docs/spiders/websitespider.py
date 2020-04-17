import scrapy
from docs.items import DocsItem
from urllib.parse import urljoin
from scrapy.selector import Selector
from scrapy.http.request import Request
from pprint import pprint
import hashlib
import re

class WebsiteSpider(scrapy.Spider):
    name = 'website'
    allowed_domains = ['platform.sh']
    start_urls = ['https://platform.sh/', 'https://platform.sh/product/demos/']

    seen = set()

    def parse(self, response):
        hxs = Selector(response)
        if response.url in self.seen:
            self.log('already seen  %s' % response.url)
        else:
            self.log('parsing  %s' % response.url)
            self.seen.add(response.url)
        for url in hxs.xpath('//a/@href').extract():
            url = urljoin(response.url, url)
            if not url in self.seen and not re.search(r'.(pdf|zip)$', url) and url.startswith( self.start_urls[0] ):
                self.log("yielding request " + url)
                yield Request(url, callback=self.parse)
        item = DocsItem()
        item['site'] = self.name
        item['title'] = hxs.xpath('//title/text()').get().replace('| Platform.sh', '') 
        item['url'] = response.url
        item['documentId'] = hashlib.sha1(str(response.url).encode('utf-8')).hexdigest()
        item['text'] =  " ".join(response.xpath('.//div[contains(@class,"container-fluid") and not(contains(@class,"footer"))]//text()').getall())
        yield item