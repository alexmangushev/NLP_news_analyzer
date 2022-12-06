import pymorphy2    # words normalizing lib
import re           # regular expressions lib
import requests     # site reading lib
import textwrap
import os
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime
from typing import (
    Any,
    Dict,
    List
)

URL_ADDRESS = "https://www.volgograd.kp.ru/online/"
# https://www.volgograd.kp.ru/daily/27444/4647659/
# https://www.volgograd.kp.ru/online/news/5035762/
# https://www.volgograd.kp.ru/video/
# https://www.volgograd.kp.ru/photo/

# "    data.url = window.location.href;"
# "full_path":"https://www.volgograd.kp.ru/daily/27432/4634521/"

# /mnt/c/Users/fredo/Desktop/Work_Stereotech/repositories/NLP_news_analyzer/cloud_env/bin/pip


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
        with open(r"C:\Users\fredo\Desktop\Work_Stereotech\repositories\NLP_news_analyzer\www.volgograd.kp.ru_internal_links.txt") as file:
            for internal_link in file:
                internal_link_separate = re.findall(r"https://www.volgograd.kp.ru/daily/\d{4,7}" or 
                                                    r"https://www.volgograd.kp.ru/online/news/\d{4,7}" or
                                                    r"https://www.volgograd.kp.ru/video/" or
                                                    r"https://www.volgograd.kp.ru/photo/", 
                                                    internal_link)
                if internal_link_separate == []:
                    self.links_for_links.append(internal_link.strip())
                elif internal_link_separate[0] == "https://www.volgograd.kp.ru/video/" or internal_link_separate[0] == "https://www.volgograd.kp.ru/photo/":
                    self.photo_video_links.append(internal_link.strip())
                else:
                    self.internal_links.append(internal_link.strip())
        
        # for link in self.internal_links:
        #     print(link)
        json_for_mongo: List[Dict[str, Any]] = []
        for url in self.internal_links:
            #self.url = URL_ADDRESS
            self.url = url
            
            r = requests.get(self.url).text
            soup = BeautifulSoup(r, 'html.parser')
            
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
            
            # Get path and filename for saving article by splitting URL.
            # If the URL ends with some.html, then the previous (-2) element
            # of the path is taken to form the path and the filename = some.html.txt respectively.
            path_arr = self.url.split('/')
            if path_arr[-1] != '':
                self.filename = path_arr[-1] + ".txt"
                self.path = os.getcwd() + "/".join(path_arr[1:-1])
            else:
                self.filename = path_arr[-2] + ".txt"
                self.path = os.getcwd() + "/".join(path_arr[1:-2])
            if not os.path.exists(self.path):
                os.makedirs(self.path)
                
            news_text = self.get_text()
            
            dict_for_mongo: Dict[str, Any] = {}
            
            dict_for_mongo['news_name'] = news_name
            dict_for_mongo['date'] = news_data
            dict_for_mongo['link'] = url
            dict_for_mongo['text'] = news_text
            json_for_mongo.append(dict_for_mongo)
            
        self.input_in_mongo(json_for_mongo)
            
    def input_in_mongo(self, json):
        compling_sema = self.collection
        compling_sema.insert_many(json)
        
        # self.url = url
        # # Get path and filename for saving article by splitting URL.
        # # If the URL ends with some.html, then the previous (-2) element
        # # of the path is taken to form the path and the filename = some.html.txt respectively.
        # path_arr = self.url.split('/')
        # if path_arr[-1] != '':
        #     self.filename = path_arr[-1] + ".txt"
        #     self.path = os.getcwd() + "/".join(path_arr[1:-1])
        # else:
        #     self.filename = path_arr[-2] + ".txt"
        #     self.path = os.getcwd() + "/".join(path_arr[1:-2])
        # if not os.path.exists(self.path):
        #     os.makedirs(self.path)
        
    def get_text(self):
        r = requests.get(self.url).text
        soup = BeautifulSoup(r, 'html.parser')
        # найдем все теги по списку self.content_tags
        content = soup.find_all(self.content_tags)
        wrapped_text = ""
        for p in content:
            # пропускаем теги без значений
            if p.text != '':
                # форматирование ссылок в вид [ссылка]
                links = p.find_all('a')
                if links != '':
                    for link in links:
                        p.a.replace_with(link.text + str("[" + link['href'] + "]"))
                # устанавливаем ширину строки равной self.wrap (по умолчанию, 80 символов)
                wrapped_text += ''.join(textwrap.fill(p.text, self.wrap)) + "\n\n"
        self.write_in_file(wrapped_text)
        
        return wrapped_text
        
    def write_in_file(self, text):
        # записывает text в каталог self.path:"[CUR_DIR]/host.ru/path_item1/path_item2/..."
        file = open(str(self.path) + '/' + str(self.filename), mode="a")
        file.write(text)
        file.close()
    
    def parser(self, url, description, tags):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        bunch_of_text = soup.find_all('div', class_='listcot col-md-9 col-sm-9 col-xs-9')
        bunch_of_a = [c.a for c in bunch_of_text]
        # full description
        for c in bunch_of_a:
            description.append(c.text + "\n" + c['href'])
        # description = [c.text + " " + c['href'] for c in bunch_of_a] # - earlier version

        # turn description text into tags
        text = [c.text for c in bunch_of_a]
        morph = pymorphy2.MorphAnalyzer(lang='ru')
        #if morph.parse("1000")[0].tag.string.consist('NUMB'): print("ye")
        for i in range(len(text)):
            phrase = re.split('\W', text[i])
            tags.append("")
            for word in phrase:
                word = morph.parse(word)[0]
                pos = word.tag.POS
                if pos != 'PREP' and pos != 'CONJ' and pos != 'INTJ' and pos != 'PRCL' \
                        and pos != 'NUMR' and pos != 'INFN' and pos != 'VERB':
                    tags[i] = tags[i] + word.normal_form + " "


    def db_input(self, description, tags):
        # Подключаемся к PostgreSQL на сервере
        connection = psycopg2.connect(host=host, user=user, password=password, database=db_name)
        for i in range(len(description)):
            with connection.cursor() as cursor:
                connection.autocommit = True
                cursor.execute("""INSERT INTO answers (answer, tags) VALUES (%s, %s);""", (description[i], tags[i],))

obj = ParsingInMongo()
# Parsing site
# url = 'https://vse-kursy.com/onlain/free/?ysclid=l55k1ui5n9366579259'
# desc = []
# tags = []
# obj.parser(url, desc, tags)
# obj.db_input(desc, tags)

# url = 'https://vse-kursy.com/onlain/free/page/'
# for i in range(2, 54):
#     url_cycle = url + str(i) + "/"
#     desc = []
#     tags = []
#     obj.parser(url_cycle, desc, tags)
#     obj.db_input(desc, tags)
#     print(url_cycle, " is done")
obj.get_text()