"""WarmIt Dashboard - Web UI for monitoring and managing email warming campaigns.

Developed with ❤️ by Givaa
https://github.com/Givaa
"""

import streamlit as st
import requests
import sseclient
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import os
from zoneinfo import ZoneInfo
from typing import Optional
from email_providers import get_provider_config, get_all_providers, get_provider_by_name
from translations import t, get_text, TRANSLATIONS


# Date formatting helpers for consistent European format (DD/MM/YYYY)
ITALY_TZ = ZoneInfo("Europe/Rome")


def format_date(date_str: Optional[str], include_time: bool = False) -> str:
    """Format ISO date string to European format (DD/MM/YYYY).

    Args:
        date_str: ISO format date string (e.g., "2026-01-17T10:30:45+00:00")
        include_time: If True, includes time in format DD/MM/YYYY HH:MM

    Returns:
        Formatted date string or 'N/A' if invalid
    """
    if not date_str:
        return "N/A"
    try:
        # Parse ISO format
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        # Convert to Italy timezone
        dt_italy = dt.astimezone(ITALY_TZ)
        if include_time:
            return dt_italy.strftime("%d/%m/%Y %H:%M")
        return dt_italy.strftime("%d/%m/%Y")
    except (ValueError, AttributeError):
        # Fallback: try to extract just the date part
        try:
            return datetime.strptime(date_str[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
        except:
            return str(date_str)[:10] if date_str else "N/A"


def format_datetime(date_str: Optional[str]) -> str:
    """Format ISO date string to European format with time (DD/MM/YYYY HH:MM)."""
    return format_date(date_str, include_time=True)


# Additional imports (after helper functions)
from auth import (check_auth, get_or_create_password, change_password,
                  create_session_token, save_session, validate_session, delete_session)
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration - Use environment variable for Docker, fallback to localhost for local dev
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Page config
st.set_page_config(
    page_title="WarmIt Dashboard",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize password on first run (before any UI)
password_hash, is_new = get_or_create_password()

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'session_token' not in st.session_state:
    st.session_state.session_token = None

# Try to restore session from query params (persistent across reloads)
query_params = st.query_params

# Initialize language from query params or default to English
if 'language' not in st.session_state:
    lang_param = query_params.get('lang', 'en')
    st.session_state.language = lang_param if lang_param in ['en', 'it'] else 'en'
if not st.session_state.authenticated:
    # Check query params first
    if 'session' in query_params:
        token = query_params['session']
        if validate_session(token):
            st.session_state.authenticated = True
            st.session_state.session_token = token
            logger.info("✅ Session restored from query params")
    # Fallback to session_state token
    elif st.session_state.session_token:
        if validate_session(st.session_state.session_token):
            st.session_state.authenticated = True
            # Add to query params for persistence
            st.query_params['session'] = st.session_state.session_token
            logger.info("✅ Session restored from token")

# Authentication check - show login page if not authenticated
if not st.session_state.authenticated:
    # Hide sidebar completely during login
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 style="text-align: center;">🔥 WarmIt Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.subheader("🔐 Login Required")

        if is_new:
            st.success("✅ First time setup! Admin password generated.")
            st.info("🔑 Check the application logs for your admin password.")

        with st.form("login_form"):
            password_input = st.text_input(
                "Admin Password",
                type="password",
                placeholder="Enter your admin password"
            )

            submit = st.form_submit_button("🔓 Login", use_container_width=True, type="primary")

            if submit:
                if password_input:
                    if check_auth(password_input):
                        # Create and save session token
                        session_token = create_session_token()
                        save_session(session_token)

                        # Update session state and query params
                        st.session_state.authenticated = True
                        st.session_state.session_token = session_token
                        st.query_params['session'] = session_token

                        st.success("✅ Login successful! Session will last 7 days.")

                        # Use JavaScript to force a full page reload (prevents UI stacking)
                        import streamlit.components.v1 as components
                        components.html(
                            """
                            <script>
                            setTimeout(function() {
                                window.parent.location.reload();
                            }, 1000);  // 1 second delay to show success message
                            </script>
                            """,
                            height=0
                        )
                    else:
                        st.error("❌ Incorrect password")
                else:
                    st.error("⚠️ Please enter a password")

        st.markdown("---")
        st.caption("💡 **First time?** Check server logs for generated password")

    st.stop()

# Custom CSS
st.markdown("""
<style>
    /* Hide Streamlit's loading spinner */
    .stSpinner {
        display: none !important;
    }

    /* Hide the swimming person animation at top-left */
    [data-testid="stStatusWidget"] {
        display: none !important;
    }

    /* Prevent transparency/darkening on rerun */
    .stApp {
        transition: none !important;
    }

    /* Force clean page rendering */
    .main .block-container {
        max-width: 100%;
        padding-top: 1rem;
    }

    /* Clear content between reruns */
    .element-container {
        animation: none !important;
    }

    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #FF6B6B 0%, #FFA500 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-active {
        color: #00C853;
        font-weight: bold;
    }
    .status-paused {
        color: #FF9800;
        font-weight: bold;
    }
    .status-error {
        color: #FF5252;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def check_api_health():
    """Check if API is responsive."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def get_system_metrics():
    """Fetch system-wide metrics."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/metrics/system")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def get_accounts():
    """Fetch all accounts."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/accounts")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []


def get_campaigns():
    """Fetch all campaigns."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/campaigns")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []


def get_daily_metrics(days=30):
    """Fetch daily metrics."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/metrics/daily?days={days}")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []


def get_account_metrics(account_id, days=30):
    """Fetch account metrics."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/metrics/accounts/{account_id}?days={days}")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def create_account(data):
    """Create a new account."""
    try:
        response = requests.post(f"{API_BASE_URL}/api/accounts", json=data)
        return response.status_code == 201, response.json() if response.ok else response.text
    except Exception as e:
        return False, str(e)


def create_campaign(data):
    """Create a new campaign."""
    try:
        response = requests.post(f"{API_BASE_URL}/api/campaigns", json=data)
        return response.status_code == 201, response.json() if response.ok else response.text
    except Exception as e:
        return False, str(e)


def update_campaign_status(campaign_id, status):
    """Update campaign status."""
    try:
        response = requests.patch(
            f"{API_BASE_URL}/api/campaigns/{campaign_id}/status",
            json={"status": status}
        )
        return response.ok, response.json() if response.ok else response.text
    except Exception as e:
        return False, str(e)


def update_account_status(account_id, status):
    """Update account status."""
    try:
        response = requests.patch(
            f"{API_BASE_URL}/api/accounts/{account_id}",
            json={"status": status}
        )
        return response.ok, response.json() if response.ok else response.text
    except Exception as e:
        return False, str(e)


def process_campaign(campaign_id):
    """Manually trigger campaign processing."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/campaigns/{campaign_id}/process",
            timeout=60
        )

        # Check if request was successful (2xx status code)
        if response.status_code >= 200 and response.status_code < 300:
            try:
                return True, response.json()
            except:
                return True, {"emails_sent": 0, "message": "Success"}
        else:
            try:
                error_detail = response.json().get('detail', response.text)
            except:
                error_detail = response.text
            return False, error_detail
    except requests.exceptions.Timeout:
        return False, "Operation is taking longer than expected. The emails may still be sending in the background. Please check the campaign status in a few minutes."
    except Exception as e:
        return False, str(e)


def get_campaign_sender_stats(campaign_id):
    """Get detailed sender statistics for a campaign."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/campaigns/{campaign_id}/sender-stats")
        return response.json() if response.ok else None
    except Exception as e:
        st.error(f"Error fetching sender stats: {e}")
        return None


def get_campaign_receiver_stats(campaign_id):
    """Get detailed receiver statistics for a campaign."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/campaigns/{campaign_id}/receiver-stats")
        return response.json() if response.ok else None
    except Exception as e:
        st.error(f"Error fetching receiver stats: {e}")
        return None


def delete_campaign(campaign_id):
    """Delete a campaign."""
    try:
        response = requests.delete(
            f"{API_BASE_URL}/api/campaigns/{campaign_id}"
        )
        return response.status_code == 204, response.text if response.status_code != 204 else "Deleted"
    except Exception as e:
        return False, str(e)


def delete_account(account_id):
    """Delete an account."""
    try:
        response = requests.delete(
            f"{API_BASE_URL}/api/accounts/{account_id}"
        )
        return response.status_code == 204, response.text if response.status_code != 204 else "Deleted"
    except Exception as e:
        return False, str(e)


