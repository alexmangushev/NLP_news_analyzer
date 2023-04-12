import asyncio

import datetime
import aiohttp as aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from typing import List
import time

from Mongo_Connection import DBConnection, News

Connection = DBConnection()
MAX_QUERIES = 7
CUR_QUERIES = 0
news_list: List[News] = []
session: ClientSession = None


async def download_with_limited_cache(url: str) -> str:
    global CUR_QUERIES, MAX_QUERIES, session

    # if state == "article":
    #     if await Connection._if_article_exists(url):
    #         print(f'[DOWNLOADER]: cache hit: {url}')
    #         return ''
    # if no cache -> download
    
    if await Connection._if_article_exists(url):
        print(f'[DOWNLOADER]: cache hit: {url}')
        return ''
    
    while CUR_QUERIES >= MAX_QUERIES:
        await asyncio.sleep(0.1)
    CUR_QUERIES += 1
    print(f'[DOWNLOADER]: [{CUR_QUERIES}/{MAX_QUERIES}] downloading...: {url}')
    async with session.get(url, timeout=15) as resp:
        CUR_QUERIES -= 1
        # assert resp.status == 200
        if resp.status == 200:
            html_source = await resp.text()
            print(f'[DOWNLOADER]: downloaded: {url}')
            return html_source
        else:
            print(f'[DOWNLOADER]: error: {url}')
            return ''
        
async def get_all_url_data(url_list: list):
    coroutines = [get_one_url_data(link) for link in url_list]
    await asyncio.gather(*coroutines)
    
async def get_one_url_data(current_url):
    global news_list
    new_html = await download_with_limited_cache(url=current_url)
    if not new_html:
        return
    
    soup = BeautifulSoup(new_html, "lxml")
    h1_heading = str(soup.find('h1'))
    span_data = str(soup.find('span', {'class': 'sc-j7em19-1 eDdTDf'}))
                    
    # Получаем дату публикации статьи
    span_data_list = []
    span_data_list = span_data.split('>')
    news_data = span_data_list[1].strip('</span')
                    
    # Получаем название статьи
    heading_list = []
    heading_list = h1_heading.split('>')
    news_name = heading_list[1].strip('</h1')
                    
    # Проверяем на <span> и если он есть, устанавливаем новое значение в news_name
    news_name_list = news_name.split(' ')
    if news_name_list[0] == 'span':
        news_name = heading_list[2].strip('</span') + heading_list[3].strip('</h1')
        
    # Получаем весь нужный текст со сраницы            
    wrapped_text = ""
    content_tags = ['p']
    wrap = 200
    # найдем все теги по списку self.content_tags
    content = soup.find_all(content_tags)
    for p in content:
        # пропускаем теги без значений
        if p.text != '':
            # форматирование ссылок в вид [ссылка]
            links = p.find_all('a')
            if links != '':
                for link in links:
                    try:
                        if p is not None:
                            p.a.replace_with(link.text + str("[" + link['href'] + "]"))
                    except:
                        print("Непредвиденная ошибка связанная с формированием ссылки")
            # устанавливаем ширину строки равной self.wrap (по умолчанию, 80 символов)
            wrapped_text += ''.join(textwrap.fill(p.text, wrap)) + "\n\n"
        
    # Формируем данные для занесения в MongoDB
    sample = News(news_name=news_name, date=news_data, url=current_url, body=wrapped_text)
    ins_res = await Connection.insert_article(sample)
    print(f"[DATABASE] Article Is Added. {current_url}")
            
    # dict_for_mongo: Dict[str, Any] = {}
                    
    # dict_for_mongo['news_name'] = news_name
    # dict_for_mongo['date'] = news_data
    # dict_for_mongo['link'] = current_url
    # dict_for_mongo['text'] = wrapped_text
    
async def main():
    global session, Connection
    internal_links = []
    with open('news_links.txt', 'r') as file:
        for link in file:
            internal_links.append(link.strip())
    session = aiohttp.ClientSession()
    await Connection.my_init()
    get_all_url_data(internal_links)
    await session.close()
    
if __name__ == "__main__":
    begin = time.time()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
    loop.close()
    end = time.time()
    print(f"Time is: {end-begin}")