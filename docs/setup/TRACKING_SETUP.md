# Email Tracking Setup Guide

## Overview

WarmIt includes email open tracking using invisible tracking pixels. The system is secured with:

1. **Nginx Reverse Proxy**: Only exposes `/track/*` endpoints, blocks all API access
2. **HMAC Token Signatures**: Cryptographically signed tracking URLs prevent unauthorized access

---

## 🔒 Security Architecture

```
Internet
    │
    ▼
┌─────────────────────────────────────┐
│        Nginx (port 80/443)          │
├─────────────────────────────────────┤
│ /              → Dashboard (8501)   │  ← Protected by login
│ /track/*       → API (8000)         │  ← Requires valid HMAC token
│ /api/*         → BLOCKED            │  ← Not accessible
│ /docs          → BLOCKED            │  ← Not accessible
└─────────────────────────────────────┘
```

**Tracking URLs are secured with HMAC-SHA256 tokens:**
```
/track/open/123?token=a1b2c3d4e5f6...&ts=1705484400
```

- Token is generated using `TRACKING_SECRET_KEY`
- Tokens expire after 30 days
- Invalid/missing tokens are rejected (pixel returned but no tracking)

---

## 🔧 Configuration

### 1. Generate Security Keys

```bash
# Generate TRACKING_SECRET_KEY (required for secure tracking)
python -c "import secrets; print(secrets.token_hex(32))"

# Example output: a3f8c2e1d9b7f6a5c4e3d2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1
```

### 2. Edit docker/.env

```bash
# Required: Secret key for HMAC token signatures
TRACKING_SECRET_KEY=a3f8c2e1d9b7f6a5c4e3d2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1

# Public URL where emails can reach tracking pixels
# This goes through Nginx (port 80), NOT directly to API (port 8000)
API_BASE_URL=http://YOUR_SERVER_IP

# Or with HTTPS (recommended)
API_BASE_URL=https://warmit.yourdomain.com
```

### 3. Open Firewall Port

Only port 80 (or 443 for HTTPS) needs to be open:

```bash
# Ubuntu/Debian with UFW
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp  # If using HTTPS

# CentOS/RHEL with firewalld
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

**Note**: Port 8000 should NOT be exposed publicly - Nginx handles all traffic.

### 4. Start Services

```bash
./warmit.sh restart
```

---

## 🔐 HTTPS Setup (Recommended)

### Option 1: External Reverse Proxy

If you have an existing Nginx/Caddy setup:

1. Proxy port 80/443 to the WarmIt Nginx container (port 80)
2. Handle SSL termination at your external proxy

### Option 2: Built-in HTTPS

1. Create SSL certificates directory:
```bash
mkdir -p docker/ssl
```

2. Copy certificates:
```bash
cp /path/to/fullchain.pem docker/ssl/
cp /path/to/privkey.pem docker/ssl/
```

3. Update `docker/nginx.conf` to enable HTTPS:
```nginx
server {
    listen 443 ssl;
    server_name warmit.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    # ... rest of config
}
```

4. Uncomment in `docker-compose.prod.yml`:
```yaml
nginx:
  ports:
    - "80:80"
    - "443:443"  # Uncomment this
  volumes:
    - ./ssl:/etc/nginx/ssl:ro  # Uncomment this
```

---

## 🧪 Testing

### 1. Verify Security (API Blocked)

```bash
# These should return 403 Forbidden
curl http://YOUR_SERVER/api/accounts
curl http://YOUR_SERVER/docs
curl http://YOUR_SERVER/health

# Example response: "Forbidden - API access not allowed"
```

### 2. Verify Tracking (Token Required)

```bash
# Without token - returns pixel but doesn't track (warning logged)
curl -I http://YOUR_SERVER/track/open/1

# Returns: HTTP/1.1 403 Forbidden (blocked by Nginx)

# With valid token - tracks and returns pixel
# (You need a real token from an email)
curl -I "http://YOUR_SERVER/track/open/1?token=VALID_TOKEN&ts=1705484400"

# Returns: HTTP/1.1 200 OK, content-type: image/gif
```

### 3. Send Test Email

1. Go to dashboard: http://YOUR_SERVER
2. Navigate to "🧪 Quick Test" page
3. Send a test email with a sender and receiver
4. Open the email in the receiver's inbox
5. Check dashboard - you should see the open tracked

### 4. Check Logs

```bash
# Check tracking requests
docker compose -f docker/docker-compose.prod.yml logs nginx | grep track

# Check for invalid token attempts
docker compose -f docker/docker-compose.prod.yml logs api | grep "Invalid tracking token"
```

---

## ❓ Troubleshooting

### Problem: Opens Not Tracking

**Check 1**: Verify TRACKING_SECRET_KEY is set
```bash
# Should show your key
grep TRACKING_SECRET_KEY docker/.env
```

**Check 2**: Verify API_BASE_URL is correct
```bash
# Should NOT include port 8000 (Nginx handles routing)
grep API_BASE_URL docker/.env

# WRONG: API_BASE_URL=http://server:8000
# RIGHT: API_BASE_URL=http://server
```

**Check 3**: Check email HTML source
- Open the email → View Source
- Search for `<img src=`
- Verify URL has `?token=...&ts=...` parameters

**Check 4**: Check Nginx logs
```bash
docker compose -f docker/docker-compose.prod.yml logs nginx
```

### Problem: 403 on Tracking URLs

**Cause**: Nginx blocks requests without token parameter

**Solution**: This is expected! Emails must include `?token=...&ts=...` parameters. Old emails without tokens won't track.

### Problem: Dashboard Not Loading

**Check**: Nginx is running
```bash
docker compose -f docker/docker-compose.prod.yml ps nginx
```

---

## 📊 Understanding Tracking Data

### What Gets Tracked

| Event | How Tracked | Recorded In |
|-------|-------------|-------------|
| **Opens** | Tracking pixel loaded | `Email.opened_at` |
| **Bounces** | IMAP inbox monitoring | `Email.bounced_at` |
| **Replies** | IMAP inbox monitoring | `Email.replied_at` |

### Security Features

| Feature | Description |
|---------|-------------|
| **Token Signing** | HMAC-SHA256 prevents forgery |
| **Token Expiry** | 30 days (matches campaign duration) |
| **Nginx Blocking** | Only `/track/*` exposed |
| **First-Open Only** | Multiple opens don't inflate stats |

### Tracking Limitations

1. **Opens**: Only tracked if email client loads images
2. **Token Required**: Old emails without tokens won't track
3. **30-Day Expiry**: Tokens expire after 30 days

---

## 🛡️ Security Best Practices

1. **Keep TRACKING_SECRET_KEY secret**: Never commit to git
2. **Use HTTPS in production**: Prevents token interception
3. **Monitor logs**: Watch for unusual tracking patterns
4. **Rotate keys periodically**: Generate new key every few months

---

## 📝 Summary

| Setting | Value |
|---------|-------|
| **Public Port** | 80 (via Nginx) |
| **Internal API** | 8000 (not exposed) |
| **Internal Dashboard** | 8501 (not exposed) |
| **TRACKING_SECRET_KEY** | Required for secure tracking |
| **API_BASE_URL** | Public URL (no port 8000) |

✅ **After setup**:
1. Restart services: `./warmit.sh restart`
2. Verify API is blocked: `curl http://SERVER/api/accounts` → 403
3. Send test email and verify tracking works
4. Check logs for any issues

---

Need help? Check the logs:
```bash
./warmit.sh logs nginx
./warmit.sh logs api
```
