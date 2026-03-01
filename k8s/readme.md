# Deployment Guide

Example: deploying to Google Cloud

1. Install the `gcloud` CLI.
2. Create a cluster; choose the Autopilot type and name the cluster `starroll-cluster`.
3. Create a Cloud SQL instance named `starroll-rds`. Create a database named `starroll`, create a user `starroll-prod`, and create the necessary tables. Enable private IP access, wait a few minutes, and obtain the private/internal IP address.
4. Create a Cloud Storage bucket named `identify-stars`. Google Cloud lets you generate S3-compatible interoperability keys:
   - Go to the GCP Console -> Cloud Storage -> Settings.
   - Click the "Interoperability" tab.
   - Click "Create a key".
5. Create an Artifact Registry named `starroll`. Follow the setup instructions and run a command like:

```
gcloud auth configure-docker europe-west1-docker.pkg.dev
```

After that you can push images to Google Artifact Registry. Create repositories for each component: `console`, `cronjob`, and `frontend`.

## Building images

### backend (console)

The `-t` path must match the Artifact Registry path. On the Artifact Registry page click "Copy Path" to get something like `europe-west1-docker.pkg.dev/starroll/console`.

```bash
docker build --platform linux/amd64 -f backend/console/Dockerfile . -t europe-west1-docker.pkg.dev/starroll/console/console:0.1
docker push europe-west1-docker.pkg.dev/starroll/console/console:0.1
```

### frontend

```bash
docker build --platform linux/amd64 -f frontend/Dockerfile . -t europe-west1-docker.pkg.dev/starroll/frontend/frontend:0.1
docker push europe-west1-docker.pkg.dev/starroll/frontend/frontend:0.1
```

## Deployment

```bash
kubectl create namespace starroll

kubectl create secret tls ssl-secret --cert=fullchain.pem --key=privkey.pem -n starroll

kubectl apply -f k8s/prod/redis/pvc.yaml
kubectl apply -f k8s/prod/redis/service.yaml
kubectl apply -f k8s/prod/redis/deployment.yaml

kubectl apply -f k8s/prod/config/secret.yaml
kubectl apply -f k8s/prod/console/backendconfig.yaml
kubectl apply -f k8s/prod/console/service.yaml
kubectl apply -f k8s/prod/console/deployment.yaml

kubectl apply -f k8s/prod/nginx/service.yaml
kubectl apply -f k8s/prod/nginx/ingress.yaml
kubectl apply -f k8s/prod/nginx/deployment.yaml
```
