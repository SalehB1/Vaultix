import json
from datetime import timedelta
from enum import Enum
from typing import Any, Optional, Union
from redis.asyncio import Redis
from redis.exceptions import (
    RedisError,
    ConnectionError,
    TimeoutError,
    AuthenticationError
)

from configurations.environments import Values

class CacheException(Exception):
    """Base exception for cache operations"""
    pass

class CacheConnectionError(CacheException):
    """Raised when Redis connection fails"""
    pass

class CacheOperationError(CacheException):
    """Raised when a cache operation fails"""
    pass

class Cache:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Initialize only if not already initialized
        if not hasattr(self, '_initialized'):
            self._redis: Optional[Redis] = None
            self.REDIS_URL = (
                f"redis://:{Values.REDIS_PASSWORD}@{Values.REDIS_HOST}:{Values.REDIS_PORT}/{Values.REDIS_DB}"
                if Values.REDIS_PASSWORD
                else f"redis://{Values.REDIS_HOST}:{Values.REDIS_PORT}/{Values.REDIS_DB}"
            )
            self._initialized = True

    async def initialize(self):
        """Initialize Redis connection if not already initialized"""
        if self._redis is None:
            self._redis = self._create_redis_client()
            await self.check_connection()

    @classmethod
    def clear_instance(cls):
        """Clear the singleton instance"""
        cls._instance = None

    @property
    def redis(self) -> Redis:
        """Get Redis client instance"""
        if self._redis is None:
            raise CacheConnectionError("Redis not initialized. Call 'await initialize()' first")
        return self._redis

    def _create_redis_client(self) -> Redis:
        """Create a new Redis client with proper configuration"""
        try:
            return Redis.from_url(
                self.REDIS_URL,
                decode_responses=True,
                socket_timeout=Values.REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=Values.REDIS_SOCKET_CONNECT_TIMEOUT,
                retry_on_timeout=True,
                max_connections=10,
                health_check_interval=30
            )
        except (ConnectionError, TimeoutError) as e:
            raise CacheConnectionError(f"Failed to connect to Redis: {str(e)}")
        except AuthenticationError as e:
            raise CacheConnectionError(f"Redis authentication failed: {str(e)}")
        except RedisError as e:
            raise CacheConnectionError(f"Redis client creation failed: {str(e)}")

    async def check_connection(self) -> bool:
        """Check if Redis connection is alive"""
        try:
            await self.redis.ping()
            return True
        except RedisError:
            return False

    def _serialize_value(self, value: Any) -> Union[dict, Any]:
        """Helper method to serialize different types of values"""
        try:
            # Handle SQLAlchemy models
            if hasattr(value, '__class__') and hasattr(value.__class__, '__mapper__'):
                return {
                    c.name: self._handle_value(getattr(value, c.name))
                    for c in value.__table__.columns
                }
            # Handle dictionaries
            elif isinstance(value, dict):
                return {
                    str(k): self._handle_value(v)
                    for k, v in value.items()
                }
            # Handle other types
            return self._handle_value(value)
        except Exception as e:
            raise CacheOperationError(f"Serialization failed: {str(e)}")

    def _handle_value(self, value: Any) -> Any:
        """Helper method to handle individual values"""
        try:
            if isinstance(value, Enum):
                return value.value
            elif hasattr(value, '__class__') and hasattr(value.__class__, '__mapper__'):
                return self._serialize_value(value)
            elif isinstance(value, (str, int, float, bool, type(None))):
                return value
            return str(value)
        except Exception as e:
            raise CacheOperationError(f"Value handling failed: {str(e)}")

    def _deserialize_value(self, value: Optional[str]) -> Any:
        """Helper method to deserialize values"""
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
        except Exception as e:
            raise CacheOperationError(f"Deserialization failed: {str(e)}")

    async def set(self, key: str, value: Any, expire_time: Optional[timedelta] = None) -> bool:
        """
        Set a value in Redis
        :param key: Redis key
        :param value: Value to store (can be dict or SQLAlchemy model)
        :param expire_time: Optional expiration time
        :return: True if successful
        """
        try:
            if not await self.check_connection():
                raise CacheConnectionError("Redis connection lost")

            serialized_value = self._serialize_value(value)
            json_value = json.dumps(serialized_value)

            async with self.redis.client() as conn:
                return await conn.set(
                    name=key,
                    value=json_value,
                    ex=int(expire_time.total_seconds()) if expire_time else None
                )
        except (ConnectionError, TimeoutError) as e:
            raise CacheConnectionError(f"Redis connection error: {str(e)}")
        except CacheException:
            raise
        except Exception as e:
            raise CacheOperationError(f"Failed to set cache value: {str(e)}")

    async def get(self, key: str) -> Any:
        """
        Get a value from Redis
        :param key: Redis key
        :return: Deserialized value
        """
        try:
            if not await self.check_connection():
                raise CacheConnectionError("Redis connection lost")

            async with self.redis.client() as conn:
                value = await conn.get(key)
                return self._deserialize_value(value)
        except (ConnectionError, TimeoutError) as e:
            raise CacheConnectionError(f"Redis connection error: {str(e)}")
        except CacheException:
            raise
        except Exception as e:
            raise CacheOperationError(f"Failed to get cache value: {str(e)}")

    async def delete(self, key: str) -> bool:
        """
        Delete a value from Redis
        :param key: Redis key
        :return: True if key was deleted, False if key didn't exist
        """
        try:
            if not await self.check_connection():
                raise CacheConnectionError("Redis connection lost")

            async with self.redis.client() as conn:
                result = await conn.delete(key)
                return bool(result)
        except (ConnectionError, TimeoutError) as e:
            raise CacheConnectionError(f"Redis connection error: {str(e)}")
        except CacheException:
            raise
        except Exception as e:
            raise CacheOperationError(f"Failed to delete cache value: {str(e)}")

    async def close(self) -> None:
        """Close Redis connection"""
        if self._redis:
            await self._redis.close()
            self._redis = None
            self.clear_instance()