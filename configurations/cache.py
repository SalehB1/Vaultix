import json
from datetime import timedelta
from enum import Enum

from redis.asyncio import Redis

from configurations.environments import Values


class Cache:
    def __init__(self):
        self.redis = self.on_startup()

    @staticmethod
    def on_startup():
        return Redis.from_url(Values.REDIS_URL)

    def _serialize_value(self, value):
        """Helper method to serialize different types of values"""
        # Handle SQLAlchemy models
        if hasattr(value, '__class__') and hasattr(value.__class__, '__mapper__'):
            return {
                c.name: self._handle_value(getattr(value, c.name))
                for c in value.__table__.columns
            }
        # Handle dictionaries
        elif isinstance(value, dict):
            return {
                k: self._handle_value(v)
                for k, v in value.items()
            }
        # Handle other types
        return self._handle_value(value)

    def _handle_value(self, value):
        """Helper method to handle individual values"""
        if isinstance(value, Enum):
            return value.value
        elif hasattr(value, '__class__') and hasattr(value.__class__, '__mapper__'):
            return self._serialize_value(value)
        elif isinstance(value, (str, int, float, bool, type(None))):
            return value
        return str(value)

    def _deserialize_value(self, value):
        """Helper method to deserialize values"""
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    async def set(self, key, value, expire_time: timedelta = None):
        """
        Set a value in Redis
        :param key: Redis key
        :param value: Value to store (can be dict or SQLAlchemy model)
        :param expire_time: Optional expiration time
        """
        try:
            # Serialize the value
            serialized_value = self._serialize_value(value)
            # Convert to JSON string
            json_value = json.dumps(serialized_value)

            async with self.redis.client() as conn:
                return await conn.set(
                    name=key,
                    value=json_value,
                    ex=expire_time if expire_time else None
                )
        except Exception as e:
            raise Exception(f"Failed to set cache value: {str(e)}")

    async def get(self, key):
        """
        Get a value from Redis
        :param key: Redis key
        :return: Deserialized value
        """
        try:
            async with self.redis.client() as conn:
                value = await conn.get(key)
                return self._deserialize_value(value)
        except Exception as e:
            raise Exception(f"Failed to get cache value: {str(e)}")

    async def delete(self, key):
        """Delete a value from Redis"""
        try:
            async with self.redis.client() as conn:
                return await conn.delete(key)
        except Exception as e:
            raise Exception(f"Failed to delete cache value: {str(e)}")