# Sidebar
with st.sidebar:
    # Header with logo and language selector
    col_logo, col_lang = st.columns([3, 1])
    with col_logo:
        st.markdown("# 🔥 WarmIt")
    with col_lang:
        # Language selector
        lang_options = {"en": "🇬🇧", "it": "🇮🇹"}
        current_lang = st.session_state.language
        selected_lang = st.selectbox(
            "Lang",
            options=list(lang_options.keys()),
            format_func=lambda x: lang_options[x],
            index=list(lang_options.keys()).index(current_lang),
            label_visibility="collapsed",
            key="lang_selector"
        )
        if selected_lang != st.session_state.language:
            st.session_state.language = selected_lang
            st.query_params['lang'] = selected_lang
            st.rerun()

    st.markdown("---")

    # API Health Check
    api_healthy = check_api_health()
    if api_healthy:
        st.success(f"✅ {t('api_connected')}")
    else:
        st.error(f"❌ {t('api_disconnected')}")
        st.warning(t('error_api_connection'))
        st.stop()

    st.markdown("---")

    # Navigation with translated labels
    nav_items = {
        f"📊 {t('nav_dashboard')}": "dashboard",
        f"📧 {t('nav_accounts')}": "accounts",
        f"🎯 {t('nav_campaigns')}": "campaigns",
        f"📈 {t('nav_analytics')}": "analytics",
        f"➕ {t('nav_add_new')}": "add_new",
        f"🧪 {t('nav_quick_test')}": "quick_test",
        f"🧮 {t('nav_estimate')}": "estimate",
        f"💰 {t('nav_api_costs')}": "api_costs",
        f"⚙️ {t('nav_settings')}": "settings",
    }

    page = st.radio(
        "Navigation",
        list(nav_items.keys()),
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Auto-refresh with query param persistence
    if 'auto_refresh' not in st.session_state:
        # Check query params first
        st.session_state.auto_refresh = query_params.get('auto_refresh') == 'true'

    auto_refresh = st.checkbox(
        "Auto-refresh (30s)",
        value=st.session_state.auto_refresh,
        key='auto_refresh_checkbox'
    )

    # Update both session state and query params when checkbox changes
    if auto_refresh != st.session_state.auto_refresh:
        st.session_state.auto_refresh = auto_refresh
        if auto_refresh:
            st.query_params['auto_refresh'] = 'true'
        else:
            st.query_params.pop('auto_refresh', None)

    if auto_refresh:
        st.info("🔄 Auto-refresh enabled (30s)")

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; font-size: 0.8em; color: #666; padding: 10px;'>"
        "Made with ❤️ by <a href='https://github.com/Givaa' target='_blank' style='color: #666; text-decoration: none;'>Givaa</a>"
        "</div>",
        unsafe_allow_html=True
    )

# Track page changes in session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = page

# If page changed, force a clean rerun
if st.session_state.current_page != page:
    st.session_state.current_page = page
    st.rerun()

# Get current page key for comparison (extract from nav_items)
current_page_key = nav_items.get(page, "dashboard")

