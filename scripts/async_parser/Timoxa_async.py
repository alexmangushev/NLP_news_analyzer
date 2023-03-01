import asyncio

import datetime
import aiohttp as aiohttp
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from typing import List
import time

from db import DBConnection, News

month_transporter = {
    1: "Янв",
    2: "Фев",
    3: "Мар",
    4: "Апр",
    5: "Май",
    6: "Июн",
    7: "Июл",
    8: "Авг",
    9: "Сен",
    10: "Окт",
    11: "Ноя",
    12: "Дек",
}

Connection = DBConnection()
MAX_QUERIES = 7
CUR_QUERIES = 0
news_list: List[News] = []
session: ClientSession = None


async def download_with_limited_cache(url: str, state: str) -> str:
    global CUR_QUERIES, MAX_QUERIES, session

    if state == "article":
        if await Connection._if_article_exists(url):
            print(f'[DOWNLOADER]: cache hit: {url}')
            return ''
    # if no cache -> download
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


async def handle_all_news_page(page: int):
    url = f'https://gorvesti.ru/feed/{page}'
    page_html = await download_with_limited_cache(url=url, state="page")
    soup = BeautifulSoup(page_html, "lxml")
    all_hrefs = soup.find_all("div", class_="itm-body")

    links = ["https://gorvesti.ru" + el.find("a").get("href") for el in all_hrefs]
    # спарсить ссылки на каждую из 20 новостей
    coroutines = [handle_one_news_page(link) for link in links]
    await asyncio.gather(*coroutines)


async def handle_one_news_page(url: str):
    global news_list
    new_html = await download_with_limited_cache(url=url, state="article")
    if not new_html:
        return

    soup = BeautifulSoup(new_html, "lxml")
    title = soup.find(class_="item block").find(class_="title-block").text
    body = ''.join([el.text for el in soup.find(class_="item block").find_all("p")])
    date = soup.find(class_="article-title-block").find(class_="summary").find("span", class_="dt").text
    # fix date if it is today's news
    if len(date) == 5:
        day = str(datetime.datetime.now()).split()[0].split("-")[-1]
        month = month_transporter[int(str(datetime.datetime.now()).split()[0].split("-")[-2])]
        date = f"{day} {month} {date}"

    sample = News(title=title, date=date, url=url, body=body)

    ins_res = await Connection.insert_article(sample)
    print(f"[DATABASE] Article Is Added. {url}")
    # парсинг самой страницы с новостью


async def main():
    global session, Connection
    session = aiohttp.ClientSession()
    await Connection.my_init()
    coroutines = [handle_all_news_page(i) for i in range(1, 500)]
    await asyncio.gather(*coroutines)
    await session.close()


if __name__ == "__main__":
    begin = time.time()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
    loop.close()
    end = time.time()
    print(f"Time is: {end-begin}")