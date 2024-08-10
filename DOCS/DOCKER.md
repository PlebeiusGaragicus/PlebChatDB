
---


## run with Docker

Note: don't do this - it's not ready


```sh
docker-compose up --build
```


### build/run docker image

```sh
docker build -t fastapi-mongo-app .

docker run -d -p 8000:8000 --name fastapi_app fastapi-mongo-app
```
