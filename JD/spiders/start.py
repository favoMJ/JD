from scrapy import cmdline
import redis
def start_jd_crawl():
    cmdline.execute('scrapy runspider JDSpider.py'.split())

def start_jd_search():
    cmdline.execute('scrapy runspider JDSearchSpider.py'.split())

if __name__ == '__main__':
    start_jd_search()