# Main content
if current_page_key == "dashboard":
    st.markdown(f'<h1 style="text-align: center;">🔥 {t("app_title")}</h1>', unsafe_allow_html=True)

    # Fetch data
    metrics = get_system_metrics()
    accounts = get_accounts()
    campaigns = get_campaigns()

    if not metrics:
        st.error(t("error_load_metrics"))
        st.stop()

    # Top metrics
    col1, col2, col3, col4 = st.columns(4)

    active_label = t("active_accounts").split()[-1] if st.session_state.language == "it" else "active"

    with col1:
        st.metric(
            label=f"📧 {t('total_accounts')}",
            value=metrics.get("total_accounts", 0),
            delta=f"{metrics.get('active_accounts', 0)} {active_label}"
        )

    with col2:
        st.metric(
            label=f"🎯 {t('total_campaigns')}",
            value=metrics.get("total_campaigns", 0),
            delta=f"{metrics.get('active_campaigns', 0)} {active_label}"
        )

    with col3:
        today_label = t("today").lower()
        st.metric(
            label=f"📨 {t('total_emails_sent')}",
            value=f"{metrics.get('total_emails_sent', 0):,}",
            delta=f"{metrics.get('emails_sent_today', 0)} {today_label}"
        )

    with col4:
        avg_open = metrics.get('average_open_rate', 0) * 100
        st.metric(
            label=f"📬 {t('avg_open_rate')}",
            value=f"{avg_open:.1f}%",
            delta=f"Bounce: {metrics.get('average_bounce_rate', 0)*100:.1f}%",
            delta_color="inverse"
        )

    st.markdown("---")

    # Recent activity
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 Active Campaigns")
        active_campaigns = [c for c in campaigns if c.get('status') == 'active']

        if active_campaigns:
            for camp in active_campaigns[:5]:
                progress = camp.get('progress_percentage', 0)
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"**{camp.get('name')}**")
                    st.progress(progress / 100)
                    st.caption(f"Week {camp.get('current_week')}/{camp.get('duration_weeks')} • {camp.get('emails_sent_today')}/{camp.get('target_emails_today')} today")
                with col_b:
                    st.metric("Open", f"{camp.get('open_rate', 0)*100:.0f}%")
        else:
            st.info("No active campaigns")

    with col2:
        st.subheader("📧 Email Accounts")

        if accounts:
            sender_accounts = [a for a in accounts if a.get('type') == 'sender']
            receiver_accounts = [a for a in accounts if a.get('type') == 'receiver']

            tab1, tab2 = st.tabs([f"Senders ({len(sender_accounts)})", f"Receivers ({len(receiver_accounts)})"])

            with tab1:
                for acc in sender_accounts[:5]:
                    status = acc.get('status', 'unknown')
                    status_class = f"status-{status}"
                    st.markdown(f"""
                    **{acc.get('email')}**
                    <span class="{status_class}">{status.upper()}</span> •
                    Sent: {acc.get('total_sent', 0)} •
                    Bounce: {acc.get('bounce_rate', 0)*100:.1f}%
                    """, unsafe_allow_html=True)
                    st.markdown("---")

            with tab2:
                for acc in receiver_accounts[:5]:
                    status = acc.get('status', 'unknown')
                    status_class = f"status-{status}"
                    st.markdown(f"""
                    **{acc.get('email')}**
                    <span class="{status_class}">{status.upper()}</span> •
                    Received: {acc.get('total_received', 0)} •
                    Replied: {acc.get('total_replied', 0)}
                    """, unsafe_allow_html=True)
                    st.markdown("---")
        else:
            st.info("No accounts configured")

    # Charts
    st.markdown("---")
    st.subheader("📈 Email Activity (Last 30 Days)")

    daily_metrics = get_daily_metrics(30)

    if daily_metrics:
        df = pd.DataFrame(daily_metrics)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['emails_sent'],
            name='Sent',
            line=dict(color='#FF6B6B', width=3)
        ))
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['emails_opened'],
            name='Opened',
            line=dict(color='#4CAF50', width=3)
        ))
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['emails_replied'],
            name='Replied',
            line=dict(color='#2196F3', width=3)
        ))

        fig.update_layout(
            height=400,
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(tickformat="%d/%m/%Y")  # European date format
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available yet")


elif current_page_key == "accounts":
    st.title(f"📧 {t('accounts_title')}")

    accounts = get_accounts()

    # Filter options based on language
    type_options = [t('all_statuses'), t('sender'), t('receiver')]
    status_options = [t('all_statuses'), t('status_active'), t('status_paused'), "Disabled"]

    # Filter
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        account_type = st.selectbox(t('account_type'), type_options)
    with col2:
        account_status = st.selectbox(t('status'), status_options)
    with col3:
        st.write("")
        st.write("")
        if st.button(f"🔄 {t('refresh')}", use_container_width=True):
            st.rerun()

    # Filter accounts
    filtered = accounts
    if account_type != type_options[0]:  # Not "All"
        filter_type = "sender" if account_type == t('sender') else "receiver"
        filtered = [a for a in filtered if a.get('type') == filter_type]
    if account_status != status_options[0]:  # Not "All"
        filter_status = "active" if account_status == t('status_active') else "paused" if account_status == t('status_paused') else "disabled"
        filtered = [a for a in filtered if a.get('status') == filter_status]

    st.markdown(f"**{len(filtered)} / {len(accounts)} accounts**")

    # Display accounts
    for acc in filtered:
        acc_type_label = t('sender').upper() if acc.get('type') == 'sender' else t('receiver').upper()
        with st.expander(f"{acc.get('email')} - {acc_type_label}"):
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                st.write(f"**{t('status')}:**", acc.get('status').upper())
                st.write(f"**{t('account_domain')}:**", acc.get('domain', t('na')))
                st.write(f"**{t('account_domain_age')}:**", f"{acc.get('domain_age_days', t('na'))} {t('account_days')}" if acc.get('domain_age_days') else t('na'))
                st.write(f"**{t('account_daily_limit')}:**", acc.get('current_daily_limit'))

            with col2:
                st.write(f"**{t('sent')}:**", acc.get('total_sent', 0))
                st.write(f"**{t('received')}:**", acc.get('total_received', 0))
                st.write(f"**{t('opened')}:**", acc.get('total_opened', 0))
                st.write(f"**{t('replied')}:**", acc.get('total_replied', 0))

            with col3:
                st.metric(t('open_rate'), f"{acc.get('open_rate', 0)*100:.1f}%")
                st.metric(t('reply_rate'), f"{acc.get('reply_rate', 0)*100:.1f}%")
                st.metric("Bounce Rate", f"{acc.get('bounce_rate', 0)*100:.1f}%")

            # Actions
            col1, col2, col3 = st.columns(3)
            with col1:
                if acc.get('status') == 'active':
                    if st.button(f"⏸ Pause", key=f"pause_{acc['id']}"):
                        success, _ = update_account_status(acc['id'], 'paused')
                        if success:
                            st.success("Account paused")
                            time.sleep(1)
                            st.rerun()
                else:
                    if st.button(f"▶️ Resume", key=f"resume_{acc['id']}"):
                        success, _ = update_account_status(acc['id'], 'active')
                        if success:
                            st.success("Account resumed")
                            time.sleep(1)
                            st.rerun()

            with col2:
                if st.button(f"📊 View Metrics", key=f"metrics_{acc['id']}"):
                    st.session_state.selected_account = acc['id']
                    st.rerun()

            with col3:
                if st.button(f"🗑️ Delete", key=f"delete_acc_{acc['id']}", type="secondary"):
                    # Initialize confirmation state
                    if 'confirm_delete_account' not in st.session_state:
                        st.session_state.confirm_delete_account = None
                    st.session_state.confirm_delete_account = acc['id']

            # Show confirmation dialog if delete was clicked
            if st.session_state.get('confirm_delete_account') == acc['id']:
                st.warning(f"⚠️ Are you sure you want to delete account '{acc.get('email')}'?")
                st.caption("This action cannot be undone. All associated data will be lost.")
                conf_col1, conf_col2 = st.columns(2)
                with conf_col1:
                    if st.button("✅ Yes, delete", key=f"confirm_yes_acc_{acc['id']}", type="primary"):
                        success, msg = delete_account(acc['id'])
                        if success:
                            st.success("Account deleted successfully")
                            st.session_state.confirm_delete_account = None
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Failed to delete account: {msg}")
                with conf_col2:
                    if st.button("❌ Cancel", key=f"confirm_no_acc_{acc['id']}"):
                        st.session_state.confirm_delete_account = None
                        st.rerun()


elif current_page_key == "campaigns":
    st.title(f"🎯 {t('campaigns_title')}")

    campaigns = get_campaigns()

    # Filter options
    status_filter_options = {
        t('all_statuses'): None,
        t('status_active'): 'active',
        t('status_paused'): 'paused',
        t('status_completed'): 'completed',
        t('status_pending'): 'pending'
    }

    # Filter
    col1, col2 = st.columns([3, 1])
    with col1:
        campaign_status = st.selectbox(t('status'), list(status_filter_options.keys()))
    with col2:
        st.write("")
        st.write("")
        if st.button(f"🔄 {t('refresh')}", use_container_width=True):
            st.rerun()

    # Filter campaigns
    filtered = campaigns
    filter_value = status_filter_options.get(campaign_status)
    if filter_value:
        filtered = [c for c in filtered if c.get('status') == filter_value]

    st.markdown(f"**{len(filtered)} / {len(campaigns)} {t('total_campaigns').lower()}**")

    # Display campaigns
    for camp in filtered:
        status_label = camp.get('status', '').upper()
        with st.expander(f"{camp.get('name')} - {status_label}"):
            # Progress bar
            progress = camp.get('progress_percentage', 0)
            st.progress(progress / 100)
            st.caption(f"{t('campaign_progress')}: {progress:.0f}% • {t('campaign_week')} {camp.get('current_week')}/{camp.get('duration_weeks')}")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(f"**{t('todays_target')}:**", camp.get('target_emails_today'))
                st.write(f"**{t('sent_today')}:**", camp.get('emails_sent_today'))
                st.write(f"**{t('total_sent')}:**", camp.get('total_emails_sent'))
                st.write(f"**{t('senders')}:**", len(camp.get('sender_account_ids', [])))
                st.write(f"**{t('receivers')}:**", len(camp.get('receiver_account_ids', [])))

            with col2:
                st.metric(t('open_rate'), f"{camp.get('open_rate', 0)*100:.1f}%")
                st.metric(t('reply_rate'), f"{camp.get('reply_rate', 0)*100:.1f}%")
                st.metric(t('bounce_rate'), f"{camp.get('bounce_rate', 0)*100:.1f}%")

            with col3:
                st.write(f"**{t('start_date')}:**", format_date(camp.get('start_date')))
                st.write(f"**{t('end_date')}:**", format_date(camp.get('end_date')) if camp.get('end_date') else t('ongoing'))
                st.write(f"**{t('campaign_duration')}:**", f"{camp.get('duration_weeks')} {t('campaign_weeks')}")
                lang = camp.get('language', 'en')
                lang_display = "🇬🇧 English" if lang == "en" else "🇮🇹 Italiano"
                st.write(f"**{t('campaign_language')}:**", lang_display)

                # Display next send time if available
                if camp.get('next_send_time'):
                    st.write(f"**{t('next_send')}:**", format_datetime(camp.get('next_send_time')))

            st.markdown("---")

            # Sender Statistics Section
            st.subheader(f"📊 {t('sender_stats')}")

            sender_stats_data = get_campaign_sender_stats(camp['id'])

            if sender_stats_data and sender_stats_data.get('sender_stats'):
                sender_stats = sender_stats_data['sender_stats']

                # Create DataFrame for better visualization
                import pandas as pd
                df = pd.DataFrame(sender_stats)

                # Reorder columns for better readability
                column_order = [
                    'sender_email',
                    'domain_age_days',
                    'emails_sent',
                    'emails_opened',
                    'open_rate',
                    'emails_replied',
                    'reply_rate',
                    'emails_bounced',
                    'bounce_rate',
                    'status'
                ]

                # Filter to only existing columns
                available_columns = [col for col in column_order if col in df.columns]
                df_display = df[available_columns].copy()

                # Rename columns for display
                df_display.columns = [
                    'Sender',
                    'Domain Age (days)',
                    'Sent',
                    'Opened',
                    'Open %',
                    'Replied',
                    'Reply %',
                    'Bounced',
                    'Bounce %',
                    'Status'
                ]

                # Format the dataframe
                st.dataframe(
                    df_display,
                    use_container_width=True,
                    hide_index=True
                )

                # Summary metrics in columns
                st.markdown("**Summary:**")
                col_s1, col_s2, col_s3, col_s4 = st.columns(4)

                total_sent = sum(s['emails_sent'] for s in sender_stats)
                total_opened = sum(s['emails_opened'] for s in sender_stats)
                total_replied = sum(s['emails_replied'] for s in sender_stats)
                total_bounced = sum(s['emails_bounced'] for s in sender_stats)

                with col_s1:
                    st.metric("Total Sent", total_sent)
                with col_s2:
                    avg_open = (total_opened / total_sent * 100) if total_sent > 0 else 0
                    st.metric("Avg Open Rate", f"{avg_open:.1f}%")
                with col_s3:
                    avg_reply = (total_replied / total_sent * 100) if total_sent > 0 else 0
                    st.metric("Avg Reply Rate", f"{avg_reply:.1f}%")
                with col_s4:
                    avg_bounce = (total_bounced / total_sent * 100) if total_sent > 0 else 0
                    st.metric("Avg Bounce Rate", f"{avg_bounce:.1f}%")

                # Health warnings
                high_bounce_senders = [s for s in sender_stats if s['bounce_rate'] > 5]
                if high_bounce_senders:
                    st.warning(f"⚠️ {len(high_bounce_senders)} sender(s) have bounce rate > 5%")
                    for sender in high_bounce_senders:
                        st.caption(f"  • {sender['sender_email']}: {sender['bounce_rate']:.1f}% bounce rate")

                low_open_senders = [s for s in sender_stats if s['emails_sent'] > 10 and s['open_rate'] < 10]
                if low_open_senders:
                    st.info(f"ℹ️ {len(low_open_senders)} sender(s) have open rate < 10% (with 10+ emails sent)")
                    for sender in low_open_senders:
                        st.caption(f"  • {sender['sender_email']}: {sender['open_rate']:.1f}% open rate")
            else:
                st.info("No sender statistics available yet. Send some emails first!")

            st.markdown("---")

            # Receiver Statistics Section
            st.subheader("📥 Per-Receiver Statistics")

            receiver_stats_data = get_campaign_receiver_stats(camp['id'])

            if receiver_stats_data and receiver_stats_data.get('receiver_stats'):
                receiver_stats = receiver_stats_data['receiver_stats']

                # Create DataFrame for better visualization
                df_recv = pd.DataFrame(receiver_stats)

                # Reorder columns for better readability
                column_order_recv = [
                    'receiver_email',
                    'emails_received',
                    'emails_opened',
                    'open_rate',
                    'replies_sent',
                    'reply_rate',
                    'emails_bounced',
                    'bounce_rate',
                    'status'
                ]

                # Filter to only existing columns
                available_columns_recv = [col for col in column_order_recv if col in df_recv.columns]
                df_recv_display = df_recv[available_columns_recv].copy()

                # Rename columns for display
                df_recv_display.columns = [
                    'Receiver',
                    'Received',
                    'Opened',
                    'Open %',
                    'Replies Sent',
                    'Reply %',
                    'Bounced',
                    'Bounce %',
                    'Status'
                ]

                # Format the dataframe
                st.dataframe(
                    df_recv_display,
                    use_container_width=True,
                    hide_index=True
                )

                # Summary metrics in columns
                st.markdown("**Summary:**")
                col_r1, col_r2, col_r3, col_r4 = st.columns(4)

                total_received = sum(s['emails_received'] for s in receiver_stats)
                total_opened_recv = sum(s['emails_opened'] for s in receiver_stats)
                total_replies = sum(s['replies_sent'] for s in receiver_stats)
                total_bounced_recv = sum(s['emails_bounced'] for s in receiver_stats)

                with col_r1:
                    st.metric("Total Received", total_received)
                with col_r2:
                    avg_open_recv = (total_opened_recv / total_received * 100) if total_received > 0 else 0
                    st.metric("Avg Open Rate", f"{avg_open_recv:.1f}%")
                with col_r3:
                    avg_reply_recv = (total_replies / total_received * 100) if total_received > 0 else 0
                    st.metric("Avg Reply Rate", f"{avg_reply_recv:.1f}%")
                with col_r4:
                    avg_bounce_recv = (total_bounced_recv / total_received * 100) if total_received > 0 else 0
                    st.metric("Avg Bounce Rate", f"{avg_bounce_recv:.1f}%")

                # Health warnings for receivers
                inactive_receivers = [r for r in receiver_stats if r['status'] != 'active']
                if inactive_receivers:
                    st.warning(f"⚠️ {len(inactive_receivers)} receiver(s) are not active")
                    for recv in inactive_receivers:
                        st.caption(f"  • {recv['receiver_email']}: {recv['status']}")

                low_reply_receivers = [r for r in receiver_stats if r['emails_received'] > 5 and r['reply_rate'] < 50]
                if low_reply_receivers:
                    st.info(f"ℹ️ {len(low_reply_receivers)} receiver(s) have reply rate < 50% (with 5+ emails received)")
                    for recv in low_reply_receivers:
                        st.caption(f"  • {recv['receiver_email']}: {recv['reply_rate']:.1f}% reply rate")
            else:
                st.info("No receiver statistics available yet. Send some emails first!")

            st.markdown("---")

            # Actions
            col1, col2 = st.columns(2)

            with col1:
                if camp.get('status') == 'active':
                    if st.button("⏸ Pause", key=f"pause_c_{camp['id']}"):
                        success, _ = update_campaign_status(camp['id'], 'paused')
                        if success:
                            st.success("Campaign paused")
                            time.sleep(1)
                            st.rerun()
                elif camp.get('status') == 'paused':
                    if st.button("▶️ Resume", key=f"resume_c_{camp['id']}"):
                        success, _ = update_campaign_status(camp['id'], 'active')
                        if success:
                            st.success("Campaign resumed")
                            time.sleep(1)
                            st.rerun()

            with col2:
                if st.button("🗑️ Delete", key=f"delete_c_{camp['id']}", type="secondary"):
                    # Use a confirmation dialog
                    if 'confirm_delete_campaign' not in st.session_state:
                        st.session_state.confirm_delete_campaign = None

                    st.session_state.confirm_delete_campaign = camp['id']

            # Show confirmation dialog if delete was clicked
            if st.session_state.get('confirm_delete_campaign') == camp['id']:
                st.warning(f"⚠️ Are you sure you want to delete campaign '{camp.get('name')}'?")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("✅ Yes, delete", key=f"confirm_yes_{camp['id']}"):
                        success, _ = delete_campaign(camp['id'])
                        if success:
                            st.success("Campaign deleted")
                            st.session_state.confirm_delete_campaign = None
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Failed to delete campaign")
                with col_no:
                    if st.button("❌ Cancel", key=f"confirm_no_{camp['id']}"):
                        st.session_state.confirm_delete_campaign = None
                        st.rerun()


elif current_page_key == "analytics":
    st.title("📈 Analytics & Reports")

    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        days = st.selectbox("Time Range", [7, 14, 30, 60, 90], index=2)

    daily_metrics = get_daily_metrics(days)

    if daily_metrics:
        df = pd.DataFrame(daily_metrics)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        # Email Volume
        st.subheader("📊 Email Volume")
        fig = px.area(
            df,
            x='date',
            y=['emails_sent', 'emails_opened', 'emails_replied'],
            labels={'value': 'Count', 'variable': 'Type'},
            color_discrete_map={
                'emails_sent': '#FF6B6B',
                'emails_opened': '#4CAF50',
                'emails_replied': '#2196F3'
            }
        )
        fig.update_layout(xaxis=dict(tickformat="%d/%m/%Y"))  # European date format
        st.plotly_chart(fig, use_container_width=True)

        # Rates
        st.subheader("📈 Performance Rates")
        df['open_rate_pct'] = df['open_rate'] * 100
        df['reply_rate_pct'] = df['reply_rate'] * 100
        df['bounce_rate_pct'] = df['bounce_rate'] * 100

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['date'], y=df['open_rate_pct'], name='Open Rate', line=dict(color='#4CAF50')))
        fig.add_trace(go.Scatter(x=df['date'], y=df['reply_rate_pct'], name='Reply Rate', line=dict(color='#2196F3')))
        fig.add_trace(go.Scatter(x=df['date'], y=df['bounce_rate_pct'], name='Bounce Rate', line=dict(color='#FF5252')))
        fig.update_layout(
            yaxis_title='Rate (%)',
            hovermode='x unified',
            xaxis=dict(tickformat="%d/%m/%Y")  # European date format
        )
        st.plotly_chart(fig, use_container_width=True)

        # Summary stats
        st.subheader("📊 Summary Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Sent", f"{df['emails_sent'].sum():,.0f}")
        with col2:
            st.metric("Avg Open Rate", f"{df['open_rate'].mean()*100:.1f}%")
        with col3:
            st.metric("Avg Reply Rate", f"{df['reply_rate'].mean()*100:.1f}%")
        with col4:
            st.metric("Avg Bounce Rate", f"{df['bounce_rate'].mean()*100:.1f}%")
    else:
        st.info("No data available for the selected time range")


