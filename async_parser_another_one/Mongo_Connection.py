from motor.motor_asyncio import AsyncIOMotorClient
from beanie import Document, init_beanie


class News(Document):
    news_name: str
    date: str
    url: str
    text: str


class DBConnection:
    async def my_init(self):
        client = AsyncIOMotorClient("mongodb://localhost:27017/")
        await init_beanie(database=client.beanie_compling_sema_test, document_models=[News])

    async def _if_article_exists(self, url: str):
        return await News.find_one(News.url == url)

    async def insert_article(self, article):
        return await article.insert()