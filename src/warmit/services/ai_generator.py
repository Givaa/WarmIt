"""AI content generation for emails using OpenRouter/Groq."""

import logging
import random
from typing import Optional
from openai import AsyncOpenAI
from warmit.config import settings
import asyncio


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

    # Template greetings
    GREETINGS = [
        "Hi there",
        "Hey",
        "Hello",
        "Hi",
        "Good morning",
        "Hope you're doing well",
        "Hope this finds you well",
        "Trust you're having a great day",
    ]

    # Template openings
    OPENINGS = [
        "I've been thinking about {topic}",
        "I came across something interesting about {topic}",
        "I wanted to share a quick thought on {topic}",
        "Recently, I've been exploring {topic}",
        "Something about {topic} caught my attention",
        "I read something fascinating about {topic}",
        "I had an interesting conversation about {topic}",
    ]

    # Template middle sections
    MIDDLES = [
        "and I thought you might find it interesting too.",
        "and I'd love to hear your perspective on it.",
        "and it reminded me of our previous discussions.",
        "and I think it could be relevant to what you're working on.",
        "and I wanted to get your thoughts on this.",
        "and I believe it's worth considering.",
        "and I think it's something worth exploring further.",
    ]

    # Template closings
    CLOSINGS = [
        "Let me know what you think when you have a moment.",
        "Would love to hear your thoughts on this.",
        "Looking forward to your take on this.",
        "Curious to know your opinion.",
        "Feel free to share your thoughts anytime.",
        "Let's catch up about this soon.",
        "Would be great to discuss this further.",
    ]

    # Reply acknowledgments
    REPLY_ACKS = [
        "Thanks for reaching out!",
        "Great to hear from you!",
        "Thanks for your email!",
        "Appreciate you getting in touch.",
        "Thanks for sharing that.",
        "Good to hear from you.",
        "Thanks for the message!",
    ]

    # Reply responses
    REPLY_RESPONSES = [
        "That's a really interesting point.",
        "I completely agree with what you're saying.",
        "That's something I've been thinking about too.",
        "You raise a great question.",
        "I see what you mean.",
        "That's a perspective I hadn't considered.",
        "That resonates with me.",
    ]

    def __init__(self):
        """Initialize AI client with configured provider."""
        self.api_configs = settings.get_all_api_configs()
        self.current_config_index = 0
        self.failed_providers = set()  # Track failed providers

        if not self.api_configs:
            logger.error("No API configurations available!")
            self.client = None
            self.model = None
            self.provider = None
        else:
            config = self.api_configs[0]
            self.client = AsyncOpenAI(
                api_key=config["api_key"],
                base_url=config["base_url"],
            )
            self.model = config["model"]
            self.provider = config["provider"]

    def _switch_to_next_provider(self) -> bool:
        """
        Switch to the next available API provider.
        Returns True if switched successfully, False if no more providers.
        """
        # Mark current provider as failed
        if self.provider:
            self.failed_providers.add(self.provider)

        # Find next available provider
        self.current_config_index += 1

        while self.current_config_index < len(self.api_configs):
            config = self.api_configs[self.current_config_index]

            # Skip if this provider already failed
            if config["provider"] in self.failed_providers:
                self.current_config_index += 1
                continue

            # Switch to this provider
            try:
                self.client = AsyncOpenAI(
                    api_key=config["api_key"],
                    base_url=config["base_url"],
                )
                self.model = config["model"]
                self.provider = config["provider"]
                logger.info(f"Switched to fallback provider: {self.provider}")
                return True
            except Exception as e:
                logger.error(f"Failed to initialize provider {config['provider']}: {e}")
                self.failed_providers.add(config["provider"])
                self.current_config_index += 1

        return False

    async def generate_email(
        self,
        context: Optional[str] = None,
        is_reply: bool = False,
        previous_content: Optional[str] = None,
        sender_name: Optional[str] = None,
    ) -> EmailContent:
        """
        Generate email content using AI.

        Args:
            context: Optional context or theme for the email
            is_reply: Whether this is a reply to another email
            previous_content: Content of email being replied to
            sender_name: Name of the person sending the email

        Returns:
            EmailContent with subject and body
        """
        if is_reply and previous_content:
            prompt = self._create_reply_prompt(previous_content, sender_name)
        else:
            prompt = self._create_initial_prompt(context, sender_name)

        # If no API client available, use local fallback immediately
        if not self.client:
            logger.warning("No API client available, using local fallback")
            return self._generate_fallback_email(is_reply, sender_name)

        max_retries = len(self.api_configs)  # Try all providers
        retry_count = 0

        while retry_count < max_retries:
            logger.info(f"Generating email with {self.provider} ({self.model}) - attempt {retry_count + 1}/{max_retries}")

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
                    timeout=30.0,  # 30 second timeout
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
                logger.error(f"Failed to generate email with {self.provider}: {e}")

                # Try to switch to next provider
                if self._switch_to_next_provider():
                    retry_count += 1
                    await asyncio.sleep(1)  # Brief delay before retry
                    continue
                else:
                    # No more providers available
                    logger.warning("All API providers exhausted, using local fallback")
                    return self._generate_fallback_email(is_reply, sender_name)

        # If we've exhausted retries
        logger.warning("Max retries reached, using local fallback")
        return self._generate_fallback_email(is_reply, sender_name)

    def _create_initial_prompt(self, context: Optional[str] = None, sender_name: Optional[str] = None) -> str:
        """Create prompt for initial email."""
        topic = context or random.choice(self.TOPICS)
        tone = random.choice(self.TONES)
        length = random.choice(["short (100-150 words)", "medium (150-200 words)"])

        signature = f"Sign the email with '{sender_name}' at the end." if sender_name else "End with a generic closing like 'Best regards' or similar."

        return (
            f"Write a {tone} email about {topic}. "
            f"The email should be {length}. "
            f"Start with a natural greeting and end with a friendly closing. "
            f"{signature} "
            f"Format: First line should be 'Subject: [subject line]', "
            f"then a blank line, then the email body. "
            f"Make it feel like a real person wrote it, not a marketing email."
        )

    def _create_reply_prompt(self, previous_content: str, sender_name: Optional[str] = None) -> str:
        """Create prompt for reply email."""
        tone = random.choice(self.TONES)

        signature = f"Sign the reply with '{sender_name}' at the end." if sender_name else "End with a generic closing like 'Best regards' or similar."

        return (
            f"Write a {tone} reply to this email:\n\n{previous_content}\n\n"
            f"Keep the reply concise (100-200 words). "
            f"Acknowledge what they said and continue the conversation naturally. "
            f"{signature} "
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

    def _generate_fallback_email(self, is_reply: bool = False, sender_name: Optional[str] = None) -> EmailContent:
        """Generate randomized conversational email from templates if AI fails."""
        signature = sender_name if sender_name else "Best regards"

        if is_reply:
            # Build reply email from templates
            ack = random.choice(self.REPLY_ACKS)
            response = random.choice(self.REPLY_RESPONSES)
            closing = random.choice(self.CLOSINGS)

            # Random additional content
            extras = [
                "I've been mulling this over and have some thoughts.",
                "This is definitely worth discussing further.",
                "I think we're on the same page about this.",
                "Let me know if you'd like to explore this more.",
                "I'd be happy to share more details if you're interested.",
            ]
            extra = random.choice(extras) if random.random() > 0.5 else ""

            subject = "Re: Thanks for reaching out"
            body = f"{ack}\n\n{response}"
            if extra:
                body += f" {extra}"
            body += f"\n\n{closing}\n\n{signature}"

        else:
            # Build initial email from templates
            greeting = random.choice(self.GREETINGS)
            topic = random.choice(self.TOPICS)
            opening = random.choice(self.OPENINGS).format(topic=topic)
            middle = random.choice(self.MIDDLES)
            closing = random.choice(self.CLOSINGS)

            # Subject variations
            subject_templates = [
                f"Quick thought on {topic}",
                f"Thoughts on {topic}",
                f"Something interesting about {topic}",
                f"Re: {topic}",
                topic.title(),
            ]
            subject = random.choice(subject_templates)

            # Build body with random variation
            body = f"{greeting},\n\n{opening} {middle}\n\n{closing}\n\n{signature}"

        return EmailContent(
            subject=subject,
            body=body,
            prompt="Local fallback template",
            model="local_template",
        )

    async def generate_reply(
        self,
        original_subject: str,
        original_body: str,
        sender_name: Optional[str] = None,
    ) -> tuple[str, str]:
        """
        Generate a reply to an email.

        Args:
            original_subject: Subject of original email
            original_body: Body of original email
            sender_name: Name of person replying

        Returns:
            Tuple of (subject, body)
        """
        previous_content = f"Subject: {original_subject}\n\n{original_body}"
        email_content = await self.generate_email(
            is_reply=True,
            previous_content=previous_content,
            sender_name=sender_name,
        )
        return email_content.subject, email_content.body

    async def generate_batch(self, count: int, is_reply: bool = False, sender_name: Optional[str] = None) -> list[EmailContent]:
        """
        Generate multiple emails in batch.

        Args:
            count: Number of emails to generate
            is_reply: Whether these are replies
            sender_name: Name of the sender

        Returns:
            List of EmailContent objects
        """
        emails = []
        for _ in range(count):
            email = await self.generate_email(is_reply=is_reply, sender_name=sender_name)
            emails.append(email)
        return emails
