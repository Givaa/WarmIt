"""Quick test endpoints for sending emails immediately."""

import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from warmit.database import get_session, async_session_maker
from warmit.models.account import Account, AccountType
from warmit.services.email_service import EmailService, EmailMessage
from warmit.services.ai_generator import AIGenerator
import logging
import asyncio

router = APIRouter()
logger = logging.getLogger(__name__)


class TestEmailRequest(BaseModel):
    """Request to send test emails."""
    sender_id: int
    receiver_id: int
    count: int = 1
    include_replies: bool = True  # Whether receivers should auto-reply
    language: str = "en"  # Language for emails ("en" or "it")


class TestEmailResponse(BaseModel):
    """Response with test email results."""
    emails_sent: int
    replies_sent: int
    emails: list[dict]


@router.post("/send-emails", response_model=TestEmailResponse)
async def send_test_emails(
    request: TestEmailRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Send test emails immediately.

    This endpoint generates and sends test emails without creating a campaign.
    Useful for testing account configurations and AI content generation.
    """
    # Validate count
    if request.count < 1 or request.count > 10:
        raise HTTPException(status_code=400, detail="Count must be between 1 and 10")

    # Get sender account
    result = await session.execute(
        select(Account).where(Account.id == request.sender_id)
    )

    sender = result.scalar_one_or_none()

    if not sender:
        raise HTTPException(status_code=404, detail="Sender account not found")

    if sender.type != AccountType.SENDER:
        raise HTTPException(status_code=400, detail="Selected account is not a sender")

    # Get receiver account
    result = await session.execute(
        select(Account).where(Account.id == request.receiver_id)
    )
    receiver = result.scalar_one_or_none()

    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver account not found")

    if receiver.type != AccountType.RECEIVER:
        raise HTTPException(status_code=400, detail="Selected account is not a receiver")

    # Initialize AI generator
    ai_generator = AIGenerator()

    emails_sent = 0
    replies_sent = 0
    email_details = []

    # Send test emails
    for i in range(request.count):
        try:
            # Generate email content with sender's name and language
            email_content = await ai_generator.generate_email(
                sender_name=sender.full_name,
                language=request.language  # type: ignore
            )

            # Create email message
            message = EmailMessage(
                sender=sender.email,
                receiver=receiver.email,
                subject=f"[TEST {i+1}/{request.count}] {email_content.subject}",
                body=email_content.body,
            )

            # Send email (decrypt password for SMTP)
            success = await EmailService.send_email(
                smtp_host=sender.smtp_host,
                smtp_port=sender.smtp_port,
                username=sender.email,
                password=sender.get_password(),
                message=message,
                use_tls=sender.smtp_use_tls,
            )

            if success:
                emails_sent += 1
                email_details.append({
                    "subject": message.subject,
                    "from": message.sender,
                    "to": message.receiver,
                    "status": "sent",
                    "number": i + 1,
                    "has_reply": False,
                })
                logger.info(f"Test email {i+1}/{request.count} sent successfully")

                # Send automatic reply if requested
                if request.include_replies:
                    # Wait a few seconds before replying
                    await asyncio.sleep(2)

                    # Generate reply content with receiver's name and language
                    reply_subject, reply_body = await ai_generator.generate_reply(
                        email_content.subject,
                        email_content.body,
                        sender_name=receiver.full_name,
                        language=request.language  # type: ignore
                    )

                    # Create reply message
                    reply_message = EmailMessage(
                        sender=receiver.email,
                        receiver=sender.email,
                        subject=f"Re: {message.subject}",
                        body=reply_body,
                    )

                    # Send reply (decrypt password for SMTP)
                    reply_success = await EmailService.send_email(
                        smtp_host=receiver.smtp_host,
                        smtp_port=receiver.smtp_port,
                        username=receiver.email,
                        password=receiver.get_password(),
                        message=reply_message,
                        use_tls=receiver.smtp_use_tls,
                    )

                    if reply_success:
                        replies_sent += 1
                        email_details[-1]["has_reply"] = True
                        email_details[-1]["reply_subject"] = reply_message.subject
                        logger.info(f"Auto-reply sent for test email {i+1}/{request.count}")
                    else:
                        logger.error(f"Failed to send auto-reply for test email {i+1}/{request.count}")
            else:
                email_details.append({
                    "subject": message.subject,
                    "from": message.sender,
                    "to": message.receiver,
                    "status": "failed",
                    "number": i + 1,
                    "has_reply": False,
                })
                logger.error(f"Failed to send test email {i+1}/{request.count}")

        except Exception as e:
            logger.error(f"Error sending test email {i+1}/{request.count}: {e}")
            email_details.append({
                "subject": "Error",
                "from": sender.email,
                "to": receiver.email,
                "status": f"error: {str(e)}",
                "number": i + 1,
                "has_reply": False,
            })

    return TestEmailResponse(
        emails_sent=emails_sent,
        replies_sent=replies_sent,
        emails=email_details,
    )


@router.post("/send-emails-stream")
async def send_test_emails_stream(
    request: TestEmailRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Send test emails with real-time progress streaming via SSE.

    Returns Server-Sent Events with progress updates.
    """
    # Validate inputs first
    if request.count < 1 or request.count > 10:
        raise HTTPException(status_code=400, detail="Count must be between 1 and 10")

    # Get sender account
    result = await session.execute(
        select(Account).where(Account.id == request.sender_id)
    )
    sender = result.scalar_one_or_none()
    if not sender:
        raise HTTPException(status_code=404, detail="Sender account not found")
    if sender.type != AccountType.SENDER:
        raise HTTPException(status_code=400, detail="Selected account is not a sender")

    # Get receiver account
    result = await session.execute(
        select(Account).where(Account.id == request.receiver_id)
    )
    receiver = result.scalar_one_or_none()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver account not found")
    if receiver.type != AccountType.RECEIVER:
        raise HTTPException(status_code=400, detail="Selected account is not a receiver")

    # Store account data for use in generator (avoid detached instance issues)
    sender_data = {
        "email": sender.email,
        "full_name": sender.full_name,
        "smtp_host": sender.smtp_host,
        "smtp_port": sender.smtp_port,
        "smtp_use_tls": sender.smtp_use_tls,
        "password": sender.get_password(),
    }
    receiver_data = {
        "email": receiver.email,
        "full_name": receiver.full_name,
        "smtp_host": receiver.smtp_host,
        "smtp_port": receiver.smtp_port,
        "smtp_use_tls": receiver.smtp_use_tls,
        "password": receiver.get_password(),
    }

    async def generate_events():
        """Generate SSE events for email sending progress."""
        ai_generator = AIGenerator()
        emails_sent = 0
        replies_sent = 0
        email_details = []

        total_steps = request.count * (2 if request.include_replies else 1)
        current_step = 0

        for i in range(request.count):
            try:
                # Step 1: Generating email
                yield f"data: {json.dumps({'type': 'progress', 'step': 'generating', 'email_num': i+1, 'total': request.count, 'message': f'Generating email {i+1}/{request.count}...'})}\n\n"

                email_content = await ai_generator.generate_email(
                    sender_name=sender_data["full_name"],
                    language=request.language
                )

                # Step 2: Sending email
                yield f"data: {json.dumps({'type': 'progress', 'step': 'sending', 'email_num': i+1, 'total': request.count, 'message': f'Sending email {i+1}/{request.count}...'})}\n\n"

                message = EmailMessage(
                    sender=sender_data["email"],
                    receiver=receiver_data["email"],
                    subject=f"[TEST {i+1}/{request.count}] {email_content.subject}",
                    body=email_content.body,
                )

                success = await EmailService.send_email(
                    smtp_host=sender_data["smtp_host"],
                    smtp_port=sender_data["smtp_port"],
                    username=sender_data["email"],
                    password=sender_data["password"],
                    message=message,
                    use_tls=sender_data["smtp_use_tls"],
                )

                current_step += 1
                progress = int((current_step / total_steps) * 100)

                if success:
                    emails_sent += 1
                    email_info = {
                        "subject": message.subject,
                        "from": message.sender,
                        "to": message.receiver,
                        "status": "sent",
                        "number": i + 1,
                        "has_reply": False,
                    }
                    email_details.append(email_info)

                    yield f"data: {json.dumps({'type': 'email_sent', 'email_num': i+1, 'progress': progress, 'email': email_info})}\n\n"

                    # Send auto-reply if requested
                    if request.include_replies:
                        yield f"data: {json.dumps({'type': 'progress', 'step': 'generating_reply', 'email_num': i+1, 'message': f'Generating reply for email {i+1}...'})}\n\n"

                        await asyncio.sleep(2)

                        reply_subject, reply_body = await ai_generator.generate_reply(
                            email_content.subject,
                            email_content.body,
                            sender_name=receiver_data["full_name"],
                            language=request.language
                        )

                        yield f"data: {json.dumps({'type': 'progress', 'step': 'sending_reply', 'email_num': i+1, 'message': f'Sending reply for email {i+1}...'})}\n\n"

                        reply_message = EmailMessage(
                            sender=receiver_data["email"],
                            receiver=sender_data["email"],
                            subject=f"Re: {message.subject}",
                            body=reply_body,
                        )

                        reply_success = await EmailService.send_email(
                            smtp_host=receiver_data["smtp_host"],
                            smtp_port=receiver_data["smtp_port"],
                            username=receiver_data["email"],
                            password=receiver_data["password"],
                            message=reply_message,
                            use_tls=receiver_data["smtp_use_tls"],
                        )

                        current_step += 1
                        progress = int((current_step / total_steps) * 100)

                        if reply_success:
                            replies_sent += 1
                            email_details[-1]["has_reply"] = True
                            email_details[-1]["reply_subject"] = reply_message.subject

                            yield f"data: {json.dumps({'type': 'reply_sent', 'email_num': i+1, 'progress': progress})}\n\n"
                        else:
                            yield f"data: {json.dumps({'type': 'reply_failed', 'email_num': i+1, 'progress': progress})}\n\n"
                else:
                    email_details.append({
                        "subject": message.subject,
                        "from": message.sender,
                        "to": message.receiver,
                        "status": "failed",
                        "number": i + 1,
                        "has_reply": False,
                    })
                    yield f"data: {json.dumps({'type': 'email_failed', 'email_num': i+1, 'progress': progress})}\n\n"

            except Exception as e:
                logger.error(f"Error sending test email {i+1}: {e}")
                yield f"data: {json.dumps({'type': 'error', 'email_num': i+1, 'message': str(e)})}\n\n"

        # Final result
        yield f"data: {json.dumps({'type': 'complete', 'emails_sent': emails_sent, 'replies_sent': replies_sent, 'emails': email_details})}\n\n"

    return StreamingResponse(
        generate_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
