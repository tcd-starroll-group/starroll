import os
import time
import threading


class SnowflakeIDGenerator:
    def __init__(self, worker_id, datacenter_id):
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

            new_id = ((timestamp - 1609459200000) << 22) | \
                     (self.datacenter_id << 17) | \
                     (self.worker_id << 12) | \
                     self.sequence
            return new_id


id_worker = SnowflakeIDGenerator(worker_id=1, datacenter_id=1)