from typing import Optional

from redis.asyncio import Redis

redis: Optional[Redis] = None


import os
from redis.asyncio import Redis

async def get_redis() -> Redis:
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    return Redis.from_url(redis_url)


# # Функция понадобится при внедрении зависимостей
# async def get_redis() -> Redis:
#     return redis
