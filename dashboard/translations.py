"""Translations for WarmIt Dashboard.

Supports English (en) and Italian (it).

Developed with ❤️ by Givaa
https://github.com/Givaa
"""

TRANSLATIONS = {
    "en": {
        # General
        "app_title": "WarmIt Dashboard",
        "loading": "Loading...",
        "refresh": "Refresh",
        "save": "Save",
        "cancel": "Cancel",
        "delete": "Delete",
        "edit": "Edit",
        "add": "Add",
        "confirm": "Confirm",
        "success": "Success",
        "error": "Error",
        "warning": "Warning",
        "info": "Info",
        "yes": "Yes",
        "no": "No",
        "na": "N/A",
        "actions": "Actions",
        "status": "Status",
        "details": "Details",
        "back": "Back",
        "next": "Next",
        "close": "Close",

        # Login
        "login_title": "Login",
        "login_subtitle": "Enter your password to access the dashboard",
        "password": "Password",
        "login_button": "Login",
        "login_error": "Incorrect password",
        "logout": "Logout",
        "logout_success": "Logged out successfully",

        # Sidebar
        "sidebar_title": "WarmIt",
        "sidebar_language": "Language",
        "sidebar_auto_refresh": "Auto-refresh (30s)",
        "sidebar_auto_refresh_enabled": "Auto-refresh enabled (30s)",

        # Navigation
        "nav_dashboard": "Dashboard",
        "nav_accounts": "Accounts",
        "nav_campaigns": "Campaigns",
        "nav_analytics": "Analytics",
        "nav_add_new": "Add New",
        "nav_quick_test": "Quick Test",
        "nav_estimate": "Estimate",
        "nav_api_costs": "API Costs",
        "nav_settings": "Settings",

        # Dashboard page
        "dashboard_title": "System Overview",
        "dashboard_subtitle": "Real-time status of your email warming system",
        "total_accounts": "Total Accounts",
        "active_accounts": "Active Accounts",
        "total_campaigns": "Total Campaigns",
        "active_campaigns": "Active Campaigns",
        "emails_sent_today": "Emails Sent Today",
        "total_emails_sent": "Total Emails Sent",
        "total_emails_received": "Total Emails Received",
        "avg_open_rate": "Avg Open Rate",
        "avg_reply_rate": "Avg Reply Rate",
        "avg_bounce_rate": "Avg Bounce Rate",
        "recent_activity": "Recent Activity",
        "system_health": "System Health",
        "api_status": "API Status",
        "api_connected": "Connected",
        "api_disconnected": "Disconnected",

        # Accounts page
        "accounts_title": "Account Management",
        "accounts_subtitle": "Manage your sender and receiver email accounts",
        "senders": "Senders",
        "receivers": "Receivers",
        "sender_accounts": "Sender Accounts",
        "receiver_accounts": "Receiver Accounts",
        "no_senders": "No sender accounts found",
        "no_receivers": "No receiver accounts found",
        "add_account": "Add Account",
        "edit_account": "Edit Account",
        "delete_account": "Delete Account",
        "account_email": "Email",
        "account_name": "Name",
        "account_domain": "Domain",
        "account_domain_age": "Domain Age",
        "account_days": "days",
        "account_daily_limit": "Daily Limit",
        "account_provider": "Provider",
        "test_connection": "Test Connection",
        "connection_success": "Connection successful",
        "connection_failed": "Connection failed",
        "activate": "Activate",
        "pause": "Pause",
        "account_activated": "Account activated",
        "account_paused": "Account paused",

        # Campaigns page
        "campaigns_title": "Campaign Management",
        "campaigns_subtitle": "Create and manage email warming campaigns",
        "create_campaign": "Create Campaign",
        "campaign_name": "Campaign Name",
        "campaign_status": "Status",
        "campaign_progress": "Progress",
        "campaign_week": "Week",
        "campaign_duration": "Duration",
        "campaign_weeks": "weeks",
        "campaign_language": "Language",
        "todays_target": "Today's Target",
        "sent_today": "Sent Today",
        "total_sent": "Total Sent",
        "next_send": "Next Send",
        "start_date": "Start Date",
        "end_date": "End Date",
        "ongoing": "Ongoing",
        "open_rate": "Open Rate",
        "reply_rate": "Reply Rate",
        "bounce_rate": "Bounce Rate",
        "select_senders": "Select Senders",
        "select_receivers": "Select Receivers",
        "sender_stats": "Sender Statistics",
        "receiver_stats": "Receiver Statistics",
        "send_now": "Send Now",
        "pause_campaign": "Pause",
        "resume_campaign": "Resume",
        "complete_campaign": "Complete",
        "delete_campaign": "Delete",
        "campaign_created": "Campaign created successfully",
        "campaign_deleted": "Campaign deleted",
        "filter_by_status": "Filter by status",
        "all_statuses": "All",
        "status_pending": "Pending",
        "status_active": "Active",
        "status_paused": "Paused",
        "status_completed": "Completed",
        "status_failed": "Failed",

        # Quick Test page
        "quick_test_title": "Quick Test",
        "quick_test_subtitle": "Send test emails immediately to verify account configurations and email generation.",
        "select_sender": "Select Sender",
        "select_receiver": "Select Receiver",
        "num_emails": "Number of test emails",
        "include_replies": "Include auto-replies",
        "include_replies_help": "Receivers will automatically reply to test emails",
        "email_language": "Email Language",
        "send_test_emails": "Send Test Email(s)",
        "generating_email": "Generating email",
        "sending_email": "Sending email",
        "generating_reply": "Generating reply for email",
        "sending_reply": "Sending reply for email",
        "email_sent": "Email sent!",
        "reply_sent": "Reply sent!",
        "email_failed": "Email failed!",
        "reply_failed": "Reply failed!",
        "test_success": "Successfully sent {emails} test email(s)",
        "test_success_replies": "and {replies} auto-reply(ies)",
        "check_inboxes": "Check both inboxes to verify email delivery, replies, and content quality.",
        "email_details": "Email Details",
        "about_quick_test": "About Quick Test",
        "quick_test_info": """**Quick Test** allows you to:
- Test AI-generated email content quality
- Verify SMTP configurations
- Test email delivery between accounts
- Test emails in multiple languages (English/Italian)""",
        "quick_test_warning": """**Important Notes:**
- **AI API usage** - Each test email uses AI to generate content, consuming API credits
- With auto-replies enabled, each test uses **2 AI calls** (email + reply)""",
        "quick_test_replies_info": "**Auto-replies:** When enabled, receivers will automatically reply to test emails after 2 seconds, simulating real email conversations.",

        # Estimate page
        "estimate_title": "Resource Estimation",
        "estimate_subtitle": "Estimate resources needed for your warming campaigns",

        # API Costs page
        "api_costs_title": "API Usage & Costs",
        "api_costs_subtitle": "Monitor your AI API usage and rate limits",
        "provider": "Provider",
        "requests_today": "Requests Today",
        "requests_minute": "Requests/Min",
        "daily_limit": "Daily Limit",
        "minute_limit": "Minute Limit",
        "utilization": "Utilization",
        "available_keys": "Available Keys",
        "total_keys": "Total Keys",
        "no_api_keys": "No API keys configured",
        "reset_counters": "Reset Counters",
        "counters_reset": "Counters reset",

        # Analytics page
        "analytics_title": "Analytics",
        "analytics_subtitle": "Detailed statistics and performance metrics",
        "time_range": "Time Range",
        "last_7_days": "Last 7 Days",
        "last_30_days": "Last 30 Days",
        "last_90_days": "Last 90 Days",
        "emails_over_time": "Emails Over Time",
        "performance_metrics": "Performance Metrics",
        "sent": "Sent",
        "received": "Received",
        "opened": "Opened",
        "replied": "Replied",
        "bounced": "Bounced",

        # Settings page
        "settings_title": "Settings",
        "settings_subtitle": "Configure your WarmIt dashboard",
        "change_password": "Change Password",
        "current_password": "Current Password",
        "new_password": "New Password",
        "confirm_password": "Confirm Password",
        "password_changed": "Password changed successfully",
        "password_mismatch": "Passwords do not match",
        "wrong_password": "Current password is incorrect",
        "system_info": "System Information",
        "version": "Version",
        "api_url": "API URL",
        "timezone": "Timezone",

        # Add Account form
        "add_account_title": "Add New Account",
        "account_type": "Account Type",
        "sender": "Sender",
        "receiver": "Receiver",
        "full_name": "Full Name",
        "email_address": "Email Address",
        "smtp_settings": "SMTP Settings",
        "smtp_host": "SMTP Host",
        "smtp_port": "SMTP Port",
        "smtp_password": "SMTP Password",
        "use_tls": "Use TLS",
        "imap_settings": "IMAP Settings",
        "imap_host": "IMAP Host",
        "imap_port": "IMAP Port",
        "auto_detect": "Auto-detect from email provider",
        "manual_config": "Manual configuration",
        "account_added": "Account added successfully",
        "account_updated": "Account updated successfully",
        "account_deleted": "Account deleted",

        # Errors
        "error_api_connection": "Cannot connect to API",
        "error_load_accounts": "Error loading accounts",
        "error_load_campaigns": "Error loading campaigns",
        "error_load_metrics": "Error loading metrics",
        "error_send_email": "Error sending email",
        "error_unknown": "An unknown error occurred",

        # Confirmations
        "confirm_delete_account": "Are you sure you want to delete this account?",
        "confirm_delete_campaign": "Are you sure you want to delete this campaign?",
        "confirm_logout": "Are you sure you want to logout?",

        # Time
        "today": "Today",
        "yesterday": "Yesterday",
        "this_week": "This Week",
        "this_month": "This Month",
        "hours_ago": "{n} hours ago",
        "minutes_ago": "{n} minutes ago",
        "just_now": "Just now",
    },

    "it": {
        # General
        "app_title": "WarmIt Dashboard",
        "loading": "Caricamento...",
        "refresh": "Aggiorna",
        "save": "Salva",
        "cancel": "Annulla",
        "delete": "Elimina",
        "edit": "Modifica",
        "add": "Aggiungi",
        "confirm": "Conferma",
        "success": "Successo",
        "error": "Errore",
        "warning": "Attenzione",
        "info": "Info",
        "yes": "Si",
        "no": "No",
        "na": "N/D",
        "actions": "Azioni",
        "status": "Stato",
        "details": "Dettagli",
        "back": "Indietro",
        "next": "Avanti",
        "close": "Chiudi",

        # Login
        "login_title": "Accedi",
        "login_subtitle": "Inserisci la password per accedere alla dashboard",
        "password": "Password",
        "login_button": "Accedi",
        "login_error": "Password errata",
        "logout": "Esci",
        "logout_success": "Disconnesso con successo",

        # Sidebar
        "sidebar_title": "WarmIt",
        "sidebar_language": "Lingua",
        "sidebar_auto_refresh": "Auto-aggiornamento (30s)",
        "sidebar_auto_refresh_enabled": "Auto-aggiornamento attivo (30s)",

        # Navigation
        "nav_dashboard": "Dashboard",
        "nav_accounts": "Account",
        "nav_campaigns": "Campagne",
        "nav_analytics": "Statistiche",
        "nav_add_new": "Aggiungi",
        "nav_quick_test": "Test Rapido",
        "nav_estimate": "Stima",
        "nav_api_costs": "Costi API",
        "nav_settings": "Impostazioni",

        # Dashboard page
        "dashboard_title": "Panoramica Sistema",
        "dashboard_subtitle": "Stato in tempo reale del sistema di warming email",
        "total_accounts": "Account Totali",
        "active_accounts": "Account Attivi",
        "total_campaigns": "Campagne Totali",
        "active_campaigns": "Campagne Attive",
        "emails_sent_today": "Email Inviate Oggi",
        "total_emails_sent": "Email Totali Inviate",
        "total_emails_received": "Email Totali Ricevute",
        "avg_open_rate": "Tasso Apertura Medio",
        "avg_reply_rate": "Tasso Risposta Medio",
        "avg_bounce_rate": "Tasso Bounce Medio",
        "recent_activity": "Attivita Recente",
        "system_health": "Stato Sistema",
        "api_status": "Stato API",
        "api_connected": "Connesso",
        "api_disconnected": "Disconnesso",

        # Accounts page
        "accounts_title": "Gestione Account",
        "accounts_subtitle": "Gestisci i tuoi account email mittenti e destinatari",
        "senders": "Mittenti",
        "receivers": "Destinatari",
        "sender_accounts": "Account Mittenti",
        "receiver_accounts": "Account Destinatari",
        "no_senders": "Nessun account mittente trovato",
        "no_receivers": "Nessun account destinatario trovato",
        "add_account": "Aggiungi Account",
        "edit_account": "Modifica Account",
        "delete_account": "Elimina Account",
        "account_email": "Email",
        "account_name": "Nome",
        "account_domain": "Dominio",
        "account_domain_age": "Eta Dominio",
        "account_days": "giorni",
        "account_daily_limit": "Limite Giornaliero",
        "account_provider": "Provider",
        "test_connection": "Testa Connessione",
        "connection_success": "Connessione riuscita",
        "connection_failed": "Connessione fallita",
        "activate": "Attiva",
        "pause": "Pausa",
        "account_activated": "Account attivato",
        "account_paused": "Account in pausa",

        # Campaigns page
        "campaigns_title": "Gestione Campagne",
        "campaigns_subtitle": "Crea e gestisci le campagne di warming email",
        "create_campaign": "Crea Campagna",
        "campaign_name": "Nome Campagna",
        "campaign_status": "Stato",
        "campaign_progress": "Progresso",
        "campaign_week": "Settimana",
        "campaign_duration": "Durata",
        "campaign_weeks": "settimane",
        "campaign_language": "Lingua",
        "todays_target": "Obiettivo Oggi",
        "sent_today": "Inviate Oggi",
        "total_sent": "Totale Inviate",
        "next_send": "Prossimo Invio",
        "start_date": "Data Inizio",
        "end_date": "Data Fine",
        "ongoing": "In corso",
        "open_rate": "Tasso Apertura",
        "reply_rate": "Tasso Risposta",
        "bounce_rate": "Tasso Bounce",
        "select_senders": "Seleziona Mittenti",
        "select_receivers": "Seleziona Destinatari",
        "sender_stats": "Statistiche Mittenti",
        "receiver_stats": "Statistiche Destinatari",
        "send_now": "Invia Ora",
        "pause_campaign": "Pausa",
        "resume_campaign": "Riprendi",
        "complete_campaign": "Completa",
        "delete_campaign": "Elimina",
        "campaign_created": "Campagna creata con successo",
        "campaign_deleted": "Campagna eliminata",
        "filter_by_status": "Filtra per stato",
        "all_statuses": "Tutti",
        "status_pending": "In attesa",
        "status_active": "Attiva",
        "status_paused": "In pausa",
        "status_completed": "Completata",
        "status_failed": "Fallita",

        # Quick Test page
        "quick_test_title": "Test Rapido",
        "quick_test_subtitle": "Invia email di test immediatamente per verificare le configurazioni degli account e la generazione email.",
        "select_sender": "Seleziona Mittente",
        "select_receiver": "Seleziona Destinatario",
        "num_emails": "Numero di email di test",
        "include_replies": "Includi risposte automatiche",
        "include_replies_help": "I destinatari risponderanno automaticamente alle email di test",
        "email_language": "Lingua Email",
        "send_test_emails": "Invia Email di Test",
        "generating_email": "Generando email",
        "sending_email": "Inviando email",
        "generating_reply": "Generando risposta per email",
        "sending_reply": "Inviando risposta per email",
        "email_sent": "Email inviata!",
        "reply_sent": "Risposta inviata!",
        "email_failed": "Invio email fallito!",
        "reply_failed": "Invio risposta fallito!",
        "test_success": "Inviate con successo {emails} email di test",
        "test_success_replies": "e {replies} risposte automatiche",
        "check_inboxes": "Controlla entrambe le caselle di posta per verificare la consegna, le risposte e la qualita del contenuto.",
        "email_details": "Dettagli Email",
        "about_quick_test": "Info Test Rapido",
        "quick_test_info": """**Test Rapido** ti permette di:
- Testare la qualita del contenuto email generato dall'IA
- Verificare le configurazioni SMTP
- Testare la consegna email tra account
- Testare email in piu lingue (Inglese/Italiano)""",
        "quick_test_warning": """**Note importanti:**
- **Uso API IA** - Ogni email di test usa l'IA per generare contenuto, consumando crediti API
- Con le risposte automatiche abilitate, ogni test usa **2 chiamate IA** (email + risposta)""",
        "quick_test_replies_info": "**Risposte automatiche:** Quando abilitate, i destinatari risponderanno automaticamente alle email di test dopo 2 secondi, simulando conversazioni email reali.",

        # Estimate page
        "estimate_title": "Stima Risorse",
        "estimate_subtitle": "Stima le risorse necessarie per le tue campagne di warming",

        # API Costs page
        "api_costs_title": "Uso API e Costi",
        "api_costs_subtitle": "Monitora l'utilizzo delle API IA e i limiti di frequenza",
        "provider": "Provider",
        "requests_today": "Richieste Oggi",
        "requests_minute": "Richieste/Min",
        "daily_limit": "Limite Giornaliero",
        "minute_limit": "Limite al Minuto",
        "utilization": "Utilizzo",
        "available_keys": "Chiavi Disponibili",
        "total_keys": "Chiavi Totali",
        "no_api_keys": "Nessuna chiave API configurata",
        "reset_counters": "Resetta Contatori",
        "counters_reset": "Contatori resettati",

        # Analytics page
        "analytics_title": "Statistiche",
        "analytics_subtitle": "Statistiche dettagliate e metriche di performance",
        "time_range": "Periodo",
        "last_7_days": "Ultimi 7 Giorni",
        "last_30_days": "Ultimi 30 Giorni",
        "last_90_days": "Ultimi 90 Giorni",
        "emails_over_time": "Email nel Tempo",
        "performance_metrics": "Metriche di Performance",
        "sent": "Inviate",
        "received": "Ricevute",
        "opened": "Aperte",
        "replied": "Risposte",
        "bounced": "Bounce",

        # Settings page
        "settings_title": "Impostazioni",
        "settings_subtitle": "Configura la tua dashboard WarmIt",
        "change_password": "Cambia Password",
        "current_password": "Password Attuale",
        "new_password": "Nuova Password",
        "confirm_password": "Conferma Password",
        "password_changed": "Password cambiata con successo",
        "password_mismatch": "Le password non corrispondono",
        "wrong_password": "La password attuale non e corretta",
        "system_info": "Informazioni Sistema",
        "version": "Versione",
        "api_url": "URL API",
        "timezone": "Fuso Orario",

        # Add Account form
        "add_account_title": "Aggiungi Nuovo Account",
        "account_type": "Tipo Account",
        "sender": "Mittente",
        "receiver": "Destinatario",
        "full_name": "Nome Completo",
        "email_address": "Indirizzo Email",
        "smtp_settings": "Impostazioni SMTP",
        "smtp_host": "Host SMTP",
        "smtp_port": "Porta SMTP",
        "smtp_password": "Password SMTP",
        "use_tls": "Usa TLS",
        "imap_settings": "Impostazioni IMAP",
        "imap_host": "Host IMAP",
        "imap_port": "Porta IMAP",
        "auto_detect": "Rileva automaticamente dal provider email",
        "manual_config": "Configurazione manuale",
        "account_added": "Account aggiunto con successo",
        "account_updated": "Account aggiornato con successo",
        "account_deleted": "Account eliminato",

        # Errors
        "error_api_connection": "Impossibile connettersi all'API",
        "error_load_accounts": "Errore nel caricamento degli account",
        "error_load_campaigns": "Errore nel caricamento delle campagne",
        "error_load_metrics": "Errore nel caricamento delle metriche",
        "error_send_email": "Errore nell'invio dell'email",
        "error_unknown": "Si e verificato un errore sconosciuto",

        # Confirmations
        "confirm_delete_account": "Sei sicuro di voler eliminare questo account?",
        "confirm_delete_campaign": "Sei sicuro di voler eliminare questa campagna?",
        "confirm_logout": "Sei sicuro di voler uscire?",

        # Time
        "today": "Oggi",
        "yesterday": "Ieri",
        "this_week": "Questa Settimana",
        "this_month": "Questo Mese",
        "hours_ago": "{n} ore fa",
        "minutes_ago": "{n} minuti fa",
        "just_now": "Adesso",
    }
}


def get_text(key: str, lang: str = "en", **kwargs) -> str:
    """Get translated text for a key.

    Args:
        key: Translation key
        lang: Language code ('en' or 'it')
        **kwargs: Format arguments for string interpolation

    Returns:
        Translated string, or the key itself if not found
    """
    text = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return text


def t(key: str, **kwargs) -> str:
    """Shorthand for get_text using current session language.

    Must be called after st.session_state.language is set.

    Args:
        key: Translation key
        **kwargs: Format arguments

    Returns:
        Translated string
    """
    import streamlit as st
    lang = st.session_state.get('language', 'en')
    return get_text(key, lang, **kwargs)
