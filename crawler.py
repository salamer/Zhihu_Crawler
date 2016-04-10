# -*- coding: utf-8 -*-
#encoding:utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import gevent.monkey
gevent.monkey.patch_all()

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
        self.cookies={"z_c0":'"QUZDQUp3czV3QWtYQUFBQVlRSlZUZkx3TVZmaFBMWlp2em04Ym1PN01BMldtRktscHRMOVVBPT0=|1460298735|34e9183179a0555057f1cfcc2c8f63660a2f4fc5"',
                "unlock_ticket":'QUZDQUp3czV3QWtYQUFBQVlRSlZUZnBxQ2xmSWNXX3NuVXo3SVJleUM5Uy1BLUpEdXJEcEpBPT0',
                "login":'"ZjliNTRhNzViMDQ2NDMzY2FmZTczNjNjZDA4N2U0NGU=|1460298735|b1048ba322e44c391aa15306198503eab8b28f26"',
                "n_c":"1",
                "q_c1":"a15d5ad71c734d5b9ab4b1eddacea368|1460298703000|1460298703000",
                "l_cap_id":'"YjMzMGNjMTUxMWIzNGZiMWI2OWI2ZGI1ZDM5NTAzZTQ=|1460298703|dd2d5dec11620d64a65ea057bd852f10124a283f"',
                "d_c0":'"AJAAgETzqAmPTgxl_8gbpkFvESCkSwIZMoU=|1458736882"',
                "cap_id":'"MmI2OTJiNWVkZGFmNGNmZDk0NDY2YTBlODI1ZjgyMWQ=|1460298703|b185f46c6887417393049379e47d961708cfdac7"'}

    def send_request(self):
        '''
        send a request to get HTML source

        '''
        added_followee_url=self.url+"/followees"
        try:
            r=requests.get(added_followee_url,cookies=self.cookies,headers=self.header,verify=False)
        except:
            re_crawl_url(self.url)
            return

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
        try:
            self.user_followees=tree.xpath("//div[@class='zu-main-sidebar']//strong")[0].text
            self.user_followers=tree.xpath("//div[@class='zu-main-sidebar']//strong")[1].text
        except:
            return

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
        print "用户信息:%s" % self.user_info
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
