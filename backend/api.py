from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from minio import Minio
import mysql.connector
import io
from datetime import datetime
import sys
from typing import Optional
from metrics import *

app = FastAPI()

# --- 1. MinIO 配置 ---
# 确保你的 Docker 容器正在运行，且端口映射为 9000
MINIO_CONF = {
    "endpoint": "localhost:9000",
    "access_key": "minioadmin",
    "secret_key": "minioadmin",
    "secure": False,
    "bucket": "camera-upload"
}

# 初始化 MinIO 客户端
minio_client = Minio(
    endpoint=MINIO_CONF["endpoint"],
    access_key=MINIO_CONF["access_key"],
    secret_key=MINIO_CONF["secret_key"],
    secure=MINIO_CONF["secure"]
)

# 确保 Bucket 存在
if not minio_client.bucket_exists(bucket_name=MINIO_CONF["bucket"]):
    minio_client.make_bucket(bucket_name=MINIO_CONF["bucket"])

# --- 2. MySQL 配置与初始化 ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'port': 3307
}


# 辅助函数：获取数据库连接
def get_db_conn():
    conn = mysql.connector.connect(**DB_CONFIG)
    conn.database = "minio_gallery"
    return conn

# 向kafka发送消息


def produce_messages(bootstrap: str, topic: str, messages: str,
                     key: Optional[str] = None, interval: float = 0.0,
                     timeout: float = 10.0) -> bool:
    """
    Produce messages to Kafka using confluent-kafka Producer.
    Returns True if all messages were queued/flushed without fatal errors.
    """
    try:
        from confluent_kafka import Producer  # type: ignore
    except Exception as e:
        print(f"confluent-kafka not available: {e}", file=sys.stderr)
        return False

    delivered = {"count": 0, "errors": 0}

    def delivery_report(err, msg):
        if err is not None:
            delivered["errors"] += 1
            print(
                f"Delivery failed for message {msg.key()}: {err}", file=sys.stderr)
        else:
            delivered["count"] += 1
            # minimal output to stdout for successful delivery
            print(
                f"Delivered to {msg.topic()} [{msg.partition()}] @ {msg.offset()}")

    p = Producer({'bootstrap.servers': bootstrap})

    try:
        p.produce(topic=topic, key=key, value=messages.encode('utf-8'),
                  callback=delivery_report)
        p.poll(0)  # serve delivery callbacks
        p.flush(timeout=timeout)
    except Exception as e:
        print(f"Failed to produce messages: {e}", file=sys.stderr)
        return False

    if delivered["errors"] > 0:
        return False
    return True

# --- 3. API: 上传图片 ---


@app.post("/upload")
async def upload_file(photo: UploadFile = File(...), sensorData: str = Form(...)):
    try:
        with tracer.start_as_current_span("api/upload") as parent_span:
            # 1. 存入 MinIO
            file_content = await photo.read()
            file_data = io.BytesIO(file_content)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{photo.filename}"
            parent_span.set_attribute("filename", filename)

            with tracer.start_as_current_span("minio/put_object") as put_object_span:
                minio_client.put_object(
                    bucket_name=MINIO_CONF["bucket"],
                    object_name=filename,
                    data=file_data,
                    length=len(file_content),
                    content_type=photo.content_type
                )

            # 2. 存入 MySQL
            with tracer.start_as_current_span("mysql/insert") as mysql_span:
                conn = get_db_conn()
                cursor = conn.cursor()
                sql = "INSERT INTO photos (filename, sensor_data) VALUES (%s, %s)"
                cursor.execute(sql, (filename, sensorData))
                conn.commit()
                cursor.close()
                conn.close()

            with tracer.start_as_current_span("kafka/produce") as produce_messages_span:
                ok = produce_messages(
                    "localhost:9092",
                    "post-image",
                    str(filename),
                )
            print(f"produce message {ok}")
            print(f"✅ 图片上传成功: {filename}")
            return {"status": "success", "filename": filename}

    except Exception as e:
        print(f"❌ 上传失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- 5. API: 获取图片列表 ---
@app.get("/images")
async def get_images():
    try:
        conn = get_db_conn()
        cursor = conn.cursor(dictionary=True)
        # 查最新的 10 张图
        cursor.execute(
            "SELECT * FROM photos WHERE url is not null ORDER BY id  DESC LIMIT 10;")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        results = []
        for row in rows:
            results.append({
                "id": row['id'],
                "url": row['url'],
                "sensor": row['sensor_data'],
                "time": row['created_at']
            })

        return results

    except Exception as e:
        print(f"❌ 获取列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    # 启动服务
    uvicorn.run(app, host="0.0.0.0", port=3000)
