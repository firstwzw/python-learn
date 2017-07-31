# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import re

import scrapy
import datetime
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join


# class ArticlespiderItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     pass


# 日期转换
def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value.replace("·", "").strip(), '%Y/%m/%d').date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date


# 获取字符串中的数字
def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


def return_value(value):
    return value


# 自定义ItemLoader，指定默认的后置过滤器
class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


# 自定义Join，过滤某个标签
class TagsJoin(object):
    def __init__(self, separator=u' ', exclude=""):
        self.separator = separator
        self.exclude = exclude

    def __call__(self, values):
        values = [element for element in values if not element.strip().endswith(self.exclude)]
        return self.separator.join(values)


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_path = scrapy.Field()
    content = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    tags = scrapy.Field(
        output_processor=TagsJoin(",", "评论")
    )

    def get_insert_sql(self):
        insert_sql = """
            INSERT INTO jobbole_article(
              url_object_id, 
              title, 
              url, 
              create_date, 
              fav_nums, 
              front_image_url, 
              front_image_path,
              praise_nums, 
              comment_nums, 
              tags, 
              content
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            ON DUPLICATE KEY UPDATE 
              content=VALUES(content), 
              comment_nums=VALUES(comment_nums), 
              fav_nums=VALUES(fav_nums), 
              praise_nums=VALUES(praise_nums)
        """
        fron_image_url = ""
        if self["front_image_url"]:
            fron_image_url = self["front_image_url"][0]
        params = (
            self["url_object_id"],
            self["title"],
            self["url"],
            self["create_date"],
            self["fav_nums"],
            fron_image_url,
            self["front_image_path"],
            self["praise_nums"],
            self["comment_nums"],
            self["tags"],
            self["content"]
        )
        return insert_sql, params
