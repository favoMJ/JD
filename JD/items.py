# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy
from scrapy import Item

class JDItem(Item):

    #第几级链接，链接名，链接url，由哪个链接转至
    type = scrapy.Field()
    name = scrapy.Field()
    src = scrapy.Field()
    fa_url = scrapy.Field()

    #商品id，名称，介绍，规格，评论总数，好评率
    item_id = scrapy.Field()
    item_name = scrapy.Field()
    specification = scrapy.Field()
    introduction = scrapy.Field()
    item_price = scrapy.Field()
    commentsCount = scrapy.Field()
    keyname = scrapy.Field()

    #爬虫模块，名字
    crawled = scrapy.Field()
    spider = scrapy.Field()

class CommentItem(Item):
    comment = scrapy.Field()
    item_id = scrapy.Field()
    comment_product = scrapy.Field()
    keyname = scrapy.Field()
    # 爬虫模块，名字
    crawled = scrapy.Field()
    spider = scrapy.Field()


class CSDNItem(Item):
    title = scrapy.Field()
    detail = scrapy.Field()
    keyname = scrapy.Field()
    src = scrapy.Field()

    # 爬虫模块，名字
    crawled = scrapy.Field()
    spider = scrapy.Field()


class Article(Item):
    keyname = scrapy.Field()
    content = scrapy.Field()
    abstract = scrapy.Field()
