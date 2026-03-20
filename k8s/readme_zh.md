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

## metrics

为 grafana 读取 Google Cloud 托管的普罗米修斯的数据创建一个账户

```bash

# 这里的 PROJECT_ID 就是 starroll
export PROJECT_ID=$(gcloud config get-value project)
export GSA_NAME="grafana-monitoring-reader"

gcloud iam service-accounts create  $GSA_NAME --display-name="Grafana Metrics Reader"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$GSA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/monitoring.viewer"

# 创建 k8s service account
kubectl create serviceaccount grafana-sa --namespace starroll
# 绑定到 Google cloud 的 service account
gcloud iam service-accounts add-iam-policy-binding \
    $GSA_NAME@$PROJECT_ID.iam.gserviceaccount.com \
    --role="roles/iam.workloadIdentityUser" \
    --member="serviceAccount:$PROJECT_ID.svc.id.goog[starroll/grafana-sa]"

# Mutating Admission Webhook 会自动向 Pod 注入环境变量：GOOGLE_APPLICATION_CREDENTIALS 指向一个预定义的路径。
# 和特定的 Volume 挂载：挂载一个包含预取令牌（OIDC Token）的投影卷（Projected Volume）。
kubectl annotate serviceaccount grafana-sa \
    --namespace starroll \
    iam.gke.io/gcp-service-account=$GSA_NAME@$PROJECT_ID.iam.gserviceaccount.com
```

在完成grafana的部署之后，添加 connections，选择 google cloud monitoring
Authentication type 选择 GCE Default Service Account ，禁用 Service account impersonation

```bash
kubectl create secret generic grafana-api-credentials \
  --from-literal=token='<你的-GRAFANA-TOKEN>' \
  --namespace starroll
```

> 参考 https://github.com/GoogleCloudPlatform/prometheus-engine/tree/main/cmd/datasource-syncer

## 部署

```bash
kubectl create namespace starroll

kubectl create secret tls ssl-secret --cert=fullchain.pem --key=privkey.pem -n starroll

# redis
kubectl apply -f k8s/prod/redis/pvc.yaml
kubectl apply -f k8s/prod/redis/service.yaml
kubectl apply -f k8s/prod/redis/deployment.yaml
# kafka
kubectl apply -f k8s/prod/kafka/pvc.yaml
kubectl apply -f k8s/prod/kafka/service.yaml
kubectl apply -f k8s/prod/kafka/deployment.yaml
# chat message consumer
kubectl apply -f k8s/prod/consumer/deployment.yaml
# console
kubectl apply -f k8s/prod/config/secret.yaml
kubectl apply -f k8s/prod/console/backendconfig.yaml
kubectl apply -f k8s/prod/console/service.yaml
kubectl apply -f k8s/prod/console/headless-service.yaml
kubectl apply -f k8s/prod/console/statefulset.yaml
# metrics collection rule for google cloud's Prometheus
kubectl apply -f k8s/prod/metrics/pm.yaml
# our cronjobs, not k8s cronjob
kubectl apply -f k8s/prod/cronjob/deployment.yaml
# astronomy.net
kubectl apply -f k8s/prod/astronomy/deployment.yaml
kubectl apply -f k8s/prod/astronomy/service.yaml
# nginx
kubectl apply -f k8s/prod/nginx/service.yaml
kubectl apply -f k8s/prod/nginx/ingress.yaml
kubectl apply -f k8s/prod/nginx/deployment.yaml
# grafana
kubectl apply -f k8s/prod/grafana/deployment.yaml
kubectl apply -f k8s/prod/grafana/pvc.yaml
kubectl apply -f k8s/prod/grafana/service.yaml
# 需要先修改 cronjob.yaml 中的 --datasource-uids
kubectl apply -f k8s/prod/grafana/cronjob.yaml

```
