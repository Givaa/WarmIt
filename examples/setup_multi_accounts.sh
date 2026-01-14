#!/bin/bash

# WarmIt - Multi-Account Setup Script (Auto-Detection)
#
# HOW TO USE:
# 1. Edit SENDERS array with your sender emails
# 2. Edit RECEIVERS array with your receiver emails
# 3. Run: ./setup_multi_accounts.sh
#
# FEATURES:
# - Auto-detects provider (Gmail, Outlook, Libero, Yahoo, Custom)
# - Auto-configures SMTP/IMAP settings
# - Calculates distribution automatically
# - Shows expected email volumes
#
# EXAMPLE - Complete Italian setup:
# SENDERS=(
#     "vendite@tuodominio.com"   # Aruba domain - auto-detects smtp.tuodominio.com
#     "info@tuodominio.com"
#     "supporto@tuodominio.com"
# )
#
# RECEIVERS=(
#     "warmup1@gmail.com"        # Gmail - App Password required
#     "warmup2@gmail.com"
#     "warmup3@outlook.com"      # Outlook
#     "warmup4@libero.it"        # Libero
# )

set -e

API_URL="http://localhost:8000"

echo "🔥 WarmIt - Multi-Account Setup (Smart Auto-Detection)"
echo "======================================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Arrays to store account IDs
SENDER_IDS=()
RECEIVER_IDS=()

echo -e "${BLUE}Step 1: Adding SENDER accounts...${NC}"
echo ""

# Sender accounts - CUSTOMIZE WITH YOUR EMAILS!
# For Aruba hosted domains, the script will auto-detect smtp.yourdomain.com
#
# EXAMPLE - Aruba hosted domain:
SENDERS=(
    "vendite@tuodominio.com"      # Will use smtp.tuodominio.com:587
    "info@tuodominio.com"
    "supporto@tuodominio.com"
    "marketing@tuodominio.com"
    "commerciale@tuodominio.com"

    # Add more as needed...
)

# Option 1: Same password for all senders (convenient but less secure)
USE_SAME_PASSWORD=true  # Set to false to enter password for each account
SENDER_PASSWORD="your_password_here"  # Only used if USE_SAME_PASSWORD=true

for email in "${SENDERS[@]}"; do
    # Auto-detect SMTP/IMAP configuration
    domain=$(echo "$email" | sed 's/.*@//')
    smtp_host="smtp.$domain"
    imap_host="imap.$domain"
    smtp_port=587
    imap_port=993

    echo "Adding sender: $email"
    echo "  Auto-detected: $smtp_host:$smtp_port / $imap_host:$imap_port"

    # Get password
    if [ "$USE_SAME_PASSWORD" = true ]; then
        PASSWORD="$SENDER_PASSWORD"
    else
        echo -e "${YELLOW}Enter password for $email:${NC}"
        read -s PASSWORD
    fi

    RESPONSE=$(curl -s -X POST "$API_URL/api/accounts" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$email\",
            \"type\": \"sender\",
            \"smtp_host\": \"$smtp_host\",
            \"smtp_port\": $smtp_port,
            \"smtp_use_tls\": true,
            \"imap_host\": \"$imap_host\",
            \"imap_port\": $imap_port,
            \"imap_use_ssl\": true,
            \"password\": \"$PASSWORD\"
        }")

    ACCOUNT_ID=$(echo $RESPONSE | jq -r '.id')

    if [ "$ACCOUNT_ID" != "null" ]; then
        SENDER_IDS+=($ACCOUNT_ID)
        echo -e "${GREEN}✅ Added: $email (ID: $ACCOUNT_ID)${NC}"
    else
        echo -e "${YELLOW}⚠️  Warning: Failed to add $email${NC}"
        echo "Response: $RESPONSE"
    fi
    echo ""
done

echo ""
echo -e "${BLUE}Step 2: Adding RECEIVER accounts...${NC}"
echo ""

