"""WarmIt Dashboard - Web UI for monitoring and managing email warming campaigns."""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import os
from zoneinfo import ZoneInfo
from email_providers import get_provider_config, get_all_providers, get_provider_by_name
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
            st.warning("⚠️ The password is also saved in `dashboard/first_run_password.txt` and will be deleted after first login.")

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
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Incorrect password")
                else:
                    st.error("⚠️ Please enter a password")

        st.markdown("---")
        st.caption("💡 **First time?** Check logs for generated password")
        st.caption("📁 Logs location: `docker/logs/dashboard.log` or console output")

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
            timeout=60  # 60 second timeout for processing
        )
        return response.ok, response.json() if response.ok else response.text
    except requests.exceptions.Timeout:
        return False, "Request timed out. Check API logs for campaign status."
    except Exception as e:
        return False, str(e)


# Sidebar
with st.sidebar:
    st.markdown("# 🔥 WarmIt")
    st.markdown("---")

    # API Health Check
    api_healthy = check_api_health()
    if api_healthy:
        st.success("✅ API Online")
    else:
        st.error("❌ API Offline")
        st.warning("Make sure the API server is running on http://localhost:8000")
        st.stop()

    st.markdown("---")

    # Navigation (only shown when authenticated)
    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "📧 Accounts", "🎯 Campaigns", "📈 Analytics", "➕ Add New", "🧪 Quick Test", "🧮 Estimate", "💰 API Costs", "⚙️ Settings"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Auto-refresh
    auto_refresh = st.checkbox("Auto-refresh (30s)", value=True)
    if auto_refresh:
        st.info("Dashboard refreshes every 30 seconds")

# Force clean page rendering by clearing DOM
st.markdown(f"""
<script>
// Force clean render on page change - key by page name
window.currentPage = '{page}';
if (window.lastPage !== window.currentPage) {{
    console.log('Page changed from', window.lastPage, 'to', window.currentPage);
    window.lastPage = window.currentPage;
}}
</script>
<style>
/* Hide all page content by default, show only current */
.main .block-container > div {{
    display: none !important;
}}
.main .block-container > div:last-child {{
    display: block !important;
}}
</style>
""", unsafe_allow_html=True)

