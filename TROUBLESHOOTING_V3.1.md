# v3.1 Troubleshooting Guide

**Updated:** February 10, 2026
**Latest commit:** `68d547f`
**SESSION_VERSION:** `v3.1.5`

---

## 🔍 KNOWN ISSUES & SOLUTIONS

### Issue 1: Questions Skipped — Goes Straight to Offer
**Status:** ✅ FIXED (commit `68d547f`)

**Root Cause:** Three interacting bugs:
1. `set_product_info()` added auto-extracted specs to `asked_fields` (should only be `collected_fields`)
2. `validate_ai_question()` rejected mandatory fields (condition) that were in `asked_fields` from auto-collection
3. Stale sessions persisted across deploys due to unchanged `SESSION_VERSION`

**If this reoccurs:**
1. Check `SESSION_VERSION` in `app.py` — must be bumped on each deploy
2. Check server logs for `APPROVE_QUESTIONS DEBUG` and `VALIDATE_AI_QUESTION DEBUG` prints
3. `asked_fields (should be empty)` should show `set()` after product identification
4. If `asked_fields` contains auto-collected fields, the `set_product_info()` fix has regressed

### Issue 2: Old Browser Session Caching
**Status:** ✅ MITIGATED with SESSION_VERSION

**Solution:** `SESSION_VERSION` in `app.py` auto-clears old sessions. If users report stale behavior:

#### Option A: Bump SESSION_VERSION
Change the version string in `app.py` and redeploy:
```python
SESSION_VERSION = "v3.1.6"  # Increment on each deploy
```

#### Option B: Manual Session Clear
User can open browser DevTools → Application → Cookies → delete `session` cookie

#### Option C: API Reset
```javascript
fetch('/api/reset-session', {method: 'POST'}).then(r => r.json()).then(console.log)
```

### Issue 3: Condition Question Not Asked
**Status:** ✅ FIXED (commit `0fbe8ba`)

**Fix:** `MANDATORY_QUESTION_FIELDS` set ensures condition is always asked first. If AI doesn't propose it, engine injects `['condition']`.

### Issue 4: Buyer Language in Acknowledgment
**Status:** ✅ FIXED (commit `11bfbcc`)

**Fix:** Updated `generate_acknowledgment()` prompt with explicit seller context and bad examples.

### Issue 5: Offer Screen Too Dark / Unreadable
**Status:** ✅ FIXED (commit `0f8046d`)

**Fix:** Card backgrounds #1a1a1a, borders #444, explicit white text for titles/prices.

---

## 🧪 VERIFICATION TESTS

### Test 1: Question Flow
```javascript
// Paste in browser console after clearing session
fetch('/api/reset-session', {method: 'POST'})
.then(() => fetch('/api/message/v3', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: 'iPhone 16 Pro 256GB' })
}))
.then(r => r.json())
.then(data => {
    console.log('Field asked:', data.field_name);
    console.log('Should be "condition":', data.field_name === 'condition');
    console.log('IMEI warning:', data.imei_warning);
    console.log('Should calculate:', data.should_calculate);
});
```

**Expected:**
- `field_name: "condition"` (NOT "storage")
- `imei_warning: true`
- `should_calculate: false`

### Test 2: IMEI Detection
Phones, tablets, smartwatches should show `imei_warning: true`.
Laptops, TVs, appliances should show `imei_warning: false` (or undefined).

### Test 3: Category Limits
| Category | Expected Limit |
|----------|---------------|
| Electronics (phones, laptops) | 4 |
| Vehicle (cars, bikes) | 6 |
| Appliance (Dyson, fridge) | 3 |
| Fashion (sneakers, bags) | 3 |
| Furniture (couch, desk) | 2 |

---

## 🔍 SERVER LOG READING GUIDE

After the fixes in commit `68d547f`, the server logs show detailed debug info at every decision point:

### Product Identification
```
🎯 PRODUCT IDENTIFIED: Apple iPhone 16 Pro
   Category: phone → electronics
   Question limit: 4
   IMEI device: True
   Auto-collected fields: ['storage', 'year']
   asked_fields (should be empty): set()    ← KEY: Must be empty!
```

### Question Approval
```
📋 APPROVE_QUESTIONS DEBUG:
   Proposed: ['condition', 'unlock_status', 'color']
   Mandatory: ['condition']
   Optional: ['unlock_status', 'color']
   Ordered: ['condition', 'unlock_status', 'color']
   asked_fields: set()
   collected_fields: ['storage', 'year']
   question_count: 0, limit: 4
   ⏭️  Skipping 'storage' - auto-collected from input
   ✅ Approved questions: ['condition', 'unlock_status', 'color']
```

### Question Validation
```
🔍 VALIDATE_AI_QUESTION DEBUG:
   Field: condition
   Is mandatory: True
   In asked_fields: False
   In collected_fields: False
   question_count: 0, limit: 4

   ❓ Question 1/4: condition
```

### Phase 1 Decision
```
🔑 PHASE 1 DECISION POINT:
   approved_questions: ['condition', 'unlock_status', 'color']
   engine.asked_fields: set()
   engine.collected_fields: ['storage', 'year']
   engine.question_count: 0
```

**Red flags to watch for:**
- `asked_fields (should be empty): {'storage', 'year'}` → Bug 1 has regressed
- `approved_questions: []` → No questions approved, will skip to calculation
- `Is mandatory: True` + `valid: False` → Bug 2 has regressed

---

## 📋 DEBUGGING CHECKLIST

If questions are being skipped:

- [ ] Check `SESSION_VERSION` — has it been bumped since last deploy?
- [ ] Check server logs for `asked_fields (should be empty): set()` after product identification
- [ ] Check server logs for `APPROVE_QUESTIONS DEBUG` — are questions being approved?
- [ ] Check server logs for `VALIDATE_AI_QUESTION DEBUG` — is validation passing?
- [ ] Check server logs for `PHASE 1 DECISION POINT` — what's the approved list?
- [ ] Clear browser session / use incognito
- [ ] Test via API directly (see Test 1 above)

---

## 📊 TEST MATRIX

| # | Product | Expected Qs | Must NOT Ask | IMEI? |
|---|---------|-------------|--------------|-------|
| 1 | iPhone 14 128GB | 2-3 | Storage | Yes |
| 2 | iPhone 16 Pro 256GB | 2-3 | Storage, Year | Yes |
| 3 | 2019 VW Polo 1.0 TSI | 4-6 | — | No |
| 4 | Nike AJ4 Military Black | 1-2 | Unlock, Contract | No |
| 5 | Dyson Airwrap | 2-3 | Unlock | No |
| 6 | Weylandts leather couch | 1-2 | Storage, Unlock | No |
| 7 | Samsung 65" QLED TV | 2-3 | Size | No |
| 8 | MacBook Air M2 16GB | 2-3 | RAM | No |
| 9 | Samsung Galaxy Tab S9 | 2-3 | — | Yes |
| 10 | Apple Watch Series 9 | 2-3 | — | Yes |

---

## 🆘 ESCALATION

If fixes don't resolve the issue:

1. **Check Render logs** — All debug prints will show exact flow
2. **Compare logs to expected output** in "Server Log Reading Guide" above
3. **If `asked_fields` is not empty** after product identification → `set_product_info()` regression
4. **If approved_questions is empty** → Check `approve_questions()` logic, mandatory injection
5. **If validation fails** → Check `validate_ai_question()` mandatory exemption
6. **If session is stale** → Bump `SESSION_VERSION` and redeploy

---

**Last updated:** Commit `68d547f` — All known issues resolved
