import requests
from bs4 import BeautifulSoup
import webbrowser

url = "https://lightnovels.live"
response = requests.get(url)

soup = BeautifulSoup(response.content, 'html.parser')

novels = soup.select('div > div.relative.mx-2.mb-8.relative.rounded-lg.overflow-hidden > a')
print(len(novels))
for novel in novels:
    print(novel.get('title'))
    novel_link = novel.get('href')
    webbrowser.open(url+novel_link)
    url = url+novel_link
    response = requests.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')

    # chapters = soup.select('ul.chapter-list.flex.flex-wrap.m-0.p-0.h-96.overflow-scroll.p-4.rounded-2xl > li')
    # print(chapters)
    chapters = soup.select('ul.chapter-list > li')
    print(chapters)

    for chapter in chapters:
        print(chapter.get('title'))

    break
        

