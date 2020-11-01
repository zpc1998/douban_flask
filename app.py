from flask import Flask,render_template
import sqlite3
import requests

from bs4 import BeautifulSoup        #网页解析
import re                            #正则表达式，进行文字匹配
import urllib.request,urllib.error   #制定url，获取网页数据
import xlwt                          #进行excel操作
import sqlite3                       #进行sqlite数据库操作

findLink = re.compile(r'<a href="(.*)">')
#获取影片详情链接的规则

findTitle = re.compile(r'<span class="title">(.*)</span>')
# 获取影片名称

findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
# 获取影片评分

findJudge = re.compile(r'<span>(\d*)人评价</span>')
# 获取评价人数

findInq = re.compile(r'<span class="inq">(.*)</span>')
# 获取影片概括

findBD = re.compile(r'<p class="">(.*?)</p>',re.S)
# 影片背景

def getData(baseurl):
    dataList = []

    for i in range(0,10):   #调用获取页面信息的函数
        url = baseurl + str(i*25)
        html = askURL(url)      #保存获取到的网页源码

        # 逐一解析数据
        soup = BeautifulSoup(html,'html.parser')
        for item in soup.find_all('div',class_="item"): #查找符合要求的字符串，形成列表
            data = [] #保存一部电影的所有信息
            item = str(item)

            link = re.findall(findLink,item)[0]
            data.append(link)          #添加链接

            # imgSrc = re.findall(findImgSrc,item)[0]
            # data.append(imgSrc)        #添加图片

            titles = re.findall(findTitle,item)
            if(len(titles)==2):
                ctitle = titles[0]
                data.append(ctitle.strip()) #存储中文名
                otitle = titles[1].replace("\xa0", "")
                otitle = otitle.replace("/", "")
                data.append(otitle) #存储外文名
            else:
                data.append(titles[0])
                data.append('')    #外文名留空

            rating = re.findall(findRating,item)[0]
            data.append(rating) # 存储评分

            judgeNum = re.findall(findJudge,item)[0]
            data.append(judgeNum) # 存储评分人数

            inq = re.findall(findInq,item)
            if len(inq)!=0:
                inq = inq[0].replace("。","")
                data.append(inq)     # 添加概述
            else:
                data.append("")       #留空

            bd = re.findall(findBD,item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?',"",bd)
            bd = bd.replace("\xa0", "")
            data.append(bd.strip()) #strip用来去除空格，存储bd

            dataList.append(data) #把处理好的电影信息放入dataList中
    # print(dataList)

    return dataList

#得到指定一个URL的网页内容
def askURL(url):
    # 用户代理，表示告诉豆瓣浏览器，我们是什么类型的浏览器
    head = {            #模拟浏览器头部，向豆瓣发送消息
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"
    }

    request = urllib.request.Request(url,headers=head)

    html = ""

    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        # print(html)
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
    return html

def saveData2DB(datalist,dbpath):
    init_db(dbpath)

    conn = sqlite3.connect(dbpath)
    c = conn.cursor()  # 获取游标

    for data in datalist:
        for index in range(len(data)):
            data[index] = '"'+data[index]+'"'
            sql = '''
            insert into movie250(
            info_link,cname,ename,score,rated,instroduction,info)
            values(%s)'''%",".join(data)
        c.execute(sql)
        conn.commit()
    c.close()
    conn.close()

def init_db(dbpath):
    sql='''
    create table movie250(
    id integer primary key autoincrement,
    info_link teoxt,
    cname varchar,
    ename varchar,
    score numeric,
    rated numeric,
    instroduction text,
    info text
    )
    ''' #创建数据库

    conn = sqlite3.connect(dbpath)

    c = conn.cursor()  # 获取游标
    c.execute(sql)   #执行sql语句
    conn.commit()  # 提交数据库操作
    conn.close()  # 关闭数据库连接



app = Flask(__name__)


@app.route('/')
def index():
    baseurl = "https://movie.douban.com/top250?start="
    # # 爬取网页
    datalist = getData(baseurl)
    # # savepath = '豆瓣电影Top250.xls'
    dbpath = "movie.db"
    # # 保存数据
    # # saveData(datalist, savepath)
    #
    saveData2DB(datalist, dbpath)

    return render_template("index.html")


@app.route('/movie')
def movie():
    datalist = []
    con = sqlite3.connect("movie.db")
    cur = con.cursor()
    sql = "select * from movie250"
    data = cur.execute(sql)

    for item in data:
        datalist.append(item)

    cur.close()
    con.close()

    # baseurl = "https://movie.douban.com/top250?start="
    # # 爬取网页
    # datalist = getData(baseurl)


    return render_template("movie.html",movies=datalist)

@app.route('/score')
def score():
    score = [] #评分
    number = [] #电影数量

    con = sqlite3.connect("movie.db")
    cur = con.cursor()
    sql = "select score,count(score) from movie250 group by score"
    data = cur.execute(sql)
    for item in data:
        score.append(item[0])
        number.append(item[1])

    cur.close()
    con.close()


    return render_template("score.html",score=score,number=number)

@app.route('/word')
def word():
    return render_template("word.html")

@app.route('/team')
def team():
    return render_template("team.html")

if __name__ == '__main__':
    app.run(debug=True)
