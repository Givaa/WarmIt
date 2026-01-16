"""Celery tasks for bounce detection."""

import logging
from warmit.tasks import celery_app
from warmit.database import async_session_maker
from warmit.services.bounce_detector import BounceDetector


logger = logging.getLogger(__name__)


@celery_app.task(name="warmit.tasks.bounce.detect_bounces")
def detect_bounces() -> dict:
    """
    Detect and process email bounces from sender accounts.

    This task should be scheduled to run every 30-60 minutes
    to check for bounce notifications.
    """
    import asyncio

    async def _detect():
        async with async_session_maker() as session:
            detector = BounceDetector(session)
            results = await detector.process_all_senders()
            return results

    # Use new_event_loop instead of asyncio.run to avoid event loop conflicts
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        results = loop.run_until_complete(_detect())
    finally:
        loop.close()
    total_bounces = sum(results.values())

    logger.info(f"Detected {total_bounces} bounces across {len(results)} sender accounts")

    return {
        "senders_processed": len(results),
        "total_bounces_detected": total_bounces,
        "sender_results": results,
    }
