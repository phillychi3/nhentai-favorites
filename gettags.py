from bs4 import BeautifulSoup
import requests
import fake_useragent
import json
import yaml


URL = "https://nhentai.net/tags/"
ua = fake_useragent.UserAgent()
useragent = ua.random

with open('set.yaml', 'r') as f:
    cookie = yaml.load(f, Loader=yaml.CLoader)["cookid"]
    if cookie == "":
        print("Please edit set.yaml")
        exit()
def wtfcloudflare(url,method="get",data=None):
    session = requests.Session()
    session.headers = {
        'Referer': "https://nhentai.net/login/",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        'Cookie': cookie,
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    if method == "get":
        r = session.get(url)
    elif method == "post":
        r = session.post(url,data=data)
    return r

def get_tags():
    now = 1
    tagjson = {}

    while True:
        data = wtfcloudflare(f"{URL}?page={now}")
        soup = BeautifulSoup(data.text, 'html.parser')
        print(data.text)
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
        now += 1
    with open('tag.json', 'w') as f:
        json.dump(tagjson, f)
    return


if __name__ == '__main__':
    get_tags()
