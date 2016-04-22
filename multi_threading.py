# -*- coding: utf-8 -*-
# encoding:utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import redis
import thread_crawler
import time
from multiprocessing.dummy import Pool
from red_filter import red,red_queue




def create_new_slave(url, option):
    new_slave = thread_crawler.Zhihu_Crawler(url, option)
    new_slave.send_request()
    return "ok"

def thread_worker(option):
    while True:
        url = red.lpop(red_queue)
        if not url:
            break
        create_new_slave(url, option)

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
    for i in range(20):
        url=red.lpop(red_queue)
        create_new_slave(url, option=option)

    threading_pool=Pool(50)
    threading_pool.map_async(thread_worker, option)
    threading_pool.close()
    threading_pool.join()

    print "crawler has crawled %d people ,it cost %s" % (count, time.time() - start)
