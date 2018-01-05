import json
import logging

import pymysql
import redis
import pymysql.cursors

Redis_conn = redis.StrictRedis(host='47.94.141.99', port=6379, password='favomj', db=0)
MySql_conn = pymysql.connect(host='47.94.141.99', user='out', passwd='123456', port=3306, db='crawl',
                             charset='utf8', cursorclass=pymysql.cursors.DictCursor)


class RedisControl(object):

    # lpush start_url
    def lpush_start_url(self,redisname,url):
        logging.log(logging.INFO, '%s start url' % (url))
        Redis_conn.lpush('%s:start_url'%(redisname),url)


    # 初始化redis
    def redis_mysql_init(self,redisname):
        # try:
        #     cur = MySql_conn.cursor()
        #     cur.execute('truncate jd_search_shop')
        #     cur.execute('truncate jd_comment')
        #     MySql_conn.commit()
        #     cur.close()
        # except:
        #     print('mysql init error')
        keys = Redis_conn.keys('*'+redisname+'*')
        if len(keys):
            Redis_conn.delete(*keys)
        logging.log(logging.INFO,'%s init'%(redisname))


    #爬虫停止
    def redis_stop(self,redisname):
        keys = Redis_conn.keys(redisname + ':request' + '*')
        if len(keys):
            Redis_conn.delete(*keys)
        logging.log(logging.INFO, '%s stop' % (redisname))


    #获取京东商品数据
    def jd_item(self,startno,pagesize):
        try:
            cur = MySql_conn.cursor()
            cur.execute('select item_id,item_name,introduction,item_price,src from jd_search_shop limit %s ,%s'%(startno,pagesize))
            info = cur.fetchall()
            cur.close()
            info = json.dumps(info,ensure_ascii=False)
            print(info)
            return info
        except Exception as e:
            print(e)
            print('mysql jd_item error')

    # 获取京东商品评论
    def jd_comment(self,startno,pagesize):
        try:
            cur = MySql_conn.cursor()
            cur.execute('select * from jd_comment limit %s ,%s'%(startno,pagesize))
            info = cur.fetchall()
            cur.close()
            info = json.dumps(info, ensure_ascii=False)
            return info
        except Exception as e:
            print(e)
            print('mysql jd_comment error')
            return ''


if __name__ == '__main__':
    control = RedisControl()
    a= control.jd_item(111,10)
    print(a)