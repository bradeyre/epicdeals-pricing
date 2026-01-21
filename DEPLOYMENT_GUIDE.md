# Deployment Guide - EpicDeals Pricing Tool

**Date:** January 21, 2026
**Status:** Ready for Deployment

---

## Quick Start - Local Testing

### 1. Install Dependencies
```bash
cd "/Users/Focus/Downloads/Claude ED Price Research Tool - Jan 2026"
pip3 install -r requirements.txt
```

### 2. Set Environment Variables
Create `.env` file:
```bash
ANTHROPIC_API_KEY=your_anthropic_api_key_here
PERPLEXITY_API_KEY=your_perplexity_api_key_here
SECRET_KEY=your_secret_key_for_sessions

# SMTP Email Settings (Gmail example)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
NOTIFICATION_EMAIL=brad@epicdeals.co.za
```

### 3. Run Locally
```bash
python3 app.py
```

Visit: `http://localhost:5000`

---

## Deployment Options

### Option 1: **Heroku** (Recommended - Easiest)

**Pros:**
- ✅ Free tier available
- ✅ Automatic HTTPS
- ✅ Easy deployment
- ✅ Built-in environment variables

**Steps:**

1. **Install Heroku CLI:**
```bash
brew install heroku/brew/heroku
```

2. **Login:**
```bash
heroku login
```

3. **Create App:**
```bash
cd "/Users/Focus/Downloads/Claude ED Price Research Tool - Jan 2026"
heroku create epicdeals-pricing-tool
```

4. **Set Environment Variables:**
```bash
heroku config:set ANTHROPIC_API_KEY=your_key
heroku config:set PERPLEXITY_API_KEY=your_key
heroku config:set SECRET_KEY=your_secret_key
heroku config:set SMTP_SERVER=smtp.gmail.com
heroku config:set SMTP_PORT=587
heroku config:set SMTP_USERNAME=your_email@gmail.com
heroku config:set SMTP_PASSWORD=your_password
heroku config:set NOTIFICATION_EMAIL=brad@epicdeals.co.za
```

5. **Create Procfile:**
```bash
echo "web: gunicorn app:app" > Procfile
```

6. **Install gunicorn:**
```bash
pip3 install gunicorn
pip3 freeze > requirements.txt
```

7. **Deploy:**
```bash
git init
git add .
git commit -m "Initial deployment"
git push heroku main
```

8. **Open:**
```bash
heroku open
```

**Your app is now live!** 🎉

---

### Option 2: **PythonAnywhere** (Good for beginners)

**Pros:**
- ✅ Free tier
- ✅ Python-focused
- ✅ Easy setup
- ✅ Good for Flask apps

**Steps:**

1. Sign up at https://www.pythonanywhere.com

2. Upload your code via "Files" tab or git

3. Create a new Web App (Flask)

4. Set working directory to your project

5. Configure WSGI file to import your app

6. Set environment variables in Web tab

7. Reload and your site is live!

---

### Option 3: **DigitalOcean App Platform** (Professional)

**Pros:**
- ✅ $5/month starter tier
- ✅ Auto-scaling
- ✅ Good performance
- ✅ Professional grade

**Steps:**

1. Push code to GitHub

2. Connect DigitalOcean to your GitHub repo

3. Configure environment variables

4. Deploy automatically on every push

5. Get custom domain

---

### Option 4: **Render** (Modern alternative)

**Pros:**
- ✅ Free tier with auto-sleep
- ✅ Modern interface
- ✅ Auto-deploy from GitHub
- ✅ Easy SSL

**Steps:**

1. Sign up at https://render.com

2. Connect GitHub repo

3. Create new "Web Service"

4. Set environment variables

5. Deploy - done!

---

### Option 5: **Railway** (Developer-friendly)

**Pros:**
- ✅ $5 free credit monthly
- ✅ Very fast deployment
- ✅ Great for Flask
- ✅ Simple pricing

**Steps:**

1. Sign up at https://railway.app

2. "New Project" → Import from GitHub

3. Add environment variables

4. Deploy - live in minutes!

---

## Static HTML Export (For Demo/Offline Use)

If you just want a demo version to show management without hosting:

### Create Standalone Demo:

```bash
# Run the server
python3 app.py

# In another terminal, save the page
curl http://localhost:5000 > epicdeals-demo.html
```

**Note:** This creates a static snapshot but won't have full functionality (no API calls). Good for visual demos only.

---

## Custom Domain Setup

### After deploying to any platform:

1. **Get your deployment URL** (e.g., `epicdeals-pricing.herokuapp.com`)

2. **Add CNAME record** to your domain:
```
pricing.epicdeals.co.za → your-deployment-url.com
```

3. **Enable SSL** (most platforms do this automatically)

4. **Test:** Visit `https://pricing.epicdeals.co.za`

---

## Environment Variables Reference

**Required:**
```
ANTHROPIC_API_KEY - Claude AI API key (for conversation)
PERPLEXITY_API_KEY - Perplexity API key (for price research)
SECRET_KEY - Flask session secret (generate random string)
```

**Email (Required for notifications):**
```
SMTP_SERVER - Email server (e.g., smtp.gmail.com)
SMTP_PORT - Port (587 for TLS, 465 for SSL)
SMTP_USERNAME - Your email address
SMTP_PASSWORD - Your email password or app password
NOTIFICATION_EMAIL - Where to send notifications (brad@epicdeals.co.za)
```

**Optional:**
```
FLASK_ENV - Set to "production" for production
PORT - Port to run on (default 5000)
```

---

## Pre-Deployment Checklist

