"""WarmIt Dashboard - Web UI for monitoring and managing email warming campaigns."""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import os

# Configuration - Use environment variable for Docker, fallback to localhost for local dev
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Page config
st.set_page_config(
    page_title="WarmIt Dashboard",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
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
        response = requests.post(f"{API_BASE_URL}/api/campaigns/{campaign_id}/process")
        return response.ok, response.json() if response.ok else response.text
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

    # Navigation
    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "📧 Accounts", "🎯 Campaigns", "📈 Analytics", "➕ Add New"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Auto-refresh
    auto_refresh = st.checkbox("Auto-refresh (30s)", value=True)
    if auto_refresh:
        st.info("Dashboard refreshes every 30 seconds")


# Main content
if page == "📊 Dashboard":
    st.markdown('<h1 class="main-header">🔥 WarmIt Dashboard</h1>', unsafe_allow_html=True)

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

        with st.form("add_account"):
            col1, col2 = st.columns(2)

            with col1:
                email = st.text_input("Email Address*", placeholder="sender@example.com")
                account_type = st.selectbox("Account Type*", ["sender", "receiver"])
                password = st.text_input("Password*", type="password", help="Use App Password for Gmail")

            with col2:
                smtp_host = st.text_input("SMTP Host*", value="smtp.gmail.com")
                smtp_port = st.number_input("SMTP Port*", value=587, min_value=1, max_value=65535)
                imap_host = st.text_input("IMAP Host*", value="imap.gmail.com")
                imap_port = st.number_input("IMAP Port*", value=993, min_value=1, max_value=65535)

            smtp_tls = st.checkbox("Use TLS for SMTP", value=True)
            imap_ssl = st.checkbox("Use SSL for IMAP", value=True)

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
                                st.json(result)
                            time.sleep(2)
                            st.rerun()
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
                                st.json(result)
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to create campaign: {result}")


# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🔥 WarmIt Dashboard v0.1.0")
with col2:
    st.caption("📡 API: http://localhost:8000")
with col3:
    st.caption("🔄 Last updated: " + datetime.now().strftime("%H:%M:%S"))

# Auto-refresh
if auto_refresh:
    time.sleep(30)
    st.rerun()
