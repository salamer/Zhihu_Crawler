'''
import gevent.monkey
gevent.monkey.patch_socket()
import time

import gevent
from gevent.pool import Pool
import requests

class h():
    def __init__(self,n,x):
        self.n=n
        self.print_out(self.n,x)
    def print_out(self,n,x):
        requests.get(n)
        print n
        print x

pool=Pool(2)
urls=set=()
urls=[
    'http://zhihu.com',
    'http://baidu.com',
    'http://zhaduixueshe.com',
    'http://douban.com',

]
for url in urls:
    pool.spawn(h,url,3)

pool.join()
'''
import sys
if 'mongo' in sys.argv[1]:
    print "yes"
