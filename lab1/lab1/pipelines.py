from lxml import etree
from itemadapter import ItemAdapter


class Lab1Pipeline:

    def __init__(self):
        self.root: etree.Element = None

    def open_spider(self, spider):
        self.root = etree.Element("data")

    def close_spider(self, spider):
        with open(f'output/{spider.name}.xml', 'wb+') as file:
            file.write(etree.tostring(self.root, encoding="UTF-8", pretty_print=True, xml_declaration=True))

    def process_item(self, item, spider):
        if spider.name == "ex1":
            page = etree.SubElement(self.root, 'page', url=item['url'])
            for el in item['text']:
                etree.SubElement(page, 'fragment', type='text').text = el
            for image in item['images']:
                etree.SubElement(page, 'fragment', type='image').text = image
        else:
            article = etree.SubElement(self.root, 'article', description=item['description'])
            etree.SubElement(article, 'image').text = item['image']
            etree.SubElement(article, 'price').text = item['price']
        return item
