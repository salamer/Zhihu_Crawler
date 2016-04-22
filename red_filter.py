# -*- coding: utf-8 -*-
# encoding:utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import redis

red_queue = "the_test_the_url_queue"
red_crawled_set = "the_test_url_has_crawled"

# connect to redis server
red = redis.Redis(host='localhost', port=6379, db=1)


def re_crawl_url(url):
    red.lpush(red_queue, url)


def check_url(url):
    if red.sadd(red_crawled_set, url):
        red.lpush(red_queue, url)
