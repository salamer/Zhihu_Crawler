# -*- coding: utf-8 -*-
#encoding:utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import gevent.monkey
gevent.monkey.patch_socket()

import gevent
import redis
import crawler

#connect to redis server
red=redis.Redis(host='localhost', port=6379, db=1)


def check_url(url):
    if red.sadd("url_crawled",url):
        red.lpush("url_queue",url)


if __name__=="__main__":
    option=sys.argv[1][2:]
    if "mongo" not in option:
        option="print_data_out"
    i=0
    red.lpush("url_queue","https://www.zhihu.com/people/gaoming623")
    url=red.lpop("url_queue")
    new_crawler=crawler.Zhihu_Crawler(url,option=option)
    while(True):
        i=i+1
        if (i==100):
            break

        url_list=[]

        for i in range(10):

            url=red.lpop("url_queue")
            if url:
                url=url+"/followees"
                url_list.append(url.replace("https","http"))

        if url_list[0]=='':
            break

        pool=gevent.Pool(10)

        for url in url_list:
            if url:
                pool.spawn(crawler.Zhihu_Crawler,url,option)

        pool.join()
