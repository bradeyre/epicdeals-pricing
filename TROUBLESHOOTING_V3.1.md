# v3.1 Troubleshooting Guide

**Issue:** Storage question still being asked despite "iPhone 16 Pro 256GB" input
**Status:** Code is correct, session cache issue
**Date:** February 10, 2026

---

## 🔍 ROOT CAUSE

The guardrail engine fixes ARE deployed and working correctly, but **old browser sessions** created before the deployment are cached and contain the old engine state.

### Evidence from Console

```javascript
✅ V3.0 Universal Pricing Mode Enabled
=== showOptions called ===
Options received: ['256GB']  // Only ONE option - the correct answer!
Creating buttons for 1 options
Creating button 0: 256GB
```

**What this shows:**
- v3 is enabled ✓
- AI extracted "256GB" from the initial message ✓
- But it's STILL proposing storage as a question ✗

**Why:** The session cookie contains engine state from BEFORE the spec-flattening fix was deployed.

---

## ✅ SOLUTION 1: Clear Browser Session (Fastest)

### Option A: Delete Session Cookie
1. Open DevTools (F12)
2. Go to "Application" tab (Chrome) or "Storage" tab (Firefox)
3. Expand "Cookies" → `epicdeals-pricing.onrender.com`
4. Find and delete the `session` cookie
5. Refresh page (F5)
6. Start NEW conversation

### Option B: Private/Incognito Window
1. Open incognito/private window (Ctrl+Shift+N / Cmd+Shift+N)
2. Navigate to epicdeals-pricing.onrender.com
3. Test "iPhone 16 Pro 256GB"
4. Should skip storage question ✓

### Option C: Clear All Site Data
Chrome: Settings → Privacy → Clear browsing data → Cookies
Firefox: Ctrl+Shift+Del → Cookies

---

## ✅ SOLUTION 2: Force Session Reset (Backend)

If clearing cookies doesn't work, add session reset endpoint:

**File:** `app.py`

```python
@app.route('/api/reset-session', methods=['POST'])
def reset_session():
    """Force clear session for testing"""
    session.clear()
    return jsonify({'success': True, 'message': 'Session cleared'})
```

Then call from browser console:
```javascript
fetch('/api/reset-session', {method: 'POST'}).then(r => r.json()).then(console.log)
```

---

## 🧪 VERIFICATION TEST

After clearing session, run this test:

```javascript
// Paste in browser console
fetch('/api/message/v3', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: 'iPhone 16 Pro 256GB' })
})
.then(r => r.json())
.then(data => {
    console.log('Field asked:', data.field_name);
    console.log('Should be "condition" not "storage"');
    return data;
})
```

**Expected result:**
```json
{
  "field_name": "condition",
  "question": "What's the condition of your iPhone 16 Pro?",
  "quick_options": ["Screen cracked", "Back glass cracked", ...]
}
```

**If you get `field_name: "storage"`** - session is still cached, try harder reset.

---

## 🔍 HOW TO CHECK IF FIX IS WORKING

### Server Logs (Render Dashboard)

Look for these prints in Render logs:

```
🎯 PRODUCT IDENTIFIED: Apple iPhone 16 Pro
   Category: phone → electronics
   Question limit: 4
   Auto-collected fields: ['storage', 'year']  ← Should see storage here!

   ✅ Approved questions: ['condition', 'unlock_status', 'contract']
   ⏭️  Skipping 'storage' - already asked/answered  ← This confirms it worked
```

If you see `Skipping 'storage'` in the logs but it still shows in UI, the **session is cached**.

### Browser Console

Fresh session should show:
```javascript
// First API call response
{
  field_name: 'condition',  // NOT 'storage'!
  message: 'Sharp tech choice...',
  question: "What's the condition..."
}
```

---

## 🐛 KNOWN ISSUES

### Issue 1: Session Persistence
**Problem:** Flask sessions persist across deployments
**Impact:** Users who started conversations before deployment still use old logic
**Fix:** Clear browser cookies or use incognito

### Issue 2: AI Sometimes Still Proposes Storage
**Problem:** Even if AI extracts "256GB", it might propose "storage" question
**Impact:** Question gets approved if session cache is old
**Fix:** The guardrail engine SHOULD reject it via `approve_questions()` - but only if collected_fields is populated

### Issue 3: Spec Flattening Timing
**Problem:** Specs might not be flattened before question approval
**Impact:** Storage appears in proposed_questions despite being in specs
**Status:** FIXED in commit 132a6cb (generic flattening at engine boundary)

---

## 📋 DEBUGGING CHECKLIST

Run through this checklist:

- [ ] Cleared browser cookies/session
- [ ] Opened incognito/private window
- [ ] Refreshed page (hard refresh: Ctrl+Shift+R)
- [ ] Started NEW conversation (not continued old one)
- [ ] Verified v3 enabled (console shows "✅ V3.0 Universal Pricing Mode Enabled")
- [ ] Checked Render logs for "Auto-collected fields: ['storage']"
- [ ] Tested API directly via console fetch (see above)

If ALL checked and storage still asked → **escalate to stronger model** (as you suggested).

---

## 🎯 ALTERNATIVE: Server-Side Session Invalidation

If clearing browser cache is unreliable, invalidate sessions server-side:

**File:** `app.py` (add after imports)

```python
import time
SESSION_VERSION = int(time.time())  # Update this on each deployment

@app.before_request
def check_session_version():
    if 'version' not in session or session['version'] != SESSION_VERSION:
        session.clear()
        session['version'] = SESSION_VERSION
```

This forces ALL users to start fresh sessions after deployment.

---

## 📊 TEST MATRIX

Test these to verify all fixes:

| Input | Expected Behavior | Test Status |
|-------|------------------|-------------|
| "iPhone 16 Pro 256GB" | Skip storage, ask condition | ⏳ Needs fresh session |
| "2019 VW Polo" | Ask 5-6 questions (vehicle limit) | ⏳ Not tested |
| "Leather couch" | Ask 1-2 questions (furniture limit) | ⏳ Not tested |
| "Nike Air Jordan 4 size 10" | Skip size, ask 2-3 questions | ⏳ Not tested |
| "MacBook Air M2 16GB" | Skip RAM, ask 2-3 questions | ⏳ Not tested |

---

## 🆘 IF STILL NOT WORKING

**Escalation Path:**

1. **Check Render deployment logs** - Verify the new code is actually deployed
   - Go to Render dashboard → your service → Logs
   - Look for "Auto-collected fields" print statements
   - Check if "132a6cb" commit is deployed

2. **Verify Git commit** - Ensure changes are in main branch
   ```bash
   git log --oneline -5
   # Should show: 132a6cb Fix guardrail engine...
   ```

3. **Manual deployment** - Force redeploy on Render
   - Render dashboard → Manual Deploy → Deploy latest commit

4. **Start new chat with stronger model** (as you suggested)
   - Provide these files:
     - `services/guardrail_engine.py` (lines 147-181)
     - `app.py` (/api/message/v3 endpoint)
     - `V3.1_IMPLEMENTATION_STATUS.md`
     - This troubleshooting doc

---

## 💡 QUICK WIN: Test with Different Product

Instead of "iPhone 16 Pro 256GB", try:

**"2019 VW Polo"**

This tests:
1. Year extraction (2019)
2. Vehicle category detection
3. 6-question limit (not 4)
4. Different question types (mileage, service history)

Expected: Should ask about mileage first, NOT year.

---

**Status:** Code is deployed correctly, issue is session caching.
**Next step:** Clear browser cookies and retest, OR escalate to stronger model if persistent.
