import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from globalance.items import Article


class GlobalanceSpider(scrapy.Spider):
    name = 'globalance'
    start_urls = ['https://www.globalance.com/news-trends/']

    def parse(self, response):
        links = response.xpath('//a[@class="arrow-link"]/@href').getall()
        yield from response.follow_all(links, self.parse_related)


    def parse_related(self, response):
        yield response.follow(response.url, self.parse_article, dont_filter=True)

        links = response.xpath('//a[@class="arrow-link"]/@href').getall()
        yield from response.follow_all(links, self.parse_related)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//strong[@class="single-post__date"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="single-post__top cell small-12 medium-10 large-8"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
