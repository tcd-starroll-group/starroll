# Deployment Guide

The following uses deployment on Google Cloud as an example.

1. Install the `gcloud` CLI.
2. Create a cluster of type Auto Pilot, and name it `starroll-cluster`.
3. Create a Cloud SQL instance named `starroll-rds`.
   Create a database named `starroll`, create a user `starroll-prod`, and create the tables.
   Modify the Cloud SQL instance settings: in security settings, allow non-SSL access; in connectivity settings, enable private IP access. Wait a few minutes, then obtain the internal address.

4. Create a Cloud Storage bucket `identify-stars`.
   Google Cloud allows you to generate an S3-compatible key pair:
   Go to GCP Console -> Cloud Storage -> Settings.
   Click the Interoperability tab.
   Click Create a key.
5. Create an Artifact Registry repository named `starroll`.
   Follow the setup instructions and run a command similar to `gcloud auth configure-docker europe-west1-docker.pkg.dev`. After that, you can push images to Google Artifact Registry.
   Create separate repositories for each component, such as `console` and `frontend`.

## Build Images

### backend console

The path after `-t` must match the path in Artifact Registry. On the Artifact Registry page, click Copy Path to get something like `europe-west1-docker.pkg.dev/starroll/console`.

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

Create an account for Grafana to read data from Google Cloud Managed Prometheus:

```bash

# PROJECT_ID is your GCP project ID (for example, starroll)
export PROJECT_ID=$(gcloud config get-value project)
export GSA_NAME="grafana-monitoring-reader"

gcloud iam service-accounts create  $GSA_NAME --display-name="Grafana Metrics Reader"

gcloud projects add-iam-policy-binding $PROJECT_ID \
	--member="serviceAccount:$GSA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
	--role="roles/monitoring.viewer"

# Create a K8s service account
kubectl create serviceaccount grafana-sa --namespace starroll
# Bind it to the Google Cloud service account
gcloud iam service-accounts add-iam-policy-binding \
	$GSA_NAME@$PROJECT_ID.iam.gserviceaccount.com \
	--role="roles/iam.workloadIdentityUser" \
	--member="serviceAccount:$PROJECT_ID.svc.id.goog[starroll/grafana-sa]"

# Mutating Admission Webhook will automatically inject the environment variable
# GOOGLE_APPLICATION_CREDENTIALS (pointing to a predefined path) into the Pod,
# and mount a Projected Volume containing a prefetched OIDC token.
kubectl annotate serviceaccount grafana-sa \
	--namespace starroll \
	iam.gke.io/gcp-service-account=$GSA_NAME@$PROJECT_ID.iam.gserviceaccount.com
```

After Grafana is deployed, add a connection and select Prometheus:

```bash
kubectl create secret generic grafana-api-credentials \
  --from-literal=token='<your-GRAFANA-TOKEN>' \
  --namespace starroll
```

> Reference: https://github.com/GoogleCloudPlatform/prometheus-engine/tree/main/cmd/datasource-syncer

## keda

Install:

```bash
helm repo add kedacore https://kedacore.github.io/charts
helm repo update

helm install keda kedacore/keda --namespace keda --create-namespace
```

Configure permissions for reading Google Monitoring:

```bash
export PROJECT_ID=$(gcloud config get-value project)
export GSA_NAME="grafana-monitoring-reader"

# The GSA has already been created in the metrics section; reuse it here

gcloud iam service-accounts add-iam-policy-binding \
	$GSA_NAME@$PROJECT_ID.iam.gserviceaccount.com \
	--role="roles/iam.workloadIdentityUser" \
	--member="serviceAccount:$PROJECT_ID.svc.id.goog[keda/keda-operator]"

kubectl annotate serviceaccount keda-operator \
	--namespace keda \
	iam.gke.io/gcp-service-account=$GSA_NAME@$PROJECT_ID.iam.gserviceaccount.com

# Restart the KEDA operator afterward

kubectl rollout restart deployment keda-operator -n keda
```

## Deployment

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
# metrics collection rule for Google Cloud Prometheus
kubectl apply -f k8s/prod/metrics/pm.yaml
# our cronjobs (not Kubernetes CronJobs)
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
# You need to modify --datasource-uids in cronjob.yaml first
kubectl apply -f k8s/prod/grafana/cronjob.yaml

# keda
kubectl apply -f k8s/prod/keda/ScaledObject.yaml
kubectl apply -f k8s/prod/keda/TriggerAuthentication.yaml
```
