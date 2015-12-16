from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

from SiteWatcher.items import XboxItem


class XboxSpider(BaseSpider):
    name = 'xbox'
    allowed_domains = ['xbox360iso.com']
    start_urls = ['http://xbox360iso.com']

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        titles = hxs.select('//div[@class="items"]//a/text()').extract()
        items = []
        for title in titles:
            item = XboxItem()
            item['title'] = title
            items.append(item)
        return items
