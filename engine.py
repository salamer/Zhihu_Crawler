# -*- coding: utf-8 -*-
#encoding:utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import redis
import crawler

#connect to redis server
red=redis.Redis(host='localhost', port=6379, db=1)


def check_url(url):
    if red.sadd("url_crawled",url):
        red.lpush("url_queue",url)


if __name__=="__main__":
    i=0
    red.lpush("url_queue","https://www.zhihu.com/people/gaoming623")
    url=red.lpop("url_queue")
    while(url):
        i=i+1
        url=url+'/followees'
        new_crawler=crawler.Zhihu_Crawler(url)
        new_crawler.send_request()
        if (i==100):
            break
        url=red.lpop("url_queue")
