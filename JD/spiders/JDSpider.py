import json
import re

import scrapy
import logging

from scrapy_redis.spiders import RedisSpider
from JD.items import JDItem


class JDSpider(RedisSpider):
    name = 'crawl_JD'
    allowed_domains = ["jd.com",
                       "3.cn"]
    redis_key = 'crwal_jd:start_url'

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
    }

    # start_urls=['lpush crwal_jd:start_url https://www.jd.com']
    def parse(self, response):
        logging.log(logging.WARNING, "first url %s" % response.url)
        names = response.xpath('//ul[@class="JS_navCtn cate_menu"]//a/text()').extract()
        srcs = response.xpath('//ul[@class="JS_navCtn cate_menu"]//a/@href').extract()
        for i in range(len(names)):
            item = JDItem()
            item['name'] = names[i]
            if i < len(srcs):
                src = self.deal_src(srcs[i])
                item['src'] = src
                item['type'] = 1
                if self.jd_check_firstlink(src):
                    item['fa_url'] = response.url
                    yield item
                    yield scrapy.Request(src, meta={'url': response.url}, callback=self.jd_spage)

    def jd_spage(self,response):
        #如果页面返回状态成功
        if response.status != 200:
            return None
        logging.log(logging.WARNING, "second url %s" % response.url)
        names = self.get_name(response)
        srcs = self.get_src(response)
        for i in range(len(names)):
            item = JDItem()
            # 链接类型
            item['type'] = 2
            #链接名字
            item['name'] = names[i]
            if i < len(srcs):
                src = self.deal_src(srcs[i])
                item['src'] = src
                if self.jd_check_secondlink(src):
                    #链接父级url
                    item['fa_url'] = response.meta['url']
                    yield item
                    yield scrapy.Request(src, meta={'url': src},callback=self.jd_tpage)
                elif self.jd_check_firstlink(src):
                    #如果有同级的，继续使用父级url
                    yield scrapy.Request(src, meta={'url':  response.url}, callback=self.jd_spage)

    def jd_tpage(self, response):
        if response.status != 200:
            return None
        logging.log(logging.WARNING, "third url %s" % response.url)
        names = self.get_name(response)
        srcs = self.get_src(response)

        for i in range(len(names)):
            item = JDItem()
            item['type'] = 3
            item['name'] = names[i]
            if i < len(srcs):
                src = self.deal_src(srcs[i])
                item['src'] = src

                if self.jd_check_thirdlink(src):
                    item['fa_url'] = response.meta['url']
                    yield item
                    yield scrapy.Request(src,callback=self.jd_shoppage)
                elif self.jd_check_secondlink(src):
                    yield scrapy.Request(src, meta={'url': response.url}, callback=self.jd_tpage)

    def jd_shoppage(self, response):
        logging.log(logging.WARNING, "item url %s" % response.url)
        if response.status != 200:
            return None
        item = JDItem()
        item['src'] =response.url
        item['type'] = 4
        each_id = self.jd_get_itemid(response)
        item['item_id'] = each_id
        item['item_name'] = response.xpath('normalize-space(//div[@class="sku-name"])').extract()  # 到了美国有空格了，不知道为何，已修复
        item['specification'] = response.xpath('normalize-space(//*[@id="detail"]/div[2]/div[2]/div[1]/div)').extract()
        item['introduction'] = response.xpath('normalize-space(//*[@id="detail"]/div[2]/div[1]/div[1])').extract()
        each_id = str(each_id)
        url = "https://p.3.cn/prices/mgets?&skuIds=J_" + each_id
        yield scrapy.Request(url, meta={'item': item,'each_id':each_id}, callback=self.jd_price)

    def jd_price(self, response):
        logging.log(logging.WARNING, "price url %s" % response.url)
        item = response.meta['item']
        price_str = response.body
        price_str = price_str[1:-2]
        js = eval(bytes.decode(price_str))
        if 'p' in js:
            item['item_price'] = js['p']
        elif 'pcp' in js:
            item['item_price'] = js['pcp']
        comment_sum = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds=%s' % (response.meta['each_id'])
        yield scrapy.Request(comment_sum, meta={'item': item}, callback=self.jd_comments_count)

    def jd_comments_count(self,response):
        logging.log(logging.WARNING, "comment url %s" % response.url)
        item = response.meta['item']
        if response.status != 200:
            return
        js = response.body.decode('gbk').encode('utf8').decode('utf8')
        js = json.loads(js)
        item['commentsCount'] = js['CommentsCount'][0]
        # yield item

    def get_name(self,response):
        return response.xpath('//a/text()').extract()

    def get_src(self,response):
        return response.xpath('//a/@href').extract()

    def deal_src(self,src):
        res = src
        if not src.startswith('http'):
            res = 'https:' + src
        return res

    def jd_check_firstlink(self,src):
        return re.search('channel.jd.com/(.*)html$', src) or re.search('(.*)jd.com$', src)

    def jd_check_secondlink(self,src):
        return re.search('jd.com/(list|Search)', src)

    def jd_check_thirdlink(self,src):
        return re.search('item', src)

    def jd_get_itemid(self,response):
        res =  response.xpath('//ul[@class="parameter2 p-parameter-list"]/li[2]/@title').extract()
        if len(res):
            return res[0]
        return None