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
import time

#connect to redis server
red=redis.Redis(host='localhost', port=6379, db=1)


def check_url(url):
    if red.sadd("url_crawled",url):
        red.lpush("url_queue",url)


if __name__=="__main__":

    '''
    start the crawler

    '''

    start=time.time()
    count=0

    #choose the running way of using database or not

    try:
        option=sys.argv[1]
    except:
        option=''
    if "mongo" not in option:
        option="print_data_out"
    i=0

    #the start page

    red.lpush("url_queue","https://www.zhihu.com/people/shi-wei-hu-bu-gui/followees")
    url=red.lpop("url_queue")
    new_crawler=crawler.Zhihu_Crawler(url,option=option)
    while(True):
        i=i+1
        if (i==5000000):
            break

        url_list=[]

        for i in range(600):

            url=red.lpop("url_queue")
            if url:
                url=url+"/followees"
                url_list.append(url.replace("https","http"))
                count+=1

        if not url_list:
            break

        #use gevent for asyn way crawling

        slaver=[]
        for url in url_list:
            slaver.append(gevent.spawn(crawler.Zhihu_Crawler,url,option))

        gevent.joinall(slaver)

    print "crawler has crawled %d people ,it cost %s" % (count,time.time()-start)