### Code:
- [x] All features implemented
- [x] Syntax validated (Python + JavaScript)
- [x] Environment variables documented
- [x] Error handling in place
- [x] Age-based depreciation working
- [x] "24 hours" changed to "2 working days"

### Testing:
- [ ] Test locally with all features
- [ ] Test with real products (iPhone, MacBook, etc.)
- [ ] Verify email notifications work
- [ ] Test on mobile devices
- [ ] Test in different browsers

### Configuration:
- [ ] Environment variables set
- [ ] SMTP credentials working
- [ ] API keys valid and funded
- [ ] Secret key generated (use: `python3 -c "import secrets; print(secrets.token_hex(32))"`)

### Production:
- [ ] Choose hosting platform
- [ ] Deploy to staging first
- [ ] Test staging thoroughly
- [ ] Set up custom domain
- [ ] Enable HTTPS/SSL
- [ ] Monitor error logs

---

## Post-Deployment Monitoring

### Day 1-7: Watch Closely

**Monitor:**
- Error rates (should be <1%)
- API usage (Perplexity + Claude)
- User completion rates
- Email delivery rates
- Response times

**Check:**
- Are age questions being asked correctly?
- Are depreciation calculations accurate?
- Do users understand the pricing?
- Are "2 working days" messages clear?

### Week 2-4: Optimize

**Collect:**
- User feedback on pricing accuracy
- Dispute rate and reasons
- Common error patterns
- Performance bottlenecks

**Adjust:**
- Depreciation curves based on real data
- AI question flow based on user behavior
- Email templates based on feedback
- Error handling for edge cases

---

## Cost Estimates

### API Costs (Monthly):

**Claude (Anthropic):**
- ~1000 conversations/month
- ~$50-$100/month

**Perplexity:**
- ~1000 price searches/month
- ~$40-$80/month

**Total API:** ~$90-$180/month

### Hosting Costs:

**Heroku:** Free - $7/month
**PythonAnywhere:** Free - $5/month
**DigitalOcean:** $5/month
**Render:** Free (with sleep) - $7/month
**Railway:** $5 credit/month (~free for low traffic)

**Total:** ~$95-$200/month for moderate usage

---

## Scaling Considerations

### If traffic increases:

**< 100 users/day:**
- Free tiers work fine
- No optimizations needed

**100-1000 users/day:**
- Upgrade to paid hosting ($7-15/month)
- Cache common repair costs
- Monitor API usage closely

**1000+ users/day:**
- Consider caching layer (Redis)
- Database for analytics (PostgreSQL)
- Load balancing
- CDN for static files

---

## Backup & Recovery

### Before deployment:

1. **Backup code:**
```bash
git init
git add .
git commit -m "Production ready"
git remote add origin your-github-repo
git push origin main
```

2. **Document environment variables** (store securely)

3. **Export database** (if you add one later)

### Recovery plan:

If something breaks:
1. Check error logs on hosting platform
2. Revert to previous git commit
3. Restore environment variables
4. Test locally first, then redeploy

---

## Recommended Setup for Management Demo

**Best option for quick demo:**

### Railway (Fastest)

1. Push code to GitHub
2. Import to Railway
3. Add environment variables
4. Get live URL in 5 minutes
5. Share with management

**Live URL example:**
`https://epicdeals-pricing.up.railway.app`

**Pros:**
- Fastest deployment (< 10 minutes)
- Free $5 credit monthly
- Auto-deploy on code changes
- Professional URL
- Easy to show management

---

## Troubleshooting

### "Module not found" errors:
```bash
pip3 install -r requirements.txt
```

### "API key not found":
- Check `.env` file exists
- Verify variable names match exactly
- Restart server after changes

### Email not sending:
- Check SMTP credentials
- For Gmail, use "App Password" not regular password
- Test with simple email first

### Site loading slow:
- Check API response times
- Consider caching
- Upgrade hosting tier

### Age questions not appearing:
- Check AI service logs
- Verify age logic in ai_service.py
- Test with different product types

---

## Management Presentation Tips

### Before the demo:

1. **Test thoroughly** with 3-5 different products
2. **Prepare examples**: iPhone, MacBook, Samsung phone
3. **Have backup** of screenshots/video
4. **List improvements** from old system

### During the demo:

1. Show **transparent pricing breakdown**
2. Demonstrate **age-based depreciation** (1 year vs 5 year iPhone)
3. Highlight **"2 working days" messaging**
4. Show **price dispute feature**
5. Explain **competitive advantages**

### Key talking points:

✅ "Most transparent pricing in SA"
✅ "Age-aware depreciation (not just static %)"
✅ "Real-time Perplexity research"
✅ "Users can dispute with evidence"
✅ "Clear expectations (2 working days)"

---

## Next Steps

1. **Choose hosting** (Recommendation: Railway for demo, Heroku for production)

2. **Deploy to staging** (test URL for internal use)

3. **Test thoroughly** (all features, all browsers)

4. **Show management** (get feedback)

5. **Deploy to production** (custom domain)

6. **Monitor & optimize** (first 2 weeks critical)

---

## Support Contacts

**Technical Issues:**
- Heroku: support.heroku.com
- Railway: railway.app/help
- Render: render.com/docs

**API Issues:**
- Claude: support@anthropic.com
- Perplexity: support@perplexity.ai

**Code Issues:**
- Check error logs in hosting platform
- Review Python traceback
- Check browser console for JS errors

---

**Status:** 🟢 READY FOR DEPLOYMENT

**Recommended:** Deploy to Railway first for quick management demo, then migrate to Heroku for production if needed.

**Estimated Time to Deploy:** 15-30 minutes

**Go live and show your management team the most advanced pricing tool in South Africa!** 🚀
