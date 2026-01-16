# Email Tracking Setup Guide

## Overview

WarmIt includes email open tracking using invisible tracking pixels. For this to work in production, your API must be **publicly accessible** from the internet.

---

## 🔧 Configuration

### 1. Set API_BASE_URL

Edit your `docker/.env` file:

```bash
# ❌ WRONG for production (localhost is not accessible from internet)
API_BASE_URL=http://localhost:8000

# ✅ CORRECT for production (use your server's public IP or domain)
API_BASE_URL=http://123.45.67.89:8000

# ✅ BEST for production (use HTTPS with domain)
API_BASE_URL=https://warmit.yourdomain.com
```

### 2. Open Firewall Port

Your server must allow incoming connections on port 8000 (or your configured port):

```bash
# Ubuntu/Debian with UFW
sudo ufw allow 8000/tcp

# CentOS/RHEL with firewalld
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# Check if port is open
sudo netstat -tulpn | grep :8000
```

### 3. Verify Public Accessibility

Test from an external machine (not your server):

```bash
# Replace with your server's IP/domain
curl http://YOUR_SERVER_IP:8000/health

# Should return: {"status":"healthy"}
```

---

## 🔒 Production Best Practices

### Option 1: Direct Port Access (Quick Setup)

**Pros**: Quick and easy
**Cons**: Exposes port 8000 directly, no HTTPS

```bash
API_BASE_URL=http://YOUR_SERVER_IP:8000
```

### Option 2: Reverse Proxy with HTTPS (Recommended)

**Pros**: HTTPS encryption, better security, standard ports (80/443)
**Cons**: Requires domain name and SSL certificate

#### Using Nginx

1. Install Nginx and Certbot:
```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx
```

2. Create Nginx config `/etc/nginx/sites-available/warmit`:
```nginx
server {
    listen 80;
    server_name warmit.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. Enable site and get SSL:
```bash
sudo ln -s /etc/nginx/sites-available/warmit /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d warmit.yourdomain.com
```

4. Update .env:
```bash
API_BASE_URL=https://warmit.yourdomain.com
```

#### Using Caddy (Simpler Alternative)

1. Install Caddy:
```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
```

2. Create Caddyfile:
```
warmit.yourdomain.com {
    reverse_proxy localhost:8000
}
```

3. Start Caddy (automatically gets SSL):
```bash
sudo caddy run --config Caddyfile
```

4. Update .env:
```bash
API_BASE_URL=https://warmit.yourdomain.com
```

---

## 🧪 Testing Tracking

### 1. Check Tracking Endpoint

```bash
# Should return a 1x1 transparent GIF
curl -I http://YOUR_API_URL/track/open/1

# Expected response:
# HTTP/1.1 200 OK
# content-type: image/gif
```

### 2. Send Test Email

1. Go to dashboard: http://YOUR_SERVER:8501
2. Create a campaign with 1 sender and 1 receiver
3. Click "Send Now"
4. Check the receiver's email inbox
5. Open the email
6. Wait 10-20 seconds
7. Refresh dashboard - you should see "Opens: 1"

### 3. Check Logs

```bash
# Check if tracking requests are coming in
docker compose -f docker/docker-compose.prod.yml logs api | grep track/open

# You should see entries like:
# INFO:     123.45.67.89:12345 - "GET /track/open/123 HTTP/1.1" 200 OK
```

---

## ❓ Troubleshooting

### Problem: Opens Not Tracking

**Check 1**: Verify API_BASE_URL is publicly accessible
```bash
# From OUTSIDE your server
curl http://YOUR_API_URL/health
```

**Check 2**: Check email HTML source
- Open the email in your email client
- View source (usually right-click → View Source)
- Search for `<img src=`
- Verify the URL matches your API_BASE_URL

**Check 3**: Email client blocks images
- Some email clients block images by default (Gmail "Display images below")
- Click "Display images" to load tracking pixel

**Check 4**: Check firewall
```bash
# Test if port is reachable
telnet YOUR_SERVER_IP 8000

# If it times out, firewall is blocking it
```

### Problem: API Not Accessible

**Solution 1**: Check Docker port binding
```bash
# Verify container is listening
docker compose -f docker/docker-compose.prod.yml ps

# Should show: 0.0.0.0:8000->8000/tcp
```

**Solution 2**: Check cloud provider security groups
- AWS: EC2 → Security Groups → Inbound Rules
- GCP: VPC Network → Firewall Rules
- Azure: Network Security Groups
- Add rule: TCP port 8000 from 0.0.0.0/0

---

## 📊 Understanding Tracking Data

### What Gets Tracked

1. **Opens**: When recipient's email client loads the tracking pixel
   - Recorded in: `Email.opened_at`
   - Counted in: `Account.total_opened`

2. **Bounces**: When email delivery fails
   - Detected automatically by checking sender inbox for bounce notifications
   - Recorded in: `Email.bounced_at`, `Email.status = BOUNCED`
   - Counted in: `Account.total_bounced`

3. **Replies**: When receiver responds to email
   - Detected by response bot checking receiver inbox
   - Recorded in: `Email.replied_at`, `Email.status = REPLIED`
   - Counted in: `Account.total_replied`

### Tracking Limitations

1. **Opens**:
   - Only tracked when email client loads images
   - Blocked by "Disable remote images" setting
   - May be double-counted if email opened multiple times
   - First open only is recorded

2. **Bounces**:
   - Detected via inbox monitoring (checks every 30 minutes)
   - Not instant - may take up to 30 minutes to detect
   - Some bounce notifications may not match standard patterns

3. **Privacy**:
   - Tracking pixels are standard in email marketing
   - Fully GDPR compliant (no personal data collected)
   - Only tracks: email ID, timestamp

---

## 🔐 Security Considerations

1. **Rate Limiting**: Consider adding rate limits to tracking endpoint to prevent abuse
2. **HTTPS**: Always use HTTPS in production to prevent MITM attacks
3. **IP Whitelisting**: If possible, restrict tracking endpoint to known email providers
4. **Monitoring**: Monitor tracking endpoint for unusual traffic patterns

---

## 📝 Summary

✅ **Required for tracking to work**:
- API_BASE_URL must be publicly accessible (not localhost)
- Port 8000 (or your port) must be open in firewall
- Recipients' email clients must load images

✅ **Recommended for production**:
- Use HTTPS with reverse proxy (Nginx/Caddy)
- Use a domain name instead of IP address
- Monitor tracking endpoint logs

✅ **After setup**:
- Restart services: `./warmit.sh restart`
- Send test email and verify tracking
- Check logs for tracking requests

---

Need help? Check the logs:
```bash
./warmit.sh logs api
./warmit.sh logs worker
```
