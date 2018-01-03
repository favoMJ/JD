import json

import scrapy
import logging

from scrapy_redis.spiders import RedisSpider
from JD.conf import config
from JD.items import JDItem, CommentItem


class JDSearchSpider(RedisSpider):
    name = 'crawl_jd_search'
    allowed_domains = ["jd.com",
                       "3.cn"]
    # 读取APP配置文件
    app_conf = config.configs['JD']
    comment_pagesize = app_conf['comment_pagesize']
    search_page = app_conf['search_page']
    comment_page = app_conf['comment_page']
    
    # #每一页评论个数
    # comment_pagesize = 10
    # #list页数限制
    # search_page = 1
    # #评论总页数
    # comment_page = 10

    redis_key = 'crawl_jd_search:start_url'

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
    }
    #start_urls = ['lpush crawl_jd_search:start_url https://search.jd.com/Search?keyword=spark&page=1']

    def parse(self, response):
        pageno = response.url.split('&')[-1].split('=')[1]
        lis = response.xpath("//ul[@class='gl-warp clearfix']/li")
        for li in lis:
            title = li.xpath("div/div[@class='p-img']/a/@title").extract_first()
            url = li.xpath("div/div[@class='p-img']/a/@href").extract_first()
            url = self.deal_src(url)
            yield scrapy.Request(url, callback='jd_shop_parse')
        if int(pageno) < JDSearchSpider.search_page:
            url = self.change_pageno(response.url,pageno)
            yield scrapy.Request(url=url,  callback=self.parse)

    def jd_search(self,response):
        lis = response.xpath("//ul[@class='gl-warp clearfix']/li")
        for li in lis:
            title = li.xpath("div/div[@class='p-img']/a/@title").extract_first()
            url = li.xpath("div/div[@class='p-img']/a/@href").extract_first()
            url = self.deal_src(url)
            yield scrapy.Request(url, callback=self.jd_shop_parse)

    #解析商品页面
    def jd_shop_parse(self,response):
        item = JDItem()
        item['src'] = response.url
        item['type'] = 4
        each_id = response.url.split('/')[-1].split('.')[0]
        item['item_id'] = each_id
        item['item_name'] =  self.get_name(response)
        item['specification'] = self.get_specification(response)
        item['introduction'] = self.get_introduction(response)
        each_id = str(each_id)
        url = "https://p.3.cn/prices/mgets?&skuIds=J_" + each_id
        #解析价格和总评论
        yield scrapy.Request(url, meta={'item': item, 'each_id': each_id}, callback=self.jd_price)
        url = 'https://sclub.jd.com/comment/productPageComments.action?productId=%s&score=0&sortType=3&page=1&pageSize=10' % (each_id)
        #解析评论
        yield scrapy.Request(url, meta={'item': item }, callback=self.jd_comment)

    #迭代解析评论
    def jd_comment(self,response):
        item = response.meta['item']
        pageno = response.url.split('&')[-2].split('=')[1]
        try:
            body = response.body
            bjson = json.loads(body.decode('gbk'))
            commentsummary = bjson['productCommentSummary']
            if JDSearchSpider.comment_page == 0:
                #获取总记录数
                JDSearchSpider.comment_page = int(commentsummary['commentCount'] / JDSearchSpider.comment_pagesize)
            for comment in bjson['comments']:
                citem = CommentItem()
                citem['item_id'] = item['item_id']
                citem['comment_product'] = item['item_name']
                citem['comment'] = comment
                yield citem
        except:
            print('解析发生了异常')
        if int(pageno) < JDSearchSpider.comment_page:
            url = self.change_pageno(response.url,pageno)
            yield scrapy.Request(url=url, meta={'item': item }, callback='jd_comment')

    # 解析价格
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
        comment_sum = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds=%s' % (item['item_id'])
        yield scrapy.Request(comment_sum, meta={'item': item}, callback=self.jd_comments_count)


    #解析评论总信息
    def jd_comments_count(self,response):
        logging.log(logging.WARNING, "comment url %s" % response.url)
        if response.status != 200:
            return
        item = response.meta['item']
        js = response.body.decode('gbk').encode('utf8').decode('utf8')
        js = json.loads(js)
        item['commentsCount'] = js['CommentsCount'][0]
        yield item

    def deal_src(self,src):
        res = src
        if not src.startswith('http'):
            res = 'https:' + src
        return res

    def get_name(self,response):
        res = response.xpath('normalize-space(//div[@class="sku-name"])').extract()
        if not len(res[0]):
            res = response.xpath('normalize-space(//div[@id="name"]/h1)').extract()
        return res


    def get_introduction(self,response):
        res = response.xpath('normalize-space(//*[@id="detail"]/div[2]/div[1]/div[1])').extract()
        #会取出一个集合，长度至少为1，通过判断第一个长度来决定是否查询下一个
        if not len(res[0]):
            res = response.xpath('normalize-space(//*[@id="parameter2"])').extract()
        return res


    def get_specification(self,response):
        return  response.xpath('normalize-space(//*[@id="detail"]/div[2]/div[2]/div[1]/div)').extract()


    def change_pageno(self,url,pageno):
        res = url.replace('page=%s' % (str(pageno)), 'page=%s' % (str(int(pageno) + 1)))
        return res
