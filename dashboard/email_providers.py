"""Email provider configurations for common services."""

EMAIL_PROVIDERS = {
    "gmail.com": {
        "name": "Gmail / Google Workspace",
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "imap_host": "imap.gmail.com",
        "imap_port": 993,
        "imap_use_ssl": True,
        "notes": "Use App Password (not your regular password). Enable 2FA first, then create App Password in Google Account settings."
    },
    "outlook.com": {
        "name": "Outlook.com / Hotmail",
        "smtp_host": "smtp-mail.outlook.com",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "imap_host": "outlook.office365.com",
        "imap_port": 993,
        "imap_use_ssl": True,
        "notes": "Use your regular password or App Password if 2FA is enabled."
    },
    "hotmail.com": {
        "name": "Outlook.com / Hotmail",
        "smtp_host": "smtp-mail.outlook.com",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "imap_host": "outlook.office365.com",
        "imap_port": 993,
        "imap_use_ssl": True,
        "notes": "Use your regular password or App Password if 2FA is enabled."
    },
    "live.com": {
        "name": "Outlook.com / Hotmail",
        "smtp_host": "smtp-mail.outlook.com",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "imap_host": "outlook.office365.com",
        "imap_port": 993,
        "imap_use_ssl": True,
        "notes": "Use your regular password or App Password if 2FA is enabled."
    },
    "yahoo.com": {
        "name": "Yahoo Mail",
        "smtp_host": "smtp.mail.yahoo.com",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "imap_host": "imap.mail.yahoo.com",
        "imap_port": 993,
        "imap_use_ssl": True,
        "notes": "Generate App Password in Yahoo Account Security settings."
    },
    "yahoo.it": {
        "name": "Yahoo Mail",
        "smtp_host": "smtp.mail.yahoo.com",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "imap_host": "imap.mail.yahoo.com",
        "imap_port": 993,
        "imap_use_ssl": True,
        "notes": "Generate App Password in Yahoo Account Security settings."
    },
    "libero.it": {
        "name": "Libero Mail",
        "smtp_host": "smtp.libero.it",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "imap_host": "imapmail.libero.it",
        "imap_port": 993,
        "imap_use_ssl": True,
        "notes": "Use your regular email password."
    },
    "virgilio.it": {
        "name": "Virgilio Mail",
        "smtp_host": "out.virgilio.it",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "imap_host": "in.virgilio.it",
        "imap_port": 993,
        "imap_use_ssl": True,
        "notes": "Use your regular email password."
    },
    "aruba.it": {
        "name": "Aruba PEC / Email",
        "smtp_host": "smtps.aruba.it",
        "smtp_port": 465,
        "smtp_use_tls": False,  # Uses SSL instead
        "imap_host": "imaps.aruba.it",
        "imap_port": 993,
        "imap_use_ssl": True,
        "notes": "Use your email password. For PEC accounts, use PEC-specific servers."
    },
    "pec.it": {
        "name": "Aruba PEC",
        "smtp_host": "smtps.pec.aruba.it",
        "smtp_port": 465,
        "smtp_use_tls": False,
        "imap_host": "imaps.pec.aruba.it",
        "imap_port": 993,
        "imap_use_ssl": True,
        "notes": "Aruba PEC service. Use your PEC password."
    },
    "office365.com": {
        "name": "Microsoft 365 / Office 365",
        "smtp_host": "smtp.office365.com",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "imap_host": "outlook.office365.com",
        "imap_port": 993,
        "imap_use_ssl": True,
        "notes": "For business/enterprise accounts. May require App Password with Modern Auth."
    },
    "icloud.com": {
        "name": "iCloud Mail",
        "smtp_host": "smtp.mail.me.com",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "imap_host": "imap.mail.me.com",
        "imap_port": 993,
        "imap_use_ssl": True,
        "notes": "Generate App-Specific Password in iCloud settings."
    },
    "me.com": {
        "name": "iCloud Mail",
        "smtp_host": "smtp.mail.me.com",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "imap_host": "imap.mail.me.com",
        "imap_port": 993,
        "imap_use_ssl": True,
        "notes": "Generate App-Specific Password in iCloud settings."
    },
    "mac.com": {
        "name": "iCloud Mail",
        "smtp_host": "smtp.mail.me.com",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "imap_host": "imap.mail.me.com",
        "imap_port": 993,
        "imap_use_ssl": True,
        "notes": "Generate App-Specific Password in iCloud settings."
    },
    "fastwebnet.it": {
        "name": "Fastweb Mail",
        "smtp_host": "smtp.fastwebnet.it",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "imap_host": "imap.fastwebnet.it",
        "imap_port": 993,
        "imap_use_ssl": True,
        "notes": "Use your Fastweb email password."
    },
    "tin.it": {
        "name": "TIM Mail (ex Tin.it)",
        "smtp_host": "smtp.tim.it",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "imap_host": "imap.tim.it",
        "imap_port": 993,
        "imap_use_ssl": True,
        "notes": "Use your TIM email password."
    },
    "alice.it": {
        "name": "TIM Mail (ex Alice)",
        "smtp_host": "smtp.tim.it",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "imap_host": "imap.tim.it",
        "imap_port": 993,
        "imap_use_ssl": True,
        "notes": "Use your TIM email password."
    },
    "tiscali.it": {
        "name": "Tiscali Mail",
        "smtp_host": "smtp.tiscali.it",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "imap_host": "imap.tiscali.it",
        "imap_port": 993,
        "imap_use_ssl": True,
        "notes": "Use your Tiscali email password."
    },
    "protonmail.com": {
        "name": "ProtonMail",
        "smtp_host": "127.0.0.1",
        "smtp_port": 1025,
        "smtp_use_tls": True,
        "imap_host": "127.0.0.1",
        "imap_port": 1143,
        "imap_use_ssl": True,
        "notes": "Requires ProtonMail Bridge application running locally. Download from protonmail.com/bridge"
    },
    "zoho.com": {
        "name": "Zoho Mail",
        "smtp_host": "smtp.zoho.com",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "imap_host": "imap.zoho.com",
        "imap_port": 993,
        "imap_use_ssl": True,
        "notes": "Use your Zoho password or App-Specific Password."
    },
    "gmx.com": {
        "name": "GMX Mail",
        "smtp_host": "smtp.gmx.com",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "imap_host": "imap.gmx.com",
        "imap_port": 993,
        "imap_use_ssl": True,
        "notes": "Use your GMX password."
    },
    "mail.com": {
        "name": "Mail.com",
        "smtp_host": "smtp.mail.com",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "imap_host": "imap.mail.com",
        "imap_port": 993,
        "imap_use_ssl": True,
        "notes": "Use your Mail.com password."
    },
    "aol.com": {
        "name": "AOL Mail",
        "smtp_host": "smtp.aol.com",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "imap_host": "imap.aol.com",
        "imap_port": 993,
        "imap_use_ssl": True,
        "notes": "Generate App Password in AOL Account Security."
    }
}


