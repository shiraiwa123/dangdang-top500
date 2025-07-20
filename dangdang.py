import urllib.request
import re
from bs4 import BeautifulSoup
import xlwt


def main():
    old_url = 'http://bang.dangdang.com/books/bestsellers/01.00.00.00.00.00-24hours-0-0-1-'
    datalist = getdata(old_url)
    savepath = "当当前500畅销书籍.xls"
    savedata(datalist,savepath)




findlink = re.compile(r'<a href="(.*?)">')
findpage = re.compile(r'<img[^>]*src="([^"]*)"', re.S)
findtitle = re.compile(r'title="(.*?)">')
findauthor = re.compile(r'<div class="publisher_info">\s*<a.*?>(.*?)</a>')
findrelease = re.compile(r'<div class="publisher_info">\s*<span>(.*?)</span>')


def getdata(parurl):
    datalist = []
    for i in range(1,26):
        url = parurl + str(i)
        html = askurl(url)

        soup = BeautifulSoup(html, "html.parser")
        for item in soup.select("ul[class=\"bang_list clearfix bang_list_mode\"] > li"):
            # print(item)
            data = []
            item = str(item)

            link = re.findall(findlink, item)[0].replace("\" target=\"_blank","")
            data.append(link)

            page = re.findall(findpage,item)
            if len(page) != 0:
                page=page[0]
                data.append(page)

            title = re.findall(findtitle,item)[0]
            data.append(title)

            author = re.findall(findauthor,item)
            if len(author) != 0:
                author[0]
                data.append(author)
            else:
                data.append(" ")

            release = re.findall(findrelease,item)[0]
            data.append(release)

            datalist.append(data)
    return datalist











def askurl(url):
    headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0'}

    request = urllib.request.Request(url=url,headers=headers)

    response = urllib.request.urlopen(request)

    html = response.read().decode('gbk')
    return html




def savedata(datalist,savepath):
    book = xlwt.Workbook(encoding="utf-8")
    sheet = book.add_sheet("当当前500畅销书籍.xls")
    col = ("详情超链接","书籍封面","书籍名","书籍作者","发售日期")
    for i in range(0,5):
        sheet.write(0,i,col[i])
    for i in range(0,500):
        data = datalist[i]
        for j in range(0,5):
            sheet.write(i+1,j,data[j])
    book.save(savepath)




if __name__ == "__main__":
     main()

