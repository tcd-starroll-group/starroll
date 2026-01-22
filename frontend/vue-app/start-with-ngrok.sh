#!/bin/bash

# 传感器应用启动脚本
# 此脚本帮助您快速启动开发服务器并获取ngrok HTTPS地址

echo "📱 启动传感器应用..."
echo ""
echo "步骤 1: 启动开发服务器"
echo "================================"

# 检查是否已安装依赖
if [ ! -d "node_modules" ]; then
  echo "安装依赖..."
  npm install
fi

# 启动开发服务器（后台运行）
echo "启动 Vite 开发服务器..."
npm run dev &
DEV_PID=$!

# 等待服务器启动
sleep 3

echo ""
echo "✅ 开发服务器已启动（端口 5173）"
echo ""
echo "步骤 2: 使用 ngrok 获取 HTTPS 地址"
echo "================================"
echo ""
echo "请在另一个终端窗口运行以下命令："
echo ""
echo "    ngrok http 5173"
echo ""
echo "然后："
echo "  1. 复制 ngrok 提供的 HTTPS 地址（如 https://xxxx.ngrok.io）"
echo "  2. 在手机浏览器中访问该地址"
echo "  3. 点击'授予权限并开始读取'按钮"
echo ""
echo "注意事项："
echo "  - iOS 设备必须使用 Safari 浏览器"
echo "  - Android 设备推荐使用 Chrome"
echo "  - 确保手机和电脑在同一网络（如果不使用ngrok）"
echo ""
echo "按 Ctrl+C 停止开发服务器"
echo ""

# 等待用户中断
wait $DEV_PID

