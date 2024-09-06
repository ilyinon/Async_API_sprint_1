import os
from logging import config as logging_config

from core.logger import LOGGING
from pydantic import AnyUrl, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class EtlSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=DOTENV)

    PROJECT_NAME: str

    ELASTIC_HOST: str
    ELASTIC_PORT: int

    REDIS_HOST: str
    REDIS_PORT: int

    FILM_CACHE_EXPIRE_IN_SECONDS: int
    GENRE_CACHE_EXPIRE_IN_SECONDS: int
    PERSON_CACHE_EXPIRE_IN_SECONDS: int

    @property
    def elastic_dsn(self):
        return f"http://{self.ELASTIC_HOST}:{self.ELASTIC_PORT}"

    @property
    def redis_dsn(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"


settings = EtlSettings()