elif current_page_key == "add_new":
    st.title(f"➕ {t('nav_add_new')}")

    tab1, tab2 = st.tabs([f"📧 {t('add_account')}", f"🎯 {t('create_campaign')}"])

    with tab1:
        st.subheader(t('add_account_title'))

        # Provider selection or auto-detection
        st.markdown(f"##### 📬 {t('account_provider')}")

        # Get list of providers for dropdown
        providers_list = get_all_providers()
        provider_names = [t('auto_detect')] + [name for _, name in providers_list]

        selected_provider_name = st.selectbox(
            t('account_provider'),
            provider_names,
            help=t('auto_detect'),
            label_visibility="collapsed"
        )

        # Initialize session state for form fields if not exists
        if 'form_email' not in st.session_state:
            st.session_state.form_email = ""
        if 'form_config' not in st.session_state:
            st.session_state.form_config = get_provider_config("")

        with st.form("add_account"):
            col1, col2 = st.columns(2)

            with col1:
                email = st.text_input(
                    f"{t('email_address')}*",
                    value=st.session_state.form_email,
                    placeholder="example@gmail.com",
                    key="email_input"
                )
                type_options = [t('sender'), t('receiver')]
                account_type_label = st.selectbox(f"{t('account_type')}*", type_options)
                account_type = "sender" if account_type_label == t('sender') else "receiver"
                password = st.text_input(
                    f"{t('smtp_password')}*",
                    type="password",
                    help=t('smtp_password')
                )

            # Get config based on selection or auto-detect
            if selected_provider_name == t('auto_detect'):
                config = get_provider_config(email)
            else:
                config = get_provider_by_name(selected_provider_name)

            with col2:
                smtp_host = st.text_input(f"{t('smtp_host')}*", value=config.get("smtp_host", "smtp.gmail.com"))
                smtp_port = st.number_input(
                    f"{t('smtp_port')}*",
                    value=config.get("smtp_port", 587),
                    min_value=1,
                    max_value=65535
                )
                imap_host = st.text_input(f"{t('imap_host')}*", value=config.get("imap_host", "imap.gmail.com"))
                imap_port = st.number_input(
                    f"{t('imap_port')}*",
                    value=config.get("imap_port", 993),
                    min_value=1,
                    max_value=65535
                )

            col_a, col_b = st.columns(2)
            with col_a:
                smtp_tls = st.checkbox("Use TLS for SMTP", value=config.get("smtp_use_tls", True))
            with col_b:
                imap_ssl = st.checkbox("Use SSL for IMAP", value=config.get("imap_use_ssl", True))

            # Show provider notes if available
            if config.get("notes"):
                st.info(f"ℹ️ **{config.get('name', 'Provider')} Note:** {config['notes']}")

            submit = st.form_submit_button("➕ Add Account", use_container_width=True, type="primary")

            if submit:
                if not email or not password:
                    st.error("Please fill in all required fields")
                else:
                    data = {
                        "email": email,
                        "type": account_type,
                        "smtp_host": smtp_host,
                        "smtp_port": smtp_port,
                        "smtp_use_tls": smtp_tls,
                        "imap_host": imap_host,
                        "imap_port": imap_port,
                        "imap_use_ssl": imap_ssl,
                        "password": password
                    }

                    with st.spinner("Testing connection and creating account..."):
                        success, result = create_account(data)

                        if success:
                            st.success(f"✅ Account created successfully!")
                            if isinstance(result, dict):
                                # Show account details
                                st.write("**Account Details:**")
                                col_info1, col_info2 = st.columns(2)
                                with col_info1:
                                    st.write(f"📧 Email: `{result.get('email')}`")
                                    st.write(f"🏷️ Type: `{result.get('type')}`")
                                    st.write(f"✅ Status: `{result.get('status')}`")
                                with col_info2:
                                    if result.get('domain'):
                                        st.write(f"🌐 Domain: `{result.get('domain')}`")
                                    if result.get('domain_age_days') is not None:
                                        st.write(f"📅 Domain Age: `{result.get('domain_age_days')} days`")
                                    st.write(f"📊 Daily Limit: `{result.get('current_daily_limit')}`")

                                # Show expandable raw JSON
                                with st.expander("View raw API response"):
                                    st.json(result)

                            st.info("💡 Go to **'📧 Accounts'** page to view all accounts, or add another account below.")
                        else:
                            st.error(f"❌ Failed to create account: {result}")

    with tab2:
        st.subheader("Create Warming Campaign")

        accounts = get_accounts()
        senders = [a for a in accounts if a.get('type') == 'sender']
        receivers = [a for a in accounts if a.get('type') == 'receiver']

        if not senders or not receivers:
            st.warning("You need at least 1 sender and 1 receiver account to create a campaign")
            st.stop()

        with st.form("create_campaign"):
            name = st.text_input("Campaign Name*", placeholder="My First Campaign")

            # Sender accounts (full width to avoid layout issues)
            sender_ids = st.multiselect(
                "Sender Accounts*",
                options=[s['id'] for s in senders],
                format_func=lambda x: next(s['email'] for s in senders if s['id'] == x),
                help="Select one or more sender accounts to warm up"
            )

            # Receiver accounts (full width to avoid layout issues)
            receiver_ids = st.multiselect(
                "Receiver Accounts*",
                options=[r['id'] for r in receivers],
                format_func=lambda x: next(r['email'] for r in receivers if r['id'] == x),
                help="Select one or more receiver accounts"
            )

            # Duration and language in columns
            col_d1, col_d2 = st.columns(2)

            with col_d1:
                duration = st.slider("Duration (weeks)", min_value=2, max_value=12, value=6)

            with col_d2:
                campaign_language = st.selectbox(
                    "Email Language",
                    options=["en", "it"],
                    format_func=lambda x: "🇬🇧 English" if x == "en" else "🇮🇹 Italiano",
                    help="Language for AI-generated email content"
                )

            st.info(f"Campaign will warm up {len(sender_ids)} sender(s) over {duration} weeks using {len(receiver_ids)} receiver(s)")

            submit = st.form_submit_button("🚀 Create Campaign", use_container_width=True, type="primary")

            if submit:
                if not name or not sender_ids or not receiver_ids:
                    st.error("Please fill in all required fields")
                else:
                    data = {
                        "name": name,
                        "sender_account_ids": sender_ids,
                        "receiver_account_ids": receiver_ids,
                        "duration_weeks": duration,
                        "language": campaign_language
                    }

                    with st.spinner("Creating campaign..."):
                        success, result = create_campaign(data)

                        if success:
                            st.success("✅ Campaign created successfully!")
                            if isinstance(result, dict):
                                # Show campaign details
                                st.write("**Campaign Details:**")
                                col_c1, col_c2 = st.columns(2)
                                with col_c1:
                                    st.write(f"📛 Name: `{result.get('name')}`")
                                    st.write(f"✅ Status: `{result.get('status')}`")
                                    st.write(f"📅 Duration: `{result.get('duration_weeks')} weeks`")
                                with col_c2:
                                    st.write(f"📧 Senders: `{len(result.get('sender_account_ids', []))}`")
                                    st.write(f"📬 Receivers: `{len(result.get('receiver_account_ids', []))}`")
                                    st.write(f"📊 Week: `{result.get('current_week')}/{result.get('duration_weeks')}`")
                                    lang = result.get('language', 'en')
                                    lang_display = "🇬🇧 English" if lang == "en" else "🇮🇹 Italiano"
                                    st.write(f"🌐 Language: `{lang_display}`")

                                # Show expandable raw JSON
                                with st.expander("View raw API response"):
                                    st.json(result)

                            st.info("💡 Go to **'🎯 Campaigns'** page to monitor progress, or create another campaign below.")
                        else:
                            st.error(f"❌ Failed to create campaign: {result}")


