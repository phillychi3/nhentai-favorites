import gevent.monkey

gevent.monkey.patch_all()
import csv
import json
import os
import queue
import random
import threading
import time

import fake_useragent
import requests
import yaml
from bs4 import BeautifulSoup
from progress.spinner import PixelSpinner

from gettags import get_tags


with open('set.yaml', 'r') as f:
    cookie = yaml.load(f, Loader=yaml.CLoader)["cookid"]
# setting
url = "https://nhentai.net/favorites/"
apiurl = "https://nhentai.net/api/gallery/"
table = [
    ["id", "name", "tags"]
]
now = 1
allnumbers = []
allnames = []
alltags = []

class gettagonline(threading.Thread):
    def __init__(self, queue,number):
        threading.Thread.__init__(self)
        self.number = number
        self.queue = queue

    def run(self):
        while self.queue.qsize() > 0:
            num = self.queue.get()
            #print("get %d: %s" % (self.number, num))
            ua = fake_useragent.UserAgent()
            useragent = ua.random
            headers = {
                'user-agent': useragent
            }
            r = requests.get(apiurl + num, headers=headers)
            data = r.json()
            ctag = []
            for i in enumerate(data['tags']):
                ctag.append(i[1]['name'])
            alltags.append(ctag)
            time.sleep(random.uniform(0.5,1))



set1 = input("請問要使用離線資料嗎?(y/n)(默認為否)")
if set1 == "y".lower() or  set1 == "yes".lower() :
    if not os.path.isfile("tag.json"):
        print("沒有發現離線資料 抓取中請稍後...")
        get_tags()
        print("抓取完畢")
    print("使用離線資料")
else:
    print("使用線上資料")
    threadscount = input("請輸入要使用幾個線程(默認為5 不可超過10)")
    if threadscount == "":
        threadscount = 5
    else:
        try:
            threadscount = int(threadscount)
            if threadscount > 10:
                threadscount = 10
        except:
            threadscount = 5

spinner = PixelSpinner('抓取資料中...')
while True:
    ua = fake_useragent.UserAgent()
    useragent = ua.random
    headers = {
        'user-agent': useragent,
        'cookie': cookie
    }
    data = requests.get(f"{url}?page={now}", headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    book = soup.find_all("div", class_='gallery-favorite')
    if book == []:
        break
    numbers = [t.get('data-id') for t in book]
    names = [t.find('div',class_="caption").get_text() for t in book]
    tags_ = [t.find('div',class_="gallery").get('data-tags') for t in book]
    tags = []
    for i in tags_:
        tags__ = i.split(' ')
        tags.append(tags__)
    allnumbers.extend(numbers)
    allnames.extend(names)
    alltags.extend(tags)
    now += 1
    spinner.next()



if set1 == "y".lower() or  set1 == "yes".lower() :
    with open('tag.json', 'r') as f:
        tagjson = json.load(f)
    for i in enumerate(allnumbers):
        tagstr = ""
        for j in alltags[i[0]]:
            if j in tagjson:
                tagstr += tagjson[j] + ", "

        table.append([i[1], allnames[i[0]], tagstr])    
else:
    alltags=[] # 清空
    get_tags_queue = queue.Queue()
    threads = []
    for i in allnumbers:
        get_tags_queue.put(i)
    for i in range(threadscount):
        t = gettagonline(get_tags_queue,i)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    

    for i in enumerate(allnumbers):
        table.append([i[1], allnames[i[0]], alltags[i[0]]])    


with open('output.csv', 'w', newline='',encoding="utf_8_sig") as csvfile:
  writer = csv.writer(csvfile)
  writer.writerows(table)
