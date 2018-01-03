import json
import logging

import pymysql
import redis


Redis_conn = redis.StrictRedis(host='47.94.141.99', port=6379, password='favomj', db=0)
MySql_conn = pymysql.connect(host='47.94.141.99', user='out', passwd='123456', port=3306, db='crawl', charset='utf8')


class RedisControl(object):

    info = []

    def lpush_start_url(self,redisname,url):
        logging.log(logging.INFO, '%s start url' % (url))
        Redis_conn.lpush('%s:start_url'%(redisname),url)

    def redis_init(self,redisname):
        try:
            cur = MySql_conn.cursor()
            cur.execute('truncate jd_search_shop')
            cur.execute('truncate jd_comment')
            MySql_conn.commit()
            cur.close()
        except:
            print('mysql init error')
        keys = Redis_conn.keys('*'+redisname+'*')
        if len(keys):
            Redis_conn.delete(*keys)
        logging.log(logging.INFO,'%s init'%(redisname))

    def redis_stop(self,redisname):
        keys = Redis_conn.keys(redisname + ':request' + '*')
        if len(keys):
            Redis_conn.delete(*keys)
        logging.log(logging.INFO, '%s stop' % (redisname))

    def get_item(self,redisname,startno,pagesize):
        try:
            cur = MySql_conn.cursor()
            cur.execute('select item_id,item_name,introduction,item_price,src from jd_search_shop limit %s ,%s'%(startno,pagesize))
            info = cur.fetchall()
            cur.close()
            print(info)
            return info
        except Exception as e:
            print(e)
            print('mysql get_item error')
