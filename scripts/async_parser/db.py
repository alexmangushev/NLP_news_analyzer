from motor.motor_asyncio import AsyncIOMotorClient
from beanie import Document, init_beanie


class News(Document):
    title: str
    date: str
    url: str
    body: str


class DBConnection:
    async def my_init(self):
        client = AsyncIOMotorClient("localhost", 27017, username="root", password="root123")
        await init_beanie(database=client.parser, document_models=[News])

    async def _if_article_exists(self, url: str):
        return await News.find_one(News.url == url)

    async def insert_article(self, article):
        return await article.insert()