# -*- coding: utf-8 -*-
#encoding:utf-8

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import requests
from lxml import html
from db import Zhihu_User_Profile
from engine import check_url
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
        self.header["Host"]="www.zhihu.com"
        self.header["Referer"]="www.zhihu.com"


        #cookie
        self.cookies={"z_c0":'"QUFBQUpVVXlBQUFYQUFBQVlRSlZUYUJpTFZkNkRDRlo0NFhyLWhIb2R4ckM1MFR3WUxjbTBRPT0=|1460000159|885154c5438da099d6c714797acfd3f3749bfa8b"',
                "unlock_ticket":'"QUFBQUpVVXlBQUFYQUFBQVlRSlZUYWpjQlZkcmp4NG1qOFltekZNNEtRV3hWWlZiNjBhM1lRPT0=|1460000159|b00a762b7ee4771983926ba19056b83106753fd1"',
                "login":'"Y2U5ZGQ5MjgwMjdlNGM2MmFhOGEyNWU2N2VjZGI3Mzk=|1460000159|b8d32ec0b7dbcd12ec7bb1ea94738d7681f05fac"',
                "n_c":"1",
                "q_c1":"d7e4b7d6167e43f888c8ba0aef6c7ff8|1460000159000|1460000159000",
                "l_cap_id":'"Y2U5ZGQ5MjgwMjdlNGM2MmFhOGEyNWU2N2VjZGI3Mzk=|1460000159|b8d32ec0b7dbcd12ec7bb1ea94738d7681f05fac"',
                "d_c0":'"AHAA9ozGuwmPToJX_XSZ7l2aeKFKaTKYt80=|1460000226"',
                "cap_id":'"MDk0MzBlNWU1YzliNDkzY2E4MDdjMDcxZmU1NDI3MjY=|1460000159|857d62637fceb8ffb8adaceaefad405c44be2054"'}

        self.send_request()


    def send_request(self):
        '''
        send a request to get HTML source

        '''

        r=requests.get(self.url,cookies=self.cookies,headers=self.header,verify=False)
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
        )
        new_profile.save()
        print "saved:%s \n" % self.user_name
