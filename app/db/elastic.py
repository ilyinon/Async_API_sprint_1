from typing import Optional

from elasticsearch import AsyncElasticsearch

es: Optional[AsyncElasticsearch] = None

import os
from elasticsearch import AsyncElasticsearch

async def get_elastic() -> AsyncElasticsearch:
    elastic_url = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')
    return AsyncElasticsearch(hosts=[elastic_url])


# # Функция понадобится при внедрении зависимостей
# async def get_elastic() -> AsyncElasticsearch:
#     return es
