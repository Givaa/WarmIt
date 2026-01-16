# Changelog - Version 0.2.2

**Release Date:** 2026-01-16
**Focus:** Random Email Timing, UI Improvements, Security Hardening

---

## 🚀 New Features

### Random Email Scheduling
- **Smart Timing**: Emails are now sent at random times throughout business hours (9 AM - 6 PM)
- **Next Send Display**: Dashboard shows when the next batch of emails will be sent for each campaign
- **Natural Patterns**: Scheduling mimics human behavior patterns to improve deliverability

### Campaign Management
- **Delete Campaigns**: Added ability to delete campaigns with confirmation dialog
- **Stop Campaigns**: Pause campaigns at any time (already existed, now alongside delete)
- **Better Status Indicators**: Improved visual feedback for campaign states

---

## 🔧 Bug Fixes

### API Costs Page
- **Fixed**: Provider details and optimization recommendations now display correctly
- **Fixed**: Error handling when rate limit tracker fails to load
- **Improved**: Method name corrected from `reset_provider()` to `reset_key()`

### Auto-Refresh
- **Fixed**: Auto-refresh checkbox now maintains state across page reloads
- **Improved**: Uses query parameters for persistence instead of JavaScript reload
- **Better UX**: Checkbox stays checked when page auto-refreshes

### Campaign "Send Now" Button
- **Fixed**: Button no longer shows failure message when emails are successfully sent
- **Improved**: Better error handling with proper status code checking (2xx = success)
- **Enhanced**: More informative success/error messages

---

## 🔒 Security Improvements

### Login Page Cleanup
- **Removed**: Exposed file paths (dashboard/first_run_password.txt)
- **Removed**: Internal API URLs (localhost:8000) from user-facing messages
- **Removed**: Docker command suggestions from error messages
- **Improved**: Generic error messages suitable for public-facing deployments

**Example Changes:**
- ❌ "Make sure the API server is running on http://localhost:8000"
- ✅ "The application backend is not responding. Please contact your administrator."

---

## 📊 Database Changes

### New Migration: 002_add_next_send_time.sql
Adds scheduling fields to support random timing:
- `campaigns.next_send_time` - Tracks when campaign should next send emails
- `emails.scheduled_send_time` - For future delayed reply functionality

**⚠️ IMPORTANT: You MUST apply this migration before using v0.2.2**

**How to Apply:**
```bash
# Method 1: Apply manually (recommended for existing installations)
docker compose -f docker/docker-compose.prod.yml exec -T postgres \
  psql -U warmit -d warmit < scripts/migrations/002_add_next_send_time.sql

# Method 2: Restart services (migrations auto-applied on startup)
./warmit.sh restart

# Verify migration was applied
docker compose -f docker/docker-compose.prod.yml exec -T postgres \
  psql -U warmit -d warmit -c "\d campaigns" | grep next_send_time
```

---

## 📝 Model Updates

### Campaign Model
- Added `next_send_time` field (DateTime, nullable)
- Updated API response schema to include next_send_time

### Email Model
- Added `scheduled_send_time` field (DateTime, nullable)
- Prepared for future delayed reply implementation

---

## 🎨 UI/UX Improvements

### Dashboard
- Version updated to v0.2.2
- Next send time displayed in campaign cards (Italy timezone)
- Delete button added to campaigns
- Confirmation dialog for campaign deletion
- Cleaner status indicators ("Service Online" instead of "API Online")

### Footer & Captions
- Removed hardcoded API URLs
- Shows connection status without exposing technical details
- Professional appearance suitable for public-facing deployments

### warmit.sh Script
- **New**: Help menu with `./warmit.sh help` or `./warmit.sh --help`
- **New**: Explicit `start` command support
- **Improved**: Unknown command error handling with help display
- **Enhanced**: Better command documentation and examples

---

## 🔄 Scheduler Updates

### WarmupScheduler Class
New methods:
- `_calculate_random_send_time()` - Generates random time within business hours
- `_calculate_random_reply_time()` - Calculates reply timing (2-8 hours after original)

Updated behavior:
- Checks `next_send_time` before sending emails
- Automatically schedules next send time after processing
- Logs scheduled times for visibility

---

## 📚 Documentation

### New Files
- **IMPLEMENTATION_NOTES.md** - Details on scheduling system and limitations
- **CHANGELOG_v0.2.2.md** - This file

### Updated Files
- **scripts/migrations/README.md** - Added migration 002
- **warmit.sh** - Updated acknowledgments with correct GitHub link

---

## ⚠️ Known Limitations

### Reply Timing
While the system calculates random reply times (2-8 hours after original email), replies are currently sent immediately due to the synchronous nature of `response_bot.py`.

**To implement delayed replies** (future enhancement):
1. Modify `response_bot.py` to save replies with `status=PENDING`
2. Create background worker to send emails at `scheduled_send_time`
3. Worker updates `status=SENT` after sending

See **IMPLEMENTATION_NOTES.md** for details.

---

## 🔗 Developer Credits

All code includes acknowledgments:
```python
"""Module description.

Developed with ❤️ by Givaa
https://github.com/Givaa
"""
```

Applied to:
- `warmit.sh` startup script
- `dashboard/app.py`
- `src/warmit/main.py`
- `src/warmit/services/ai_generator.py`
- `src/warmit/services/rate_limit_tracker.py`

---

## 🧪 Testing Recommendations

Before deploying to production:

1. **Test Random Timing**
   ```bash
   # Create campaign and check next_send_time
   # Verify emails sent at scheduled time
   ```

2. **Test Campaign Deletion**
   ```bash
   # Create test campaign
   # Delete via dashboard
   # Verify database cascade deletes related emails
   ```

3. **Test API Costs Page**
   ```bash
   # Navigate to API Costs
   # Verify provider details display
   # Check optimization recommendations
   ```

4. **Test Auto-Refresh**
   ```bash
   # Enable auto-refresh
   # Wait 30 seconds
   # Verify checkbox stays checked
   ```

---

## 📦 Upgrade Instructions

### From v0.2.1 to v0.2.2

1. **Stop services**
   ```bash
   ./warmit.sh stop
   ```

2. **Pull latest code**
   ```bash
   git pull origin main
   ```

3. **Restart services** (migrations auto-apply)
   ```bash
   ./warmit.sh start
   ```

4. **Verify migration**
   ```bash
   docker compose -f docker/docker-compose.prod.yml exec postgres \
     psql -U warmit -d warmit -c "\d campaigns"

   # Should see next_send_time column
   ```

---

## 🐛 Bug Reports

Found an issue? Please report at:
https://github.com/Givaa/WarmIt/issues

---

**Made with ❤️ by [Givaa](https://github.com/Givaa)**
