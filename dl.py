# -*- encoding: UTF-8 -*-
#!/usr/bin/python


import requests
import re,os
import time,random
def tupian(leixing):
    page=1                 #初始page=1
    i=1                    #记录图片个数
    while True:           #爬到地老天荒
        url = 'https://unsplash.com/napi/search/photos?query='+leixing+'&xp=&per_page=20&page='+str(page)
        r = requests.get(url)        #获取网页代码
        r.headers={
    'Pragma' : 'no-cache',
    'Cache-Control' : 'no-cache',
    'Upgrade-Insecure-Requests' : '1',
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36',
    'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language' : 'zh-CN,zh;q=0.9',
    'Connection' : 'close',
}              #设置requests的一些特征，防止反爬虫机制
        #print(r.text)
        key = '\"download\":\"https://unsplash.com/photos/(.*?)/download\"'  #下载图片的固定url
        c = re.findall(key,r.text, re.S)        #提取图片id
        # print(c)
        for id in c:                
            time.sleep(random.uniform(0,1))                #为了尽量友好，设置超时时间
            if i%10==0:                                    #也是为了友好。
                time.sleep(10)
            try:
                fp=open('E:\\图片\\'+leixing+"\\"+id+'.jpg',"wb")               #打开文件
            except:
                os.makedirs('E:\\图片\\' + leixing + "\\")            #没有此文件夹的话，新建文件夹
            print("正在下载第{}张图片".format(i))
            d = requests.get('https://unsplash.com/photos/'+id+'/download')        #获取图片数据
            try:
                fp.write(d.content)         #将数据写入文件
                fp.close()                  
                print("完成！")
            except:
                print("无法连接！")
                continue
            page = page + 1             #page数量变换达到重复爬取的目的
            i = i + 1                   #爬取数量计数
leixing=input("输入你想要的图片类型：") #输入图片类型
tupian(leixing)
