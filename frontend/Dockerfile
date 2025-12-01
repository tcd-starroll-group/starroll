# 1. 基础镜像
FROM nginx:alpine

# 2. 复制你的 HTML 文件
COPY . /usr/share/nginx/html

# 3. 【新增步骤】复制你刚才写的 default.conf 覆盖镜像里的默认配置
# 注意：一定要放在 /etc/nginx/conf.d/ 目录下
COPY default.conf /etc/nginx/conf.d/default.conf

# 4. 暴露端口
EXPOSE 80