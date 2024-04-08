import scrapy
from scrapy.exporters import JsonItemExporter

class IMDbItem(scrapy.Item):
    title = scrapy.Field()
    release_date = scrapy.Field()
    certification = scrapy.Field()
    runtime = scrapy.Field()
    rating = scrapy.Field()
    director = scrapy.Field()
    writers = scrapy.Field()
    stars = scrapy.Field()
    awards = scrapy.Field()
    keywords = scrapy.Field()

class IMDbSpider(scrapy.Spider):
    name = 'imdb_spider'
    start_urls = ['https://www.imdb.com/title/tt0198460/']

    def __init__(self):
        self.file = open('movies.json', 'wb')
        self.exporter = JsonItemExporter(self.file)
        self.exporter.start_exporting()

    def close(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def parse(self, response):
        item = IMDbItem()
        item['title'] = response.css('span.hero__primary-text::text').get()
        item['release_date'] = response.css('a.ipc-link[href*="releaseinfo"]::text').get()
        item['certification'] = response.css('li.ipc-inline-list__item a.ipc-link::text').get()
        item['runtime'] = response.css('li.ipc-inline-list__item::text').get(default='')
        item['rating'] = response.css('span.sc-bde20123-1::text').get()
        item['director'] = response.css('a.ipc-metadata-list-item__list-content-item--link::text').get()
        item['writers'] = response.css('a.ipc-metadata-list-item__list-content-item--link::text').getall()
        item['stars'] = response.css('a.ipc-metadata-list-item__list-content-item--link::text').getall()
        item['awards'] = response.css('a.ipc-metadata-list-item__icon-link::attr(href)').get()
        item['keywords'] = response.css('a.ipc-chip span.ipc-chip__text::text').getall()

        yield item