import logging
import re

import scrapy
from scrapy import cmdline
from scrapy_redis.spiders import RedisSpider
from w3lib.html import remove_tags

from JD.conf import config
from JD.items import CSDNItem, Article
from JD.package_contract.parse import PageContract

pagecontract = PageContract()

class CSDNSpider(RedisSpider):
    name = 'csdn_search'
    allowed_domains = ["blog.csdn.net"]

    # 读取APP配置文件
    csdn_conf = config.configs['CSDN']
    search_page = csdn_conf['search_page']
    redis_key = 'csdn_search:start_url'

    keyname = ''

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
    }
    # start_urls = ['http://so.csdn.net/so/search/s.do?q=mysql&t=blog&p=1']
    # start_urls = ['lpush csdn_search:start_url http://so.csdn.net/so/search/s.do?q=mysql&p=1']

    def parse(self, response):
        searchkey = response.url.split('?')[1].split('=')[1].split('&')[0]
        if CSDNSpider.keyname == '' and searchkey != '':
            CSDNSpider.keyname = searchkey

        pageno = response.url.split('&')[-1].split('=')[1]
        lis = response.xpath("//dl[@class='search-list J_search']")

        for li in lis:
            item = CSDNItem()
            title = self.get_list_title(li)
            detail = self.get_detail(li)
            src = self.get_src(li)

            item['title'] = title
            item['detail'] = detail
            item['src'] = src
            item['keyname'] = CSDNSpider.keyname

            yield item
            yield scrapy.Request(url=src,callback=self.pageparse)

        if int(pageno) < CSDNSpider.search_page:
            url = self.change_pageno(response.url, pageno)
            yield scrapy.Request(url=url, callback=self.parse)


    def pageparse(self,response):
        item = Article()
        logging.log(logging.WARNING,response.url)
        title = self.get_article_title(response)
        content = response.xpath("//div[@id='article_content']").extract_first()
        content = remove_tags(content)
        content = re.sub(r'[\n]', '', content)
        abstract = pagecontract.contract(text=content)
        item['title'] = title
        item['keyname'] = CSDNSpider.keyname
        item['content'] = content
        item['abstract'] = abstract
        item['src'] = response.url
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


    def get_list_title(self,selector):
        li = selector.xpath("dt/a/em/text()|dt/a/text()").extract()
        title = ''.join(li)
        return title

    def get_article_title(self,response):
        res = response.xpath('//article/h1').extract()
        if not len(res):
            res = response.xpath('//main/article/h1').extract()
        return res


    def get_src(self,selector):
        src = selector.xpath("dt/a[1]/@href").extract_first()
        return src

    def get_detail(self,selector):
        detail = selector.xpath("dd/text()|dd/em/text()|dd[1]/a/text()").extract()
        detail = ''.join(detail).replace('\n', '')
        return detail

    def get_introduction(self,response):
        res = response.xpath('normalize-space(//*[@id="detail"]/div[2]/div[1]/div[1])').extract()
        #会取出一个集合，长度至少为1，通过判断第一个长度来决定是否查询下一个
        if not len(res[0]):
            res = response.xpath('normalize-space(//*[@id="parameter2"])').extract()
        return res

    def get_specification(self,response):
        return  response.xpath('normalize-space(//*[@id="detail"]/div[2]/div[2]/div[1]/div)').extract()

    def change_pageno(self,url,pageno):
        res = url.replace('page=%s' % (str(pageno)), 'page=%s' % str(int(pageno) + 1))
        return res


if __name__ == '__main__':
    cmdline.execute('scrapy runspider csdn_spider.py'.split())
