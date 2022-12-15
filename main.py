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

cnt_news = 0
for news in raw_news:

    if cnt_news == 10:
        break

    # print("news: ", news)

    # for each news set her text into "input.txt"
    f = open('/home/alex/nlp/sema/tomita/input.txt', 'w')
    f.write(news['text'])
    f.close()

    # start tomita-parser
    os.system("cd tomita/; ./tomita-parser config.proto")

    f = open('/home/alex/nlp/sema/tomita/output.txt', 'r').readlines()

    line = 0
    new_news = ""
    while line < len(f):
        str_p = "Person: "
        if f[line].find('Polit') > -1:
            new_news += str(f[line - 1][:-1])
            while True:
                str_p += str(f[line + 2][12:-1]) + "|"
                line += 4
                if line >=len(f) or f[line].find('Polit') == -1:
                    break
            str_p += "#\n"
            new_news += str_p

        if line >=len(f):
            break

        str_pl = "Place: "
        if f[line].find('Place') > -1:
            new_news += str(f[line - 1][:-1])
            while True:
                str_pl += str(f[line + 2][12:-1]) + "|"
                line += 4
                if line >=len(f) or f[line].find('Polit') == -1:
                    break
            str_pl += "#\n"
            new_news += str_pl
        
            #print(f[line])
        
        line+=1

    
    if len(new_news) > 0: 
        news_id = news['_id']
        print(news_id)

        new_collection = db.Second
        old_news = new_collection.find_one_and_delete({'_id': news_id})
        new_collection.insert_one(
            {
                '_id': news_id,
                'text': new_news
            }
        )

    cnt_news += 1


print("FINISH")
