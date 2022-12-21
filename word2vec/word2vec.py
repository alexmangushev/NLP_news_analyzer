# -*- encoding: utf-8 -*-
import os
import sys
import re
from pymongo import MongoClient

from pyspark.ml.feature import Word2VecModel
from pyspark.sql import SparkSession

from pyspark.ml.feature import Tokenizer
from pyspark.ml.feature import StopWordsRemover
from pyspark.ml.feature import CountVectorizer
from pyspark.ml.feature import IDF
from pyspark.ml.feature import Word2Vec


spark = SparkSession\
        .builder \
        .appName("Word2VecApplication") \
        .getOrCreate()


if not os.path.exists('/home/alex/nlp/sema/word2vec/word2vec_model'):
    print("START")

    if not os.path.exists('/home/alex/nlp/sema/word2vec/news.txt'):

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

        f = open('/home/alex/nlp/sema/word2vec/news.txt', 'a')

        i = 0
        for news in raw_news:
            # if i == 20:
            #   break
            text =(re.sub(r'volgograd.kp.ru', '', news['text']))
            text = re.sub(r'\[[^\[]*\]', '', text)
            #text =(re.sub(r'\n', '', text))
            p = ''
            for ch in range(len(text) - 1):
                if text[ch] == '\n' and text[ch+1] == '\n':
                    ch+=1
                else:
                    p += text[ch]
            f.write(p)
            print(i)
            i+=1

        f.close()

    #sys.exit()

    # Построчная загрузка файла в RDD
    input_file = spark.sparkContext.textFile('/home/alex/nlp/sema/word2vec/news.txt')
    prepared = input_file.map(lambda x: ([x]))
    df = prepared.toDF()
    prepared_df = df.selectExpr('_1 as text')

    # Разбить на токены
    tokenizer = Tokenizer(inputCol='text', outputCol='words')
    words = tokenizer.transform(prepared_df)

    # Удалить стоп-слова
    stop_words = StopWordsRemover.loadDefaultStopWords('russian')
    remover = StopWordsRemover(inputCol='words', outputCol='filtered', stopWords=stop_words)
    filtered = remover.transform(words)

    # Вывести таблицу filtered
    #filtered.show()

    # Вывести столбец таблицы words с токенами до удаления стоп-слов
    #words.select('words').show(truncate=False, vertical=True)

    # Вывести столбец "filtered" таблицы filtered с токенами после удаления стоп-слов
    #filtered.select('filtered').show(truncate=False, vertical=True)

    word2Vec = Word2Vec(vectorSize=3, minCount=0, inputCol='words', outputCol='result')
    model = word2Vec.fit(filtered)
    w2v_df = model.transform(filtered)
    w2v_df.show()
    model.save("/home/alex/nlp/sema/word2vec/word2vec_model")

    spark.stop()


model = Word2VecModel.load('/home/alex/nlp/sema/word2vec/word2vec_model')


while True:
    try:
        entry_word = input("Введите слово для поиска синонимов:")
        if entry_word == "-x":
            break
        entry_word = entry_word.replace(' ', '')
        entry_word = entry_word.lower()
        model.findSynonyms(entry_word, 30).show()
    except Exception as ex:
        print("Данного слова нет в словаре!")
        print(ex)

spark.stop()