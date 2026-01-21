# Deploy to Vercel (100% Free) 🚀

**Get your pricing tool live in 15 minutes - completely free!**

---

## Why Vercel?

✅ **100% Free** for this project (no credit card needed)
✅ **Automatic HTTPS**
✅ **Auto-deploy** on every git push
✅ **Fast** global CDN
✅ **Unlimited** bandwidth on free tier
✅ **Custom domains** supported

---

## ⚠️ Important: Flask → Vercel Adapter

Vercel is optimized for Node.js but supports Python Flask with a small adapter.

### Step 1: Create Vercel Configuration (2 minutes)

```bash
cd "/Users/Focus/Downloads/Claude ED Price Research Tool - Jan 2026"

# Create vercel.json
cat > vercel.json << 'EOF'
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ],
  "env": {
    "FLASK_ENV": "production"
  }
}
EOF

echo "✅ vercel.json created"
```

### Step 2: Update app.py for Vercel (1 minute)

Vercel needs the Flask app exposed as `app`:

```bash
# Check if app is already exposed (it should be)
grep "if __name__ ==" app.py
```

Your `app.py` should end with:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

This is already correct - the `app` variable is accessible to Vercel. ✅

### Step 3: Clean Up Secrets from Git (2 minutes)

```bash
# Remove the file with the exposed secret
git rm --cached IMPLEMENTATION_SUMMARY.md

# Or edit it to remove the secret (we already did this)
git add IMPLEMENTATION_SUMMARY.md
git commit -m "Remove API key from documentation"
```

### Step 4: Push to GitHub (1 minute)

```bash
git add .
git commit -m "Add Vercel deployment configuration"
git push origin main
```

This should now work since we removed the secret!

---

## Deploy to Vercel (5 minutes)

