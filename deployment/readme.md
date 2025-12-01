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

## set host

- mac

```bash
sudo vim /etc/hosts
```

add

```text
127.0.0.1 starroll-minio
```
