import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import tqdm
import datetime

options = Options()
options.add_argument('--headless')
# options.add_argument('--disable-web-security')
# options.add_argument('--allow-running-insecure-content')
options.add_argument("--log-level=3")

# Set up the webdriver
driver = webdriver.Chrome(options=options)

genres = ['', 'action', 'adult', 'adventure', 'comedy', 'drama', 'ecchi', 'fantasy', 'harem', 'historical', 'horror', 'josei', 'martial-arts', 'mature', 'mecha', 'mystery', 'psychological', 'romance', 'school-life', 'sci-fi', 'seinen', 'shoujo', 'shounen', 'slice-of-life', 'smut', 'sports', 'supernatural', 'tragedy', 'wuxia', 'xianxia', 'xuanhuan']
url = "https://webnovelfull.net/"
novels = []
for genre in tqdm.tqdm(genres):
    if genre:
        genre = 'genre/' + genre
    driver.get(url + genre)

    # Wait for the page to fully render
    time.sleep(5)

    genre_novels = driver.find_elements('css selector', 'div > div > div.main_text > h3 > a')
    for genre_novel in genre_novels:
        novels.append((genre_novel.get_attribute("innerHTML"), genre_novel.get_attribute("href")))


# print(novels)
print(len(novels))
novel_links = list(set(novel for novel in novels))
print(len(novel_links))


# Find all the novel links on the page
# novels = driver.find_elements('css selector', 'div > div.relative.mx-2.mb-8.relative.rounded-lg.overflow-hidden > a')
# novels = WebDriverWait(driver, 20).until(
#     EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div > div.relative.mx-2.mb-8.relative.rounded-lg.overflow-hidden > a'))
# )
# novel_links = [(novel.get_attribute("title"), novel.get_attribute("href")) for novel in novels]
# novel_links = list(set((novel.get_attribute("title"), novel.get_attribute("href")) for novel in novels))
# novel_links = []
# for i,novel in enumerate(novels):
#     novel_links.append((novel.get_attribute("title"), novel.get_attribute("href")))
#     break

print(novel_links)
missed_chapter = {}

for i,novel_link in enumerate(novel_links):
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(f"Scraping novel: {novel_link[0]} ({novel_link[1]}) --- Progress: {(i/len(novel_links)*100):.2f}% - Time: {current_time}")

    # Find all the chapter links on the page 
    
    # Open the novel page
    driver.get(f'{novel_link[1]}')

    # Wait for the page to fully render
    time.sleep(5)

    try: 
        chapters = driver.find_elements('css selector', 'ul.chapter-list > li > a')
    except:
        while len(chapters) == 0:
            print(f'No chapters found for {novel_link[0]}')
            chapters = driver.find_elements('css selector', 'ul.chapter-list > li > a')
        
    # for chapter in chapters:
    #     chapter_links.append((chapter.get_attribute("title"), chapter.get_attribute("href")))
    

    #glo_contents > div > section.ep-body > div:nth-child(2) > div > nav > ul.pagination > li > a
    chapter_links = [(chapter.get_attribute("title"), chapter.get_attribute("href")) for chapter in tqdm.tqdm(chapters, total=len(chapters))]
    # chapter_links = []
    # for i,chapter in enumerate(chapters):
    #     chapter_links.append((chapter.get_attribute("title"), chapter.get_attribute("href")))
    #     if i >= 9:
    #         break
    title = False
    missed_chapter[novel_link[0]] = []

    for j,chapter_link in tqdm.tqdm(enumerate(chapter_links), total=len(chapter_links)):
        # print(f"{j+1}.Chapter: {chapter_link[0]} ({chapter_link[1]})")

        # Open the chapter page
        response = requests.get(chapter_link[1])

        # Wait for the page to fully render
        # time.sleep(20)

        # content_inner = []
        # try:
        #     content_inner = driver.find_element('css selector', 'div.chapter-content > div')
        # except:
        #     while len(content_inner) == 0:
        #         print(f'No content found for Chapter {j+1} of {novel_link[0]}')
        #         content_inner = driver.find_element('css selector', 'div.chapter-content > div')

        soup = BeautifulSoup(response.content, 'html.parser')

        # content_inner = soup.select('div.chapter-content > div').get_attribute('innerHTML')

        content = [p.text.strip() for p in soup.select('div.chapter-content > p:not(:has(strong)):not(:has(sub))') if not any(keyword in p.text for keyword in ["Chapter", "Translator", "Editor"])]
        # print(content)
        # if len(content) == 0:
        #     print(content)
        #     print(f'Retry loading {j+1}.Chapter of {novel_link[0]}')
        #     driver.get(chapter_link[1])
        #     time.sleep(20)
        #     try:
        #         # content_inner = WebDriverWait(driver, 20).until(
        #         #     EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.chapter-content > div'))
        #         # ).get_attribute(('inner_HTML'))
        #         content_inner = driver.find_element('css selector', 'div.chapter-content > div').get_attribute(('inner_HTML'))
        #         content = [p.text for p in soup.select('p:not(:has(strong)):not(:has(sub))') if 'Chapter' not in p.text or 'Translator' not in p.text or 'Editor' not in p.text]
                
        #     except:
        #         print(response.content)

        # print(content)
        if len(content) > 1:
            if not title:
                with open('novels.txt', 'a', encoding='utf-8') as file:
                    file.write(novel_link[0] + '\n\n\n')
                title = True

            description = f"Chapter {j+1}"
            with open('novels.txt', 'a' , encoding='utf-8') as file:
                file.write(description + '\n\n')
                
            for row in content:
                with open('novels.txt', 'a', encoding='utf-8') as file:
                    file.write(row + '\n')
            
            with open('novels.txt', 'a', encoding='utf-8') as file:
                file.write('\n\n')
        else:
            description = f"Chapter {j+1}"
            missed_chapter[novel_link[0]].append(description)

    print(f'For {novel_link[0]} i missed {len(missed_chapter[novel_link[0]])} Chapters.\n {missed_chapter[novel_link[0]]}')



driver.quit()
