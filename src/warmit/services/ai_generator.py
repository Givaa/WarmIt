"""AI content generation for emails using OpenRouter/Groq with multi-language support.

Developed with ❤️ by Givaa
https://github.com/Givaa
"""

import logging
import random
from typing import Optional, Literal
from openai import AsyncOpenAI
from warmit.config import settings
from warmit.services.rate_limit_tracker import get_rate_limit_tracker, record_api_request
import asyncio


logger = logging.getLogger(__name__)

Language = Literal["en", "it"]


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
    """AI-powered email content generator with multi-language support."""

    # Email topics - English
    TOPICS_EN = [
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

    # Email topics - Italian
    TOPICS_IT = [
        "novità tecnologiche e innovazioni",
        "consigli di produttività",
        "approfondimenti di settore",
        "strategie di business",
        "crescita personale",
        "salute e benessere",
        "esperienze di viaggio",
        "consigli sui libri",
        "cinema e intrattenimento",
        "cucina e ricette",
        "consigli di fotografia",
        "tendenze di marketing",
        "consigli per startup",
        "pratiche di lavoro da remoto",
        "vita sostenibile",
    ]

    # Tones - English
    TONES_EN = [
        "friendly and casual",
        "professional and informative",
        "enthusiastic and energetic",
        "thoughtful and reflective",
        "humorous and light-hearted",
    ]

    # Tones - Italian
    TONES_IT = [
        "amichevole e informale",
        "professionale e informativo",
        "entusiasta ed energico",
        "riflessivo e ponderato",
        "divertente e leggero",
    ]

    # Template greetings - English
    GREETINGS_EN = [
        "Hi there",
        "Hey",
        "Hello",
        "Hi",
        "Good morning",
        "Hope you're doing well",
        "Hope this finds you well",
        "Trust you're having a great day",
    ]

    # Template greetings - Italian
    GREETINGS_IT = [
        "Ciao",
        "Ehi",
        "Salve",
        "Buongiorno",
        "Spero tu stia bene",
        "Spero che tu stia passando una bella giornata",
    ]

    # Template openings - English
    OPENINGS_EN = [
        "I've been thinking about {topic}",
        "I came across something interesting about {topic}",
        "I wanted to share a quick thought on {topic}",
        "Recently, I've been exploring {topic}",
        "Something about {topic} caught my attention",
        "I read something fascinating about {topic}",
        "I had an interesting conversation about {topic}",
    ]

    # Template openings - Italian
    OPENINGS_IT = [
        "Stavo pensando a {topic}",
        "Ho trovato qualcosa di interessante su {topic}",
        "Volevo condividere un pensiero veloce su {topic}",
        "Recentemente, ho esplorato {topic}",
        "Qualcosa su {topic} ha catturato la mia attenzione",
        "Ho letto qualcosa di affascinante su {topic}",
        "Ho avuto una conversazione interessante su {topic}",
    ]

    # Template middle sections - English
    MIDDLES_EN = [
        "and I thought you might find it interesting too.",
        "and I'd love to hear your perspective on it.",
        "and it reminded me of our previous discussions.",
        "and I think it could be relevant to what you're working on.",
        "and I wanted to get your thoughts on this.",
        "and I believe it's worth considering.",
        "and I think it's something worth exploring further.",
    ]

    # Template middle sections - Italian
    MIDDLES_IT = [
        "e ho pensato che potresti trovarlo interessante anche tu.",
        "e mi piacerebbe sentire la tua opinione al riguardo.",
        "e mi ha ricordato le nostre discussioni precedenti.",
        "e penso potrebbe essere rilevante per quello su cui stai lavorando.",
        "e volevo sapere cosa ne pensi.",
        "e credo valga la pena considerarlo.",
        "e penso sia qualcosa che vale la pena esplorare ulteriormente.",
    ]

    # Template closings - English
    CLOSINGS_EN = [
        "Let me know what you think when you have a moment.",
        "Would love to hear your thoughts on this.",
        "Looking forward to your take on this.",
        "Curious to know your opinion.",
        "Feel free to share your thoughts anytime.",
        "Let's catch up about this soon.",
        "Would be great to discuss this further.",
    ]

    # Template closings - Italian
    CLOSINGS_IT = [
        "Fammi sapere cosa ne pensi quando hai un momento.",
        "Mi piacerebbe sentire la tua opinione su questo.",
        "Non vedo l'ora di sapere cosa ne pensi.",
        "Sono curioso di conoscere la tua opinione.",
        "Sentiti libero di condividere i tuoi pensieri quando vuoi.",
        "Parliamone presto.",
        "Sarebbe bello discuterne più approfonditamente.",
    ]

    # Reply acknowledgments - English
    REPLY_ACKS_EN = [
        "Thanks for reaching out!",
        "Great to hear from you!",
        "Thanks for your email!",
        "Appreciate you getting in touch.",
        "Thanks for sharing that.",
        "Good to hear from you.",
        "Thanks for the message!",
    ]

    # Reply acknowledgments - Italian
    REPLY_ACKS_IT = [
        "Grazie per avermi contattato!",
        "Felice di sentirti!",
        "Grazie per la tua email!",
        "Apprezzo che tu mi abbia contattato.",
        "Grazie per aver condiviso questo.",
        "Bello sentirti.",
        "Grazie per il messaggio!",
    ]

    # Reply responses - English
    REPLY_RESPONSES_EN = [
        "That's a really interesting point.",
        "I completely agree with what you're saying.",
        "That's something I've been thinking about too.",
        "You raise a great question.",
        "I see what you mean.",
        "That's a perspective I hadn't considered.",
        "That resonates with me.",
    ]

    # Reply responses - Italian
    REPLY_RESPONSES_IT = [
        "È un punto davvero interessante.",
        "Sono completamente d'accordo con quello che dici.",
        "È qualcosa a cui stavo pensando anch'io.",
        "Sollevi un'ottima domanda.",
        "Capisco cosa intendi.",
        "È una prospettiva che non avevo considerato.",
        "Questo risuona con me.",
    ]

    def __init__(self):
        """Initialize AI client with configured provider."""
        self.api_configs = settings.get_all_api_configs()
        self.current_config_index = 0
        self.failed_providers = set()  # Track failed providers
        self.rate_tracker = get_rate_limit_tracker()

        if not self.api_configs:
            logger.error("No API configurations available!")
            self.client = None
            self.model = None
            self.provider = None
            self.key_id = None
        else:
            config = self.api_configs[0]
            self.client = AsyncOpenAI(
                api_key=config["api_key"],
                base_url=config["base_url"],
            )
            self.model = config["model"]
            self.provider = config["provider"]
            self.key_id = config["provider"]  # Now provider is already in correct format

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
                self.key_id = config["provider"]  # Now provider is already in correct format
                logger.info(f"Switched to fallback provider: {self.provider} (key: {self.key_id})")
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
        language: Language = "en",
    ) -> EmailContent:
        """
        Generate email content using AI.

        Args:
            context: Optional context or theme for the email
            is_reply: Whether this is a reply to another email
            previous_content: Content of email being replied to
            sender_name: Name of the person sending the email
            language: Language for the email ("en" or "it")

        Returns:
            EmailContent with subject and body
        """
        if is_reply and previous_content:
            prompt = self._create_reply_prompt(previous_content, sender_name, language)
        else:
            prompt = self._create_initial_prompt(context, sender_name, language)

        # If no API client available, use local fallback immediately
        if not self.client:
            logger.warning("No API client available, using local fallback")
            return self._generate_fallback_email(is_reply, sender_name, language)

        max_retries = len(self.api_configs)  # Try all providers
        retry_count = 0

        while retry_count < max_retries:
            logger.info(f"Generating email with {self.provider} ({self.model}) - attempt {retry_count + 1}/{max_retries}")

            try:
                system_prompt_lang = (
                    "You are a helpful assistant that writes natural, conversational emails in Italian. "
                    "Keep emails concise (100-250 words), friendly, and authentic. "
                    "Avoid being overly formal or salesy."
                    if language == "it"
                    else
                    "You are a helpful assistant that writes natural, conversational emails. "
                    "Keep emails concise (100-250 words), friendly, and authentic. "
                    "Avoid being overly formal or salesy."
                )

                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt_lang,
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

                # Record successful API request
                if self.key_id:
                    record_api_request(self.key_id)
                    logger.debug(f"Recorded API request for {self.key_id}")

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
                    return self._generate_fallback_email(is_reply, sender_name, language)

        # If we've exhausted retries
        logger.warning("Max retries reached, using local fallback")
        return self._generate_fallback_email(is_reply, sender_name, language)

    def _create_initial_prompt(self, context: Optional[str] = None, sender_name: Optional[str] = None, language: Language = "en") -> str:
        """Create prompt for initial email."""
        topics = self.TOPICS_IT if language == "it" else self.TOPICS_EN
        tones = self.TONES_IT if language == "it" else self.TONES_EN

        topic = context or random.choice(topics)
        tone = random.choice(tones)
        length = random.choice(["short (100-150 words)", "medium (150-200 words)"])

        if language == "it":
            signature = f"Firma l'email con '{sender_name}' alla fine." if sender_name else "Termina con un saluto generico come 'Cordiali saluti' o simile."
            return (
                f"Scrivi un'email {tone} su {topic}. "
                f"L'email dovrebbe essere {length}. "
                f"Inizia con un saluto naturale e termina con una chiusura amichevole. "
                f"{signature} "
                f"Formato: La prima riga deve essere 'Oggetto: [oggetto email]', "
                f"poi una riga vuota, poi il corpo dell'email. "
                f"Fai in modo che sembri scritta da una persona reale, non un'email di marketing."
            )
        else:
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

    def _create_reply_prompt(self, previous_content: str, sender_name: Optional[str] = None, language: Language = "en") -> str:
        """Create prompt for reply email."""
        tones = self.TONES_IT if language == "it" else self.TONES_EN
        tone = random.choice(tones)

        if language == "it":
            signature = f"Firma la risposta con '{sender_name}' alla fine." if sender_name else "Termina con un saluto generico come 'Cordiali saluti' o simile."
            return (
                f"Scrivi una risposta {tone} a questa email:\n\n{previous_content}\n\n"
                f"Mantieni la risposta concisa (100-200 parole). "
                f"Riconosci quello che hanno detto e continua la conversazione in modo naturale. "
                f"{signature} "
                f"Formato: La prima riga deve essere 'Oggetto: Re: [oggetto originale]', "
                f"poi una riga vuota, poi il corpo della risposta. "
                f"Rendila conversazionale e autentica."
            )
        else:
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
            if line.lower().startswith("subject:") or line.lower().startswith("oggetto:"):
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

    def _generate_fallback_email(self, is_reply: bool = False, sender_name: Optional[str] = None, language: Language = "en") -> EmailContent:
        """Generate randomized conversational email from templates if AI fails."""
        signature = sender_name if sender_name else ("Cordiali saluti" if language == "it" else "Best regards")

        if is_reply:
            # Build reply email from templates
            acks = self.REPLY_ACKS_IT if language == "it" else self.REPLY_ACKS_EN
            responses = self.REPLY_RESPONSES_IT if language == "it" else self.REPLY_RESPONSES_EN
            closings = self.CLOSINGS_IT if language == "it" else self.CLOSINGS_EN

            ack = random.choice(acks)
            response = random.choice(responses)
            closing = random.choice(closings)

            # Random additional content
            extras = (
                [
                    "Ci ho riflettuto e ho alcuni pensieri.",
                    "Vale sicuramente la pena discuterne ulteriormente.",
                    "Penso che siamo sulla stessa lunghezza d'onda su questo.",
                    "Fammi sapere se vuoi approfondire questo argomento.",
                    "Sarei felice di condividere più dettagli se sei interessato.",
                ] if language == "it" else
                [
                    "I've been mulling this over and have some thoughts.",
                    "This is definitely worth discussing further.",
                    "I think we're on the same page about this.",
                    "Let me know if you'd like to explore this more.",
                    "I'd be happy to share more details if you're interested.",
                ]
            )
            extra = random.choice(extras) if random.random() > 0.5 else ""

            subject = "Re: Grazie per il contatto" if language == "it" else "Re: Thanks for reaching out"
            body = f"{ack}\n\n{response}"
            if extra:
                body += f" {extra}"
            body += f"\n\n{closing}\n\n{signature}"

        else:
            # Build initial email from templates
            greetings = self.GREETINGS_IT if language == "it" else self.GREETINGS_EN
            topics = self.TOPICS_IT if language == "it" else self.TOPICS_EN
            openings = self.OPENINGS_IT if language == "it" else self.OPENINGS_EN
            middles = self.MIDDLES_IT if language == "it" else self.MIDDLES_EN
            closings = self.CLOSINGS_IT if language == "it" else self.CLOSINGS_EN

            greeting = random.choice(greetings)
            topic = random.choice(topics)
            opening = random.choice(openings).format(topic=topic)
            middle = random.choice(middles)
            closing = random.choice(closings)

            # Subject variations
            subject_templates = (
                [
                    f"Pensiero veloce su {topic}",
                    f"Riflessioni su {topic}",
                    f"Qualcosa di interessante su {topic}",
                    f"Re: {topic}",
                    topic.title(),
                ] if language == "it" else
                [
                    f"Quick thought on {topic}",
                    f"Thoughts on {topic}",
                    f"Something interesting about {topic}",
                    f"Re: {topic}",
                    topic.title(),
                ]
            )
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
        language: Language = "en",
    ) -> tuple[str, str]:
        """
        Generate a reply to an email.

        Args:
            original_subject: Subject of original email
            original_body: Body of original email
            sender_name: Name of person replying
            language: Language for the reply ("en" or "it")

        Returns:
            Tuple of (subject, body)
        """
        subject_prefix = "Oggetto:" if language == "it" else "Subject:"
        previous_content = f"{subject_prefix} {original_subject}\n\n{original_body}"
        email_content = await self.generate_email(
            is_reply=True,
            previous_content=previous_content,
            sender_name=sender_name,
            language=language,
        )
        return email_content.subject, email_content.body

    async def generate_batch(
        self,
        count: int,
        is_reply: bool = False,
        sender_name: Optional[str] = None,
        language: Language = "en",
    ) -> list[EmailContent]:
        """
        Generate multiple emails in batch.

        Args:
            count: Number of emails to generate
            is_reply: Whether these are replies
            sender_name: Name of the sender
            language: Language for the emails ("en" or "it")

        Returns:
            List of EmailContent objects
        """
        emails = []
        for _ in range(count):
            email = await self.generate_email(is_reply=is_reply, sender_name=sender_name, language=language)
            emails.append(email)
        return emails
