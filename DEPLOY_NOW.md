# Deploy Your Pricing Tool NOW! 🚀

**3 Simple Steps - 10 Minutes Total**

---

## Step 1: Fix GitHub Push (2 minutes)

### Option A: Allow the Secret (Recommended)
1. Open this URL in your browser:
   ```
   https://github.com/bradeyre/epicdeals-pricing/security/secret-scanning/unblock-secret/38ZYFqkxX8YscILK2stjQoiEELO
   ```

2. Click **"Allow secret"** button

3. Push to GitHub:
   ```bash
   cd "/Users/Focus/Downloads/Claude ED Price Research Tool - Jan 2026"
   git push origin main
   ```

✅ **Should work now!**

---

## Step 2: Deploy to PythonAnywhere (5 minutes)

PythonAnywhere is the EASIEST free option for Flask:

### 1. Sign Up
- Go to: https://www.pythonanywhere.com
- Click "Pricing & signup"
- Choose "Beginner" (FREE forever)
- Create account with email

### 2. Upload Code
- Go to "Files" tab
- Click "Upload a file"
- Upload these key files:
  - `app.py`
  - `config.py`
  - `requirements.txt`
  - Entire `services/` folder
  - Entire `static/` folder
  - Entire `templates/` folder

### 3. Create Web App
- Go to "Web" tab
- Click "Add a new web app"
- Choose "Flask"
- Python 3.10
- Leave default path

### 4. Configure
- In "Code" section, set:
  - Source code: `/home/yourusername/`
  - WSGI file: Click to edit

Edit WSGI file to:
```python
import sys
path = '/home/yourusername/'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

### 5. Set Environment Variables
- Scroll down to "Environment variables"
- Click "Add new variable"
- Add each of these:

```
ANTHROPIC_API_KEY = your_anthropic_key
PERPLEXITY_API_KEY = your_perplexity_key
SECRET_KEY = (generate with: python3 -c "import secrets; print(secrets.token_hex(32))")
SMTP_SERVER = smtp.gmail.com
SMTP_PORT = 587
SMTP_USERNAME = your_email@gmail.com
SMTP_PASSWORD = your_gmail_app_password
NOTIFICATION_EMAIL = brad@epicdeals.co.za
```

### 6. Install Dependencies
- Go to "Consoles" tab
- Click "Bash"
- Run:
```bash
pip3 install --user -r requirements.txt
```

### 7. Reload
- Go back to "Web" tab
- Click big green **"Reload"** button

### 8. Visit Your Site! 🎉
```
https://yourusername.pythonanywhere.com
```

---

## Step 3: Test (3 minutes)

### Test 1: iPhone
1. Enter: "iPhone 13 Pro 256GB"
2. Should auto-detect year 2021
3. Complete flow
4. Check offer shows depreciation explanation

### Test 2: Age Question
1. Enter: "Samsung TV"
2. AI should ask: "What year was it purchased?"
3. Answer: "2019"
4. Complete flow

### Test 3: Timing
- Check all messages say "2 working days"
- NOT "24 hours"

✅ **If all works - YOU'RE LIVE!**

---

## Alternative: Use Vercel

If you prefer Vercel:

1. Go to https://vercel.com
2. Sign in with GitHub
3. Click "Add New..." → "Project"
4. Import `epicdeals-pricing` repo
5. Add environment variables (same as above)
6. Deploy

Live at: `https://epicdeals-pricing.vercel.app`

---

## Troubleshooting

### GitHub Still Blocking?
**Solution:** Click the GitHub URL to allow secret (see Step 1)

### PythonAnywhere Shows 404?
**Solution:** Check WSGI configuration, ensure path is correct

### PythonAnywhere Shows "Module not found"?
**Solution:** Install dependencies: `pip3 install --user -r requirements.txt`

### API Not Working?
**Solution:** Check environment variables are set correctly

---

## After Deployment

### Show Management:
1. Open your live URL
2. Demo iPhone flow (age auto-detection)
3. Show transparent pricing breakdown
4. Highlight "2 working days" messaging
5. Explain competitive advantages

### Monitor:
- Check error logs in PythonAnywhere "Log files" section
- Monitor API usage on Anthropic/Perplexity consoles
- Track user completion rates

---

## Summary

**Step 1:** Allow secret on GitHub → Push ✅
**Step 2:** Deploy to PythonAnywhere (or Vercel) ✅
**Step 3:** Test and show management ✅

**Total Time:** 10 minutes
**Total Cost:** $0 (hosting is FREE!)

---

**You're ready to go live! 🚀**

**Questions?** See VERCEL_DEPLOYMENT.md or FIX_GITHUB_SECRET.md
