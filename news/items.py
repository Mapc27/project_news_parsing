import unicodedata
from pprint import pformat

import scrapy
from itemloaders.processors import TakeFirst, MapCompose
from w3lib.html import remove_tags


def replace_more(value):
    value = value.strip().replace(u'\r', u'').replace(u'\n', u'').replace(u'\t', u'')\
        .replace(u'\u200c', u'').replace(u'\u200b', u'')
    value = unicodedata.normalize("NFKD", value)
    return value


class CompetitorsNewsItem(scrapy.Item):
    from_site = scrapy.Field(output_processor=TakeFirst())
    published_date = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(input_processor=MapCompose(remove_tags, replace_more), output_processor=TakeFirst())
    href = scrapy.Field(output_processor=TakeFirst())
    text = scrapy.Field(input_processor=MapCompose(remove_tags, replace_more), output_processor=TakeFirst())
    is_match = scrapy.Field(output_processor=TakeFirst())
    ti_id = scrapy.Field(output_processor=TakeFirst())

    def __repr__(self):
        return dict(self).__str__()


class TatarInformNewsItem(scrapy.Item):
    from_site = scrapy.Field(output_processor=TakeFirst())
    published_date = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(input_processor=MapCompose(remove_tags, replace_more), output_processor=TakeFirst())
    href = scrapy.Field(output_processor=TakeFirst())
    text = scrapy.Field(input_processor=MapCompose(remove_tags, replace_more), output_processor=TakeFirst())
    id = scrapy.Field(output_processor=TakeFirst())

    def __repr__(self):
        return dict(self).__str__()
