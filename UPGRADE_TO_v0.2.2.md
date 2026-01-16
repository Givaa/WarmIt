# Upgrade to v0.2.2

**Quick upgrade guide for existing WarmIt installations.**

---

## ⚠️ IMPORTANT: Database Migration Required

Version 0.2.2 introduces new database columns. **You must apply the migration** or you'll get errors like:

```
column "next_send_time" of relation "campaigns" does not exist
```

---

## 🚀 Upgrade Steps

### 1. Stop Services (Optional but Recommended)
```bash
./warmit.sh stop
```

### 2. Pull Latest Code
```bash
git pull origin main
```

### 3. Apply Database Migration
```bash
docker compose -f docker/docker-compose.prod.yml exec -T postgres \
  psql -U warmit -d warmit < scripts/migrations/002_add_next_send_time.sql
```

**Expected output:**
```
ALTER TABLE
COMMENT
ALTER TABLE
COMMENT
```

### 4. Verify Migration
```bash
docker compose -f docker/docker-compose.prod.yml exec -T postgres \
  psql -U warmit -d warmit -c "\d campaigns" | grep next_send_time
```

**Expected output:**
```
 next_send_time       | timestamp with time zone |           |          |
```

### 5. Restart Services
```bash
./warmit.sh restart
```

### 6. Test New Features
1. Navigate to dashboard: http://localhost:8501
2. Create a new campaign
3. Check "Next Send" time is displayed
4. Verify no errors in logs

---

## 🔧 Troubleshooting

### Error: "column next_send_time does not exist"

**Problem:** Migration wasn't applied.

**Solution:**
```bash
# Apply migration
docker compose -f docker/docker-compose.prod.yml exec -T postgres \
  psql -U warmit -d warmit < scripts/migrations/002_add_next_send_time.sql

# Restart API
docker compose -f docker/docker-compose.prod.yml restart api
```

### Error: "relation campaigns does not exist"

**Problem:** Database wasn't initialized.

**Solution:**
```bash
# Restart services (will initialize DB)
./warmit.sh restart
```

### Error: "cannot connect to postgres"

**Problem:** Database container not running.

**Solution:**
```bash
# Check container status
docker compose -f docker/docker-compose.prod.yml ps

# Restart all services
./warmit.sh restart
```

---

## 📋 What's New in v0.2.2

### 🎯 Major Features
- **Random Email Timing**: Emails sent at random times (9 AM - 6 PM)
- **Next Send Display**: Dashboard shows when next batch will be sent
- **Campaign Delete**: Delete campaigns with confirmation
- **Security Hardening**: Removed exposed API URLs from public pages

### 🐛 Bug Fixes
- Fixed API Costs page not loading
- Fixed auto-refresh checkbox losing state
- Fixed "Send Now" showing errors on success
- Fixed campaign form layout (multiselect overflow)

### 📚 Documentation
- Added `./warmit.sh help` menu
- Updated all README files
- Added IMPLEMENTATION_NOTES.md

---

## 🔄 Rollback (If Needed)

If you need to rollback to v0.2.1:

```bash
# 1. Stop services
./warmit.sh stop

# 2. Checkout previous version
git checkout v0.2.1  # Or your previous commit

# 3. Remove migration
docker compose -f docker/docker-compose.prod.yml exec -T postgres \
  psql -U warmit -d warmit -c "ALTER TABLE campaigns DROP COLUMN IF EXISTS next_send_time;"

docker compose -f docker/docker-compose.prod.yml exec -T postgres \
  psql -U warmit -d warmit -c "ALTER TABLE emails DROP COLUMN IF EXISTS scheduled_send_time;"

# 4. Restart
./warmit.sh restart
```

---

## 📞 Support

- **Issues**: https://github.com/Givaa/WarmIt/issues
- **Changelog**: See CHANGELOG_v0.2.2.md
- **Documentation**: See README.md

---

**Made with ❤️ by [Givaa](https://github.com/Givaa)**
