from redis.asyncio import Redis

from auth_kit.settings import settings

redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
