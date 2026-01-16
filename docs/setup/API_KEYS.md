# Getting Free API Keys for WarmIt

WarmIt uses AI models to generate natural-sounding email content. To avoid rate limits, you can add multiple free API keys as fallbacks.

---

## OpenRouter (Recommended - 50 Free Requests/Day)

OpenRouter provides access to many free AI models including Llama 3.3 70B.

### 1. Create Account

1. Go to [https://openrouter.ai/](https://openrouter.ai/)
2. Click **Sign In** (top right)
3. Click **Sign Up**
4. Create account with email or Google

### 2. Get API Key

1. Go to [https://openrouter.ai/settings/keys](https://openrouter.ai/settings/keys)
2. Click **Create Key**
3. Give it a name (e.g., "WarmIt Production")
4. (Optional) Set a credit limit for safety
5. Copy the API key (starts with `sk-or-v1-...`)

⚠️ **Important**: Save the key immediately! You won't be able to view it again.

### 3. Add to WarmIt

Edit `docker/.env`:

```bash
# Primary key
OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY_HERE

# Optional: Add more OpenRouter keys for redundancy
OPENROUTER_API_KEY_2=sk-or-v1-ANOTHER_KEY
OPENROUTER_API_KEY_3=sk-or-v1-THIRD_KEY
```

### Free Tier Limits

- **50 requests per day** per key (resets at midnight UTC)
- Free models: `meta-llama/llama-3.3-70b-instruct:free`
- After limit: Need to add credits or wait for reset

**Pro Tip**: Create multiple OpenRouter accounts (different emails) to get multiple free keys!

---

## Groq (Alternative - Very Fast)

Groq offers extremely fast inference with generous free tier.

### 1. Create Account

1. Go to [https://console.groq.com/](https://console.groq.com/)
2. Sign up with Google or email
3. Verify your email

### 2. Get API Key

1. Go to [API Keys section](https://console.groq.com/keys)
2. Click **Create API Key**
3. Name it (e.g., "WarmIt")
4. Copy the key (starts with `gsk_...`)

### 3. Add to WarmIt

Edit `docker/.env`:

```bash
# Groq as fallback
GROQ_API_KEY=gsk_YOUR_KEY_HERE
GROQ_API_KEY_2=gsk_ANOTHER_KEY  # Optional
```

### Free Tier Limits

- **30 requests per minute**
- **14,400 requests per day**
- Free models: `llama-3.3-70b-versatile`

---

## OpenAI (Paid Only - Not Recommended)

OpenAI requires payment but offers high-quality models.

### Get API Key

1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create account and add payment method
3. Create API key
4. Add to `docker/.env`:

```bash
OPENAI_API_KEY=sk-YOUR_KEY_HERE
OPENAI_MODEL=gpt-4o-mini  # Cheapest option
```

### Pricing

- GPT-4o-mini: $0.15 per 1M input tokens
- Not free, but very cheap for email generation

---

## How Fallback Works

WarmIt tries API keys in this order:

1. `OPENROUTER_API_KEY` (primary)
2. `OPENROUTER_API_KEY_2` (fallback 1)
3. `OPENROUTER_API_KEY_3` (fallback 2)
4. `GROQ_API_KEY` (fallback 3)
5. `GROQ_API_KEY_2` (fallback 4)
6. `OPENAI_API_KEY` (fallback 5)
7. **Local templates** (no AI, always works)

When one key hits rate limit or fails, it automatically switches to the next.

---

## Recommended Setup

### Free Users (No Budget)

```bash
# Get 2-3 OpenRouter keys (different emails)
OPENROUTER_API_KEY=sk-or-v1-KEY1
OPENROUTER_API_KEY_2=sk-or-v1-KEY2
OPENROUTER_API_KEY_3=sk-or-v1-KEY3

# Add Groq as backup
GROQ_API_KEY=gsk_YOUR_KEY
```

**Result**: ~200 free AI-generated emails per day (50×3 OpenRouter + Groq backup)

### Production Users (Low Budget)

```bash
# Primary: OpenRouter (50 free/day)
OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY

# Fallback: Groq (very fast, generous limits)
GROQ_API_KEY=gsk_YOUR_KEY

# Last resort: OpenAI (paid, high quality)
OPENAI_API_KEY=sk-YOUR_KEY
```

**Result**: 50 free emails/day, then fast Groq, then paid OpenAI if needed

---

## After Adding Keys

1. Save `docker/.env`
2. Restart services:
   ```bash
   ./warmit.sh restart
   ```
3. Verify keys loaded:
   ```bash
   ./warmit.sh logs api | grep "Valid API configs"
   ```

---

## Troubleshooting

### "Rate limit exceeded"

- You hit the daily limit for that key
- WarmIt auto-switches to next key
- Add more keys or wait for reset (midnight UTC)

### "Invalid API Key"

- Key is wrong or expired
- Regenerate key on provider's website
- Update `docker/.env`
- Restart: `./warmit.sh restart`

### "All API providers exhausted"

- All your keys hit rate limits
- WarmIt falls back to local templates (no AI)
- Add more keys or wait for reset

---

## Links

- OpenRouter Keys: [https://openrouter.ai/settings/keys](https://openrouter.ai/settings/keys)
- OpenRouter Docs: [https://openrouter.ai/docs](https://openrouter.ai/docs)
- Groq Console: [https://console.groq.com/keys](https://console.groq.com/keys)
- OpenAI Keys: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
