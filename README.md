#ZHIHU_CRAWLER

******

this is web crawler for [zhihu.com](http://zhihu.com)

the crawler use __Redis__ for checking the url has been crawled or not,and use __mongodb__ for storing data.

if you wanna print out the data,run:

    python engine.py --mongo

the crawler would store the data in mongodb

but if just run :

    python engine.py

you will see

    ************************************************************
    用户名:Mingo鸣哥

    用户性别:female

    用户地址:香港

    被同意:59960

    被感谢:14474

    被关注:39055

    关注了:806

    工作:记者/
    教育:香港中文大学 (Chinese University of Hong Kong)/新媒体
    ************************************************************
