"""Celery tasks for automated email responses."""

import logging
from warmit.tasks import celery_app
from warmit.database import async_session_maker
from warmit.services.response_bot import ResponseBot


logger = logging.getLogger(__name__)


@celery_app.task(name="warmit.tasks.response.process_responses")
def process_responses() -> dict:
    """
    Process unread emails and send automated responses.

    This task should be scheduled to run every 30-60 minutes
    to check for new emails and respond naturally.
    """
    import asyncio

    async def _process():
        async with async_session_maker() as session:
            bot = ResponseBot(session)
            results = await bot.process_all_receivers()
            return results

    results = asyncio.run(_process())
    total_processed = sum(results.values())

    logger.info(f"Processed {total_processed} emails across {len(results)} receiver accounts")

    return {
        "receivers_processed": len(results),
        "total_emails_processed": total_processed,
        "receiver_results": results,
    }
