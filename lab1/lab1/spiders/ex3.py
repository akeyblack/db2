import scrapy


class Ex3Spider(scrapy.Spider):
    name = 'ex3'
    allowed_domains = ['allo.ua']
    start_urls = ['https://allo.ua/ua/products/mobile/klass-kommunikator_smartfon/']

    def parse(self, response):
        items = response.xpath("//*[contains(@class,'products-layout__item')]")[:20]
        for item in items:
            yield {
                "price": item.xpath(".//span[contains(@class, 'sum')]/text()").get().strip(),
                "description": item.xpath(".//a/@title").get().strip(),
                "image": item.xpath(".//img/@data-src").get()
            }
