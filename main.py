import collections
import os
from pymongo import MongoClient
import json

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

    # for each news set her text into "input.txt"
    f = open('tomita/input.txt', 'w')
    f.write(news['text'])

    # start tomita-parser
    os.system("cd tomita/; ./tomita-parser config.proto")


print("FINISH")
