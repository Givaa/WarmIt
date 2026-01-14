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

### 4. API Key Detection with Quotes/Spaces

**Problem:** `start.sh` still failed to detect API keys even when properly configured, due to quotes and comment handling.

**Root Cause:** Simple string comparison didn't handle:
- Quotes around values: `OPENROUTER_API_KEY="sk-or-v1-xxx"`
- Inline comments: `OPENROUTER_API_KEY=sk-or-v1-xxx # my key`
- Extra spaces

**Fix:** Improved parsing with proper trimming:

```bash
# Before (failed with quotes)
OPENROUTER_KEY=$(grep "^OPENROUTER_API_KEY=" "$ENV_FILE" | cut -d'=' -f2)
if [ "$OPENROUTER_KEY" = "your_openrouter_key_here" ]; then

# After (handles quotes, spaces, comments)
OPENROUTER_KEY=$(grep "^OPENROUTER_API_KEY=" "$ENV_FILE" | cut -d'=' -f2 | tr -d ' "'"'"'' | sed 's/#.*//')
if echo "$OPENROUTER_KEY" | grep -q "your_openrouter_key_here"; then
```

**Now works with:**
- ✅ `OPENROUTER_API_KEY=sk-or-v1-xxx`
- ✅ `OPENROUTER_API_KEY="sk-or-v1-xxx"`
- ✅ `OPENROUTER_API_KEY='sk-or-v1-xxx'`
- ✅ `OPENROUTER_API_KEY=sk-or-v1-xxx # comment`
- ✅ `OPENROUTER_API_KEY = sk-or-v1-xxx` (spaces)

---

### 5. Poetry Installation Failures in Docker

**Problem:**
- Worker build: Step 4/9 `RUN curl` → CANCELED
- Dashboard build: Step 6/7 `RUN poetry config` → ERROR

**Root Cause:**
1. `curl` to install Poetry fails (network/proxy issues)
2. Poetry installation is complex and unreliable in Docker
3. Slower build times with Poetry

**Fix:** Replaced Poetry with pip using requirements.txt

**Before (Dockerfile):**
```dockerfile
# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi
```

**After (Dockerfile):**
```dockerfile
# Copy dependency files
COPY requirements.txt ./

# Install Python dependencies with pip
RUN pip install --no-cache-dir -r requirements.txt
```

**Advantages:**
- ✅ No network dependency (curl)
- ✅ Faster builds (pip is faster than poetry)
- ✅ More reliable (pip is built-in)
- ✅ Simpler Dockerfile
- ✅ Better Docker layer caching

**Applied to:**
- `docker/Dockerfile` (API, Worker, Beat, Watchdog)
- `docker/Dockerfile.dashboard` (Dashboard)

---

### 6. ModuleNotFoundError: No module named 'warmit'

**Problem:** Container `warmit-api` fails with `ModuleNotFoundError: No module named 'warmit'`

**Root Cause:** Dockerfile copies `src/` to `/app/src/`, creating path `/app/src/warmit/`, but uvicorn command looks for `warmit.main:app` at `/app/warmit/`

**Fix:** Changed COPY command to copy module directly to correct location

**Before:**
```dockerfile
COPY src/ ./src/
```

**After:**
```dockerfile
COPY src/warmit/ ./warmit/
```

**Result:** Module path is now `/app/warmit/` which matches the import path `warmit.main:app`

---

### 7. Warning: "no services to build" during pull

**Problem:** During `docker compose pull`, shows warning "no services to build"

**Root Cause:** `docker compose pull` without service names tries to pull all services, including those with `build:` directive, which generates a warning

**Fix:** Specify only image-based services in pull command

**Before:**
```bash
docker compose -f $COMPOSE_FILE pull
```

**After:**
```bash
docker compose -f $COMPOSE_FILE pull redis postgres logs
```

**Result:** Only pulls pre-built images (Redis, PostgreSQL, Dozzle), avoiding warning for buildable services

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
   - Better parsing with quotes/spaces/comments support

3. `docker/Dockerfile`
   - Removed Poetry installation
   - Now uses pip with requirements.txt
   - Simpler, faster, more reliable

4. `docker/Dockerfile.dashboard`
   - Removed Poetry installation
   - Now uses pip with requirements.txt
   - Simpler, faster, more reliable

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
