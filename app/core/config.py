import os
from logging import config as logging_config

from .logger import LOGGING
from pydantic import AnyUrl, RedisDsn

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv("PROJECT_NAME", "movies")

# Настройки Redis
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Настройки Elasticsearch
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "127.0.0.1")
ELASTIC_PORT = int(os.getenv("ELASTIC_PORT", 9200))


elastic_dsn: AnyUrl = f"http://{ELASTIC_HOST}:{ELASTIC_PORT}"
redis_dsn: RedisDsn = f"redis://{REDIS_HOST}:{REDIS_PORT}"

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
