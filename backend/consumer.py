"""Consume messages from a Kafka topic.

Examples:
  # Consume 10 messages from the default topic on localhost
  python consume.py --max 10

  # Consume continuously from the beginning with a specific group id
  python consume.py --group my-group --from-beginning

  # Consume from a remote cluster
  python consume.py --bootstrap broker1:9092 --topic my-topic
"""

import sys
from typing import Optional
import minio
import os
from datetime import timedelta
import time
import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'port': 3307
}


def get_db_conn():
    conn = mysql.connector.connect(**DB_CONFIG)
    conn.database = "minio_gallery"
    return conn


def consume_messages(bootstrap: str, topic: str, group_id: str = "python-consumer",
                     from_beginning: bool = False, max_messages: Optional[int] = None,
                     poll_timeout: float = 1.0, run_timeout: Optional[float] = None,
                     partitions: Optional[list] = None) -> bool:
    """
    Subscribe to `topic` and print messages. Returns True on graceful run, False on error.
    """
    try:
        from confluent_kafka import Consumer, KafkaException  # type: ignore
        # optional imports for partition assignment/seek
        from confluent_kafka import TopicPartition, OFFSET_BEGINNING  # type: ignore
    except Exception as e:
        print(f"confluent-kafka not available: {e}", file=sys.stderr)
        return False

    conf = {
        'bootstrap.servers': bootstrap,
        'group.id': group_id,
        'auto.offset.reset': 'earliest' if from_beginning else 'latest',
        'enable.partition.eof': False,
    }
    consumer = Consumer(conf)
    # If specific partitions were provided, assign those partitions directly.
    if partitions:
        try:
            tps = [TopicPartition(topic, int(p)) for p in partitions]
            consumer.assign(tps)
            # If requested, seek to beginning for each partition
            if from_beginning:
                for tp in tps:
                    try:
                        consumer.seek(TopicPartition(
                            tp.topic, tp.partition, OFFSET_BEGINNING))
                    except Exception:
                        # best-effort: continue if seek not supported or fails
                        pass
        except Exception as e:
            print(
                f"Failed to assign partitions {partitions}: {e}", file=sys.stderr)
            try:
                consumer.close()
            except Exception:
                pass
            return False
    else:
        consumer.subscribe([topic])

    received = 0
    start_time = time.time()
    try:
        while True:
            if run_timeout is not None and (time.time() - start_time) > run_timeout:
                break
            msg = consumer.poll(timeout=poll_timeout)
            if msg is None:
                continue
            if msg.error():
                # print errors but continue; treat fatal errors as failure
                err = msg.error()
                # KafkaException may wrap error codes; print and continue
                print(f"Consumer error: {err}", file=sys.stderr)
                # If it's a fatal error, break
                try:
                    if err.fatal():
                        return False
                except Exception:
                    pass
                continue
            # print message metadata and payload
            key = msg.key().decode('utf-8', errors='replace') if msg.key() else None
            try:
                value = msg.value().decode('utf-8', errors='replace') if msg.value() else None
            except Exception:
                value = str(msg.value())
            ts = msg.timestamp()
            ts_str = f"{ts[1]} (type {ts[0]})" if ts is not None else "None"

            print(
                f"Topic:{msg.topic()} Partition:{msg.partition()} Offset:{msg.offset()} Key:{key} Timestamp:{ts_str}")
            # 为该图片生成下载地址，并保存到mysql
            file_name = value
            url = gen_download_link(file_name)
            # 将url里的 localhost:9000 替换成 starroll-minio
            fixed_url = url.replace("localhost:9000", "starroll-minio")
            update_url(file_name, fixed_url)

            if value is not None:
                print(value)
            else:
                print("<no-value>")
            received += 1
            if max_messages is not None and received >= max_messages:
                break
    except KeyboardInterrupt:
        # user interrupted
        pass
    except KafkaException as ke:
        print(f"Kafka exception: {ke}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Unexpected error while consuming: {e}", file=sys.stderr)
        return False
    finally:
        try:
            consumer.close()
        except Exception:
            pass

    return True


def main(argv: Optional[list] = None) -> int:
    ok = consume_messages("localhost:9092", "post-image")
    return 0 if ok else 1


def gen_download_link(file_name: str):
    """
    Generate a presigned MinIO download URL for the object in bucket 'camera-upload'
    with a 1-year expiration. Returns the URL string on success, otherwise None.
    """
    try:
        # Read connection details from environment with sensible defaults
        endpoint = os.environ.get("MINIO_ENDPOINT", "localhost:9000")
        access_key = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
        secret_key = os.environ.get("MINIO_SECRET_KEY", "minioadmin")

        # Normalize endpoint and determine secure flag
        secure = False
        if endpoint.startswith("http://"):
            endpoint = endpoint[len("http://"):]
            secure = False
        elif endpoint.startswith("https://"):
            endpoint = endpoint[len("https://"):]
            secure = True

        client = minio.Minio(endpoint, access_key=access_key,
                             secret_key=secret_key, secure=secure)

        bucket = "camera-upload"
        object_name = (file_name or "").lstrip("/")

        if not object_name:
            print("Empty file name, cannot generate link", file=sys.stderr)
            return None

        expires = timedelta(days=7)
        url = client.presigned_get_object(bucket, object_name, expires=expires)

        print(f"Generated download link: {url}")
        return url
    except Exception as e:
        print(
            f"Failed to generate download link for {file_name}: {e}", file=sys.stderr)
        return None


def update_url(filename: str, url: str):
    conn = get_db_conn()
    cursor = conn.cursor()
    sql = "UPDATE photos SET url = %s where filename = %s"
    cursor.execute(sql, (url, filename))
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    sys.exit(main())
