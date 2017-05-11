#! /usr/bin/python3
from urllib import request
from lxml import html
import os
import time
import multiprocessing

url = 'http://www.mzitu.com/'

def getStr(url):
    return html.fromstring(request.urlopen(url).read().decode())
def getMainPage():
    return [x for x in getStr(url).xpath("//ul[@id='pins']/li/a/@href")]

def getPiclink(url):
    str = getStr(url)
    total = str.xpath("//div[@class='pagenavi']/a[last()-1]/span/text()")[0]
    title = str.xpath("//h2[@class='main-title']/text()")[0]
    def inUrl(x):
        link = '{}/{}'.format(url, x+1)
        s = getStr(link)
        return s.xpath("//div[@class='main-image']/p/a/img/@src")[0]
    jpgList = list(map(inUrl,range(int(total))))
    print('getPiclink',jpgList)
    return [[title,jpgList]]
def downloadPic(args,pid=0):
    print('downloadPic pid is %d : ' % pid)
    title,picList = args
    k = 1
    count = len(picList)
    dirName = u"[%sP] %s" % (str(count), title)
    if os.path.exists(dirName):
        return True
    os.mkdir(dirName)
    for i in picList:
        filename = '%s/%s/%s.jpg' % (os.path.abspath('.'),dirName, k)
        print(u"pid %d downloading :%s the  %s piece" % (pid, dirName, k))
        try:
            sjpg = request.urlopen(i).read()
        except Exception:
            return True
        with open(filename, 'wb') as f:
            f.write(sjpg)
        k += 1

def starDown(url, pid =0):
    print('starDown pid is %d : ' % pid)
    ss = getPiclink(url)
    for x in ss:
        downloadPic(x, pid)
    #list(map(downloadPic,getPiclink(url)))

class DownProcess(multiprocessing.Process):
    def __init__(self,urls):
        super().__init__()
        self.urls = urls
    def run(self):
        print('active pid is %d : ' % self.pid)
        for x in self.urls:
            starDown(x, self.pid)
        #list(map(starDown, self.urls))


if __name__ == '__main__':
    #list(map(starDown, getMainPage()))
    pages = getMainPage()
    proces = []
    for i in range(0, len(pages),6):
        proces.append(DownProcess(pages[i:i+6]))

    for i in proces:
        i.start()
