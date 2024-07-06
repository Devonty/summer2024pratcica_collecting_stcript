import csv

import ratelim
import tqdm
from bs4 import BeautifulSoup as bs
import requests
import re

mainUrl = 'https://habr.com/ru/post/'

@ratelim.patient(9, 3)
def get_post(postNum):
    curr_post_url = mainUrl + str(postNum)
    try:
        response = requests.get(curr_post_url)
        response.raise_for_status()
        return executePost(response, postNum)

    except Exception:
        return None

def executePost(page, num):
    soup = bs(page.text, 'html.parser')

    # Получаем заголовок статьи
    title = soup.find('meta', property='og:title')
    title = str(title).split('="')[1].split('" ')[0].lower()

    # Получаем текст статьи
    post = soup.find('div', xmlns="http://www.w3.org/1999/xhtml").get_text().lower()
    post = re.sub(r'[\n\r\t|]', ' ', post)
    post = ' '.join(post.split())

    # Получаем теги
    meta = soup.find('div', {'class': 'tm-article-presenter__meta'})

    tags = meta.find(string='Теги:').parent.parent.find_all('li')
    tags = list(map(lambda tag: tag.get_text().lower(), tags))

    habs = meta.find(string='Хабы:').parent.parent.find_all('li')
    habs = list(map(lambda tag: tag.get_text().lower(), habs))

    post_dict = {
        'id': num,
        'title': title,
        'post': post,
        'tags': tags,
        'habs': habs,
    }
    return post_dict


postCount = 50000
startStep = 20000

if __name__ == '__main__':
    try:
        with open("data2.csv", "w", newline='', encoding="utf-8") as file:

            fieldnames = ['id', 'title', 'post', 'tags', 'habs']
            writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter="|")
            writer.writeheader()

            for i in tqdm.tqdm(range(postCount)):
                # Берем пост
                curNum = startStep + i + 1
                post = get_post(curNum)
                # Если норм сейвим
                if post is not None:
                    writer.writerow(post)

    except Exception as err:
        print(err)
