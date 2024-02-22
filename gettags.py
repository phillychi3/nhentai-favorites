from bs4 import BeautifulSoup
import requests
import json
import yaml


URL = "https://nhentai.net/tags/"


def wtfcloudflare(url, method="get", useragent=None, cookie=None, data=None):
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


def get_tags():
    with open('set.yaml', 'r') as f:
        data = yaml.load(f, Loader=yaml.CLoader)
        cookie = data["cookid"]
        useragent = data["useragent"]
        if cookie == "":
            print("Please edit set.yaml")
            exit()
    now = 1
    tagjson = {}

    while True:
        data = wtfcloudflare(f"{URL}?page={now}",
                             useragent=useragent, cookie=cookie)
        soup = BeautifulSoup(data.text, 'html.parser')
        tags = soup.find_all("a", class_='tag')
        if tags == []:
            break
        tagnumbers = [t.get('class') for t in tags]
        tagnames = [t.find('span', class_='name').get_text() for t in tags]
        tagnumber = []
        for i in tagnumbers:
            fixnum = i[1].replace('tag-', '')
            tagnumber.append(fixnum)
        for i in enumerate(tagnumber):
            tagjson[i[1]] = tagnames[i[0]]
        print(f"page {now} done")
        now += 1
    if tagjson == {}:
        print("something wrong with your cookie or useragent")
        exit()
    with open('tag.json', 'w') as f:
        json.dump(tagjson, f)
    print("tag.json saved")
    return


if __name__ == '__main__':
    get_tags()
