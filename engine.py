# -*- coding: utf-8 -*-
# encoding:utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import gevent.monkey
gevent.monkey.patch_all()

import gevent
import redis
import crawler
import time
from multiprocessing import Pool
import multiprocessing

from red_filter import red,red_queue
# wrap the class method


def create_new_slave(url, option):
    new_slave = crawler.Zhihu_Crawler(url, option)
    new_slave.send_request()
    return "ok"


def gevent_worker(option):
    while True:
        url = red.lpop(red_queue)
        if not url:
            break
        create_new_slave(url, option)


def process_worker(option):
    jobs = []
    for i in range(50):
        jobs.append(gevent.spawn(gevent_worker, option))
    gevent.joinall()


if __name__ == "__main__":

    '''
    start the crawler

    '''

    start = time.time()
    count = 0

    # choose the running way of using database or not

    try:
        option = sys.argv[1]
    except:
        option = ''
    if "mongo" not in option:
        option = "print_data_out"
    i = 0

    # the start page

    red.lpush(red_queue, "https://www.zhihu.com/people/gaoming623")
    url = red.lpop(red_queue)
    create_new_slave(url, option=option)
    for i in range(50):
        url=red.lpop(red_queue)
        create_new_slave(url, option=option)
    process_pool=Pool(multiprocessing.cpu_count()*2)
    process_pool.map_async(process_worker, option)
    process_pool.close()
    process_pool.join()

    '''
    while(True):

        url_list=[]

        for i in range(50):
            url=red.lpop(red_queue)
            if url:
                url_list.append(url)
                count+=1

        if not url_list:
            break

        #use gevent for asyn way crawling

        slaver=[]
        for url in url_list:
            slaver.append(gevent.spawn(create_new_slave,url,option))

        gevent.joinall(slaver)
    '''

    print "crawler has crawled %d people ,it cost %s" % (count, time.time() - start)
