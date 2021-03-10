from lxml import etree


def ex2():
    with open('output/ex1.xml', 'rb') as file:
        root = etree.parse(file)
    average = root.xpath('count(//fragment[@type="image"]) div count(//page)')
    print('В середньому %.2f графічних елементів на сторінці' % average)


def ex4():
    xml_to_xhtml = etree.XSLT(etree.parse('./ex4.xsl'))
    with open('output/ex3.xml', 'rb') as file:
        root = etree.parse(file)

    xhtml = xml_to_xhtml(root)
    xhtml.write("output/ex4.xhtml", pretty_print=True, encoding="UTF-8")


ex2()
ex4()