# Main content
if page == "📊 Dashboard":
    st.markdown('<h1 style="text-align: center;">🔥 WarmIt Dashboard</h1>', unsafe_allow_html=True)

    # Fetch data
    metrics = get_system_metrics()
    accounts = get_accounts()
    campaigns = get_campaigns()

    if not metrics:
        st.error("Unable to fetch metrics from API")
        st.stop()

    # Top metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📧 Total Accounts",
            value=metrics.get("total_accounts", 0),
            delta=f"{metrics.get('active_accounts', 0)} active"
        )

    with col2:
        st.metric(
            label="🎯 Campaigns",
            value=metrics.get("total_campaigns", 0),
            delta=f"{metrics.get('active_campaigns', 0)} active"
        )

    with col3:
        st.metric(
            label="📨 Emails Sent",
            value=f"{metrics.get('total_emails_sent', 0):,}",
            delta=f"{metrics.get('emails_sent_today', 0)} today"
        )

    with col4:
        avg_open = metrics.get('average_open_rate', 0) * 100
        st.metric(
            label="📬 Avg Open Rate",
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
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available yet")


elif page == "📧 Accounts":
    st.title("📧 Email Accounts")

    accounts = get_accounts()

    # Filter
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        account_type = st.selectbox("Type", ["All", "Sender", "Receiver"])
    with col2:
        account_status = st.selectbox("Status", ["All", "Active", "Paused", "Disabled"])
    with col3:
        st.write("")
        st.write("")
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    # Filter accounts
    filtered = accounts
    if account_type != "All":
        filtered = [a for a in filtered if a.get('type') == account_type.lower()]
    if account_status != "All":
        filtered = [a for a in filtered if a.get('status') == account_status.lower()]

    st.markdown(f"**Showing {len(filtered)} of {len(accounts)} accounts**")

    # Display accounts
    for acc in filtered:
        with st.expander(f"{acc.get('email')} - {acc.get('type').upper()}"):
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                st.write("**Status:**", acc.get('status').upper())
                st.write("**Domain:**", acc.get('domain', 'Unknown'))
                st.write("**Domain Age:**", f"{acc.get('domain_age_days', 'Unknown')} days" if acc.get('domain_age_days') else "Unknown")
                st.write("**Daily Limit:**", acc.get('current_daily_limit'))

            with col2:
                st.write("**Sent:**", acc.get('total_sent', 0))
                st.write("**Received:**", acc.get('total_received', 0))
                st.write("**Opened:**", acc.get('total_opened', 0))
                st.write("**Replied:**", acc.get('total_replied', 0))

            with col3:
                st.metric("Open Rate", f"{acc.get('open_rate', 0)*100:.1f}%")
                st.metric("Reply Rate", f"{acc.get('reply_rate', 0)*100:.1f}%")
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


elif page == "🎯 Campaigns":
    st.title("🎯 Warming Campaigns")

    campaigns = get_campaigns()

    # Filter
    col1, col2 = st.columns([3, 1])
    with col1:
        campaign_status = st.selectbox("Status", ["All", "Active", "Paused", "Completed", "Pending"])
    with col2:
        st.write("")
        st.write("")
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    # Filter campaigns
    filtered = campaigns
    if campaign_status != "All":
        filtered = [c for c in filtered if c.get('status') == campaign_status.lower()]

    st.markdown(f"**Showing {len(filtered)} of {len(campaigns)} campaigns**")

    # Display campaigns
    for camp in filtered:
        with st.expander(f"{camp.get('name')} - {camp.get('status').upper()}"):
            # Progress bar
            progress = camp.get('progress_percentage', 0)
            st.progress(progress / 100)
            st.caption(f"Progress: {progress:.0f}% • Week {camp.get('current_week')}/{camp.get('duration_weeks')}")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.write("**Today's Target:**", camp.get('target_emails_today'))
                st.write("**Sent Today:**", camp.get('emails_sent_today'))
                st.write("**Total Sent:**", camp.get('total_emails_sent'))
                st.write("**Senders:**", len(camp.get('sender_account_ids', [])))
                st.write("**Receivers:**", len(camp.get('receiver_account_ids', [])))

            with col2:
                st.metric("Open Rate", f"{camp.get('open_rate', 0)*100:.1f}%")
                st.metric("Reply Rate", f"{camp.get('reply_rate', 0)*100:.1f}%")
                st.metric("Bounce Rate", f"{camp.get('bounce_rate', 0)*100:.1f}%")

            with col3:
                st.write("**Start Date:**", camp.get('start_date', 'N/A')[:10] if camp.get('start_date') else 'N/A')
                st.write("**End Date:**", camp.get('end_date', 'N/A')[:10] if camp.get('end_date') else 'Ongoing')
                st.write("**Duration:**", f"{camp.get('duration_weeks')} weeks")

            # Actions
            col1, col2, col3, col4 = st.columns(4)

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
                if st.button("🚀 Send Now", key=f"process_c_{camp['id']}"):
                    with st.spinner("Processing..."):
                        success, result = process_campaign(camp['id'])
                        if success:
                            st.success(f"Sent {result.get('emails_sent', 0)} emails")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Failed: {result}")


elif page == "📈 Analytics":
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
        fig.update_layout(yaxis_title='Rate (%)', hovermode='x unified')
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


elif page == "➕ Add New":
    st.title("➕ Add New")

    tab1, tab2 = st.tabs(["📧 Add Account", "🎯 Create Campaign"])

    with tab1:
        st.subheader("Add Email Account")

        # Provider selection or auto-detection
        st.markdown("##### 📬 Provider Configuration")

        # Get list of providers for dropdown
        providers_list = get_all_providers()
        provider_names = ["Auto-detect from email"] + [name for _, name in providers_list]

        selected_provider_name = st.selectbox(
            "Email Provider",
            provider_names,
            help="Select your email provider or choose 'Auto-detect' to auto-fill based on email address"
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
                    "Email Address*",
                    value=st.session_state.form_email,
                    placeholder="example@gmail.com",
                    key="email_input"
                )
                account_type = st.selectbox("Account Type*", ["sender", "receiver"])
                password = st.text_input(
                    "Password*",
                    type="password",
                    help="Use App Password for providers that require it (Gmail, Yahoo, etc.)"
                )

            # Get config based on selection or auto-detect
            if selected_provider_name == "Auto-detect from email":
                config = get_provider_config(email)
            else:
                config = get_provider_by_name(selected_provider_name)

            with col2:
                smtp_host = st.text_input("SMTP Host*", value=config.get("smtp_host", "smtp.gmail.com"))
                smtp_port = st.number_input(
                    "SMTP Port*",
                    value=config.get("smtp_port", 587),
                    min_value=1,
                    max_value=65535
                )
                imap_host = st.text_input("IMAP Host*", value=config.get("imap_host", "imap.gmail.com"))
                imap_port = st.number_input(
                    "IMAP Port*",
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

            col1, col2 = st.columns(2)

            with col1:
                sender_ids = st.multiselect(
                    "Sender Accounts*",
                    options=[s['id'] for s in senders],
                    format_func=lambda x: next(s['email'] for s in senders if s['id'] == x)
                )

            with col2:
                receiver_ids = st.multiselect(
                    "Receiver Accounts*",
                    options=[r['id'] for r in receivers],
                    format_func=lambda x: next(r['email'] for r in receivers if r['id'] == x)
                )

            duration = st.slider("Duration (weeks)", min_value=2, max_value=12, value=6)

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
                        "duration_weeks": duration
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

                                # Show expandable raw JSON
                                with st.expander("View raw API response"):
                                    st.json(result)

                            st.info("💡 Go to **'🎯 Campaigns'** page to monitor progress, or create another campaign below.")
                        else:
                            st.error(f"❌ Failed to create campaign: {result}")


elif page == "🧪 Quick Test":
    st.title("🧪 Quick Email Test")
    st.markdown("Send test emails immediately to verify account configurations and email generation.")

    accounts = get_accounts()
    senders = [a for a in accounts if a.get('type') == 'sender' and a.get('status') == 'active']
    receivers = [a for a in accounts if a.get('type') == 'receiver' and a.get('status') == 'active']

    if not senders or not receivers:
        st.warning("⚠️ You need at least 1 active sender and 1 active receiver to run tests.")
        if not senders:
            st.info("Add a sender account in **'➕ Add New'** → **'📧 Add Account'**")
        if not receivers:
            st.info("Add a receiver account in **'➕ Add New'** → **'📧 Add Account'**")
        st.stop()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📤 Select Sender")
        sender_id = st.selectbox(
            "Sender Account",
            options=[s['id'] for s in senders],
            format_func=lambda x: next(s['email'] for s in senders if s['id'] == x)
        )
        sender = next(s for s in senders if s['id'] == sender_id)

        st.info(f"**Email:** {sender['email']}\n\n**Domain:** {sender.get('domain', 'N/A')}\n\n**Daily Limit:** {sender.get('current_daily_limit')}")

    with col2:
        st.subheader("📥 Select Receiver")
        receiver_id = st.selectbox(
            "Receiver Account",
            options=[r['id'] for r in receivers],
            format_func=lambda x: next(r['email'] for r in receivers if r['id'] == x)
        )
        receiver = next(r for r in receivers if r['id'] == receiver_id)

        st.info(f"**Email:** {receiver['email']}\n\n**Domain:** {receiver.get('domain', 'N/A')}")

    st.markdown("---")

    # Test options
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        num_emails = st.number_input(
            "Number of test emails",
            min_value=1,
            max_value=10,
            value=1,
            help="Send multiple test emails in sequence"
        )

    with col_b:
        include_replies = st.checkbox(
            "Auto-reply from receiver",
            value=True,
            help="Receivers will automatically reply to test emails"
        )

    with col_c:
        st.write("")
        st.write("")
        if st.button("🚀 Send Test Email(s)", type="primary", use_container_width=True):
            spinner_text = f"Sending {num_emails} test email(s)"
            if include_replies:
                spinner_text += " with auto-replies"
            spinner_text += "..."

            with st.spinner(spinner_text):
                # Call API endpoint to send test emails
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/api/test/send-emails",
                        json={
                            "sender_id": sender_id,
                            "receiver_id": receiver_id,
                            "count": num_emails,
                            "include_replies": include_replies
                        },
                        timeout=120  # 2 minute timeout for test emails with replies
                    )

                    if response.status_code == 200:
                        result = response.json()
                        emails_sent = result.get('emails_sent', 0)
                        replies_sent = result.get('replies_sent', 0)

                        success_msg = f"✅ Successfully sent {emails_sent} test email(s)"
                        if include_replies and replies_sent > 0:
                            success_msg += f" and {replies_sent} auto-reply(ies)"
                        success_msg += "!"
                        st.success(success_msg)

                        # Show results
                        if result.get('emails'):
                            with st.expander("📧 Email Details", expanded=True):
                                for i, email_info in enumerate(result['emails'], 1):
                                    st.write(f"**Email {i}:**")
                                    st.write(f"- Subject: `{email_info.get('subject')}`")
                                    st.write(f"- From: `{email_info.get('from')}`")
                                    st.write(f"- To: `{email_info.get('to')}`")
                                    st.write(f"- Status: `{email_info.get('status')}`")

                                    if email_info.get('has_reply'):
                                        st.write(f"- ✅ Reply sent: `{email_info.get('reply_subject')}`")
                                    elif include_replies:
                                        st.write(f"- ❌ No reply sent")

                                    if i < len(result['emails']):
                                        st.markdown("---")

                        st.info("💡 Check both inboxes to verify email delivery, replies, and content quality.")
                    else:
                        st.error(f"❌ Failed to send test emails: {response.text}")

                except requests.exceptions.Timeout:
                    st.error("❌ Request timed out. This may happen with multiple emails and replies. Check API logs.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    st.markdown("---")

    st.subheader("ℹ️ About Quick Test")
    st.markdown("""
    **Quick Test** allows you to:
    - ✅ Verify SMTP/IMAP configurations are working
    - ✅ Test AI-generated email content quality
    - ✅ Check email delivery and inbox placement
    - ✅ Validate sender/receiver interactions
    - ✅ Test automatic replies from receivers (optional)

    **Note:** Test emails are sent immediately and **do not** count towards warming campaign metrics.

    **Auto-replies:** When enabled, receivers will automatically reply to test emails after 2 seconds, simulating real email conversations.
    """)


elif page == "🧮 Estimate":
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


elif page == "💰 API Costs":
    st.title("💰 API Costs & Rate Limits")
    st.markdown("Monitor API usage and avoid rate limit exhaustion.")

    # Import dependencies
    # In Docker, warmit is at /app/warmit (parent.parent from dashboard/app.py)
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from warmit.services.rate_limit_tracker import get_rate_limit_tracker
    from warmit.services.config_profiles import get_profile_manager

    # Get tracker
    tracker = get_rate_limit_tracker()
    statuses = tracker.get_all_statuses()

    # Overall status
    st.subheader("📊 Overall Status")

    col1, col2, col3 = st.columns(3)

    total_requests_today = sum(info.requests_today for info in statuses.values())
    total_limit_today = sum(info.rpd_limit for info in statuses.values())

    with col1:
        st.metric(
            "Total Requests Today",
            f"{total_requests_today:,}",
            help="Combined requests across all providers"
        )

    with col2:
        utilization = (total_requests_today / total_limit_today * 100) if total_limit_today > 0 else 0
        st.metric(
            "Overall Utilization",
            f"{utilization:.1f}%",
            delta=f"{total_limit_today - total_requests_today:,} remaining"
        )

    with col3:
        exhausted_count = sum(1 for info in statuses.values() if info.is_exhausted)
        status_color = "🔴" if exhausted_count > 0 else "🟢"
        st.metric(
            "Provider Status",
            f"{status_color} {len(statuses) - exhausted_count}/{len(statuses)} Available"
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
                tracker.reset_provider(provider_name)
                st.success(f"Reset {provider_name} counters")
                st.rerun()

    st.markdown("---")

    # Configuration recommendations
    st.subheader("💡 Optimization Recommendations")

    # Get current number of accounts
    accounts_data = get_accounts()
    num_senders = len([a for a in accounts_data if a.get('type') == 'sender']) if accounts_data else 10

    # Get recommended profile
    profile_manager = get_profile_manager()
    recommended_profile = profile_manager.get_recommended_profile(num_senders)

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


elif page == "⚙️ Settings":
    st.title("⚙️ Settings")

    tab1, tab2 = st.tabs(["🔐 Change Password", "ℹ️ About"])

    with tab1:
        st.subheader("Change Admin Password")
        st.markdown("Update your dashboard admin password for security.")

        with st.form("change_password_form"):
            current_password = st.text_input(
                "Current Password*",
                type="password",
                placeholder="Enter your current password"
            )

            col1, col2 = st.columns(2)

            with col1:
                new_password = st.text_input(
                    "New Password*",
                    type="password",
                    placeholder="Enter new password (min 8 chars)"
                )

            with col2:
                confirm_password = st.text_input(
                    "Confirm New Password*",
                    type="password",
                    placeholder="Confirm new password"
                )

            submit = st.form_submit_button("🔄 Change Password", use_container_width=True, type="primary")

            if submit:
                # Validation
                if not current_password or not new_password or not confirm_password:
                    st.error("⚠️ Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("❌ New passwords do not match")
                elif len(new_password) < 8:
                    st.error("❌ New password must be at least 8 characters")
                else:
                    # Attempt password change
                    success, message = change_password(current_password, new_password)

                    if success:
                        st.success(f"✅ {message}")
                        st.info("💡 Please remember your new password. There is no password recovery!")
                    else:
                        st.error(f"❌ {message}")

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
            st.metric("API URL", API_BASE_URL)

        with col_c:
            italy_tz = ZoneInfo("Europe/Rome")
            now_italy = datetime.now(italy_tz)
            st.metric("Server Time", now_italy.strftime("%H:%M:%S"))


# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🔥 WarmIt Dashboard v0.1.0")
with col2:
    st.caption("📡 API: http://localhost:8000")
with col3:
    # Use Rome/Italy timezone for display
    italy_tz = ZoneInfo("Europe/Rome")
    now_italy = datetime.now(italy_tz)
    st.caption("🔄 Last updated: " + now_italy.strftime("%H:%M:%S"))

# Auto-refresh
if auto_refresh:
    time.sleep(30)
    st.rerun()
