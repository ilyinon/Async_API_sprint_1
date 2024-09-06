from .api.v1 import films
from .core import config
from .db import elastic, redis
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event("startup")
async def startup():
    redis.redis = Redis.from_url(config.redis_dsn)
    elastic.es = AsyncElasticsearch(hosts=[config.elastic_dsn])


@app.on_event("shutdown")
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


@app.get("/")
def hello_world():
    return {"hello": "world"}


app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
