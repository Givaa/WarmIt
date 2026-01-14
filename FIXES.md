# Recent Fixes

## Issues Fixed (2026-01-14)

### 1. Docker Compose `version` Warning

**Problem:** Docker Compose showed warning about obsolete `version` attribute.

**Fix:** Removed `version: '3.8'` from `docker/docker-compose.prod.yml`

**Reason:** Docker Compose v2+ doesn't require the version field anymore.

---

### 2. API Key Validation Bug

**Problem:** `start.sh` failed validation even when only one API key (OpenRouter OR Groq) was configured, because it checked for default text in both keys.

**Before:**
```bash
# Failed if ANY default text was present
if grep -q "your_openrouter_key_here\|your_groq_key_here" "$ENV_FILE"; then
```

**After:**
```bash
# Checks only the selected provider
AI_PROVIDER=$(grep "^AI_PROVIDER=" "$ENV_FILE" | cut -d'=' -f2)

if [ "$AI_PROVIDER" = "openrouter" ]; then
    # Check only OpenRouter key
elif [ "$AI_PROVIDER" = "groq" ]; then
    # Check only Groq key
fi
```

**Now works correctly:**
- ✅ OpenRouter only: Checks only `OPENROUTER_API_KEY`
- ✅ Groq only: Checks only `GROQ_API_KEY`
- ✅ Warns if provider not set or invalid

---

### 3. Docker Build Context Error

**Problem:** Build failed with error `/dashboard not found` and `failed to compute cache key`.

**Root Cause:** Build context in `docker-compose.prod.yml` was set to `.` (current directory = `docker/`), but Dockerfiles tried to copy files from project root:
- `COPY pyproject.toml` ← Not in docker/
- `COPY dashboard/` ← Not in docker/
- `COPY src/` ← Not in docker/

**Fix:** Changed build context to `..` (parent directory = project root) for all services:

```yaml
# Before
services:
  api:
    build:
      context: .              # docker/ directory
      dockerfile: Dockerfile

# After
services:
  api:
    build:
      context: ..             # project root
      dockerfile: docker/Dockerfile
```

**Applied to:**
- `api` service
- `worker` service
- `beat` service
- `dashboard` service
- `watchdog` service

**Now builds correctly** because:
- Context = `/path/to/WarmIt/` (project root)
- Can access `pyproject.toml`, `src/`, `dashboard/`, `scripts/`
- Dockerfile paths updated: `dockerfile: docker/Dockerfile`

---

## Testing

After these fixes, the following should work:

```bash
# 1. Clone
git clone <repo> && cd warmit

# 2. Configure
nano docker/.env
# Add ONLY one key:
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# 3. Start (should build without errors)
./start.sh
```

**Expected:**
- ✅ No version warning
- ✅ API key validation passes
- ✅ Build succeeds for all services
- ✅ All 8 containers start

---

## Files Modified

1. `docker/docker-compose.prod.yml`
   - Removed `version: '3.8'`
   - Changed `context: .` → `context: ..` for all build services
   - Changed `dockerfile: Dockerfile` → `dockerfile: docker/Dockerfile`

2. `start.sh`
   - Improved API key validation logic
   - Now checks only the selected provider's key

---

## Verification

```bash
# Check Docker Compose is valid
cd docker
docker compose config

# Should show no warnings and valid config
```

---

## Related Documentation

- [docker/README.md](docker/README.md) - Docker configuration details
- [docs/UBUNTU_QUICKSTART.md](docs/UBUNTU_QUICKSTART.md) - Quick start guide
- [docs/SYSTEM_REQUIREMENTS.md](docs/SYSTEM_REQUIREMENTS.md) - System requirements
