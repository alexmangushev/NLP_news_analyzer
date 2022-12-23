import os
from pymongo import MongoClient

print("START")

# start mongodb
try:
    client = MongoClient('localhost', 27017)
except:
    os.system("mongod") 
    client = MongoClient('localhost', 27017)

# get news from database
db = client.NLP
collection = db.First
raw_news = collection.find()


for news in raw_news:

        print(news['text'])
        

print("FINISH")
