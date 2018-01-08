import json
import logging
import re
import traceback

import datetime
import pymongo
import redis

from JD.package_contract.page_parse import PageContract

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
        cols = db.collection_names(include_system_collections=False)
        regex = re.compile(redisname)
        cols = [x for x in cols if regex.match(x)]



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
            print('jd_product:'+shopname)
            jd_product = db['jd_product:' + shopname]
            info = jd_product.find({},{"item_id":1,"item_name" :1, 'introduction' : 1 , 'item_price': 1 , 'src' : 1 , "_id":0}).limit(pagesize).skip(startno)
            # info = json.dumps(info,ensure_ascii=False)
            info = json.dumps(list(info),ensure_ascii=False)
            return info
        except Exception as e:
            print(e)
            print('mysql jd_item error')

    # 获取京东商品分析
    def jd_product_sum(self,shopname,item_id):
        try:
            jd_product = db['jd_product:' + shopname]
            jd_comment = db['jd_comment:' + shopname]
            pdata = jd_product.find({'item_id':item_id}, {'commentsCount' : 1 ,'_id': 0})
            cdata = jd_comment.find({'item_id':item_id}, {'comment': 1, '_id': 0})

            pdata = self.product_parse(list(pdata))
            cdata = self.comment_sum_parse(list(cdata))
            pdata = pdata + cdata

            # info = json.dumps(info,ensure_ascii=False)
            info = json.dumps(pdata, ensure_ascii = False)
            return info
        except Exception as e:
            print(e)
            print('mysql jd_product_sum error')

    # 获取京东商品评论
    def jd_comment(self, shopname, item_id):
        try:
            jd_comment = db['jd_comment:' + shopname]
            info = jd_comment.find({'item_id': item_id}, {'comment': 1, '_id': 0})
            # info = json.dumps(info,ensure_ascii=False)
            info = self.comment_parse(list(info))
            info = json.dumps(info, ensure_ascii=False)
            return info
        except Exception as e:
            print(e)
            print('mysql jd_comment error')

    def jd_comment_keywords(self, shopname, item_id):
        try:
            jd_comment = db['jd_comment:' + shopname]
            info = jd_comment.find({'item_id': item_id}, {'comment': 1, '_id': 0})
            # info = json.dumps(info,ensure_ascii=False)
            info = self.commentkeywords_parse(list(info))
            info = json.dumps(info, ensure_ascii=False)
            return info
        except Exception as e:
            print(e)
            print('mysql jd_comment error')

    # 获取csdn列表信息
    def csdn_item(self,shopname,startno,pagesize):
        try:
            csdn_product = db['csdn_product:' + shopname]
            info = csdn_product.find({}, {"_id": 0}).limit(pagesize).skip(startno)
            print(info)
            # info = json.dumps(info,ensure_ascii=False)
            info = json.dumps(list(info), ensure_ascii=False)
            return info
        except Exception as e:
            print(e)
            print('mysql csdn_item error')

    # 获取csdn文章信息
    def csdn_article(self,shopname,src):
        try:
            jd_product = db['csdn_article:' + shopname]
            info = jd_product.find({'src':src}, {"_id": 0})
            # info = json.dumps(info,ensure_ascii=False)
            info = json.dumps(list(info), ensure_ascii=False)
            return info
        except Exception as e:
            print(e)
            print('mysql csdn_article error')

    def comment_parse(self,info):
        res = []
        try:
            for data in info:
                temp = {}
                if 'comment' not in data:
                    continue
                comment = data['comment']
                temp['creationTime'] = comment['creationTime']
                temp['content'] = comment['content']
                temp['nickname'] = comment['nickname']
                temp['userClientShow'] = comment['userClientShow']
                temp['userLevelName'] = comment['userLevelName']
                temp['productSize'] = comment['productSize']
                temp['productColor'] = comment['productColor']
                temp['score'] = comment['score']
                res.append(temp)
        except Exception as e :
            print(e)
            print('comment_parse error')
        return res

    def comment_sum_parse(self,cdata):
        res = []
        color = {}
        size = {}
        month = {1:0,2:0,3:0,4:0,5:0,6:0,7:0,
                 8:0,9:0,10:0,11:0,12:0}
        plat = {'mobile':0,'computer':0}
        try:
            for data in cdata:
                if 'comment' not in data:
                    continue
                comment = data['comment']

                cdate = comment['creationTime']
                cdate = datetime.datetime.strptime(cdate, "%Y-%m-%d %H:%M:%S").month
                month[cdate] += 1
                isMobile = comment['isMobile']
                plat['mobile'] += 1 if isMobile else 0
                plat['computer'] += 0 if isMobile else 1
                productColor = comment['productColor']
                productSize = comment['productSize']

                if productColor != '':
                    if productColor not in color :
                        color[productColor] = 0
                    else :
                        color[productColor] += 1
                if productSize != '':
                    if productSize not in size:
                        size[productSize] = 0
                    else:
                        size[productSize] += 1

            res.append(month)
            res.append(plat)
            res.append(size)
            res.append(color)
        except Exception as e :
            traceback.print_exc()
            print(e)
            print('comment_sum_parse error')
        return res

    #jd 商品分析
    def product_parse(self,pdata):
        res = []
        for p in pdata:
            if 'commentsCount' not in p:
                continue
            temp = {}
            commentsCount = p['commentsCount']
            temp['GoodRate'] = commentsCount['GoodRate']
            temp['GeneralRate'] = commentsCount['GeneralRate']
            temp['PoorRate'] = commentsCount['PoorRate']
            res.append(temp)
        return res


    def commentkeywords_parse(self,info):
        res = []
        text = ''
        try:
            for data in info:
                temp = {}
                if 'comment' not in data:
                    continue
                comment = data['comment']
                text = text + comment['content'] + '\n'
            pageParse = PageContract()
            res = pageParse.keywords(text)
        except:
            traceback.print_exc()
            print('commentkeywords_parse error')
        return res


if __name__ == '__main__':
    control = RedisControl()
    a= control.jd_comment_keywords('mysql','11863557')
    print(a)