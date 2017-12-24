import json
import re

import scrapy
import logging

import scrapy_redis
from scrapy_redis.spiders import RedisSpider
from JD.items import  JDItem

class Crawl_JD(scrapy.Spider):
    name = 'crawl_shop'
    allowed_domains =  ["jd.com",
                       "3.cn"]
    start_urls=['https://item.jd.com/4071564.html']
    custom_settings = {
        'LOG_LEVEL' : 'DEBUG'
    }
    def parse(self, response):
        logging.log(logging.WARNING, "third url %s" % response.url)
        item = JDItem()
        each_id = response.xpath('//ul[@class="parameter2 p-parameter-list"]/li[2]/@title').extract()
        item['item_id'] = each_id
        item['item_name'] = response.xpath('normalize-space(//div[@class="sku-name"])').extract()  # 到了美国有空格了，不知道为何，已修复
        item['specification'] = response.xpath('normalize-space(//*[@id="detail"]/div[2]/div[2]/div[1]/div)').extract()
        item['introduction'] = response.xpath('normalize-space(//*[@id="detail"]/div[2]/div[1]/div[1])').extract()
        each_id = str(each_id[0])
        url = "https://p.3.cn/prices/mgets?&skuIds=J_" + each_id
        yield scrapy.Request(url, meta={'item': item,'each_id':each_id}, callback=self.parse_price)

    def parse_price(self, response):
        item = response.meta['item']
        price_str = response.body
        price_str = price_str[1:-2]
        js = eval(bytes.decode(price_str))
        if 'p' in js:
            item['item_price'] = js['p']
        elif 'pcp' in js:
            item['item_price'] = js['pcp']
        comment_sum = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds=%s' % (response.meta['each_id'])
        yield scrapy.Request(comment_sum, meta={'item': item}, callback=self.parse_comment)

    def parse_comment(self,response):
        item = response.meta['item']
        if response.status != 200:
            return
        js = response.body.decode('gbk').encode('utf8').decode('utf8')
        js = json.loads(js)
        item['comment_count'] = js['CommentsCount'][0]['CommentCountStr']
        item['comment_goodrate'] = js['CommentsCount'][0]['GoodRate']
        print(item)
