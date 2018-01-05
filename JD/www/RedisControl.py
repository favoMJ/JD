import json
import logging

import pymongo
import redis

Redis_conn = redis.StrictRedis(host='47.94.141.99', port=6379, password='favomj', db=0)

r = redis.StrictRedis(host='47.94.141.99', port=6379, password='favomj', db='0')

client = pymongo.MongoClient(host='47.94.141.99', port=27017)

db = client['test']

db.authenticate("out", "out")

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
    def jd_item(self,shopname ,startno,pagesize):
        try:
            jd_product = db['jd_product:' + shopname]
            info = jd_product.find({},{"item_id":1,"item_name" :1, 'introduction' : 1 , 'item_price': 1 , 'src' : 1 , "_id":0}).limit(pagesize).skip(startno)
            # info = json.dumps(info,ensure_ascii=False)
            print(info.count())
            info = json.dumps(list(info),ensure_ascii=False)
            print(info)
            return info
        except Exception as e:
            print(e)
            print('mysql jd_item error')

    # 获取京东商品评论
    def jd_comment(self,shopname,startno,pagesize):
        try:
            jd_product = db['jd_product:' + shopname]
            info = jd_product.find({}, {"item_id": 1, "item_name": 1, 'introduction': 1, 'item_price': 1, 'src': 1,
                                        "_id": 0})
            # info = json.dumps(info,ensure_ascii=False)
            info = json.dumps(list(info), ensure_ascii=False)
            print(info)
            return info
        except Exception as e:
            print(e)
            print('mysql jd_comment error')


if __name__ == '__main__':
    control = RedisControl()
    a= control.jd_item('redis',1,2)