import urllib.parse

from flask import Flask, request
from JD.conf import config
from JD.spiders import JDSearchSpider

from JD.www.RedisControl import RedisControl

app = Flask(__name__)
# Redis控制器
redisControl = RedisControl()

'''
   读取conf中关于APP的文件配置
'''
app_conf = config.configs['APP']
jd_search_redis_name = app_conf['jd_search_redis_name']
csdn_search_redis_name = app_conf['csdn_search_redis_name']
pagesize = app_conf['pagesize']


'''
    查找京东商品
    shopname 查找关键字
'''
@app.route('/search/jd',methods=['GET','POST'])
def jd_search_shop():
    JDSearchSpider.keyname  = ''
    shopname = request.args.get('name')
    url = 'https://search.jd.com/Search?keyword=%s&page=1&enc=utf-8'%(shopname)
    # 初始化redis ，mysql中有关数据，防止爬虫因为去重启动错误 和 数据重复
    # redisControl.redis_mysql_init(jd_search_redis_name)
    # 开始爬取
    redisControl.lpush_start_url(redisname=jd_search_redis_name,url=url)
    return ""


'''
    京东商品列表换页
    get 请求中包含页号
'''
@app.route('/search/jd/shoplist/',methods=['GET'])
def jd_shoplist_page_change():
    shopname = request.args.get('shopname')
    page = request.args.get('page')
    startno = (int(page)-1)*pagesize
    # 获取页面内容并返回
    info = redisControl.jd_item(shopname,startno=startno,pagesize=pagesize)
    # print(info)
    return info


'''
    单个京东商品的评论
    get 请求中包含页号
'''
@app.route('/search/jd/comment',methods=['GET'])
def jd_comment():
    item_id = request.args.get('item_id')
    shopname = request.args.get('shopname')
    # 获取页面内容并返回
    info = redisControl.jd_comment(shopname,item_id=item_id)
    # print(info)
    return info


'''
    对于商品的分析
    shopname 请求中包含页号
'''
@app.route('/search/jd/productsum',methods=['GET'])
def jd_productsum():
    item_id = request.args.get('item_id')
    shopname = request.args.get('shopname')
    # 获取页面内容并返回
    info = redisControl.jd_product_sum(shopname,item_id=item_id)
    # print(info)
    return info


'''
    对于商品的分析
    shopname 请求中包含页号
'''
@app.route('/search/jd/commentkey',methods=['GET'])
def jd_commentkey():
    item_id = request.args.get('item_id')
    shopname = request.args.get('shopname')
    # 获取页面内容并返回
    info = redisControl.jd_comment_keywords(shopname,item_id=item_id)
    # print(info)
    return info


'''
   停止京东商品的爬取
'''
@app.route('/search/jd/stop',methods=['GET','POST'])
def jd_stop_search():
    redisControl.redis_stop(jd_search_redis_name)


'''
    查找csdn
    shopname 查找关键字
'''
@app.route('/search/csdn',methods=['GET','POST'])
def csdn_search_shop():
    JDSearchSpider.keyname  = ''
    shopname = request.args.get('name')
    url = 'http://so.csdn.net/so/search/s.do?q=%s&t=blog&p=1'%(shopname)
    redisControl.lpush_start_url(redisname=csdn_search_redis_name,url=url)
    return ""


'''
    csdn列表页
    get 请求中包含页号
'''
@app.route('/search/csdn/shoplist/',methods=['GET'])
def csdn_shoplist_page_change():
    shopname = request.args.get('shopname')
    page = request.args.get('page')

    startno = (int(page)-1)*pagesize
    # 获取页面内容并返回
    info = redisControl.csdn_item(shopname,startno=startno,pagesize=pagesize)
    return info


'''
    csdn文章页
'''
@app.route('/search/csdn/article/',methods=['GET'])
def csdn_article():
    shopname = request.args.get('shopname')
    src = request.args.get('src')
    # 获取页面内容并返回
    info = redisControl.csdn_article(shopname,src)
    # print(info)
    return info


'''
   停止csdn的爬取
'''
@app.route('/search/csdn/stop',methods=['GET','POST'])
def csdn_stop_search():
    redisControl.redis_stop(csdn_search_redis_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)