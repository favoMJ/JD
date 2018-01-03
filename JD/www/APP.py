from flask import Flask, request
from JD.conf import config

from JD.www.RedisControl import RedisControl

app = Flask(__name__)
redisControl = RedisControl()
# 读取APP配置文件
app_conf = config.configs['APP']
search_redis_name = app_conf['search_redis_name']
pagesize = app_conf['pagesize']

@app.route('/search/shop/<shopname>',methods=['GET','POST'])
def search_shop(shopname):
    url = 'https://search.jd.com/Search?keyword=%s&page=1'%(shopname)
    redisControl.redis_init(search_redis_name)
    redisControl.lpush_start_url(redisname=search_redis_name,url=url)
    # info = redisControl.get_item(search_redis_name)
    return ""

@app.route('/search/<shopname>',methods=['GET'])
def page_change(shopname):
    page = request.args.get('page')
    startno = (int(page)-1)*pagesize
    info = redisControl.get_item(search_redis_name,startno=startno,pagesize=pagesize)
    return str(list(info))

@app.route('/search/stop',methods=['GET','POST'])
def stop_search():
    redisControl.redis_stop(search_redis_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)