elif current_page_key == "quick_test":
    st.title(f"🧪 {t('quick_test_title')}")
    st.markdown(t('quick_test_subtitle'))

    accounts = get_accounts()
    senders = [a for a in accounts if a.get('type') == 'sender' and a.get('status') == 'active']
    receivers = [a for a in accounts if a.get('type') == 'receiver' and a.get('status') == 'active']

    if not senders or not receivers:
        st.warning(f"⚠️ {t('no_senders') if not senders else ''} {t('no_receivers') if not receivers else ''}")
        if not senders:
            st.info(f"{t('add_account')} → {t('sender')}")
        if not receivers:
            st.info(f"{t('add_account')} → {t('receiver')}")
        st.stop()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"📤 {t('select_sender')}")
        sender_id = st.selectbox(
            t('sender'),
            options=[s['id'] for s in senders],
            format_func=lambda x: next(s['email'] for s in senders if s['id'] == x),
            label_visibility="collapsed"
        )
        sender = next(s for s in senders if s['id'] == sender_id)

        st.info(f"**Email:** {sender['email']}\n\n**{t('account_domain')}:** {sender.get('domain', t('na'))}\n\n**{t('account_daily_limit')}:** {sender.get('current_daily_limit')}")

    with col2:
        st.subheader(f"📥 {t('select_receiver')}")
        receiver_id = st.selectbox(
            t('receiver'),
            options=[r['id'] for r in receivers],
            format_func=lambda x: next(r['email'] for r in receivers if r['id'] == x),
            label_visibility="collapsed"
        )
        receiver = next(r for r in receivers if r['id'] == receiver_id)

        st.info(f"**Email:** {receiver['email']}\n\n**{t('account_domain')}:** {receiver.get('domain', t('na'))}")

    st.markdown("---")

    # Test options
    col_a, col_b, col_c, col_d = st.columns(4)

    with col_a:
        num_emails = st.number_input(
            t('num_emails'),
            min_value=1,
            max_value=10,
            value=1,
            help=t('num_emails')
        )

    with col_b:
        include_replies = st.checkbox(
            t('include_replies'),
            value=True,
            help=t('include_replies_help')
        )

    with col_c:
        email_language = st.selectbox(
            t('email_language'),
            options=["en", "it"],
            format_func=lambda x: "🇬🇧 English" if x == "en" else "🇮🇹 Italiano",
            help=t('email_language')
        )

    with col_d:
        st.write("")
        st.write("")
        if st.button(f"🚀 {t('send_test_emails')}", type="primary", use_container_width=True):
            # Create placeholders for real-time updates
            status_placeholder = st.empty()
            progress_placeholder = st.empty()
            details_placeholder = st.empty()

            try:
                # Show initial status
                status_placeholder.info("🔄 Connecting to API...")
                progress_placeholder.progress(0)

                # Use SSE streaming endpoint for real-time progress
                import sseclient

                response = requests.post(
                    f"{API_BASE_URL}/api/test/send-emails-stream",
                    json={
                        "sender_id": sender_id,
                        "receiver_id": receiver_id,
                        "count": num_emails,
                        "include_replies": include_replies,
                        "language": email_language
                    },
                    stream=True,
                    timeout=300  # 5 minute timeout
                )

                if response.status_code != 200:
                    status_placeholder.empty()
                    progress_placeholder.empty()
                    st.error(f"❌ Failed to send test emails (HTTP {response.status_code})")
                    with st.expander("🔍 Error Details"):
                        st.code(response.text)
                else:
                    # Process SSE events
                    client = sseclient.SSEClient(response)
                    final_result = None
                    current_progress = 0

                    for event in client.events():
                        if event.data:
                            try:
                                data = json.loads(event.data)
                                event_type = data.get('type')

                                if event_type == 'progress':
                                    step = data.get('step')
                                    msg = data.get('message', '')

                                    if step == 'generating':
                                        status_placeholder.info(f"🤖 {msg}")
                                    elif step == 'sending':
                                        status_placeholder.info(f"📤 {msg}")
                                    elif step == 'generating_reply':
                                        status_placeholder.info(f"🤖 {msg}")
                                    elif step == 'sending_reply':
                                        status_placeholder.info(f"📨 {msg}")

                                elif event_type == 'email_sent':
                                    current_progress = data.get('progress', 0)
                                    progress_placeholder.progress(current_progress / 100)
                                    email_num = data.get('email_num')
                                    status_placeholder.success(f"✅ Email {email_num} sent!")

                                elif event_type == 'reply_sent':
                                    current_progress = data.get('progress', 0)
                                    progress_placeholder.progress(current_progress / 100)
                                    email_num = data.get('email_num')
                                    status_placeholder.success(f"✅ Reply {email_num} sent!")

                                elif event_type == 'email_failed':
                                    current_progress = data.get('progress', 0)
                                    progress_placeholder.progress(current_progress / 100)
                                    email_num = data.get('email_num')
                                    status_placeholder.error(f"❌ Email {email_num} failed!")

                                elif event_type == 'reply_failed':
                                    current_progress = data.get('progress', 0)
                                    progress_placeholder.progress(current_progress / 100)
                                    email_num = data.get('email_num')
                                    status_placeholder.warning(f"⚠️ Reply {email_num} failed!")

                                elif event_type == 'error':
                                    msg = data.get('message', 'Unknown error')
                                    status_placeholder.error(f"❌ Error: {msg}")

                                elif event_type == 'complete':
                                    final_result = data
                                    break

                            except json.JSONDecodeError:
                                pass

                    # Clear progress indicators
                    status_placeholder.empty()
                    progress_placeholder.empty()

                    # Show final results
                    if final_result:
                        emails_sent = final_result.get('emails_sent', 0)
                        replies_sent = final_result.get('replies_sent', 0)

                        success_msg = f"✅ Successfully sent {emails_sent} test email(s)"
                        if include_replies and replies_sent > 0:
                            success_msg += f" and {replies_sent} auto-reply(ies)"
                        success_msg += "!"
                        st.success(success_msg)

                        # Show email details
                        if final_result.get('emails'):
                            with st.expander("📧 Email Details", expanded=True):
                                for i, email_info in enumerate(final_result['emails'], 1):
                                    st.write(f"**Email {i}:**")
                                    st.write(f"- Subject: `{email_info.get('subject')}`")
                                    st.write(f"- From: `{email_info.get('from')}`")
                                    st.write(f"- To: `{email_info.get('to')}`")
                                    st.write(f"- Status: `{email_info.get('status')}`")

                                    if email_info.get('has_reply'):
                                        st.write(f"- ✅ Reply sent: `{email_info.get('reply_subject')}`")
                                    elif include_replies:
                                        st.write(f"- ❌ No reply sent")

                                    if i < len(final_result['emails']):
                                        st.markdown("---")

                        st.info("💡 Check both inboxes to verify email delivery, replies, and content quality.")
                    else:
                        st.warning("⚠️ No response received from server")

            except requests.exceptions.Timeout:
                status_placeholder.empty()
                progress_placeholder.empty()

                st.error("❌ Request timed out after 5 minutes")
                st.warning("This may happen with multiple emails and replies. The emails might still be sending in the background.")
                st.info("💡 Check server logs for details")

            except requests.exceptions.ConnectionError:
                status_placeholder.empty()
                progress_placeholder.empty()

                st.error("❌ Service Error")
                st.warning("Cannot connect to the backend service. Please try again later or contact your administrator.")

            except Exception as e:
                # Clear progress and status
                status_placeholder.empty()
                progress_placeholder.empty()

                st.error(f"❌ Unexpected error: {str(e)}")
                with st.expander("🔍 Error Details"):
                    st.code(str(e))

    st.markdown("---")

    st.subheader("ℹ️ About Quick Test")
    st.markdown("""
    **Quick Test** allows you to:
    - ✅ Verify SMTP/IMAP configurations are working
    - ✅ Test AI-generated email content quality
    - ✅ Check email delivery and inbox placement
    - ✅ Validate sender/receiver interactions
    - ✅ Test automatic replies from receivers (optional)
    - ✅ Test emails in multiple languages (English/Italian)

    **What's NOT counted:**
    - ❌ Campaign metrics (sent, opened, replied, bounced)
    - ❌ Account statistics (total_sent, bounce_rate)
    - ❌ Daily email counters
    - ❌ Analytics charts and reports

    **What IS counted:**
    - ⚠️ **AI API usage** - Each test email uses AI to generate content, consuming API credits
    - ⚠️ With auto-replies enabled, each test uses **2 AI calls** (email + reply)
    - 📊 API calls are tracked in **💰 API Costs** page (rate limits, daily usage)

    **Auto-replies:** When enabled, receivers will automatically reply to test emails after 2 seconds, simulating real email conversations.

    **Language:** Choose between English (🇬🇧) or Italian (🇮🇹) for AI-generated content. Both the initial email and auto-replies will use the selected language.
    """)


