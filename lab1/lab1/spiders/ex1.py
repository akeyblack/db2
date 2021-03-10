import scrapy
from scrapy.http import Response


class Ex1Spider(scrapy.Spider):
    name = 'ex1'
    allowed_domains = ['ua.igotoworld.com']
    start_urls = ['https://ua.igotoworld.com']
    urls = [start_urls[0]]

    pages_count = 0

    def parse(self, response):
        text_el = response.xpath("//*[not(self::script)][not(self::style)][string-length("
                                       "normalize-space(text())) > 0]/text()")
        image_el = response.xpath("//img/@src")

        yield {
            "url": response.url,
            "text": map(lambda text: text.get().strip(), text_el),
            "images": map(lambda image: image.get(), image_el)
        }

        next_url = self.get_next_page(response, 1)
        if self.pages_count < 20 and next_url is not None:
            self.pages_count += 1
            yield scrapy.Request(next_url, callback=self.parse)

    def get_next_page(self, response, n):
        href = response.xpath(f"//a[{n}]/@href[contains(., 'igotoworld')]").extract()
        print(href)
        if len(href) == 0:
            return None

        url = response.urljoin(href[0])
        print("log:" + url)

        if url in self.urls:
            n += 1
            return self.get_next_page(response, n)
        else:
            self.urls.append(url)
            return url

