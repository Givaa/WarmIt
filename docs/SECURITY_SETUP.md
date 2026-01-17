# 🔐 Security Setup Guide

Quick guide for setting up authentication and encryption in WarmIt.

---

## 🚀 Quick Start

### 1. Generate Encryption Key

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the output (looks like: `xY9Kp2mN4qR8wE5tP3sD6fG7hJ8kL9zX=`)

### 2. Add to Environment

Edit `docker/.env` (or `.env` for local dev):

```env
ENCRYPTION_KEY=<paste_your_key_here>
```

### 3. Start Application

```bash
./warmit.sh start
```

### 4. Get Admin Password

Check dashboard logs:

```bash
docker logs warmit-dashboard
```

Look for:
```
======================================================================
🔐 WARMIT ADMIN PASSWORD GENERATED
======================================================================
   Password: xY9#Kp2@mN4$qR8&
======================================================================
⚠️  SAVE THIS PASSWORD NOW - IT WILL NOT BE SHOWN AGAIN!
======================================================================
```

**Important:** The password is shown ONLY ONCE at first startup. Save it immediately!

### 5. Login

1. Open http://localhost (via Nginx on port 80)
2. Enter admin password from logs
3. Dashboard loads

### 6. Change Password (Recommended)

1. Click "⚙️ Settings" in sidebar
2. Go to "🔐 Change Password" tab
3. Enter current password
4. Enter new password (min 8 chars)
5. Confirm new password
6. Click "Change Password"

**Done!** Your WarmIt installation is now secured. 🎉

---

## 📋 For Existing Installations

If you already have accounts in the database:

### 1. Backup Database

```bash
# PostgreSQL
docker exec warmit-postgres pg_dump -U warmit warmit > backup.sql

# SQLite
cp warmit.db warmit.db.backup
```

### 2. Generate and Set Encryption Key

```bash
# Generate key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Add to docker/.env
echo "ENCRYPTION_KEY=<your_key>" >> docker/.env
```

### 3. Run Migration

Encrypt existing passwords:

```bash
python scripts/migrate_encrypt_passwords.py
```

Expected output:
```
🔐 Starting password encryption migration
✅ ENCRYPTION_KEY found
📝 Expanding password column size...
✅ Column resized
📧 Found 10 accounts to process
🔐 Encrypting passwords...
  ✅ sender1@example.com: Password encrypted
  ✅ sender2@example.com: Password encrypted
  ... (more accounts)
🎉 Migration completed successfully!
✅ Encrypted: 10 passwords
```

### 4. Restart and Login

```bash
./warmit.sh restart
docker logs warmit-dashboard | grep "Admin Password"
```

---

## 🔑 Password Management

### Change Admin Password

1. Login to dashboard
2. Go to **Settings** → **Change Password**
3. Enter current password
4. Enter new password (min 8 chars)
5. Confirm new password
6. Submit

### Forgot Admin Password?

**⚠️ There is no password recovery!**

If you lose your admin password:

1. Stop containers: `./warmit.sh stop`
2. Delete auth file: `rm dashboard/.auth`
3. Start containers: `./warmit.sh start`
4. New password will be generated (check logs)

**Important:** This does NOT affect your email account passwords. Only the dashboard login.

---

## 🔒 Encryption Key Management

### Backup Your Key

**CRITICAL:** Without the encryption key, you cannot decrypt stored passwords!

```bash
# View current key
grep ENCRYPTION_KEY docker/.env

# Backup to secure location
echo "WarmIt Encryption Key: $(grep ENCRYPTION_KEY docker/.env)" > ~/warmit-key-backup.txt
chmod 600 ~/warmit-key-backup.txt
```

### Rotate Encryption Key

To change the encryption key (advanced):

1. Backup database
2. Stop all services
3. Decrypt all passwords with old key
4. Generate new key
5. Update `.env` with new key
6. Restart services (will auto-encrypt with new key)

**Note:** Key rotation script coming soon.

---

## 🛡️ Security Best Practices

### ✅ DO:
- ✅ Set a strong `ENCRYPTION_KEY` (never use example key)
- ✅ Change default admin password immediately
- ✅ Backup encryption key securely
- ✅ Use PostgreSQL for production
- ✅ Enable HTTPS with reverse proxy
- ✅ Regularly backup database
- ✅ Monitor logs for suspicious activity
- ✅ Update WarmIt regularly

### ❌ DON'T:
- ❌ Commit `.env` files to git
- ❌ Share encryption key
- ❌ Use SQLite in production
- ❌ Expose dashboard to public internet without HTTPS
- ❌ Reuse passwords from other services
- ❌ Ignore failed login attempts in logs

---

## 🔧 Troubleshooting

### "ENCRYPTION_KEY not set" warning

**Problem:** Encryption key missing from environment.

**Solution:**
```bash
# Generate key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Add to .env
echo "ENCRYPTION_KEY=<key_here>" >> docker/.env

# Restart
./warmit.sh restart
```

### Cannot decrypt passwords

**Problem:** Wrong encryption key or corrupted data.

**Solution:**
1. Check if `ENCRYPTION_KEY` in `.env` matches backup
2. Restore database from backup
3. Run migration again

### Lost admin password

**Problem:** Forgot dashboard password.

**Solution:**
```bash
./warmit.sh stop
rm dashboard/.auth
./warmit.sh start
docker logs warmit-dashboard  # Look for password in output
```

### Migration fails with "already encrypted"

**Not a problem!** Migration is smart and skips already-encrypted passwords.

This means:
- Some passwords are already encrypted (safe to ignore)
- Or all passwords are encrypted (migration already ran)

---

## 📝 Accessing Logs (Dozzle)

Container logs are available via Dozzle at `http://localhost:8888`.

**Security:** Dozzle is bound to localhost only (`127.0.0.1:8888`) and is not accessible from the internet.

### Local Access

```bash
# Open in browser
http://localhost:8888
```

### Remote Access via SSH Tunnel

If you need to access logs from a remote server:

```bash
# Create SSH tunnel from your local machine
ssh -L 8888:localhost:8888 user@your-server

# Then open in local browser
http://localhost:8888
```

The SSH tunnel forwards your local port 8888 to the server's localhost:8888, allowing secure remote access to the logs interface.

---

## 🏗️ Network Architecture

```
Internet (port 80/443)
    │
    ▼
┌─────────────────────────────────────┐
│           Nginx Reverse Proxy        │
├─────────────────────────────────────┤
│ /              → Dashboard (8501)   │  ← Protected by login
│ /track/*       → API (8000)         │  ← HMAC token required
│ /api/*         → BLOCKED            │  ← Not accessible
│ /docs          → BLOCKED            │  ← Not accessible
└─────────────────────────────────────┘

Localhost Only (not exposed to internet):
├── Dozzle Logs: 127.0.0.1:8888
├── API: 8000 (internal)
├── Dashboard: 8501 (internal)
├── PostgreSQL: 5432 (internal)
└── Redis: 6379 (internal)
```

**Key Security Features:**
- Only port 80 (HTTP) and 443 (HTTPS) are exposed to the internet
- API endpoints are blocked by Nginx (only `/track/*` allowed)
- Tracking URLs require valid HMAC tokens
- Logs accessible only from localhost (use SSH tunnel for remote access)
- All internal services communicate via Docker network

---

## 📞 Support

- **Documentation:** [README.md](README.md)
- **Detailed Changes:** [CHANGELOG.md](../CHANGELOG.md)
- **Issues:** [GitHub Issues](https://github.com/yourusername/warmit/issues)

---

**Remember:** Keep your encryption key and admin password safe! 🔐