elif current_page_key == "estimate":
    st.title("🧮 Campaign Resource Estimator")
    st.markdown("Plan your campaign infrastructure by estimating required resources.")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Campaign Parameters")

        with st.form("estimate_form"):
            col_a, col_b, col_c = st.columns(3)

            with col_a:
                num_senders = st.number_input(
                    "Sender Accounts",
                    min_value=1,
                    max_value=1000,
                    value=10,
                    step=1,
                    help="Number of email accounts to warm up"
                )

            with col_b:
                num_receivers = st.number_input(
                    "Receiver Accounts",
                    min_value=1,
                    max_value=1000,
                    value=10,
                    step=1,
                    help="Number of accounts that will receive and reply"
                )

            with col_c:
                duration_weeks = st.number_input(
                    "Duration (weeks)",
                    min_value=1,
                    max_value=24,
                    value=6,
                    step=1,
                    help="Campaign duration in weeks"
                )

            submit = st.form_submit_button("🔍 Calculate Estimate", use_container_width=True, type="primary")

            if submit:
                # Import estimator
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent.parent))
                from scripts.estimate_resources import ResourceEstimator

                # Calculate estimate
                estimator = ResourceEstimator()
                estimate = estimator.estimate(
                    num_senders=num_senders,
                    num_receivers=num_receivers,
                    duration_weeks=duration_weeks
                )

                # Store in session state
                st.session_state.estimate = estimate

    with col2:
        st.subheader("Quick Presets")

        if st.button("🏠 Small (10 accounts)", use_container_width=True):
            st.session_state.preset_senders = 10
            st.session_state.preset_receivers = 10
            st.session_state.preset_weeks = 6
            st.rerun()

        if st.button("🏢 Medium (50 accounts)", use_container_width=True):
            st.session_state.preset_senders = 50
            st.session_state.preset_receivers = 50
            st.session_state.preset_weeks = 8
            st.rerun()

        if st.button("🏭 Large (200 accounts)", use_container_width=True):
            st.session_state.preset_senders = 200
            st.session_state.preset_receivers = 200
            st.session_state.preset_weeks = 10
            st.rerun()

        if st.button("🌐 Enterprise (500 accounts)", use_container_width=True):
            st.session_state.preset_senders = 500
            st.session_state.preset_receivers = 500
            st.session_state.preset_weeks = 12
            st.rerun()

    # Display results if estimate exists
    if 'estimate' in st.session_state:
        estimate = st.session_state.estimate

        st.markdown("---")
        st.subheader("📊 Estimation Results")

        # Campaign info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Senders", f"{estimate.num_senders:,}")
        with col2:
            st.metric("Receivers", f"{estimate.num_receivers:,}")
        with col3:
            st.metric("Duration", f"{estimate.duration_weeks} weeks")

        st.markdown("---")

        # Email volume
        st.subheader("📧 Email Volume")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Emails", f"{estimate.total_emails:,}")
        with col2:
            st.metric("Avg per Day", f"{estimate.emails_per_day_avg:,}")
        with col3:
            st.metric("Avg per Week", f"{estimate.emails_per_week_avg:,}")
        with col4:
            st.metric("Peak per Day", f"{estimate.peak_emails_per_day:,}")

        st.markdown("---")

        # Resources
        st.subheader("💾 Resource Requirements")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Memory (RAM)**")
            st.metric(
                "Minimum Required",
                f"{estimate.ram_mb:,} MB ({estimate.ram_mb / 1024:.1f} GB)"
            )
            st.metric(
                "Recommended",
                f"{estimate.ram_mb_recommended:,} MB ({estimate.ram_mb_recommended / 1024:.1f} GB)",
                delta="50% overhead"
            )

        with col2:
            st.markdown("**CPU Cores**")
            st.metric(
                "Minimum Required",
                f"{estimate.cpu_cores:.1f} cores"
            )
            st.metric(
                "Recommended",
                f"{estimate.cpu_cores_recommended:.1f} cores",
                delta="50% overhead"
            )

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("**Storage**")
            st.metric(
                "Disk Space",
                f"{estimate.storage_gb:.2f} GB"
            )

        with col4:
            st.markdown("**Configuration**")
            st.metric(
                "Profile",
                estimate.recommended_config.upper()
            )

        st.markdown("---")

        # Infrastructure details
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🗄️ Database")
            st.write(f"**Connections:** {estimate.db_connections}")
            st.write(f"**Pool Size:** {estimate.db_pool_size}")

        with col2:
            st.subheader("⚙️ Workers")
            st.write(f"**Celery Workers:** {estimate.celery_workers}")
            st.write(f"**Concurrency:** {estimate.celery_concurrency}")

        st.markdown("---")

        # API usage
        st.subheader("🔌 API Usage & Costs")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total API Calls", f"{estimate.api_calls_total:,}")
        with col2:
            st.metric("Calls per Day", f"{estimate.api_calls_per_day:,}")
        with col3:
            st.metric("Estimated Cost", f"${estimate.estimated_cost_usd:.2f}", help="Using free tier (OpenRouter/Groq)")

        # Warnings
        if estimate.warnings:
            st.markdown("---")
            st.subheader("⚠️ Warnings & Recommendations")
            for warning in estimate.warnings:
                st.warning(warning)
        else:
            st.success("✅ No warnings - your configuration looks good!")

        # Docker compose suggestion
        st.markdown("---")
        st.subheader("🐳 Docker Compose Configuration")

        docker_config = f"""```yaml
# Suggested resource limits for docker-compose.yml

services:
  api:
    deploy:
      resources:
        limits:
          cpus: '{estimate.cpu_cores_recommended / 4:.2f}'
          memory: {estimate.ram_mb_recommended // 8}M
        reservations:
          cpus: '{estimate.cpu_cores / 4:.2f}'
          memory: {estimate.ram_mb // 8}M

  worker:
    deploy:
      resources:
        limits:
          cpus: '{estimate.cpu_cores_recommended / 2:.2f}'
          memory: {estimate.ram_mb_recommended // 4}M
        reservations:
          cpus: '{estimate.cpu_cores / 2:.2f}'
          memory: {estimate.ram_mb // 4}M

  postgres:
    environment:
      POSTGRES_MAX_CONNECTIONS: {estimate.db_pool_size}
    deploy:
      resources:
        limits:
          memory: {estimate.ram_mb_recommended // 6}M

  redis:
    deploy:
      resources:
        limits:
          memory: 512M
```"""
        st.code(docker_config, language="yaml")

    st.markdown("---")

    # Info section
    st.subheader("ℹ️ About Resource Estimation")
    st.markdown("""
    **How it works:**
    - Calculates email volume based on progressive warming schedule (5 → 80 emails/day)
    - Estimates RAM based on accounts, workers, and services
    - Estimates CPU based on email processing load
    - Calculates storage for emails, accounts, and metrics
    - Determines optimal worker count and database connections
    - Provides docker-compose configuration suggestions

    **Configuration Profiles:**
    - **Small:** 1-10 accounts (development, testing)
    - **Medium:** 10-50 accounts (small business)
    - **Large:** 50-200 accounts (enterprise)
    - **Enterprise:** 200+ accounts (large scale)

    **Notes:**
    - Estimates are conservative and include overhead
    - Actual usage may vary based on email content and patterns
    - Using free API tier (OpenRouter/Groq) keeps costs at $0
    - For paid tiers, adjust cost estimates accordingly
    """)


