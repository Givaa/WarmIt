"""AI content generation for emails using OpenRouter/Groq."""

import logging
import random
from typing import Optional
from openai import AsyncOpenAI
from warmit.config import settings


logger = logging.getLogger(__name__)


class EmailContent:
    """Container for generated email content."""

    def __init__(self, subject: str, body: str, prompt: str, model: str):
        self.subject = subject
        self.body = body
        self.prompt = prompt
        self.model = model

    def __repr__(self) -> str:
        return f"<EmailContent(subject={self.subject[:30]}...)>"


class AIGenerator:
    """AI-powered email content generator."""

    # Email topics for variety
    TOPICS = [
        "tech news and innovations",
        "productivity tips",
        "industry insights",
        "business strategies",
        "personal development",
        "health and wellness",
        "travel experiences",
        "book recommendations",
        "movie and entertainment",
        "cooking and recipes",
        "photography tips",
        "marketing trends",
        "startup advice",
        "remote work practices",
        "sustainable living",
    ]

    # Tones for variety
    TONES = [
        "friendly and casual",
        "professional and informative",
        "enthusiastic and energetic",
        "thoughtful and reflective",
        "humorous and light-hearted",
    ]

    def __init__(self):
        """Initialize AI client with configured provider."""
        self.client = AsyncOpenAI(
            api_key=settings.ai_api_key,
            base_url=settings.ai_base_url,
        )
        self.model = settings.ai_model
        self.provider = settings.ai_provider

    async def generate_email(
        self,
        context: Optional[str] = None,
        is_reply: bool = False,
        previous_content: Optional[str] = None,
    ) -> EmailContent:
        """
        Generate email content using AI.

        Args:
            context: Optional context or theme for the email
            is_reply: Whether this is a reply to another email
            previous_content: Content of email being replied to

        Returns:
            EmailContent with subject and body
        """
        if is_reply and previous_content:
            prompt = self._create_reply_prompt(previous_content)
        else:
            prompt = self._create_initial_prompt(context)

        logger.info(f"Generating email with {self.provider} ({self.model})")

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant that writes natural, "
                            "conversational emails. Keep emails concise (100-250 words), "
                            "friendly, and authentic. Avoid being overly formal or salesy."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,  # Higher temperature for variety
                max_tokens=500,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from AI")

            # Parse subject and body
            subject, body = self._parse_email_content(content)

            logger.info(f"Email generated successfully: {subject[:50]}...")

            return EmailContent(
                subject=subject,
                body=body,
                prompt=prompt,
                model=self.model,
            )

        except Exception as e:
            logger.error(f"Failed to generate email: {e}")
            # Fallback to simple template
            return self._generate_fallback_email(is_reply)

    def _create_initial_prompt(self, context: Optional[str] = None) -> str:
        """Create prompt for initial email."""
        topic = context or random.choice(self.TOPICS)
        tone = random.choice(self.TONES)
        length = random.choice(["short (100-150 words)", "medium (150-200 words)"])

        return (
            f"Write a {tone} email about {topic}. "
            f"The email should be {length}. "
            f"Start with a natural greeting and end with a friendly closing. "
            f"Format: First line should be 'Subject: [subject line]', "
            f"then a blank line, then the email body. "
            f"Make it feel like a real person wrote it, not a marketing email."
        )

    def _create_reply_prompt(self, previous_content: str) -> str:
        """Create prompt for reply email."""
        tone = random.choice(self.TONES)

        return (
            f"Write a {tone} reply to this email:\n\n{previous_content}\n\n"
            f"Keep the reply concise (100-200 words). "
            f"Acknowledge what they said and continue the conversation naturally. "
            f"Format: First line should be 'Subject: Re: [original subject]', "
            f"then a blank line, then the reply body. "
            f"Make it conversational and authentic."
        )

    def _parse_email_content(self, content: str) -> tuple[str, str]:
        """
        Parse AI-generated content into subject and body.

        Args:
            content: Raw AI response

        Returns:
            Tuple of (subject, body)
        """
        lines = content.strip().split("\n")

        # Extract subject line
        subject = "Hello!"
        body_start_idx = 0

        for i, line in enumerate(lines):
            if line.lower().startswith("subject:"):
                subject = line.split(":", 1)[1].strip()
                body_start_idx = i + 1
                break

        # Extract body (skip empty lines after subject)
        body_lines = []
        for line in lines[body_start_idx:]:
            if line.strip() or body_lines:  # Start collecting after first non-empty
                body_lines.append(line)

        body = "\n".join(body_lines).strip()

        # Ensure we have content
        if not body:
            body = content.strip()

        return subject, body

    def _generate_fallback_email(self, is_reply: bool = False) -> EmailContent:
        """Generate simple fallback email if AI fails."""
        if is_reply:
            subject = "Re: Thanks for reaching out"
            body = (
                "Hi,\n\n"
                "Thanks for your email! I appreciate you taking the time to write.\n\n"
                "I'll give this some thought and get back to you soon.\n\n"
                "Best regards"
            )
        else:
            topic = random.choice(self.TOPICS)
            subject = f"Quick thought about {topic}"
            body = (
                f"Hi,\n\n"
                f"Hope you're doing well! I was thinking about {topic} "
                f"and wanted to share a quick thought with you.\n\n"
                f"Would love to hear your perspective on this when you have a moment.\n\n"
                f"Best regards"
            )

        return EmailContent(
            subject=subject,
            body=body,
            prompt="Fallback template",
            model="fallback",
        )

    async def generate_batch(self, count: int, is_reply: bool = False) -> list[EmailContent]:
        """
        Generate multiple emails in batch.

        Args:
            count: Number of emails to generate
            is_reply: Whether these are replies

        Returns:
            List of EmailContent objects
        """
        emails = []
        for _ in range(count):
            email = await self.generate_email(is_reply=is_reply)
            emails.append(email)
        return emails
