"""Email sending and receiving service using SMTP/IMAP."""

import logging
import asyncio
from datetime import datetime, timezone
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import make_msgid, formataddr
import aiosmtplib
import aioimaplib


logger = logging.getLogger(__name__)


class EmailMessage:
    """Email message container."""

    def __init__(
        self,
        sender: str,
        receiver: str,
        subject: str,
        body: str,
        message_id: Optional[str] = None,
        in_reply_to: Optional[str] = None,
        references: Optional[str] = None,
        tracking_url: Optional[str] = None,
    ):
        self.sender = sender
        self.receiver = receiver
        self.subject = subject
        self.body = body
        self.message_id = message_id or make_msgid()
        self.in_reply_to = in_reply_to
        self.references = references
        self.tracking_url = tracking_url

    def to_mime(self) -> MIMEMultipart:
        """Convert to MIME message."""
        msg = MIMEMultipart("alternative")
        msg["From"] = self.sender
        msg["To"] = self.receiver
        msg["Subject"] = self.subject
        msg["Message-ID"] = self.message_id

        if self.in_reply_to:
            msg["In-Reply-To"] = self.in_reply_to

        if self.references:
            msg["References"] = self.references

        # Add body as plain text
        text_part = MIMEText(self.body, "plain", "utf-8")
        msg.attach(text_part)

        # Add body as HTML (converts newlines to <br>)
        html_body = self.body.replace("\n", "<br>\n")

        # Add tracking pixel if URL provided
        tracking_pixel = ""
        if self.tracking_url:
            tracking_pixel = f'<img src="{self.tracking_url}" width="1" height="1" alt="" style="display:none" />'

        html_part = MIMEText(
            f'<html><body>{html_body}{tracking_pixel}</body></html>',
            "html",
            "utf-8"
        )
        msg.attach(html_part)

        return msg