elif current_page_key == "api_costs":
    st.title(f"💰 {t('api_costs_title')}")
    st.markdown(t('api_costs_subtitle'))

    # Import dependencies
    # In Docker, warmit is at /app/warmit (parent.parent from dashboard/app.py)
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from warmit.services.rate_limit_tracker import get_rate_limit_tracker
        from warmit.services.config_profiles import get_profile_manager

        # Get tracker
        tracker = get_rate_limit_tracker()
        statuses = tracker.get_all_statuses()
    except Exception as e:
        st.error(f"{t('error')}: {e}")
        st.info(t('error_api_connection'))
        st.stop()

    # Overall status
    st.subheader(f"📊 {t('status')}")

    col1, col2, col3 = st.columns(3)

    total_requests_today = sum(info.requests_today for info in statuses.values())
    total_limit_today = sum(info.rpd_limit for info in statuses.values())

    with col1:
        st.metric(
            t('requests_today'),
            f"{total_requests_today:,}",
            help=t('requests_today')
        )

    with col2:
        utilization = (total_requests_today / total_limit_today * 100) if total_limit_today > 0 else 0
        remaining_label = "rimanenti" if st.session_state.language == "it" else "remaining"
        st.metric(
            t('utilization'),
            f"{utilization:.1f}%",
            delta=f"{total_limit_today - total_requests_today:,} {remaining_label}"
        )

    with col3:
        exhausted_count = sum(1 for info in statuses.values() if info.is_exhausted)
        status_color = "🔴" if exhausted_count > 0 else "🟢"
        available_label = t('available_keys').split()[0] if st.session_state.language == "it" else "Available"
        st.metric(
            t('provider'),
            f"{status_color} {len(statuses) - exhausted_count}/{len(statuses)} {available_label}"
        )

    st.markdown("---")

    # Provider details
    st.subheader("🔌 Provider Details")

    for provider_name, info in statuses.items():
        with st.expander(f"{provider_name.upper()} - {info.utilization_rpd():.1f}% used", expanded=True):
            # Status indicator
            if info.is_exhausted:
                st.error("❌ **EXHAUSTED** - Rate limit reached")
            elif info.utilization_rpd() > 90:
                st.warning("⚠️ **CRITICAL** - Near limit")
            elif info.utilization_rpd() > 75:
                st.info("ℹ️ **WARNING** - High usage")
            else:
                st.success("✅ **HEALTHY** - Normal usage")

            # Metrics
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Requests Per Minute (RPM)**")
                rpm_utilization = info.utilization_rpm()
                st.progress(rpm_utilization / 100)
                st.write(f"{info.requests_this_minute} / {info.rpm_limit} ({rpm_utilization:.1f}%)")
                st.caption(f"Resets in {int(info.time_until_rpm_reset())}s")

            with col2:
                st.markdown("**Requests Per Day (RPD)**")
                rpd_utilization = info.utilization_rpd()
                st.progress(rpd_utilization / 100)
                st.write(f"{info.requests_today:,} / {info.rpd_limit:,} ({rpd_utilization:.1f}%)")
                hours_until_reset = info.time_until_rpd_reset() / 3600
                st.caption(f"Resets in {hours_until_reset:.1f}h")

            # Request rate and forecast
            request_rate = tracker.get_request_rate(provider_name)
            saturation_time = tracker.get_saturation_forecast(provider_name)

            col_a, col_b = st.columns(2)

            with col_a:
                st.metric(
                    "Current Rate",
                    f"{request_rate:.1f} req/h",
                    help="Requests per hour in last 60 minutes"
                )

            with col_b:
                if saturation_time:
                    hours_until = (saturation_time - datetime.now()).total_seconds() / 3600
                    st.metric(
                        "Saturation ETA",
                        f"{hours_until:.1f}h",
                        delta="⚠️ Will exhaust today",
                        delta_color="inverse",
                        help="Estimated time until daily limit is reached"
                    )
                else:
                    st.metric(
                        "Saturation ETA",
                        "Not today",
                        delta="✅ Won't exhaust",
                        help="Current rate won't exhaust daily limit"
                    )

            # Actions
            if st.button(f"Reset {provider_name} counters", key=f"reset_{provider_name}"):
                tracker.reset_key(provider_name)
                st.success(f"Reset {provider_name} counters")
                st.rerun()

    st.markdown("---")

    # Configuration recommendations
    st.subheader("💡 Optimization Recommendations")

    # Get current number of accounts
    accounts_data = get_accounts()
    num_senders = len([a for a in accounts_data if a.get('type') == 'sender']) if accounts_data else 10

    # Get recommended profile
    try:
        profile_manager = get_profile_manager()
        recommended_profile = profile_manager.get_recommended_profile(num_senders)
    except Exception as e:
        st.warning(f"Could not load configuration profiles: {e}")
        recommended_profile = None

    if recommended_profile:
        st.info(f"**Recommended Profile:** {recommended_profile.name.upper()}")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**API Limits (Recommended)**")
            st.write(f"- OpenRouter RPM: {recommended_profile.api_limits['openrouter_rpm']}")
            st.write(f"- OpenRouter RPD: {recommended_profile.api_limits['openrouter_rpd']}")
            st.write(f"- Groq RPM: {recommended_profile.api_limits['groq_rpm']}")
            st.write(f"- Groq RPD: {recommended_profile.api_limits['groq_rpd']}")

        with col2:
            st.markdown("**Current Limits**")
            for provider_name, info in statuses.items():
                st.write(f"- {provider_name.title()} RPM: {info.rpm_limit}")
                st.write(f"- {provider_name.title()} RPD: {info.rpd_limit}")

    # Recommendations based on utilization
    high_usage_providers = [name for name, info in statuses.items() if info.utilization_rpd() > 75]

    if high_usage_providers:
        st.warning("**⚠️ High Usage Detected**")
        st.markdown("Consider these actions:")
        st.markdown("- Add more API keys for load distribution")
        st.markdown("- Upgrade to paid tier for higher limits")
        st.markdown("- Reduce email sending rate")
        st.markdown("- Enable local fallback templates")

    exhausted_providers = [name for name, info in statuses.items() if info.is_exhausted]

    if exhausted_providers:
        st.error("**❌ Exhausted Providers**")
        st.markdown(f"Providers exhausted: **{', '.join(exhausted_providers)}**")
        st.markdown("**Immediate actions:**")
        st.markdown("- Wait for daily reset")
        st.markdown("- Switch to alternative provider")
        st.markdown("- Use local template fallback")

    # Show message when everything is OK
    if not recommended_profile and not high_usage_providers and not exhausted_providers:
        st.success("✅ All systems operating normally. No optimization needed at this time.")
    elif not high_usage_providers and not exhausted_providers:
        st.success("✅ No issues detected. Your API usage is within safe limits.")

    st.markdown("---")

    # Rate limit information
    st.subheader("ℹ️ About Rate Limits")

    tab1, tab2, tab3 = st.tabs(["OpenRouter", "Groq", "How It Works"])

    with tab1:
        st.markdown("""
        ### OpenRouter Free Tier

        **Rate Limits:**
        - **20 requests/minute** (RPM)
        - **50 requests/day** (RPD) if you have <$10 in credits
        - **1,000 requests/day** (RPD) if you have ≥$10 in credits

        **Models:**
        - Only models with `:free` suffix (e.g., `meta-llama/llama-3.3-70b-instruct:free`)

        **Tips:**
        - Add multiple API keys for load distribution
        - Purchase $10 in credits to unlock 1,000 RPD
        - Monitor usage closely to avoid exhaustion
        - Use local fallback when limits reached

        **Paid Tier:**
        - No platform-level rate limits
        - Pay per token used
        - Better for production workloads

        [View OpenRouter Pricing →](https://openrouter.ai/pricing)
        """)

    with tab2:
        st.markdown("""
        ### Groq Free Tier

        **Rate Limits:**
        - **Varies by model** (typically 6,000-30,000 tokens/min)
        - **~1,000 requests/day** for most models
        - **500,000 tokens/day** for some models

        **How It Works:**
        - Limits apply at organization level
        - Both RPM and tokens/minute (TPM) limits
        - Both RPD and tokens/day (TPD) limits
        - You hit whichever limit comes first

        **Tips:**
        - Check your specific limits in Groq console
        - Limits vary by model (some have higher limits)
        - Use multiple API keys for redundancy
        - Monitor tokens, not just requests

        **Paid Tier:**
        - Higher limits
        - Better SLA
        - Priority access

        [View Groq Pricing →](https://groq.com/pricing)
        """)

    with tab3:
        st.markdown("""
        ### How WarmIt Handles Rate Limits

        **Automatic Tracking:**
        - Tracks every API request in real-time
        - Monitors RPM and RPD for each provider
        - Calculates utilization percentages
        - Forecasts when limits will be reached

        **Automatic Failover:**
        When a provider hits limits:
        1. Automatically switches to next available provider
        2. Falls back to local template generation if all exhausted
        3. Never fails completely

        **Fallback Chain:**
        ```
        OpenRouter Key 1 → OpenRouter Key 2 → OpenRouter Key 3
        → Groq Key 1 → Groq Key 2 → OpenAI
        → Local Templates (always works)
        ```

        **Smart Throttling:**
        - Respects rate limits automatically
        - Adds delays when approaching limits
        - Distributes load across multiple keys
        - Buffer zone (uses only 80-90% of limit)

        **Monitoring & Alerts:**
        - Real-time dashboard (this page!)
        - Saturation forecasts
        - Warning when >75% utilized
        - Critical alert when >90% utilized
        """)

    st.markdown("---")

    st.caption("💡 **Tip:** Refresh this page to see updated statistics. Auto-refresh is enabled.")


