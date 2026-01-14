"""Celery tasks for email warming."""

import logging
from warmit.tasks import celery_app
from warmit.database import async_session_maker
from warmit.services.scheduler import WarmupScheduler


logger = logging.getLogger(__name__)


@celery_app.task(name="warmit.tasks.warming.process_campaigns")
def process_campaigns() -> dict:
    """
    Process all active warming campaigns.

    This task should be scheduled to run multiple times per day
    to distribute email sending throughout the day (8-12 hours).
    """
    import asyncio

    async def _process():
        async with async_session_maker() as session:
            scheduler = WarmupScheduler(session)
            results = await scheduler.process_all_campaigns()
            return results

    results = asyncio.run(_process())
    total_sent = sum(results.values())

    logger.info(f"Processed {len(results)} campaigns, sent {total_sent} emails")

    return {
        "campaigns_processed": len(results),
        "total_emails_sent": total_sent,
        "campaign_results": results,
    }


@celery_app.task(name="warmit.tasks.warming.reset_daily_counters")
def reset_daily_counters() -> dict:
    """
    Reset daily email counters for all campaigns.

    This task should run at midnight every day.
    """
    import asyncio

    async def _reset():
        async with async_session_maker() as session:
            scheduler = WarmupScheduler(session)
            await scheduler.reset_daily_counters()

    asyncio.run(_reset())

    logger.info("Reset daily counters for all campaigns")

    return {"status": "success"}


@celery_app.task(name="warmit.tasks.warming.update_metrics")
def update_metrics() -> dict:
    """
    Update daily metrics for all accounts.

    This task should run once per day, preferably at the end of the day.
    """
    import asyncio

    async def _update():
        async with async_session_maker() as session:
            scheduler = WarmupScheduler(session)
            await scheduler.update_metrics()

    asyncio.run(_update())

    logger.info("Updated metrics for all accounts")

    return {"status": "success"}
