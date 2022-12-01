import pymorphy2    # words normalizing lib
import re           # regular expressions lib
import requests     # site reading lib
import textwrap
import os
from bs4 import BeautifulSoup
from pymongo import MongoClient

URL_ADDRESS = "https://www.volgograd.kp.ru/online/"



class ParsingInMongo:
    url = ""
    filename = ""
    path = ""
    content_tags = ['script', 'p']
    wrap = 200
    def __init__(self):
        # Create the client
        self.client = MongoClient('localhost', 27017)
        # Connect to database
        self.db = self.client['compling_db']
        # Fetch collection
        self.collection = self.db['compling_sema']
        
        self.url = URL_ADDRESS
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