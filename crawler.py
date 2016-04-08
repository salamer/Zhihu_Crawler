# -*- coding: utf-8 -*-
#encoding:utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import gevent.monkey
gevent.monkey.patch_socket()

import requests
from lxml import html
from db import Zhihu_User_Profile
from engine import check_url,re_crawl_url
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



class Zhihu_Crawler():

    '''
    basic crawler

    '''

    def __init__(self,url,option="print_data_out"):
        '''
        initialize the crawler

        '''

        self.option=option
        self.url=url
        self.header={}
        self.header["User-Agent"]="Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0"
#        self.header["Host"]="www.zhihu.com"
        self.header["Referer"]="www.zhihu.com"


        #cookie
        self.cookies={"z_c0":'"QUFBQUpVVXlBQUFYQUFBQVlRSlZUZWdmTGxjZGQwcTFzMnppNkEwZ1hIencwbEVvY3g5aThBPT0=|1460048614|9f8703140463dd604d6c3ab5739600f38260639e"',
                "unlock_ticket":'"QUFBQUpVVXlBQUFYQUFBQVlRSlZUZkdaQmxmTHdaSHdiSnNmMEVROTZVYnZ4MDQ5YVFTSDR3PT0=|1460048614|160bdd2e71c745ece7442bdf564babea39160506"',
                "login":'"MmNiNzhjYjUwNmQ1NDYxMmJhZTY2ZWI4ZjhkZmUxYzk=|1460048614|e4bc34730f8127c3e59123f6386bcb10c741d81d"',
                "n_c":"1",
                "q_c1":"f8482709919647889bcef40c15cd08ee|1460048593000|1460048593000",
                "l_cap_id":'"NjMwZTFjY2Q2MTM2NDFhYmFiZGU3M2IxOGM4MDdhMTE=|1460048593|31afee564365fbb9bb89d9a58b8ae4c7ef052608"',
                "d_c0":'"AHAA9ozGuwmPToJX_XSZ7l2aeKFKaTKYt80=|1460000226"',
                "cap_id":'"ZTcwNjIzYzY5NTQ5NDA2MDhmMzM3ZGRjMzk1ZGUyNDg=|1460048593|41eb3ac15a4f511323d65440be04c4c2b27cb3c7"'}

    def send_request(self):
        '''
        send a request to get HTML source

        '''
        try:
            r=requests.get(self.url,cookies=self.cookies,headers=self.header,verify=False)
        except requests.exceptions.ConnectionError as e:
            re_crawl_url(self.url)
            pass

        content=r.text

        if r.status_code==200:
            self.parse_user_profile(content)

    def process_xpath_source(self,source):
        if source:
            return source[0]
        else:
            return ''

    def parse_user_profile(self,html_source):
        '''
        parse the user's profile to mongo
        '''

        #initialize variances

        self.user_name=''
        self.fuser_gender=''
        self.user_location=''
        self.user_followees=''
        self.user_followers=''
        self.user_be_agreed=''
        self.user_be_thanked=''
        self.user_education_school=''
        self.user_education_subject=''
        self.user_employment=''
        self.user_employment_extra=''
        self.user_info=''
        self.user_intro=''

        tree=html.fromstring(html_source)

        #parse the html via lxml
        self.user_name=self.process_xpath_source(tree.xpath("//a[@class='name']/text()"))
        self.user_location=self.process_xpath_source(tree.xpath("//span[@class='location item']/@title"))
        self.user_gender=self.process_xpath_source(tree.xpath("//span[@class='item gender']/i/@class"))
        if "female" in self.user_gender and self.user_gender:
            self.user_gender="female"
        else:
            self.user_gender="male"
        self.user_employment=self.process_xpath_source(tree.xpath("//span[@class='employment item']/@title"))
        self.user_employment_extra=self.process_xpath_source(tree.xpath("//span[@class='position item']/@title"))
        self.user_education_school=self.process_xpath_source(tree.xpath("//span[@class='education item']/@title"))
        self.user_education_subject=self.process_xpath_source(tree.xpath("//span[@class='education-extra item']/@title"))
        self.user_followees=tree.xpath("//div[@class='zu-main-sidebar']//strong")[0].text
        self.user_followers=tree.xpath("//div[@class='zu-main-sidebar']//strong")[1].text

        self.user_be_agreed=self.process_xpath_source(tree.xpath("//span[@class='zm-profile-header-user-agree']/strong/text()"))
        self.user_be_thanked=self.process_xpath_source(tree.xpath("//span[@class='zm-profile-header-user-thanks']/strong/text()"))
        self.user_info=self.process_xpath_source(tree.xpath("//span[@class='bio']/@title"))
        self.user_intro=self.process_xpath_source(tree.xpath("//span[@class='content']/text()"))

        if self.option=="print_data_out":
            self.print_data_out()
        else:
            self.store_data_to_mongo()

        #find the follower's url
        url_list=tree.xpath("//h2[@class='zm-list-content-title']/a/@href")
        for target_url in url_list:
            target_url=target_url.replace("https","http")
            target_url=target_url+"/followees"
            check_url(target_url)

    def print_data_out(self):
        '''
        打印用户信息
        '''

        print "*"*60
        print '用户名:%s\n' % self.user_name
        print "用户性别:%s\n" % self.user_gender
        print '用户地址:%s\n' % self.user_location
        print "被同意:%s\n" % self.user_be_agreed
        print "被感谢:%s\n" % self.user_be_thanked
        print "被关注:%s\n" % self.user_followers
        print "关注了:%s\n" % self.user_followees
        print "工作:%s/%s" % (self.user_employment,self.user_employment_extra)
        print "教育:%s/%s" % (self.user_education_school,self.user_education_subject)
        print "用户信息:%s" % self.user.info
        print "*"*60

    def store_data_to_mongo(self):
        '''
        store the data in mongo
        '''
        new_profile=Zhihu_User_Profile(
            user_name=self.user_name,
            user_be_agreed=self.user_be_agreed,
            user_be_thanked=self.user_be_thanked,
            user_followees=self.user_followees,
            user_followers=self.user_followers,
            user_education_school=self.user_education_school,
            user_education_subject=self.user_education_subject,
            user_employment=self.user_employment,
            user_employment_extra=self.user_employment_extra,
            user_location=self.user_location,
            user_gender=self.user_gender,
            user_info=self.user_info,
            user_intro=self.user_intro,
            user_url=self.url
        )
        new_profile.save()
        print "saved:%s \n" % self.user_name
