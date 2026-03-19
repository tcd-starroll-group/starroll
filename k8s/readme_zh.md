# 部署指南

以在谷歌云部署为例

1. 安装 gcloud 命令
2. 创建一个集群，选择 auto pilot 类型，集群名设置为 starroll-cluster
3. 创建一个 cloud sql 实例，名字设置为 starroll-rds
   创建 database 名为 starroll，创建用户 starroll-prod ，创建表。
   开启私网访问，等几分钟，拿到内网地址。
4. 创建 cloud storage bucket `identify-stars`
   Google Cloud 允许你生成一套兼容 S3 协议的密钥：
   进入 GCP 控制台 -> Cloud Storage -> 设置 (Settings)。
   点击 互操作性 (Interoperability) 标签页。
   点击 创建我的密钥 (Create a key)。
5. 创建 artifact regisregistry，名称为 starroll
   在 setup instruction 的指导下执行类似 `gcloud auth configure-docker europe-west1-docker.pkg.dev` 的命令，之后就可以推送镜像到谷歌的 artifact regisregistry 了
   为各个组件分别创建 console，cronjob，frontend

## 打包镜像

### backend console

这里的 -t 后面的路径需要与 artifact regisregistry 里的一致，在 artifact regisregistry 的页面点击 Copy Path 可以得到 europe-west1-docker.pkg.dev/starroll/console

```bash
docker build --platform linux/amd64 -f backend/console/Dockerfile . -t europe-west1-docker.pkg.dev/starroll/console/console:0.1
docker push europe-west1-docker.pkg.dev/starroll/console/console:0.1
```

### backend astronomy.net

```bash
docker pull dm90/astrometry:latest
docker tag dm90/astrometry:latest europe-west1-docker.pkg.dev/starroll/astronomy/astronomy:1.0
docker push europe-west1-docker.pkg.dev/starroll/astronomy/astronomy:1.0
```

### frontend

```bash
docker build --platform linux/amd64 -f frontend/Dockerfile . -t europe-west1-docker.pkg.dev/starroll/frontend/frontend:0.1
docker push europe-west1-docker.pkg.dev/starroll/frontend/frontend:0.1
```

## 部署

```bash
kubectl create namespace starroll

kubectl create secret tls ssl-secret --cert=fullchain.pem --key=privkey.pem -n starroll

kubectl apply -f k8s/prod/redis/pvc.yaml
kubectl apply -f k8s/prod/redis/service.yaml
kubectl apply -f k8s/prod/redis/deployment.yaml

kubectl apply -f k8s/prod/kafka/pvc.yaml
kubectl apply -f k8s/prod/kafka/service.yaml
kubectl apply -f k8s/prod/kafka/deployment.yaml

kubectl apply -f k8s/prod/consumer/deployment.yaml

kubectl apply -f k8s/prod/config/secret.yaml
kubectl apply -f k8s/prod/console/backendconfig.yaml
kubectl apply -f k8s/prod/console/service.yaml
kubectl apply -f k8s/prod/console/headless-service.yaml
kubectl apply -f k8s/prod/console/statefulset.yaml

kubectl apply -f k8s/prod/cronjob/deployment.yaml

kubectl apply -f k8s/prod/astronomy/deployment.yaml
kubectl apply -f k8s/prod/astronomy/service.yaml

kubectl apply -f k8s/prod/nginx/service.yaml
kubectl apply -f k8s/prod/nginx/ingress.yaml
kubectl apply -f k8s/prod/nginx/deployment.yaml
```
