import time, re
from lxml import etree
import requests
import pymysql

'''
CREATE TABLE doubanmovie(
	id int(11),
    name text,
    director text,
    actor text,
    style text,
    country text,
    release_time text,
    time text,
    score text
)ENGINE INNODB DEFAULT CHARSET=utf8;

'''

# https://movie.douban.com/top250
conn = pymysql.connect(host='localhost', user='root', passwd='123456', db='django_movie',port=3306)
cursor = conn.cursor()  # 连接数据库及光标

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}


# 获取电影详情页url
def get_movie_url(url):
    r = requests.get(url, headers=headers)
    selector = etree.HTML(r.text)
    movie_hrefs = selector.xpath('//div[@class="hd"]/a/@href')  # 电影的详情地址
    for movie_href in movie_hrefs:
        get_movie_info(movie_href)  # 调用ge_movie_info()函数获取电影信息
    pass


# 获取电影信息
def get_movie_info(url):
    r = requests.get(url, headers=headers)
    selector = etree.HTML(r.text)
    try:
        name = selector.xpath('//*[@id="content"]/h1/span[1]/text()')[0]  # 电影名
        director = selector.xpath('//div[@id="info"]/span[1]/span[2]/a/text()')[0]  # 导演
        actors = selector.xpath('//*[@id="info"]/span[3]/span[2]')[0]  # 演员
        actor = actors.xpath('string(.)')  # 标签套标签，用string(.)同时获取所有文本
        style_list = re.findall('<span property="v:genre">(.*?)</span>', r.text, re.S)
        style = '/'.join(style_list)  # 类型
        country = re.findall('<span class="pl">制片国家/地区:</span>(.*?)<br/>', r.text, re.S)[0]  # 地区
        release_time = re.findall('上映日期:</span>.*?>(.*?)</span>', r.text, re.S)  # 上映日期
        time = re.findall('片长:</span>.*?>(.*?)</span>', r.text, re.S)  # 片长
        score = selector.xpath('//*[@id="interest_sectl"]/div[1]/div[2]/strong/text()')[0]

        cursor.execute(
            "insert into doubanmovie(name,director,actor,style,country,release_time,time,score) values(%s,%s,%s,%s,%s,%s,%s,%s)",
            (str(name), str(director), str(actor), str(style), str(country), str(release_time), str(time), str(score)))
    except IndexError:
        print('出现索引错误' + url)
        pass  # 去掉索引错误


# 主函数
if __name__ == '__main__':
    urls = ['https://movie.douban.com/top250?start={}' \
                .format(str(i)) for i in range(0, 226, 25)]

    for url in urls:
        print('正在爬取' + url)
        get_movie_url(url)  # 调用get_movie_url()函数获取电影详情页的url
        time.sleep(2)

    conn.commit()