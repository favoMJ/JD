from scrapy import cmdline
import redis


# 开始京东总体爬虫服务器
from JD.mysql_save import comment_and_product, process_item_mysql


def start_jd_crawl():
    # comment_and_product.process_item()
    cmdline.execute('scrapy runspider JDSpider.py'.split())


# 开启商品查询服务器
def start_jd_search():
    # process_item_mysql.process_item()
    cmdline.execute('scrapy runspider JDSearchSpider.py'.split())


if __name__ == '__main__':
    start_jd_search()
