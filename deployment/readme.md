# deployment

## 本地 docker 部署

网络

```bash
docker network create starroll
```

minio

```bash
docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  --name starroll-minio \
  -e "MINIO_ROOT_USER=minioadmin" \
  -e "MINIO_ROOT_PASSWORD=minioadmin" \
  --network starroll \
  -v minio_data:/data \
  minio/minio server /data --console-address ":9001"
```

mysql

```bash
docker run -d \
  --name starroll-mysql \
  -v starrollsql:/var/lib/mysql \
  --network starroll \
  -p 3307:3306 \
  -e MYSQL_ROOT_PASSWORD=root \
  mysql:latest
```

nginx

```bash
docker run -d \
  --name starroll-nginx \
  -p 80:80 \
  --network starroll \
  -v /Users/glimmer/Documents/study/software_engineering/starroll/frontend:/usr/share/nginx/html:ro \
  -v /Users/glimmer/Documents/study/software_engineering/starroll/frontend/nginx.conf:/etc/nginx/conf.d/default.conf:ro \
  nginx:latest
```

> replace `/Users/glimmer/Documents/study/software_engineering/starroll` with your path

jaeger

```bash
docker run -d --name starroll-jaeger \
  -p 16686:16686 \
  -p 4317:4317 \
  -p 4318:4318 \
  -p 5778:5778 \
  -p 9411:9411 \
  cr.jaegertracing.io/jaegertracing/jaeger:2.11.0
```

## set host

- mac

```bash
sudo vim /etc/hosts
```

add

```text
127.0.0.1 starroll-minio
```
