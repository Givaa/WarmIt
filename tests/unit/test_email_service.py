"""Unit tests for EmailService."""

import pytest
from warmit.services.email_service import EmailMessage, EmailService


class TestEmailMessage:
    """Test EmailMessage class."""

    def test_create_email_message(self):
        """Test creating an email message."""
        msg = EmailMessage(
            sender="sender@example.com",
            receiver="receiver@example.com",
            subject="Test Subject",
            body="Test body content",
        )

        assert msg.sender == "sender@example.com"
        assert msg.receiver == "receiver@example.com"
        assert msg.subject == "Test Subject"
        assert msg.body == "Test body content"
        assert msg.message_id is not None

    def test_email_message_with_tracking(self):
        """Test email message with tracking URL."""
        msg = EmailMessage(
            sender="sender@example.com",
            receiver="receiver@example.com",
            subject="Test",
            body="Body",
            tracking_url="https://example.com/track/123",
        )

        assert msg.tracking_url == "https://example.com/track/123"

    def test_email_message_reply_headers(self):
        """Test email message with reply headers."""
        msg = EmailMessage(
            sender="sender@example.com",
            receiver="receiver@example.com",
            subject="Re: Original Subject",
            body="Reply body",
            in_reply_to="<original@example.com>",
            references="<thread@example.com> <original@example.com>",
        )

        assert msg.in_reply_to == "<original@example.com>"
        assert msg.references == "<thread@example.com> <original@example.com>"

    def test_to_mime_conversion(self):
        """Test conversion to MIME message."""
        msg = EmailMessage(
            sender="sender@example.com",
            receiver="receiver@example.com",
            subject="Test",
            body="Body content",
        )

        mime_msg = msg.to_mime()

        assert mime_msg["From"] == "sender@example.com"
        assert mime_msg["To"] == "receiver@example.com"
        assert mime_msg["Subject"] == "Test"
        assert mime_msg["Message-ID"] is not None

    def test_to_mime_with_tracking_pixel(self):
        """Test MIME conversion includes tracking pixel."""
        msg = EmailMessage(
            sender="sender@example.com",
            receiver="receiver@example.com",
            subject="Test",
            body="Body",
            tracking_url="https://example.com/track/123",
        )

        mime_msg = msg.to_mime()
        body = mime_msg.as_string()

        assert "https://example.com/track/123" in body
        assert 'width="1"' in body
        assert 'height="1"' in body


class TestEmailService:
    """Test EmailService class."""

    def test_email_service_instantiation(self):
        """Test creating EmailService instance."""
        service = EmailService()
        assert service is not None

    # Note: SMTP/IMAP tests require mocking or integration testing
    # These are placeholder tests for the structure

    @pytest.mark.asyncio
    async def test_send_email_structure(self):
        """Test send_email method signature."""
        service = EmailService()

        # This test verifies the method exists and has correct signature
        # Actual sending requires mocking or integration test
        assert hasattr(service, "send_email")
        assert callable(service.send_email)

    @pytest.mark.asyncio
    async def test_fetch_unread_emails_structure(self):
        """Test fetch_unread_emails method signature."""
        service = EmailService()

        # This test verifies the method exists and has correct signature
        assert hasattr(service, "fetch_unread_emails")
        assert callable(service.fetch_unread_emails)
