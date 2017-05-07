#! /usr/bin/python3

from urllib import request
from lxml import html
import os
import pickle
from functools import partial, wraps
import time


source_file = 'progress.txt'
index_url = 'http://www.mzitu.com'
page_url = 'http://www.mzitu.com/page/%d'
person_url = 'http://www.mzitu.com/%d'
person_pageurl = 'http://www.mzitu.com/%d/$d'

def dd(str):
    print(str)
    exit()

def format_name(img_title):
    '''
    对名字进行处理，如果包含下属字符，则直接剔除该字符
    :param img_title:
    :return:
    '''
    for i in ['\\','/',':','*','?','"','<','>','!','|']:
        while i in img_title:
            img_title = img_title.strip().replace(i, '')
    return img_title

def mkdir(path):
    path = format_name(path)
    ospath = os.path.join("mzitu",path)
    isExists = os.path.exists(ospath)
    if not isExists:
        print(u'make %s directory' % path)
        os.makedirs(ospath)
        return ospath
    else:
        return False


def saveImg(path,url,i):
    print(u'downloading the %d pic' % i)
    title = url.split('/')[-1]
    filename = (path + '/%d.jpg') % i
    try:
        buf = request.urlopen(url).read()
        with open(filename,'wb') as f:
            f.write(buf)
    except Exception:
        pass


class progressIndex:
    def __init__(self, filename):
        self.filename = filename
        f = open(filename,'rb')
        try:
            self.data = pickle.load(f)
        except Exception:
            f = open(filename,'rb')
            self.data = {'index':142, 'page':140, 'pic':0}
            pickle.dump(self.data,f)
        f.close()

    def getData(self):
        return self.data

    def setData(self,name,value):
        self.data[name] = value
        with open(self.filename, 'wb') as f:
            pickle.dump(self.data,f)
        return self.data

    def setPage(self,page):
        return self.setData('page',page)
    def setPic(self,page):
        return self.setData('pic',page)


def getStr(url):
    return html.fromstring(request.urlopen(url).read().decode())

def getPages(str):
    pages = str.xpath("//nav[@class='navigation pagination']//a[last()-1]/text()")
    return pages

def urlp(url,n):
    return url % (n)
def getPagePicNum(str):
    ss =  str.xpath("//div[@class='postlist']//li/span/a[1]")
    def aa(item):
        href = item.xpath("./@href")[0]
        title = item.xpath("./text()")[0]
        return [title,href]
    return list(map(aa,ss))


def getPageName(str):
    return str.xpath("//div[@class='content']/h2[@class='main-title']/text()")[0]
def getPicNum(str):
    ss = str.xpath("//div[@class='pagenavi']//a[last()-1]/span/text()")[0]
    return int(ss)

def pagePic(url):
    str = getStr(url)
    return str.xpath("//div[@class='main-image']/p/a/img/@src")[0]

getIndex = partial(urlp,index_url)
getPage = partial(urlp,page_url)
getPerson = partial(urlp,person_url)

def personStart(url):
    pass

def dirs(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(args)
        path = mkdir(args[0][0])
        if path:
            return func(*args, path = path)
        else:
            print(u'This is already have!' )
            return lambda x : x
    return wrapper


@dirs
def pageStart(l, path):
    print('downloading directory',path)
    str = getStr(l[1])
    nums = getPicNum(str) + 1
    pUrl = partial(urlp,l[1] + '/%d')
    saveJpg = partial(saveImg,path)
    picUrl = list(map(pUrl, range(1,nums))) 
    imgUrl = list(map(hrefToImgSrc, picUrl))
    list(map(saveJpg , imgUrl,range(1,nums)))

def hrefToImgSrc(url):
    return getStr(url).xpath("//div[@class='main-image']/p/a/img/@src")[0]

if __name__ == '__main__':
    p = progressIndex('progress.pkl')
    for i in range(p.data['page'], 1,-1):
        p.setPage(i)
        print(u'the %d page\n' % i)
        pageStr = getStr(getPage(i))
        picNums = getPagePicNum(pageStr)
        list(map(pageStart, picNums))
        time.sleep(0.5)



