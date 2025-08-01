from bs4 import BeautifulSoup     # 网页解析：获取数据的
import re       # 正则表达式：进行文字匹配
import urllib.request, urllib.error     # 制定URL：获取网页数据
import xlwt     # 进行excel操作
import sqlite3  # 进行SQLite数据库操作


def main():
    baseurl = "https://movie.douban.com/top250?start="
    # 1.爬取网页
    datalist = getData(baseurl)
    # 2.逐一解析数据
    # savepath = "豆瓣电影Top250.xls"
    dbpath = "moive.db"
    # 3.保存数据
    # saveData(datalist,savepath)
    saveData2DB(datalist,dbpath)


    askURL(baseurl)


# 影片详情链接的规则
findLink = re.compile(r'<a href="(.*?)">')          # 创建正则表达式对象,表示规则(字符串的模式)
# 影片图片
findImgSrc = re.compile(r'<img.*src="(.*?)"',re.S)  # re.S 让换行符包含在字符中
# 影片片名
findTitle = re.compile(r'<span class="title">(.*)</span>')
# 影片评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
# 找到评价人数
findJudge = re.compile(r'<span>(.*)人评价</span>')
# 找到概况
findInq = re.compile(r'<p class="quote"><span>(.*)</span>',re.S)
# 找到影片的相关内容
findBD = re.compile(r'<p>(.*?)</p>',re.S)

# . :表示一个字符
# * :表示0个或多个字符
# .*? :表示0个或1个字符

# 爬取网页
def getData(baseurl):
    datalist = []
    for i in range(0,10):       # 调用获取页面信息的函数，10次
        url = baseurl + str(i*25)
        html = askURL(url)      # 保存获取到的网页源码


        # 2.逐一解析数据
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all('div',class_="item"):         # 查找符合要求的字符串，形成列表
            # print(item)       # 测试:查看电影item全部信息
            data = []   # 保存一部电影的所有信息
            item = str(item)


            # 影片详情的链接
            link = re.findall(findLink, item)[0]     # re库用来通过正则表达式查找指定的字符串
            data.append(link)

            imSrc = re.findall(findImgSrc, item)[0]
            data.append(imSrc)

            titles = re.findall(findTitle,item)[0]
            if(len(titles) == 2):
                ctitle = titles[0]
                data.append(ctitle)
                otitle = titles[1].replace("/","")
                data.append(otitle)
            else:
                data.append(titles[0])
                data.append(' ')
            data.append(titles)

            rating = re.findall(findRating, item)[0]
            data.append(rating)

            judge = re.findall(findJudge, item)
            if len(judge) != 0:
                judge = judge[0]
            else:
                data.append(" ")
            data.append(judge)

            inq = re.findall(findInq, item)
            if len(inq) != 0:
                inq = inq[0].replace("。",'')    # 去掉句号
            else:
                data.append(" ")                # 留空
            data.append(inq)

            bd = re.findall(findBD, item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?'," ",bd)     # 去掉<br/>
            bd = re.sub('/'," ",bd)             # 替换/
            data.append(bd.strip())             # 去掉前后的空格

            datalist.append(data)       # 吧处理好的一部电影信息放入datalist
    print(datalist)


    return datalist

# 得到指定一个url的网页内容
def askURL(url):
    # 模拟浏览器头部信息，向豆瓣服务器发送消息
    head = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0",
        # 用户代理，表示告诉豆瓣服务器，我们是什么类型的机器，浏览器（本质上是告诉浏览器，我们可以接收什么水平的文件内容）
        'cookie': 'bid=Rfj967Jnxg8; ll="108296"; dbcl2="287686862:Wk44nmZKXM0"; ck=EBzM; push_noty_num=0; push_doumail_num=0'
    }
    request = urllib.request.Request(url=url,headers=head)
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

    return  html




# 保存数据
def saveData(datalist,savepath):
    book = xlwt.Workbook(encoding="utf-8",style_compression=0)  # 创建workbook对象
    sheet = book.add_sheet("豆瓣电影Top250",cell_overwrite_ok=True)     # 创建工作表
    col = ("电影详情链接","图片链接","影片中文名","影片外国名","评分","评分数","概况","相关信息")
    for i in range(0,8):
        sheet.write(0,i,col[i])     # 列名
    for i in range(0,250):
        print(f"第{i}条")
        data = datalist[i]
        for j in range(0,8):
            sheet.write(i+1,j,data[j])     # 数据


    book.save(savepath)        # 保存



def saveData2DB(datalist,dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cur = conn.cursor()

    for data in datalist:
        for index in range(len(data)):
            data[index] = '"' + str(data[index]) + '"'
        sql = '''
                insert into movie250 (
                info_link,pic_link,cname,ename,score,rated,instroduction,info
                )
                values(%s)'''%",".join(data)
        print(sql)
            # cur.execute(sql)
            # conn.commit()
    cur.close()
    conn.close()




def init_db(dbpath):
    sql = '''
            create table movie250
            (
            id integer primary key autoincrement,
            info_link text,
            pic_link text,
            cname varchar,
            ename varchar,
            score numeric,
            rated numeric,
            instroduction text,
            info text
            )
        '''    # 创建数据表
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()




if __name__ == "__main__":
    main()
    # init_db("movietest.db")
    print("爬取完成")