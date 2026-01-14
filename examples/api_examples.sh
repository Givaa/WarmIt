#!/bin/bash

# WarmIt API Examples
# Make sure the API server is running on http://localhost:8000

BASE_URL="http://localhost:8000"

echo "🔥 WarmIt API Examples"
echo "======================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Health Check
echo -e "${BLUE}1. Health Check${NC}"
curl -s "$BASE_URL/health" | jq
echo ""

# 2. Add Sender Account
echo -e "${BLUE}2. Add Sender Account (Gmail)${NC}"
SENDER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/accounts" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "sender@example.com",
    "type": "sender",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_use_tls": true,
    "imap_host": "imap.gmail.com",
    "imap_port": 993,
    "imap_use_ssl": true,
    "password": "your_app_password_here"
  }')
echo "$SENDER_RESPONSE" | jq
SENDER_ID=$(echo "$SENDER_RESPONSE" | jq -r '.id')
echo -e "${GREEN}Created sender with ID: $SENDER_ID${NC}"
echo ""

# 3. Add Receiver Account
echo -e "${BLUE}3. Add Receiver Account${NC}"
RECEIVER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/accounts" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "receiver@example.com",
    "type": "receiver",
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_use_tls": true,
    "imap_host": "imap.gmail.com",
    "imap_port": 993,
    "imap_use_ssl": true,
    "password": "your_app_password_here"
  }')
echo "$RECEIVER_RESPONSE" | jq
RECEIVER_ID=$(echo "$RECEIVER_RESPONSE" | jq -r '.id')
echo -e "${GREEN}Created receiver with ID: $RECEIVER_ID${NC}"
echo ""

# 4. List All Accounts
echo -e "${BLUE}4. List All Accounts${NC}"
curl -s "$BASE_URL/api/accounts" | jq
echo ""

# 5. Check Domain Age
echo -e "${BLUE}5. Check Domain Age${NC}"
curl -s -X POST "$BASE_URL/api/accounts/$SENDER_ID/check-domain" | jq
echo ""

# 6. Create Warming Campaign
echo -e "${BLUE}6. Create Warming Campaign${NC}"
CAMPAIGN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/campaigns" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Test Campaign $(date +%s)\",
    \"sender_account_ids\": [$SENDER_ID],
    \"receiver_account_ids\": [$RECEIVER_ID],
    \"duration_weeks\": 4
  }")
echo "$CAMPAIGN_RESPONSE" | jq
CAMPAIGN_ID=$(echo "$CAMPAIGN_RESPONSE" | jq -r '.id')
echo -e "${GREEN}Created campaign with ID: $CAMPAIGN_ID${NC}"
echo ""

# 7. List Campaigns
echo -e "${BLUE}7. List All Campaigns${NC}"
curl -s "$BASE_URL/api/campaigns" | jq
echo ""

# 8. Get Campaign Details
echo -e "${BLUE}8. Get Campaign Details${NC}"
curl -s "$BASE_URL/api/campaigns/$CAMPAIGN_ID" | jq
echo ""

# 9. Process Campaign (Manual Trigger)
echo -e "${BLUE}9. Process Campaign (Send Emails)${NC}"
curl -s -X POST "$BASE_URL/api/campaigns/$CAMPAIGN_ID/process" | jq
echo ""

# 10. Get Account Metrics
echo -e "${BLUE}10. Get Account Metrics${NC}"
curl -s "$BASE_URL/api/metrics/accounts/$SENDER_ID?days=7" | jq
echo ""

# 11. Get System Metrics
echo -e "${BLUE}11. Get System Metrics${NC}"
curl -s "$BASE_URL/api/metrics/system" | jq
echo ""

# 12. Get Daily Metrics
echo -e "${BLUE}12. Get Daily Metrics (Last 7 days)${NC}"
curl -s "$BASE_URL/api/metrics/daily?days=7" | jq
echo ""

# 13. Pause Campaign
echo -e "${BLUE}13. Pause Campaign${NC}"
curl -s -X PATCH "$BASE_URL/api/campaigns/$CAMPAIGN_ID/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "paused"}' | jq
echo ""

# 14. Resume Campaign
echo -e "${BLUE}14. Resume Campaign${NC}"
curl -s -X PATCH "$BASE_URL/api/campaigns/$CAMPAIGN_ID/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "active"}' | jq
echo ""

# 15. Update Account Status
echo -e "${BLUE}15. Pause Sender Account${NC}"
curl -s -X PATCH "$BASE_URL/api/accounts/$SENDER_ID" \
  -H "Content-Type: application/json" \
  -d '{"status": "paused"}' | jq
echo ""

echo -e "${GREEN}✅ All examples completed!${NC}"
echo ""
echo "Note: Replace email credentials with real values to test actual sending."
