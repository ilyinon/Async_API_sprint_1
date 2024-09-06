https://github.com/ilyinon/Async_API_sprint_1


0. При настройке интеграции с остальными компонентами нужно корреткно заполнить .env, для дев проекта можно скопировать из .env_example
```bash
cp .env_example .env
```

1. Для запуска проекта нужно выполнить команду

```bash
docker-comose-up -d --build
```

2. Для отделения логически компонентов, выгрузка данных persons и genres была добавлена в ETL.
Реализовано в репозитории: https://github.com/ilyinon/new_admin_panel_sprint_3


3. Для добавление в elastic данных нужно выполнить следующие шаги:

Удалить существующий индекс "movies" из ElasticSearch
```bash
curl -X DELETE "localhost:9200/movies?pretty"
```
Удостовериться, что индекс пропал
```bash
curl -XGET 'http://127.0.0.1:9200/movies/_mapping'
```
```bash
curl -XGET 'http://localhost:9200/_cat/indices?v'
```
Создать индекс с фильмами "movies"
```bash
curl -X PUT -H "Content-Type: application/json" -d @./data/movies_index.json "localhost:9200/movies?pretty"
```
Создать индекс с жанрами "genres"
```bash
curl -X PUT -H "Content-Type: application/json" -d @./data/genres_index.json "localhost:9200/genres?pretty"
```
Создать индекс с персоналиями "persons"
```bash
curl -X PUT -H "Content-Type: application/json" -d @./data/persons_index.json "localhost:9200/persons?pretty"
```
Запустим контейнер с ElasticDump и перенесем данные из файла movies_data.json
```bash
docker run -ti -v ./data/:/data --network=async_api_sprint_1_default  elasticdump/elasticsearch-dump:v6.111.0  --input=/data/movies_data.json --output=http://elastic:9200/movies
```
Аналогично перенесем данные из файла genres_data.json
```bash
docker run -ti -v ~/Dev/async_api_sprint_1/data/:/data --network=async_api_sprint_1_default  elasticdump/elasticsearch-dump:v6.111.0  --input=/data/genres_data.json --output=http://elastic:9200/genres
```
Аналогично перенесем данные из файла persons_data.json
```bash
docker run -ti -v ~/Dev/async_api_sprint_1/data/:/data --network=async_api_sprint_1_default  elasticdump/elasticsearch-dump:v6.111.0  --input=/data/persons_data.json --output=http://elastic:9200/persons
```

4. Сервис доступ по
```
http://localhost:80
```

```
http://localhost/api/openapi
```
