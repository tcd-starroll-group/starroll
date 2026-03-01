FROM node:20-alpine AS builder

WORKDIR /workspace

COPY frontend/vue-app/package.json frontend/vue-app/package-lock.json frontend/vue-app/
WORKDIR /workspace/frontend/vue-app
RUN npm ci

WORKDIR /workspace
COPY frontend/vue-app/ frontend/vue-app/
COPY gen/ts/ gen/ts/

WORKDIR /workspace/frontend/vue-app
RUN npm run build

FROM nginx:1.27-alpine

COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /workspace/frontend/vue-app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
