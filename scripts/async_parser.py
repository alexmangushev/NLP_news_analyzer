import pymorphy2    # words normalizing lib
import re           # regular expressions lib
import requests     # site reading lib
import textwrap
import os
import urllib3
import json
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime
from typing import (
    Any,
    Dict,
    List
)

URL_ADDRESS = "https://www.volgograd.kp.ru/online/"


class ParsingInMongo:
    url = ""
    filename = ""
    path = ""
    content_tags = ['p']
    wrap = 200
    
    def __init__(self):
        # Create the client
        self.client = MongoClient("mongodb://localhost:27017/")
        # Connect to database
        self.db = self.client['compling_db']
        # Fetch collection
        self.collection = self.db['compling_sema']
        
        self.internal_links = []
        self.links_for_links = []
        self.photo_video_links = []
        
        with open('news_link.txt', 'r') as file:
            for link in file:
                self.internal_links.append(link.strip())
    
    async def parsing_news(self):
        
        for url in self.internal_links:
            
            async with aiohttp.ClientSession() as session:
                
                async with session.get(url=url) as response:
                    
                    html = await response.text()
            
                    soup = BeautifulSoup(html, 'lxml')
                    
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
                            
                    news_text = await self.get_text(url=url)
                        
                    dict_for_mongo: Dict[str, Any] = {}
                        
                    dict_for_mongo['news_name'] = news_name
                    dict_for_mongo['date'] = news_data
                    dict_for_mongo['link'] = url
                    dict_for_mongo['text'] = news_text
                        
                    with open("full_json.json", 'w') as file_json:
                        file_json.write(json.dumps(dict_for_mongo))
                        file_json.write("\n")
                    # json_for_mongo.append(dict_for_mongo)
                        
                    await self.input_in_mongo(dict_for_mongo)
                
            
    async def input_in_mongo(self, json):
        compling_sema = self.collection
        compling_sema.insert_one(json)
        
    async def get_text(self, url):
        
        wrapped_text = ""
        
        async with aiohttp.ClientSession() as session:
                
            async with session.get(url=url) as response:
                
                html = await response.text()
            
                soup = BeautifulSoup(html, 'lxml')
                # найдем все теги по списку self.content_tags
                content = soup.find_all(self.content_tags)
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
                        wrapped_text += ''.join(textwrap.fill(p.text, self.wrap)) + "\n\n"
        
        return wrapped_text
              
if __name__ == '__main__':
    obj = ParsingInMongo()
    obj.parsing_news()
