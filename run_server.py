import sys
import os
import uvicorn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

GEN_SRC_DIR = os.path.join(BASE_DIR, "gen", "py", "src")
sys.path.insert(0, GEN_SRC_DIR)
sys.path.insert(0, BASE_DIR)

if __name__ == "__main__":
    print(f" 启动服务器... 已将以下路径加入解析: {GEN_SRC_DIR}")
    uvicorn.run("openapi_server.main:app", host="0.0.0.0", port=8000, reload=True)