def get_provider_config(email: str) -> dict:
    """
    Get email provider configuration based on email address.

    Args:
        email: Email address to detect provider from

    Returns:
        Dictionary with provider configuration or default values
    """
    if not email or '@' not in email:
        return get_default_config()

    domain = email.split('@')[1].lower()

    # Direct domain match
    if domain in EMAIL_PROVIDERS:
        return EMAIL_PROVIDERS[domain].copy()

    # Check for custom domain with common patterns
    # For custom domains, try to detect if it's a Google Workspace or Microsoft 365
    return get_default_config()


def get_default_config() -> dict:
    """Return default email configuration."""
    return {
        "name": "Custom / Unknown Provider",
        "smtp_host": "smtp.example.com",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "imap_host": "imap.example.com",
        "imap_port": 993,
        "imap_use_ssl": True,
        "notes": "Please enter your email provider's SMTP and IMAP settings manually."
    }


def get_all_providers() -> list:
    """
    Get list of all available providers with their configurations.

    Returns:
        List of tuples: (domain, provider_name)
    """
    providers = []
    seen_names = set()

    for domain, config in EMAIL_PROVIDERS.items():
        name = config["name"]
        if name not in seen_names:
            providers.append((domain, name))
            seen_names.add(name)

    return sorted(providers, key=lambda x: x[1])


def get_provider_by_name(provider_name: str) -> dict:
    """
    Get provider configuration by provider name.

    Args:
        provider_name: Name of the provider (e.g., "Gmail / Google Workspace")

    Returns:
        Dictionary with provider configuration or default
    """
    for domain, config in EMAIL_PROVIDERS.items():
        if config["name"] == provider_name:
            return config.copy()

    return get_default_config()
