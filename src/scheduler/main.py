import logging

from arq import create_pool, cron
from arq.connections import RedisSettings
from pytz import timezone

from src.configs import settings
from src.scheduler.tasks import check_events, send_reminder

redis_settings = RedisSettings(
    host=settings.redis.host,
    port=settings.redis.port,
    password=settings.redis.password,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def startup(ctx):
    ctx["redis"] = await create_pool(redis_settings)


async def shutdown(ctx):
    await ctx["redis"].aclose()


class WorkerSettings:
    functions = [send_reminder]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = redis_settings
    cron_jobs = [cron(check_events, second={1, 30})]
    timezone = timezone("Europe/Moscow")
