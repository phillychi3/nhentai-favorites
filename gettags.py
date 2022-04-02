import gevent.monkey
gevent.monkey.patch_all()
import json

import fake_useragent
import requests
from bs4 import BeautifulSoup

url = "https://nhentai.net/tags/"
def get_tags():
    now = 1
    tagjson = {}

    while True:
        ua = fake_useragent.UserAgent()
        useragent = ua.random
        headers = {
            'user-agent': useragent
        }
        data = requests.get(f"{url}?page={now}", headers=headers)
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
        now += 1
    with open('tag.json', 'w') as f:
        json.dump(tagjson, f)
    return


if __name__ == '__main__':
    get_tags()
