0. При настройке интеграции с остальными компонентами нужно корреткно заполнить .env

1. Для запуска проекта нужно выполнить команду

`docker-comose-up -d --build`

2. Во время отладки используются данные выгруженные из ETL задания часть три по, чтобы загрузить из в elastic выполните команды:

`curl -X PUT -H "Content-Type: application/json" -d @./data/movies_index.json "localhost:9200/movies?pretty"`

`curl -X PUT -H "Content-Type: application/json" -d @./data/genres_index.json "localhost:9200/genres?pretty"`

`curl -X PUT -H "Content-Type: application/json" -d @./data/persons_index.json "localhost:9200/persons?pretty"` 

Для загрузки данных:

`docker run -ti -v ./data/:/data --network=async_api_sprint_1_default  elasticdump/elasticsearch-dump:v6.111.0  --input=/data/movies_data.json --output=http://elastic:9200/movies`

`docker run -ti -v ./data/:/data --network=async_api_sprint_1_default  elasticdump/elasticsearch-dump:v6.111.0  --input=/data/genres_data.json --output=http://elastic:9200/genres`

`docker run -ti -v ./data/:/data --network=async_api_sprint_1_default  elasticdump/elasticsearch-dump:v6.111.0  --input=/data/persons_data.json --output=http://elastic:9200/persons`


Посмотреть данные по индексам 

`curl -XGET 'http://127.0.0.1:9200/movies/_mapping'`

`curl -XGET 'http://127.0.0.1:9200/genres/_mapping'`

`curl -XGET 'http://127.0.0.1:9200/persons/_mapping'`

Посмотреть список индексов

`curl -XGET 'http://localhost:9200/_cat/indices?v'`


3. Пример запросов:

`curl http://localhost:80/api/v1/films/6ecc7a32-14a1-4da8-9881-bf81f0f09897`