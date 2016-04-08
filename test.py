
import gevent.monkey
gevent.monkey.patch_socket()
import time

import gevent
from gevent.pool import Pool
import requests
import urllib2

the_list=range(6)

class h():
    def __init__(self,n,x):
        self.n=n
        self.print_out(self.n,x)
    def print_out(self,n,x):
        urllib2.urlopen(n)
        print n
        print the_list.pop()

pool=Pool(2)
urls=set=()
urls=[
    'http://zhihu.com',
    'http://facebook.com',
    'http://zhaduixueshe.com',
    'http://google.com',
    'http://hao123.com',
    'http://duoshuo.com',
    'http://v2ex.com'

]

for url in urls:
    pool.spawn(h,url,3)

pool.join()
'''
jobs=[]
for url in urls:
    jobs.append(gevent.spawn(h,url,1))
gevent.joinall(jobs)
'''
'''
import sys
if 'mongo' in sys.argv[1]:
    print "yes"
'''
