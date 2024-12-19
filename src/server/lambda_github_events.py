import asyncio
import json
import logging
import base64
from services.githubWebhookService import GithubWebhookService
from app_sql import setup_async_sql_engine
from app_logger import logger

AsyncSession = setup_async_sql_engine()


def handler(event, context):
    asyncio.run(handler_async(event, context))


async def handler_async(event, context):
    logger.info("Started async event handler")

    try:
        async with AsyncSession() as session:
            githubService = GithubWebhookService(session)

            for event in event["Records"]:
                data = event["kinesis"]["data"]
                bodyStr = base64.b64decode(data).decode("utf-8")
                logging.info("Trigger processed an event: %s", bodyStr)
                body = json.loads(bodyStr)

                await githubService.process_event_async(
                    body["event_type"], body["delivery_id"], body["data"]
                )

            await session.commit()
    except Exception as e:
        logging.error("Error processing event: %s", e)

    logger.info("Ended async event handler")