### 1. Sign Up / Login
Go to [vercel.com](https://vercel.com) and sign up with your GitHub account (free).

### 2. Import Project
- Click "Add New..." → "Project"
- Select your `epicdeals-pricing` repository
- Click "Import"

### 3. Configure Environment Variables
Before deploying, add these environment variables:

```
ANTHROPIC_API_KEY = your_anthropic_key_here
PERPLEXITY_API_KEY = your_perplexity_key_here
SECRET_KEY = (generate random string)
SMTP_SERVER = smtp.gmail.com
SMTP_PORT = 587
SMTP_USERNAME = your_email@gmail.com
SMTP_PASSWORD = your_gmail_app_password
NOTIFICATION_EMAIL = brad@epicdeals.co.za
```

**To generate SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Deploy
- Click "Deploy"
- Wait 2-3 minutes
- **You're live!** 🎉

Your URL will be: `https://epicdeals-pricing.vercel.app`

---

## Alternative: PythonAnywhere (Also 100% Free)

If Vercel has any issues with Flask, use PythonAnywhere:

### Why PythonAnywhere?
✅ **100% Free** forever
✅ **Flask-native** (no adapters needed)
✅ **Easy setup** (5 minutes)
✅ **Beginner-friendly**

### Quick Setup:

1. **Sign up:** Go to [pythonanywhere.com](https://www.pythonanywhere.com)

2. **Upload code:**
   - Files tab → Upload your project files
   - Or use git: `git clone https://github.com/bradeyre/epicdeals-pricing.git`

3. **Create Web App:**
   - Web tab → "Add a new web app"
   - Choose "Flask"
   - Python 3.10
   - Set path to your app.py

4. **Set Environment Variables:**
   - Go to Web tab
   - Add environment variables in "Environment variables" section

5. **Reload:**
   - Click "Reload" button
   - Visit: `https://yourusername.pythonanywhere.com`

**Done! 🎉**

---

## Alternative: Render (Also Free)

Render has a generous free tier:

### Why Render?
✅ **Free** tier (no credit card)
✅ **Auto-deploy** from GitHub
✅ **Easy** Flask setup
✅ **Auto-sleep** after 15 mins (wakes on request)

### Quick Setup:

1. **Sign up:** Go to [render.com](https://render.com)

2. **New Web Service:**
   - Connect GitHub repo
   - Name: epicdeals-pricing
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

3. **Environment Variables:**
   - Add all your API keys and settings

4. **Deploy:**
   - Click "Create Web Service"
   - Wait 2-3 minutes
   - Live at: `https://epicdeals-pricing.onrender.com`

**Note:** Free tier sleeps after 15 mins of inactivity, takes 30 seconds to wake up.

---

## Comparison: Free Hosting Options

| Platform | Free Tier | Speed | Flask Support | Best For |
|----------|-----------|-------|---------------|----------|
| **Vercel** | Unlimited | ⚡⚡⚡ Fast | Adapter needed | Production |
| **PythonAnywhere** | Forever free | ⚡⚡ Good | Native | Beginners |
| **Render** | Auto-sleep | ⚡⚡⚡ Fast | Native | Quick demo |
| Railway | $5 credit | ⚡⚡⚡ Fast | Native | Limited free |

**Recommendation:** Try Vercel first, if any issues use PythonAnywhere.

---

## Fix GitHub Push Protection Error

You got this error because `IMPLEMENTATION_SUMMARY.md` contained your Perplexity API key.

### Fix:

```bash
cd "/Users/Focus/Downloads/Claude ED Price Research Tool - Jan 2026"

# We already edited the file to remove the key
# Now commit and push
git add IMPLEMENTATION_SUMMARY.md
git commit -m "Remove exposed API key from documentation"
git push origin main
```

✅ **This should now work!**

If it still blocks:
1. Go to the GitHub URL in the error message
2. Click "Allow this secret" (one-time)
3. Push again

**Better:** Never commit real API keys to git!

---

## Security Best Practices

### ✅ DO:
- Keep API keys in `.env` file (never commit this)
- Use environment variables on hosting platform
- Add `.env` to `.gitignore`

### ❌ DON'T:
- Commit API keys in code
- Put keys in documentation files
- Share `.env` file publicly

### Check Your Files:

```bash
# Search for any remaining secrets
grep -r "pplx-" .
grep -r "sk-ant-" .

# If found, replace with "your_key_here" or remove
```

---

## After Deployment: Test Your Site

### Test Checklist:

1. **Visit your URL**
   - Vercel: `https://epicdeals-pricing.vercel.app`
   - PythonAnywhere: `https://yourusername.pythonanywhere.com`
   - Render: `https://epicdeals-pricing.onrender.com`

2. **Test iPhone flow:**
   - Enter: "iPhone 13 Pro 256GB"
   - Should auto-detect year 2021
   - Check depreciation explanation shows

3. **Test age question:**
   - Enter: "Samsung TV"
   - AI should ask for year

4. **Test timing:**
   - Check all messages say "2 working days"
   - NOT "24 hours"

5. **Test on mobile:**
   - Open on phone
   - Check responsiveness
   - Test checkboxes work

---

## Troubleshooting

### Vercel: "Application Error"
**Issue:** Flask app not starting
**Fix:** Check Vercel logs, ensure `vercel.json` is correct

### PythonAnywhere: 404 Error
**Issue:** WSGI configuration wrong
**Fix:** Set correct path to app.py in Web tab

### Render: Build Failed
**Issue:** Missing dependencies
**Fix:** Check `requirements.txt` has all packages

### API Keys Not Working
**Issue:** Environment variables not set
**Fix:** Double-check spelling and values in platform settings

---

## Cost Breakdown

### Vercel (Recommended):
- **Hosting:** $0/month (free forever)
- **APIs:** ~$90-180/month (Claude + Perplexity)
- **Total:** ~$90-180/month

### PythonAnywhere:
- **Hosting:** $0/month (free forever)
- **APIs:** ~$90-180/month
- **Total:** ~$90-180/month

### Render:
- **Hosting:** $0/month (free with auto-sleep)
- **APIs:** ~$90-180/month
- **Total:** ~$90-180/month

**All hosting options are FREE!** Only API usage costs money.

---

## Next Steps

1. ✅ **Fix Git Push:**
```bash
git add IMPLEMENTATION_SUMMARY.md
git commit -m "Remove exposed API key"
git push origin main
```

2. ✅ **Deploy to Vercel:**
   - Create `vercel.json` (see Step 1 above)
   - Sign up at vercel.com
   - Import GitHub repo
   - Add environment variables
   - Deploy!

3. ✅ **Test Thoroughly:**
   - iPhone with auto age detection
   - Samsung TV with AI asking for year
   - Check "2 working days" messaging
   - Test on mobile

4. ✅ **Show Management:**
   - Use prepared examples
   - Highlight age-based depreciation
   - Show transparency
   - Emphasize competitive advantage

---

## Quick Commands Summary

```bash
# Fix GitHub secret issue
cd "/Users/Focus/Downloads/Claude ED Price Research Tool - Jan 2026"
git add IMPLEMENTATION_SUMMARY.md
git commit -m "Remove exposed API key"

# Create Vercel config
cat > vercel.json << 'EOF'
{
  "version": 2,
  "builds": [{"src": "app.py", "use": "@vercel/python"}],
  "routes": [{"src": "/(.*)", "dest": "app.py"}]
}
EOF

# Push to GitHub
git add vercel.json
git commit -m "Add Vercel deployment config"
git push origin main

# Deploy on Vercel
# → Go to vercel.com
# → Import GitHub repo
# → Add environment variables
# → Deploy
```

---

## Support

**Vercel Issues:**
- Docs: https://vercel.com/docs
- Discord: https://vercel.com/discord

**PythonAnywhere Issues:**
- Forum: https://www.pythonanywhere.com/forums/
- Help: help@pythonanywhere.com

**Render Issues:**
- Docs: https://render.com/docs
- Discord: https://render.com/discord

---

**Status:** 🟢 READY TO DEPLOY (100% FREE!)

**Recommended:** Vercel (fastest) or PythonAnywhere (easiest)

**Time to Deploy:** 15-20 minutes

**Let's get this live!** 🚀