# Receiver accounts - CUSTOMIZE WITH YOUR EMAILS!
# The script will auto-detect provider and configure SMTP/IMAP automatically
#
# Supported providers (auto-detected):
# - Gmail: @gmail.com (smtp.gmail.com:587)
# - Outlook: @outlook.com, @outlook.it, @hotmail.com, @hotmail.it, @live.com, @live.it
# - Libero: @libero.it, @inwind.it, @iol.it, @blu.it, @giallo.it
# - Yahoo: @yahoo.com, @yahoo.it
# - Aruba: Domains hosted on Aruba (uses smtp.domain.com:587)
# - Custom: Any other domain (uses smtp.domain.com:587 / imap.domain.com:993)
#
# EXAMPLE - Mixed providers (recommended):
RECEIVERS=(
    # Gmail accounts (will auto-detect and remind you to use App Password)
    "warmup1@gmail.com"
    "warmup2@gmail.com"
    "warmup3@gmail.com"

    # Outlook accounts (will auto-detect outlook.office365.com)
    "warmup4@outlook.com"
    "warmup5@hotmail.com"

    # Libero accounts (will auto-detect smtp.libero.it)
    "warmup6@libero.it"
    "warmup7@libero.it"

    # Yahoo accounts (optional)
    # "warmup8@yahoo.com"

    # Custom domain (will use smtp.domain.com / imap.domain.com)
    # "warmup9@mydomain.com"

    # Add more as needed...
)

# Function to auto-detect provider and get SMTP/IMAP config
get_provider_config() {
    local email=$1
    local domain=$(echo "$email" | sed 's/.*@//')

    case "$domain" in
        gmail.com)
            echo "Gmail|smtp.gmail.com|587|imap.gmail.com|993"
            ;;
        outlook.com|outlook.it|hotmail.com|hotmail.it|live.com|live.it)
            echo "Outlook|smtp-mail.outlook.com|587|outlook.office365.com|993"
            ;;
        libero.it|inwind.it|iol.it|blu.it|giallo.it)
            echo "Libero|smtp.libero.it|587|imap.libero.it|993"
            ;;
        yahoo.com|yahoo.it)
            echo "Yahoo|smtp.mail.yahoo.com|587|imap.mail.yahoo.com|993"
            ;;
        # Aruba hosted domains - check if it's an Aruba-hosted domain
        *.aruba.it|*.pec.it)
            echo "Aruba|smtps.$domain|465|imaps.$domain|993"
            ;;
        *)
            # Try to detect if it's an Aruba-hosted custom domain
            # Aruba uses: smtps.yourdomain.com (port 465) or smtp.yourdomain.com (port 587)
            # Default to standard SMTP/IMAP for custom domains
            echo "Custom|smtp.$domain|587|imap.$domain|993"
            ;;
    esac
}

# Count providers
declare -A PROVIDER_COUNT
for email in "${RECEIVERS[@]}"; do
    config=$(get_provider_config "$email")
    provider=$(echo "$config" | cut -d'|' -f1)
    ((PROVIDER_COUNT[$provider]++))
done

