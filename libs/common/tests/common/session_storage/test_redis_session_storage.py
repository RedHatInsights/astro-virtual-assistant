import json

import pytest
from redis.asyncio import StrictRedis

from pytest_mock_resources import create_redis_fixture, RedisConfig

from common.session_storage import Session
from common.session_storage.redis import RedisSessionStorage

redis_fixture = create_redis_fixture()

@pytest.fixture(scope='session')
def pmr_redis_config() -> RedisConfig:
    return RedisConfig(image="docker.io/redis:5.0.7")

@pytest.fixture
def redis(redis_fixture):
    return StrictRedis(**redis_fixture.pmr_credentials.as_redis_kwargs())

@pytest.fixture
def session_storage(redis):
    return RedisSessionStorage(redis)

async def test_redis_session_storage_storal(session_storage, redis):
    await session_storage.put(Session(key="my-key", user_identity="my.identity"))
    raw = await redis.get("my-key")
    assert raw == b'{"key": "my-key", "user_identity": "my.identity"}'

async def test_redis_session_storage_retrieval(session_storage, redis):
    await redis.set("my-key", json.dumps({"key": "my-key", "user_identity": "my.identity"}))
    retrieved = await session_storage.get("my-key")
    assert type(retrieved) is Session
    assert retrieved.key == "my-key"
    assert retrieved.user_identity == "my.identity"