elif current_page_key == "settings":
    st.title(f"⚙️ {t('settings_title')}")

    tab1, tab2 = st.tabs([f"🔐 {t('change_password')}", "ℹ️ About"])

    with tab1:
        st.subheader(t('change_password'))
        st.markdown(t('settings_subtitle'))

        with st.form("change_password_form"):
            current_password = st.text_input(
                f"{t('current_password')}*",
                type="password",
                placeholder=t('current_password')
            )

            col1, col2 = st.columns(2)

            with col1:
                new_password = st.text_input(
                    f"{t('new_password')}*",
                    type="password",
                    placeholder=t('new_password')
                )

            with col2:
                confirm_password = st.text_input(
                    f"{t('confirm_password')}*",
                    type="password",
                    placeholder=t('confirm_password')
                )

            submit = st.form_submit_button(f"🔄 {t('change_password')}", use_container_width=True, type="primary")

            if submit:
                # Validation
                if not current_password or not new_password or not confirm_password:
                    st.error(f"⚠️ {t('error')}")
                elif new_password != confirm_password:
                    st.error(f"❌ {t('password_mismatch')}")
                elif len(new_password) < 8:
                    st.error(f"❌ {t('error')}")
                else:
                    # Attempt password change
                    success, message = change_password(current_password, new_password)

                    if success:
                        st.success(f"✅ {t('password_changed')}")
                        st.info("💡 Please remember your new password. There is no password recovery!")
                    else:
                        st.error(f"❌ {t('wrong_password')}")

        st.markdown("---")
        st.info("""
        **Security Tips:**
        - Use a strong password with a mix of letters, numbers, and special characters
        - Don't reuse passwords from other services
        - Store your password in a secure password manager
        - There is no password recovery - keep your password safe!
        """)

        # Logout button
        st.markdown("---")
        st.subheader("🚪 Logout")
        st.markdown("End your current session. You'll need to login again.")

        col_logout1, col_logout2, col_logout3 = st.columns([1, 1, 1])
        with col_logout2:
            if st.button("🚪 Logout", type="secondary", use_container_width=True):
                # Delete session token
                if st.session_state.session_token:
                    delete_session(st.session_state.session_token)

                # Clear session state and query params
                st.session_state.authenticated = False
                st.session_state.session_token = None
                if 'session' in st.query_params:
                    del st.query_params['session']

                st.success("✅ Logged out successfully")
                time.sleep(1)
                st.rerun()

    with tab2:
        st.subheader("About WarmIt")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **Version:** 0.1.1

            **Description:**
            WarmIt is an email warming platform that helps gradually increase
            your email sending reputation through automated, AI-powered
            conversations between sender and receiver accounts.

            **Features:**
            - 🔥 Progressive email warming
            - 🤖 AI-generated content
            - 📊 Real-time analytics
            - 🎯 Campaign management
            - 🔐 Secure authentication
            """)

        with col2:
            st.markdown("""
            **Tech Stack:**
            - Python 3.11
            - FastAPI
            - PostgreSQL / SQLite
            - Redis & Celery
            - Streamlit
            - Docker

            **Links:**
            - [GitHub Repository](#)
            - [Documentation](#)
            - [Report Issue](#)
            """)

        st.markdown("---")

        # System info
        st.subheader("System Information")

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.metric("API Status", "🟢 Online" if check_api_health() else "🔴 Offline")

        with col_b:
            st.metric("Backend", "Connected" if check_api_health() else "Disconnected")

        with col_c:
            italy_tz = ZoneInfo("Europe/Rome")
            now_italy = datetime.now(italy_tz)
            st.metric("Server Time", now_italy.strftime("%H:%M:%S"))


# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🔥 WarmIt Dashboard v0.2.2")
with col2:
    st.caption("📡 Status: " + ("Online" if check_api_health() else "Offline"))
with col3:
    # Use Rome/Italy timezone for display
    italy_tz = ZoneInfo("Europe/Rome")
    now_italy = datetime.now(italy_tz)
    st.caption("🔄 Last updated: " + now_italy.strftime("%H:%M:%S"))

# Auto-refresh with proper implementation using JavaScript
if auto_refresh:
    import streamlit.components.v1 as components

    # Use JavaScript timer that triggers Streamlit rerun via query param update
    # This approach doesn't block and allows clean page transitions
    components.html(
        f"""
        <script>
        // Wait 30 seconds, then trigger rerun by updating a timestamp param
        setTimeout(function() {{
            const url = new URL(window.parent.location);
            // Update a timestamp to force Streamlit to rerun
            url.searchParams.set('_refresh', Date.now());
            window.parent.location.href = url.toString();
        }}, 30000);
        </script>
        """,
        height=0
    )
