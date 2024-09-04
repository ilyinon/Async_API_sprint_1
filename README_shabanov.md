# Проектная работа 4 спринта

**Важное сообщение для тимлида:** для ускорения проверки проекта укажите ссылку на приватный репозиторий с командной работой в файле readme и отправьте свежее приглашение на аккаунт [BlueDeep](https://github.com/BigDeepBlue).

В папке **tasks** ваша команда найдёт задачи, которые необходимо выполнить в первом спринте второго модуля.  Обратите внимание на задачи **00_create_repo** и **01_create_basis**. Они расцениваются как блокирующие для командной работы, поэтому их необходимо выполнить как можно раньше.

Мы оценили задачи в стори поинтах, значения которых брались из [последовательности Фибоначчи](https://ru.wikipedia.org/wiki/Числа_Фибоначчи) (1,2,3,5,8,…).

Вы можете разбить имеющиеся задачи на более маленькие, например, распределять между участниками команды не большие куски задания, а маленькие подзадачи. В таком случае не забудьте зафиксировать изменения в issues в репозитории.

**От каждого разработчика ожидается выполнение минимум 40% от общего числа стори поинтов в спринте.**

**Запуск приложения**

Развернуть контейнеры с необходимыми компонентами
```bash
docker-compose up -d --build
```
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
docker run -ti -v ~/Dev/async_api_sprint_1/data/:/data --network=async_api_sprint_1_default  elasticdump/elasticsearch-dump:v6.111.0  --input=/data/movies_data.json --output=http://elastic:9200/movies
```
Аналогично перенесем данные из файла genres_data.json
```bash
docker run -ti -v ~/Dev/async_api_sprint_1/data/:/data --network=async_api_sprint_1_default  elasticdump/elasticsearch-dump:v6.111.0  --input=/data/genres_data.json --output=http://elastic:9200/genres
```
Аналогично перенесем данные из файла persons_data.json
```bash
docker run -ti -v ~/Dev/async_api_sprint_1/data/:/data --network=async_api_sprint_1_default  elasticdump/elasticsearch-dump:v6.111.0  --input=/data/persons_data.json --output=http://elastic:9200/persons
```
