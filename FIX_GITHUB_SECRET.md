# Fix GitHub Secret Scanning Issue

## Problem
GitHub detected your Perplexity API key in an old commit (`6050684`) and is blocking the push.

---

## Solution 1: Allow the Secret (Quickest - 1 minute)

Since this is your own private API key and the repo will be private, you can allow it:

### Steps:
1. **Click this URL** (from your error message):
   ```
   https://github.com/bradeyre/epicdeals-pricing/security/secret-scanning/unblock-secret/38ZYFqkxX8YscILK2stjQoiEELO
   ```

2. **Click "Allow secret"** button

3. **Push again:**
   ```bash
   cd "/Users/Focus/Downloads/Claude ED Price Research Tool - Jan 2026"
   git push origin main
   ```

✅ **Done!** This is safe if your repo is private and it's your own key.

---

## Solution 2: Rewrite Git History (More Secure - 5 minutes)

If you want to completely remove the secret from git history:

### Steps:

1. **Make sure repo is private** (check on GitHub)

2. **Install git-filter-repo** (if not installed):
   ```bash
   brew install git-filter-repo
   ```

3. **Remove the secret from all commits:**
   ```bash
   cd "/Users/Focus/Downloads/Claude ED Price Research Tool - Jan 2026"

   # Create a backup first
   cp -r . ../epicdeals-backup

   # Replace the secret in all commits
   git filter-repo --replace-text <(echo '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==>YOUR_KEY_HERE')
   ```

4. **Force push:**
   ```bash
   git remote add origin https://github.com/bradeyre/epicdeals-pricing.git
   git push --force origin main
   ```

⚠️ **Warning:** This rewrites history - only do if needed!

---

## Solution 3: Start Fresh (Nuclear Option - 10 minutes)

If the above don't work, create a new repo:

1. **Delete GitHub repo** (bradeyre/epicdeals-pricing)

2. **Create new repo** on GitHub

3. **Remove .git and start fresh:**
   ```bash
   cd "/Users/Focus/Downloads/Claude ED Price Research Tool - Jan 2026"
   rm -rf .git
   git init
   git add .
   git commit -m "Initial commit - production ready"
   git remote add origin https://github.com/bradeyre/NEW-REPO-NAME.git
   git push -u origin main
   ```

✅ **This guarantees no secrets in history**

---

## Best Practice: Rotate Your API Key

After exposing a key, best practice is to rotate it:

### Perplexity:
1. Go to https://www.perplexity.ai/settings/api
2. Delete the exposed key (`pplx-qlomB50...`)
3. Create a new key
4. Update your `.env` file
5. Update environment variables on hosting platform

### Anthropic:
1. Go to https://console.anthropic.com/settings/keys
2. Check if any Claude keys were exposed
3. Rotate if needed

---

## Recommended: Solution 1 (Allow Secret)

**For your case, I recommend Solution 1:**

✅ Quick (1 minute)
✅ Repo is private
✅ It's your own key
✅ Easy to rotate later

### Do This Now:

```bash
# 1. Click the GitHub URL to allow secret
# (from your error message)

# 2. Push again
cd "/Users/Focus/Downloads/Claude ED Price Research Tool - Jan 2026"
git push origin main
```

**That's it!** ✅

---

## After Fixing: Deploy to Vercel

Once the push works:

1. **Go to [vercel.com](https://vercel.com)**
2. **Import your GitHub repo**
3. **Add environment variables** (see VERCEL_DEPLOYMENT.md)
4. **Deploy!**

Your site will be live at: `https://epicdeals-pricing.vercel.app`

---

## Questions?

**"Is it safe to allow the secret?"**
- Yes, if your repo is PRIVATE
- The key is only visible to you
- You can rotate it anytime

**"Should I rotate my key?"**
- If repo is public: YES, immediately
- If repo is private: Optional, but good practice

**"Will this happen again?"**
- Not if you keep secrets in `.env` (which is in `.gitignore`)
- Never commit API keys in code or documentation

---

**Next Step:** Click the GitHub URL to allow the secret, then push! 🚀
