"""Redis client for caching operations."""

import redis
from typing import Any, Optional, List
from backend.config.settings import Settings


class RedisClient:
    """Redis client wrapper for cache operations."""
    
    _instance: Optional['RedisClient'] = None
    
    def __init__(self, settings: Settings):
        """Initialize Redis client with settings.
        
        Args:
            settings: Settings object containing Redis configuration
        """
        self.settings = settings
        self.client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            db=settings.redis_db,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True,
            health_check_interval=30,
        )
        # Test connection
        try:
            self.client.ping()
        except redis.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to Redis: {e}")
    
    @classmethod
    def get_instance(cls, settings: Settings) -> 'RedisClient':
        """Get or create Redis client singleton.
        
        Args:
            settings: Settings object containing Redis configuration
            
        Returns:
            RedisClient instance
        """
        if cls._instance is None:
            cls._instance = cls(settings)
        return cls._instance
    
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set a key-value pair in Redis.
        
        Args:
            key: Cache key
            value: Value to cache
            ex: Expiration time in seconds (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.set(key, value, ex=ex)
            return True
        except redis.RedisError as e:
            raise Exception(f"Redis set operation failed: {e}")
    
    def get(self, key: str) -> Optional[str]:
        """Get a value from Redis by key.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if key doesn't exist
        """
        try:
            return self.client.get(key)
        except redis.RedisError as e:
            raise Exception(f"Redis get operation failed: {e}")
    
    def delete(self, key: str) -> int:
        """Delete a key from Redis.
        
        Args:
            key: Cache key to delete
            
        Returns:
            Number of keys deleted
        """
        try:
            return self.client.delete(key)
        except redis.RedisError as e:
            raise Exception(f"Redis delete operation failed: {e}")
    
    def delete_many(self, keys: List[str]) -> int:
        """Delete multiple keys from Redis.
        
        Args:
            keys: List of cache keys to delete
            
        Returns:
            Number of keys deleted
        """
        if not keys:
            return 0
        try:
            return self.client.delete(*keys)
        except redis.RedisError as e:
            raise Exception(f"Redis delete_many operation failed: {e}")
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in Redis.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists, False otherwise
        """
        try:
            return self.client.exists(key) > 0
        except redis.RedisError as e:
            raise Exception(f"Redis exists operation failed: {e}")
    
    def incr(self, key: str, amount: int = 1) -> int:
        """Increment a counter in Redis.
        
        Args:
            key: Counter key
            amount: Amount to increment (default: 1)
            
        Returns:
            New value after increment
        """
        try:
            return self.client.incrby(key, amount)
        except redis.RedisError as e:
            raise Exception(f"Redis incr operation failed: {e}")
    
    def decr(self, key: str, amount: int = 1) -> int:
        """Decrement a counter in Redis.
        
        Args:
            key: Counter key
            amount: Amount to decrement (default: 1)
            
        Returns:
            New value after decrement
        """
        try:
            return self.client.decrby(key, amount)
        except redis.RedisError as e:
            raise Exception(f"Redis decr operation failed: {e}")
    
    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration time for a key.
        
        Args:
            key: Cache key
            seconds: Expiration time in seconds
            
        Returns:
            True if expiration was set, False if key doesn't exist
        """
        try:
            return self.client.expire(key, seconds)
        except redis.RedisError as e:
            raise Exception(f"Redis expire operation failed: {e}")
    
    def ttl(self, key: str) -> int:
        """Get time to live for a key in seconds.
        
        Args:
            key: Cache key
            
        Returns:
            TTL in seconds, -1 if no expiration, -2 if key doesn't exist
        """
        try:
            return self.client.ttl(key)
        except redis.RedisError as e:
            raise Exception(f"Redis ttl operation failed: {e}")
    
    def lpush(self, key: str, *values: Any) -> int:
        """Push values to the left of a list.
        
        Args:
            key: List key
            values: Values to push
            
        Returns:
            Length of list after push
        """
        try:
            return self.client.lpush(key, *values)
        except redis.RedisError as e:
            raise Exception(f"Redis lpush operation failed: {e}")
    
    def rpush(self, key: str, *values: Any) -> int:
        """Push values to the right of a list.
        
        Args:
            key: List key
            values: Values to push
            
        Returns:
            Length of list after push
        """
        try:
            return self.client.rpush(key, *values)
        except redis.RedisError as e:
            raise Exception(f"Redis rpush operation failed: {e}")
    
    def lpop(self, key: str) -> Optional[str]:
        """Pop value from the left of a list.
        
        Args:
            key: List key
            
        Returns:
            Popped value or None if list is empty
        """
        try:
            return self.client.lpop(key)
        except redis.RedisError as e:
            raise Exception(f"Redis lpop operation failed: {e}")
    
    def rpop(self, key: str) -> Optional[str]:
        """Pop value from the right of a list.
        
        Args:
            key: List key
            
        Returns:
            Popped value or None if list is empty
        """
        try:
            return self.client.rpop(key)
        except redis.RedisError as e:
            raise Exception(f"Redis rpop operation failed: {e}")
    
    def llen(self, key: str) -> int:
        """Get length of a list.
        
        Args:
            key: List key
            
        Returns:
            Length of list
        """
        try:
            return self.client.llen(key)
        except redis.RedisError as e:
            raise Exception(f"Redis llen operation failed: {e}")
    
    def hset(self, key: str, mapping: dict) -> int:
        """Set hash fields.
        
        Args:
            key: Hash key
            mapping: Dictionary of field-value pairs
            
        Returns:
            Number of fields added
        """
        try:
            return self.client.hset(key, mapping=mapping)
        except redis.RedisError as e:
            raise Exception(f"Redis hset operation failed: {e}")
    
    def hget(self, key: str, field: str) -> Optional[str]:
        """Get hash field value.
        
        Args:
            key: Hash key
            field: Field name
            
        Returns:
            Field value or None if not found
        """
        try:
            return self.client.hget(key, field)
        except redis.RedisError as e:
            raise Exception(f"Redis hget operation failed: {e}")
    
    def hgetall(self, key: str) -> dict:
        """Get all hash fields and values.
        
        Args:
            key: Hash key
            
        Returns:
            Dictionary of field-value pairs
        """
        try:
            return self.client.hgetall(key)
        except redis.RedisError as e:
            raise Exception(f"Redis hgetall operation failed: {e}")
    
    def sadd(self, key: str, *members: Any) -> int:
        """Add members to a set.
        
        Args:
            key: Set key
            members: Members to add
            
        Returns:
            Number of members added
        """
        try:
            return self.client.sadd(key, *members)
        except redis.RedisError as e:
            raise Exception(f"Redis sadd operation failed: {e}")
    
    def smembers(self, key: str) -> set:
        """Get all members of a set.
        
        Args:
            key: Set key
            
        Returns:
            Set of members
        """
        try:
            return self.client.smembers(key)
        except redis.RedisError as e:
            raise Exception(f"Redis smembers operation failed: {e}")
    
    def sismember(self, key: str, member: Any) -> bool:
        """Check if member exists in a set.
        
        Args:
            key: Set key
            member: Member to check
            
        Returns:
            True if member exists, False otherwise
        """
        try:
            return self.client.sismember(key, member)
        except redis.RedisError as e:
            raise Exception(f"Redis sismember operation failed: {e}")
    
    def flush_db(self) -> bool:
        """Flush current database.
        
        Returns:
            True if successful
        """
        try:
            self.client.flushdb()
            return True
        except redis.RedisError as e:
            raise Exception(f"Redis flush_db operation failed: {e}")
    
    def close(self):
        """Close Redis connection."""
        if self.client:
            self.client.close()
        RedisClient._instance = None