# Show distribution
echo "Detected receiver distribution:"
for provider in "${!PROVIDER_COUNT[@]}"; do
    count=${PROVIDER_COUNT[$provider]}
    percentage=$((count * 100 / ${#RECEIVERS[@]}))
    echo "  📧 $provider: $count accounts ($percentage%)"
done
echo ""

# Add each receiver with auto-detected configuration
for email in "${RECEIVERS[@]}"; do
    # Auto-detect provider configuration
    config=$(get_provider_config "$email")
    IFS='|' read -r provider smtp_host smtp_port imap_host imap_port <<< "$config"

    echo "Adding receiver [$provider]: $email"

    # Gmail requires App Password
    if [ "$provider" = "Gmail" ]; then
        echo -e "${YELLOW}⚠️  IMPORTANT: For Gmail, use App Password (not regular password)${NC}"
        echo "   Generate at: https://myaccount.google.com/apppasswords"
    fi

    echo -e "${YELLOW}Enter password for $email:${NC}"
    read -s PASSWORD

    RESPONSE=$(curl -s -X POST "$API_URL/api/accounts" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$email\",
            \"type\": \"receiver\",
            \"smtp_host\": \"$smtp_host\",
            \"smtp_port\": $smtp_port,
            \"smtp_use_tls\": true,
            \"imap_host\": \"$imap_host\",
            \"imap_port\": $imap_port,
            \"imap_use_ssl\": true,
            \"password\": \"$PASSWORD\"
        }")

    ACCOUNT_ID=$(echo $RESPONSE | jq -r '.id')

    if [ "$ACCOUNT_ID" != "null" ]; then
        RECEIVER_IDS+=($ACCOUNT_ID)
        echo -e "${GREEN}✅ Added: $email (ID: $ACCOUNT_ID)${NC}"
    else
        echo -e "${YELLOW}⚠️  Warning: Failed to add $email${NC}"
        echo "Response: $RESPONSE"
    fi
    echo ""
done

echo ""
echo -e "${BLUE}Step 3: Creating campaign...${NC}"
echo ""

# Convert arrays to JSON format
SENDER_IDS_JSON=$(printf '%s\n' "${SENDER_IDS[@]}" | jq -R . | jq -s .)
RECEIVER_IDS_JSON=$(printf '%s\n' "${RECEIVER_IDS[@]}" | jq -R . | jq -s .)

CAMPAIGN_RESPONSE=$(curl -s -X POST "$API_URL/api/campaigns" \
    -H "Content-Type: application/json" \
    -d "{
        \"name\": \"Warming Completo $(date +%Y-%m-%d)\",
        \"sender_account_ids\": $SENDER_IDS_JSON,
        \"receiver_account_ids\": $RECEIVER_IDS_JSON,
        \"duration_weeks\": 6
    }")

CAMPAIGN_ID=$(echo $CAMPAIGN_RESPONSE | jq -r '.id')

if [ "$CAMPAIGN_ID" != "null" ]; then
    echo -e "${GREEN}✅ Campaign created successfully!${NC}"
    echo "Campaign ID: $CAMPAIGN_ID"
    echo ""
    echo "Campaign Details:"
    echo $CAMPAIGN_RESPONSE | jq .
else
    echo -e "${YELLOW}⚠️  Failed to create campaign${NC}"
    echo "Response: $CAMPAIGN_RESPONSE"
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Setup Complete! 🎉${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Summary:"
echo "  Senders added: ${#SENDER_IDS[@]} accounts"
echo "  Receivers added: ${#RECEIVER_IDS[@]} accounts"
echo ""
echo "Receiver Distribution:"
for provider in "${!PROVIDER_COUNT[@]}"; do
    count=${PROVIDER_COUNT[$provider]}
    percentage=$((count * 100 / ${#RECEIVERS[@]}))
    echo "  📧 $provider: $count accounts ($percentage%)"
done
echo ""
echo "Campaign:"
echo "  ID: $CAMPAIGN_ID"
echo "  Duration: 6 weeks"
echo "  Status: Active"
echo ""
echo "Next steps:"
echo "  1. Check dashboard: http://localhost:8501"
echo "  2. Monitor campaign progress"
echo "  3. Check metrics daily"
echo ""
echo "The warming will start automatically!"
echo "Emails will be sent every 2 hours (8am-8pm)"
echo ""

# Calculate expected volumes
TOTAL_SENDERS=${#SENDER_IDS[@]}
TOTAL_RECEIVERS=${#RECEIVER_IDS[@]}
WEEK1_TOTAL=$((TOTAL_SENDERS * 5))
WEEK6_TOTAL=$((TOTAL_SENDERS * 50))
WEEK1_PER_RECEIVER=$((WEEK1_TOTAL / TOTAL_RECEIVERS))
WEEK6_PER_RECEIVER=$((WEEK6_TOTAL / TOTAL_RECEIVERS))

echo "📊 Expected Volume:"
echo "  Week 1: ~$WEEK1_TOTAL emails/day total (~$WEEK1_PER_RECEIVER per receiver)"
echo "  Week 6: ~$WEEK6_TOTAL emails/day total (~$WEEK6_PER_RECEIVER per receiver)"
echo ""
