# Render Deployment Guide for WhatsApp Messenger

## Problem: Model Deprecation Error

If you're seeing this error:
```
Error code: 400 - {'error': {'message': 'The model `llama-3.1-70b-versatile` has been decommissioned and is no longer supported...'}}
```

## Solution: Update to Supported Model

The model `llama-3.1-70b-versatile` has been decommissioned by Groq. Use `llama-3.1-8b-instant` instead (this is available for free tier users).

## Correct Render Configuration

Update your Render web service with these settings:

### Basic Settings
- **Name**: whatsapp-messenger
- **Region**: Singapore (closest to India)
- **Branch**: main
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile - app:app`
- **Instance Type**: Free

### Environment Variables (Advanced → Add Environment Variable)

| Key | Value |
|-----|-------|
| `LM_STUDIO_API_KEY` | `gsk_YOUR_ACTUAL_GROQ_KEY_HERE` ← Replace with your real Groq API key |
| `LM_STUDIO_BASE_URL` | `https://api.groq.com/openai/v1` |
| `MODEL_NAME` | `llama-3.1-8b-instant` ← **UPDATED - This is the fix!** |
| `MAX_TOKENS` | `8000` |
| `PYTHON_VERSION` | `3.11.0` |

## Important Notes

1. **API Key**: Make sure to use your actual Groq API key, not the placeholder
2. **Model Name**: Use `llama-3.1-8b-instant` (this is available for free tier users)
3. **Model Access**: Some models like `llama-3.3-70b-versatile` are enterprise-only and not available to free accounts
4. **Base URL**: Use `https://api.groq.com/openai/v1` for Groq AI

## Alternative Models (If Needed)

If you encounter issues with `llama-3.1-8b-instant`, try these alternatives:

- `llama3-70b-8192` - Meta Llama 3 70B (smaller context window)
- `openai/gpt-oss-20b` - OpenAI's 20B model
- `openai/gpt-oss-120b` - OpenAI's 120B model (more expensive)
- `gemma2-9b-it` - Google's Gemma 2 9B model

## Verification Steps

1. Update the environment variable `MODEL_NAME` to `llama-3.3-70b-versatile`
2. Save your Render configuration
3. Wait for the deployment to complete
4. Test the application

## Getting Groq API Key

1. Go to https://console.groq.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `gsk_`)
6. Use it in your Render environment variables

## Troubleshooting

### Still getting model errors?
- Double-check the model name spelling
- Ensure you're using `llama-3.1-8b-instant` (this is confirmed to work for free tier)
- Avoid enterprise models like `llama-3.3-70b-versatile` (requires paid plan)
- Check Groq's status page: https://status.groq.com
- Verify your API key has proper permissions

### API Key errors?
- Verify your API key is valid and not expired
- Ensure the key has proper permissions
- Check that you copied the full key (it's long)

### Deployment issues?
- Check Render logs for detailed error messages
- Verify all environment variables are set correctly
- Ensure the build command completes successfully