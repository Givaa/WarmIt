"""Email tracking endpoints for opens and clicks.

Secured with HMAC tokens to prevent unauthorized access.

Developed with ❤️ by Givaa
https://github.com/Givaa
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Response, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from warmit.database import get_session
from warmit.models.email import Email, EmailStatus
from warmit.services.tracking_token import validate_tracking_token, is_token_required


logger = logging.getLogger(__name__)
router = APIRouter()


# 1x1 transparent GIF pixel
TRACKING_PIXEL = bytes.fromhex(
    "47494638396101000100800000ffffff00000021f90401000000002c00000000"
    "010001000002024401003b"
)


@router.get("/track/open/{email_id}")
async def track_email_open(
    email_id: int,
    token: Optional[str] = Query(None, description="HMAC security token"),
    ts: Optional[int] = Query(None, description="Token timestamp"),
    session: AsyncSession = Depends(get_session),
):
    """
    Track email open via transparent pixel.

    When email client loads the tracking pixel, we record the open.
    Returns a 1x1 transparent GIF.

    Security: When TRACKING_SECRET_KEY is set, requires valid HMAC token.
    """
    # Validate token if security is enabled
    if is_token_required():
        if not token or ts is None:
            logger.warning(f"Tracking attempt without token for email {email_id}")
            # Still return pixel to not break email display, but don't track
            return Response(
                content=TRACKING_PIXEL,
                media_type="image/gif",
                headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                }
            )

        if not validate_tracking_token(email_id, token, ts):
            logger.warning(f"Invalid tracking token for email {email_id}")
            # Still return pixel to not break email display, but don't track
            return Response(
                content=TRACKING_PIXEL,
                media_type="image/gif",
                headers={
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                }
            )

    try:
        # Find the email with eager loading of relationships
        from sqlalchemy.orm import selectinload

        result = await session.execute(
            select(Email)
            .options(selectinload(Email.sender), selectinload(Email.receiver))
            .where(Email.id == email_id)
        )
        email = result.scalar_one_or_none()

        if email:
            # Only update if not already opened (first open only)
            if not email.opened_at:
                email.opened_at = datetime.now(timezone.utc)

                # Update sender account stats
                if email.sender:
                    email.sender.total_opened += 1

                await session.commit()

                logger.info(f"Email {email_id} opened by {email.receiver.email if email.receiver else 'unknown'}")
            else:
                logger.debug(f"Email {email_id} already tracked as opened")
        else:
            logger.warning(f"Tracking pixel accessed for unknown email ID: {email_id}")

    except Exception as e:
        logger.error(f"Error tracking email open: {e}")
        # Don't fail - just return pixel anyway

    # Always return the tracking pixel (even on error)
    return Response(
        content=TRACKING_PIXEL,
        media_type="image/gif",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
    )


@router.post("/webhooks/bounce")
async def handle_bounce_webhook(
    bounce_data: dict,
    session: AsyncSession = Depends(get_session),
):
    """
    Webhook endpoint for bounce notifications.

    This can be configured with email providers (SendGrid, Mailgun, etc.)
    to receive bounce notifications.
    """
    try:
        # Extract message ID from bounce data (format varies by provider)
        message_id = bounce_data.get("message_id")
        bounce_type = bounce_data.get("type", "hard")  # hard or soft

        if not message_id:
            raise HTTPException(status_code=400, detail="Missing message_id")

        # Find email by message_id
        result = await session.execute(
            select(Email).where(Email.message_id == message_id)
        )
        email = result.scalar_one_or_none()

        if email:
            email.status = EmailStatus.BOUNCED
            email.bounced_at = datetime.now(timezone.utc)

            # Update sender stats
            if email.sender:
                email.sender.total_bounced += 1

            await session.commit()

            logger.warning(
                f"Email {email.id} bounced ({bounce_type}): "
                f"{email.sender.email if email.sender else 'unknown'} → "
                f"{email.receiver.email if email.receiver else 'unknown'}"
            )

            return {"status": "success", "message": "Bounce recorded"}
        else:
            logger.warning(f"Bounce webhook for unknown message_id: {message_id}")
            return {"status": "not_found", "message": "Email not found"}

    except Exception as e:
        logger.error(f"Error processing bounce webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))
