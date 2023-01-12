from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tag import pos_tag
from nltk import classify
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
import string
import pickle
from pathlib import Path
import pymorphy2
from pymongo import MongoClient
from nltk.tokenize import word_tokenize

import re, string, random

def remove_noise(tweet_tokens, stop_words = ()):

    cleaned_tokens = []

    for token, tag in pos_tag(tweet_tokens):
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
        token = re.sub("(@[A-Za-z0-9_]+)","", token)

        if tag.startswith("NN"):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'

        lemmatizer = WordNetLemmatizer()
        token = lemmatizer.lemmatize(token, pos)

        if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
            cleaned_tokens.append(token.lower())
    return cleaned_tokens

def get_all_words(cleaned_tokens_list):
    for tokens in cleaned_tokens_list:
        for token in tokens:
            yield token

def get_tweets_for_model(cleaned_tokens_list):
    for tweet_tokens in cleaned_tokens_list:
        yield dict([token, True] for token in tweet_tokens)



def __main__():
    model_file = Path('classifier.pickle')
    if not model_file.exists():
        print("Необходимо создать модель.")
    else:
        # Подключаемся к базе данных
        client = MongoClient('localhost', 27017)
        db = client.NLP
        # in_bd(db)

        # Подключае модель и необходимые элементы анализа
        f = open('classifier.pickle', 'rb')
        classifier = pickle.load(f)
        f.close()

        allNews = db.Second
        cnt = 0
        rez = []
        #Для всех новостей из коллекции
        for news in allNews.find():
            # if (cnt == 1):
            #     break
            #Получаем id записи
            _id = news["_id"]
            print(_id)
            #Получаем текст для анализа тональности
            tweet = news["text"]


            string = ""

            end_sentence = tweet.find('.')

            start_sent = 0

            while ('.' in tweet[start_sent:]):
                sentence = tweet[start_sent : end_sentence]


                custom_tokens = []
                custom_tokens = remove_noise(word_tokenize(sentence))

                #Готовим данные для обновления необходимой записи с найденной тональностью


                data = str({'Тональность': classifier.classify(dict([token, True] for token in custom_tokens))})
                string = data+";"+string

                start_sent = tweet.find('\n', end_sentence) + 1
                end_sentence = tweet.find('.', start_sent)

                #Обновляем запись в БД
            news_id = news['_id']
            print(news_id)

            new_collection = db.Third
            old_news = new_collection.find_one_and_delete({'_id': news_id})
            new_collection.insert_one(
                {
                    '_id': news_id,
                    'text': tweet,
                    'ton': string
                }
            )

            # print(cnt, data)
            cnt += 1



if __name__ == "__main__":
    __main__()


