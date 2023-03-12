from gettags import get_tags
from progress.spinner import PixelSpinner
from bs4 import BeautifulSoup
import yaml
import requests
import locale
import os
import json
import csv


if not os.path.isfile("set.yaml"):
    with open('set.yaml', 'w') as f:
        yaml.dump({"cookid": "", "useragent": ""}, f)
    print("Please edit set.yaml")
    exit()

with open('set.yaml', 'r') as f:
    data = yaml.load(f, Loader=yaml.CLoader)
    cookie = data["cookid"]
    useragent = data["useragent"]
    if cookie == "":
        print("Please edit set.yaml")
        exit()
# setting
URL = "https://nhentai.net/favorites/"
APIURL = "https://nhentai.net/api/gallery/"
table = [
    ["id", "name", "tags"]
]
now = 1
allnumbers = []
allnames = []
alltags = []
locate = locale.getdefaultlocale()[0]
if locate == "zh_TW":
    language = {
        "nodata": "沒有發現離線資料 抓取中請稍後...",
        "nodata2": "抓取完畢",
        "usedata": "使用離線資料",
        "getdata": "抓取資料中...",
        "403": "403 錯誤，可能被 cloudflare 阻擋，請檢查 cookie 是否正確",
    }
else:
    language = {
        "nodata": "No offline data found, please wait a moment...",
        "nodata2": "Done",
        "usedata": "Use offline data",
        "getdata": "Getting data...",
        "403": "403 error, maby block by cloudflare , please check if the cookie is correct",
    }


def banner():
    data = """            _           _        _         ___  _         
 _ __   ___| |__  _ __ | |_ __ _(_)       / __\/_\/\   /\ 
| '_ \ / _ \ '_ \| '_ \| __/ _` | |_____ / _\ //_\\ \ / / 
| | | |  __/ | | | | | | || (_| | |_____/ /  /  _  \ V /  
|_| |_|\___|_| |_|_| |_|\__\__,_|_|     \/   \_/ \_/\_/   
                                                          """
    print(data)

# request


def wtfcloudflare(url, method="get", data=None):
    session = requests.Session()
    session.headers = {
        'Referer': "https://nhentai.net/login/",
        'User-Agent': useragent,
        'Cookie': cookie,
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    if method == "get":
        r = session.get(url)
    elif method == "post":
        r = session.post(url, data=data)
    return r


def check_pass():
    res = wtfcloudflare("https://nhentai.net/")
    if res.status_code == 403:
        print(language["403"])
        exit()


# --- main ---
banner()
check_pass()
if not os.path.isfile("tag.json"):
    print(language["nodata"])
    get_tags()
    print(language["nodata2"])
print(language["usedata"])

spinner = PixelSpinner(language["getdata"])
while True:
    data = wtfcloudflare(f"{URL}?page={now}")
    soup = BeautifulSoup(data.text, 'html.parser')
    book = soup.find_all("div", class_='gallery-favorite')
    if book == []:
        break
    numbers = [t.get('data-id') for t in book]
    names = [t.find('div', class_="caption").get_text() for t in book]
    tags_ = [t.find('div', class_="gallery").get('data-tags') for t in book]
    tags = []
    for i in tags_:
        tags__ = i.split(' ')
        tags.append(tags__)
    allnumbers.extend(numbers)
    allnames.extend(names)
    alltags.extend(tags)
    now += 1
    spinner.next()


with open('tag.json', 'r') as f:
    tagjson = json.load(f)
for i in enumerate(allnumbers):
    tagstr = ""
    for j in alltags[i[0]]:
        if j in tagjson:
            tagstr += tagjson[j] + ", "

    table.append([i[1], allnames[i[0]], tagstr])


with open('output.csv', 'w', newline='', encoding="utf_8_sig") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(table)
