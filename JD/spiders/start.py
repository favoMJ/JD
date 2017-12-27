from scrapy import cmdline
def start_jd_crawl():
    cmdline.execute('scrapy runspider crawl_JD.py'.split())
def start_jd_search():
    cmdline.execute('scrapy crawl crawl_jd_search'.split())
u = 'https://item.jd.com/12034497.html'
start_jd_search()