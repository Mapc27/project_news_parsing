import unicodedata


import scrapy
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags


def replace_more(value):
    value = value.strip().replace(u'\r', u'').replace(u'\n', u'').replace(u'\t', u'')
    value = unicodedata.normalize("NFKD", value)
    return value


class NewsItem(scrapy.Item):
    from_site = scrapy.Field(output_processor=TakeFirst())
    published_date = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(input_processor=MapCompose(remove_tags, replace_more), output_processor=TakeFirst())
    href = scrapy.Field(output_processor=TakeFirst())
    text = scrapy.Field(input_processor=MapCompose(remove_tags, replace_more), output_processor=TakeFirst())
