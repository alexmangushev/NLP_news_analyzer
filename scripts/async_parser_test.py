import aiohttp
import asyncio
from fake_useragent import UserAgent
import textwrap
import json
from bs4 import BeautifulSoup
from pymongo import MongoClient
from typing import (
    Any,
    Dict,
    List
)

full_wrapped_text = ""

async def main():
    
    # Create the client
    client = MongoClient("mongodb://localhost:27017/")
    # Connect to database
    db = client['compling_db']
    # Fetch collection
    collection = db['compling_sema_test']
    
    async with aiohttp.ClientSession() as session:
        cookie = "yandexuid=1777324561636611594; yuidss=1777324561636611594; _ym_uid=1636888652385083187; skid=8516684041638823746; gdpr=0; my=YwA=; is_gdpr=0; is_gdpr_b=CLryEBDGgAEoAg==; yandex_login=schukin.a@5dtech.pro; ymex=1951971594.yrts.1636611594#1981523619.yrtsi.1666163619; i=16iQf2C36FasmQqG2PZd3InW7x86G82kf6Sa6Jhuf8BPEW8VJ/W08XuJMAxigYj9EU/PMlPn6cwekxgk1IINdfBfKug=; _ym_d=1669188502; Session_id=3:1669631466.5.1.1648309450723:CN9RXQ:27.1.2:1|1353021078.0.2|1130000059813560.13558508.2.2:13558508|3:10261823.175429.ruShnxZOUWhZPbpcboCqM8O2OF8; sessionid2=3:1669631466.5.1.1648309450723:CN9RXQ:27.1.2:1|1353021078.0.2|1130000059813560.13558508.2.2:13558508|3:10261823.175429.fakesign0000000000000000000"
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'user_agent': UserAgent()['google_chrome'],
            'cookie': cookie
        }
        
        internal_links = []
        
        with open('news_link.txt', 'r') as file:
            for link in file:
                internal_links.append(link.strip())
                
        for url in internal_links:
            
            async with session.get(url=url, headers=headers) as response:
                response_text = await response.text()
                
                soup = BeautifulSoup(response_text, 'html.parser')
                
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
                                
                parsing_page(session=session, url=url, headers=headers).cr_code
                            
                dict_for_mongo: Dict[str, Any] = {}
                            
                dict_for_mongo['news_name'] = news_name
                dict_for_mongo['date'] = news_data
                dict_for_mongo['link'] = url
                dict_for_mongo['text'] = full_wrapped_text
                            
                # json_for_mongo.append(dict_for_mongo)
                            
                collection.insert_one(dict_for_mongo)
                


async def parsing_page(session, url, headers):
    
    wrapped_text = ""
    content_tags = ['p']
    wrap = 200
    
    async with session.get(url=url, headers=headers) as response:
        
        response_text = await response.text()
        
        soup = BeautifulSoup(response_text, 'html.parser')
        
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
    
    full_wrapped_text = wrapped_text   


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())