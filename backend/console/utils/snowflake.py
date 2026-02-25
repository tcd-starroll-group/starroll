import os
import time
import threading


class SnowflakeIDGenerator:
    def __init__(self, worker_id, datacenter_id):
        # 基础参数配置
        # self.worker_id = worker_id
        # self.datacenter_id = datacenter_id
        # self.sequence = 0
        #
        # # 机器 ID 占 5 位，数据中心 ID 占 5 位，序列号占 12 位
        # self.worker_id_bits = 5
        # self.datacenter_id_bits = 5
        # self.sequence_bits = 12
        #
        # self.last_timestamp = -1
        # self.lock = threading.Lock()
        # 从环境变量读取，解决无 Session 依赖问题
        self.worker_id = int(os.getenv("SNOWFLAKE_WORKER_ID", 1))
        self.datacenter_id = int(os.getenv("SNOWFLAKE_DATACENTER_ID", 1))
        self.sequence = 0
        self.last_timestamp = -1
        self.lock = threading.Lock()

    def _get_timestamp(self):
        return int(time.time() * 1000)

    def get_id(self):
        with self.lock:
            timestamp = self._get_timestamp()

            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & 4095
                if self.sequence == 0:
                    while timestamp <= self.last_timestamp:
                        timestamp = self._get_timestamp()
            else:
                self.sequence = 0

            self.last_timestamp = timestamp

            # 位运算拼接 ID
            new_id = ((timestamp - 1609459200000) << 22) | \
                     (self.datacenter_id << 17) | \
                     (self.worker_id << 12) | \
                     self.sequence
            return new_id


# 初始化全局实例
id_worker = SnowflakeIDGenerator(worker_id=1, datacenter_id=1)