class EmailService:
    """Service for sending and receiving emails."""

    @staticmethod
    async def send_email(
        smtp_host: str,
        smtp_port: int,
        username: str,
        password: str,
        message: EmailMessage,
        use_tls: bool = True,
    ) -> bool:
        """
        Send an email via SMTP.

        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port
            username: SMTP username
            password: SMTP password
            message: EmailMessage to send
            use_tls: Whether to use STARTTLS (True) or SSL (False)

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            logger.info(f"Sending email from {message.sender} to {message.receiver}")

            mime_msg = message.to_mime()

            # Port 465 requires SSL/TLS without STARTTLS
            # Port 587 requires STARTTLS
            if smtp_port == 465:
                # SSL/TLS direct connection (implicit TLS)
                await aiosmtplib.send(
                    mime_msg,
                    hostname=smtp_host,
                    port=smtp_port,
                    username=username,
                    password=password,
                    use_tls=True,  # Enable TLS wrapper
                    start_tls=False,  # Don't use STARTTLS
                )
            else:
                # Port 587 or other: use STARTTLS if use_tls=True
                await aiosmtplib.send(
                    mime_msg,
                    hostname=smtp_host,
                    port=smtp_port,
                    username=username,
                    password=password,
                    use_tls=False,  # Don't wrap connection in TLS
                    start_tls=use_tls,  # Use STARTTLS instead
                )

            logger.info(f"Email sent successfully: {message.subject}")
            return True

        except Exception as e:
            logger.error(f"SMTP connection failed: {e}")
            return False

    @staticmethod
    async def fetch_unread_emails(
        imap_host: str,
        imap_port: int,
        username: str,
        password: str,
        use_ssl: bool = True,
        limit: int = 50,
    ) -> list[dict]:
        """
        Fetch unread emails from IMAP server.

        Args:
            imap_host: IMAP server hostname
            imap_port: IMAP server port
            username: IMAP username
            password: IMAP password
            use_ssl: Whether to use SSL
            limit: Maximum number of emails to fetch

        Returns:
            List of email dictionaries
        """
        try:
            logger.info(f"Fetching unread emails for {username}")

            # Connect to IMAP
            imap = aioimaplib.IMAP4_SSL(imap_host, imap_port) if use_ssl else aioimaplib.IMAP4(imap_host, imap_port)
            await imap.wait_hello_from_server()
            await imap.login(username, password)
            await imap.select("INBOX")

            # Search for unread emails
            response = await imap.search("UNSEEN")
            message_numbers = response.lines[0].split() if response.lines and response.lines[0] else []

            if not message_numbers:
                logger.info("No unread emails found")
                await imap.logout()
                return []

            # Limit message IDs
            msg_ids = message_numbers[:limit] if limit else message_numbers

            emails = []
            for msg_id in msg_ids:
                try:
                    # Fetch email with RFC822
                    # Note: This WILL mark email as \Seen, but that's okay because
                    # the response bot will re-mark as unread if it doesn't respond
                    fetch_response = await imap.fetch(msg_id.decode() if isinstance(msg_id, bytes) else msg_id, "(RFC822)")

                    # aioimaplib returns the email in lines attribute
                    # The first line is the IMAP response header (e.g., "1 FETCH (RFC822 {1234}")
                    # The subsequent lines contain the actual email data
                    # The last line is ")"
                    import email
                    from email import policy

                    if fetch_response.lines and len(fetch_response.lines) > 2:
                        # Skip first line (IMAP header) and last line (")")
                        # Join the middle lines which contain the email
                        email_lines = fetch_response.lines[1:-1]
                        raw_email = b''.join(email_lines)

                        if raw_email:
                            email_message = email.message_from_bytes(
                                raw_email, policy=policy.default
                            )

                            # Extract relevant fields
                            email_dict = {
                                "message_id": email_message.get("Message-ID", "").strip("<>"),
                                "subject": email_message.get("Subject", ""),
                                "from": email_message.get("From", ""),
                                "to": email_message.get("To", ""),
                                "date": email_message.get("Date", ""),
                                "in_reply_to": email_message.get("In-Reply-To", "").strip("<>"),
                                "references": email_message.get("References", ""),
                                "body": EmailService._extract_body(email_message),
                                "imap_id": msg_id.decode() if isinstance(msg_id, bytes) else msg_id,  # Add IMAP ID for later operations
                            }

                            emails.append(email_dict)

                except Exception as e:
                    logger.error(f"Failed to fetch message {msg_id}: {e}")
                    continue

            await imap.logout()
            logger.info(f"Fetched {len(emails)} unread emails")
            return emails

        except Exception as e:
            logger.error(f"Failed to fetch emails: {e}")
            return []

    @staticmethod
    def _extract_body(email_message) -> str:
        """Extract plain text body from email message."""
        body = ""

        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode()
                        break
                    except:
                        pass
        else:
            try:
                body = email_message.get_payload(decode=True).decode()
            except:
                body = str(email_message.get_payload())

        return body.strip()

    @staticmethod
    async def mark_as_read(
        imap_host: str,
        imap_port: int,
        username: str,
        password: str,
        message_id: str,
        use_ssl: bool = True,
    ) -> bool:
        """
        Mark an email as read.

        Args:
            imap_host: IMAP server hostname
            imap_port: IMAP server port
            username: IMAP username
            password: IMAP password
            message_id: Message ID to mark as read
            use_ssl: Whether to use SSL

        Returns:
            True if successful, False otherwise
        """
        try:
            imap = aioimaplib.IMAP4_SSL(imap_host, imap_port) if use_ssl else aioimaplib.IMAP4(imap_host, imap_port)
            await imap.wait_hello_from_server()
            await imap.login(username, password)
            await imap.select("INBOX")

            # Search for message by ID
            response = await imap.search(f'HEADER Message-ID "{message_id}"')
            msg_nums = response.lines[0].split() if response.lines and response.lines[0] else []

            if msg_nums:
                msg_num = msg_nums[0].decode() if isinstance(msg_nums[0], bytes) else msg_nums[0]
                await imap.store(msg_num, "+FLAGS", "(\\Seen)")
                logger.info(f"Marked message {message_id} as read")
                await imap.logout()
                return True

            await imap.logout()
            return False

        except Exception as e:
            logger.error(f"Failed to mark message as read: {e}")
            return False

    @staticmethod
    async def test_connection(
        smtp_host: str,
        smtp_port: int,
        imap_host: str,
        imap_port: int,
        username: str,
        password: str,
        smtp_use_tls: bool = True,
        imap_use_ssl: bool = True,
    ) -> dict[str, bool]:
        """
        Test SMTP and IMAP connections.

        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port
            imap_host: IMAP server hostname
            imap_port: IMAP server port
            username: Account username
            password: Account password
            smtp_use_tls: Whether to use TLS for SMTP
            imap_use_ssl: Whether to use SSL for IMAP

        Returns:
            Dictionary with connection test results
        """
        results = {"smtp": False, "imap": False}

        # Test SMTP
        try:
            # Port 465 requires SSL/TLS wrapper, port 587 uses STARTTLS
            if smtp_port == 465:
                # SSL/TLS direct connection (implicit TLS)
                smtp = aiosmtplib.SMTP(
                    hostname=smtp_host,
                    port=smtp_port,
                    use_tls=True,
                    start_tls=False,
                )
            else:
                # Port 587 or other: use STARTTLS
                smtp = aiosmtplib.SMTP(
                    hostname=smtp_host,
                    port=smtp_port,
                    use_tls=False,  # Don't wrap connection in TLS
                    start_tls=smtp_use_tls,  # Use STARTTLS instead
                )
            await smtp.connect()
            await smtp.login(username, password)
            await smtp.quit()
            results["smtp"] = True
            logger.info("SMTP connection successful")
        except Exception as e:
            logger.error(f"SMTP connection failed: {e}")

        # Test IMAP
        try:
            imap = aioimaplib.IMAP4_SSL(imap_host, imap_port) if imap_use_ssl else aioimaplib.IMAP4(imap_host, imap_port)
            await imap.wait_hello_from_server()
            await imap.login(username, password)
            await imap.logout()
            results["imap"] = True
            logger.info("IMAP connection successful")
        except Exception as e:
            logger.error(f"IMAP connection failed: {e}")

        return results
