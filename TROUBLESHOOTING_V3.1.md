# v3.1 Troubleshooting Guide

**Updated:** February 10, 2026
**Latest commit:** See git log
**SESSION_VERSION:** `v3.1.9`

---

## KNOWN ISSUES & SOLUTIONS

### Issue 1: Questions Skipped — Goes Straight to Offer
**Status:** FIXED (commit `68d547f`)

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
**Status:** MITIGATED with SESSION_VERSION

**Solution:** `SESSION_VERSION` in `app.py` auto-clears old sessions. If users report stale behavior:

#### Option A: Bump SESSION_VERSION
Change the version string in `app.py` and redeploy:
```python
SESSION_VERSION = "v3.1.10"  # Increment on each deploy
```

#### Option B: Manual Session Clear
User can open browser DevTools > Application > Cookies > delete `session` cookie

#### Option C: API Reset
```javascript
fetch('/api/reset-session', {method: 'POST'}).then(r => r.json()).then(console.log)
```

### Issue 3: Condition Question Not Asked
**Status:** FIXED (commit `0fbe8ba`)

**Fix:** `MANDATORY_QUESTION_FIELDS` set ensures condition is always asked first. If AI doesn't propose it, engine injects `['condition']`.

### Issue 4: Buyer Language in Acknowledgment
**Status:** FIXED (commit `11bfbcc`)

**Fix:** Updated `generate_acknowledgment()` prompt with explicit seller context and bad examples.

### Issue 5: Offer Screen Too Dark / Unreadable
**Status:** FIXED (commit `0f8046d`)

**Fix:** Card backgrounds #1a1a1a, borders #444, explicit white text for titles/prices.

### Issue 6: Session Cookie Overflow — Engine Loses Context Mid-Conversation (CRITICAL)
**Status:** FIXED

**Symptom:** After answering the first question (e.g. condition), the bot says "Eish, Unknown Unknown devices..." and re-asks product identification questions. The engine loses all product context between turns.

**Root Cause:** Flask's default session uses **signed cookies stored in the browser** with a hard **~4KB limit**. The `GuardrailEngine.to_dict()` method was storing `conversation_turns` (a growing list of all user+AI messages). After 2-3 turns, the serialized session exceeded 4KB. When this happens, **the cookie is silently dropped by the browser** — the next request gets a blank session, creating a fresh engine with `product_identified = False`, which re-runs Phase 1 (product identification) on what was actually an answer to a question.

**Why "Unknown Unknown":** The user's answer (e.g. "Battery health under 85%") was sent to `identify_product()` as if it were a product name. The AI couldn't identify it, returned the fallback `brand: 'Unknown', model: 'Unknown'`, and the acknowledgment used those values.

**Fix (3 parts):**
1. **Removed `conversation_turns` from `to_dict()`** — They were only used by `get_state_for_prompt()` which can work from `collected_fields` and `asked_fields` alone. This saves ~800-1600 bytes per conversation.
2. **Removed `product_info_v3` from session** — This was a redundant copy of `engine.product_info` that was written but never read. Wasted ~200-400 bytes.
3. **Added `_log_session_size()` helper** — Estimates cookie size after each save and logs a warning if approaching the 4KB limit.

**How to detect if this regresses:**
- Server logs will show `SESSION SIZE` after saves with percentage of 4KB limit
- If `engine_v3 in session: False` appears in Phase 2 logs, the cookie was dropped
- If `Product identified: False` appears when user is answering a question, session was lost
- Any `SESSION SIZE` log showing >90% is a critical warning

**Key rule: NEVER store growing data in Flask's cookie session.** If growing data must be stored, switch to server-side sessions (Flask-Session with filesystem or Redis backend).

---

## VERIFICATION TESTS

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

### Test 2: Multi-Turn Persistence (NEW — validates Issue 6 fix)
```javascript
// Test that session persists across multiple question/answer turns
fetch('/api/reset-session', {method: 'POST'})
.then(() => fetch('/api/message/v3', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: 'iPhone 16 Pro 256GB' })
}))
.then(r => r.json())
.then(data => {
    console.log('Q1 field:', data.field_name, '(should be condition)');
    // Answer the condition question
    return fetch('/api/message/v3', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: 'Screen cracked' })
    });
})
.then(r => r.json())
.then(data => {
    console.log('Q2 field:', data.field_name, '(should NOT be condition again)');
    console.log('Should calculate:', data.should_calculate);
    console.log('Has question:', !!data.question);
    // KEY CHECK: field_name should be a DIFFERENT field (not condition, not "type")
    // And question should be about the iPhone, not "what device?"
});
```

**Expected:**
- Q1: `field_name: "condition"`
- Q2: `field_name` is something like "unlock_status" or "battery_health" (NOT "condition" again)
- Q2 should NOT have `should_calculate: false` with a question about device type

### Test 3: IMEI Detection
Phones, tablets, smartwatches should show `imei_warning: true`.
Laptops, TVs, appliances should show `imei_warning: false` (or undefined).

### Test 4: Category Limits
| Category | Expected Limit |
|----------|---------------|
| Electronics (phones, laptops) | 4 |
| Vehicle (cars, bikes) | 6 |
| Appliance (Dyson, fridge) | 3 |
| Fashion (sneakers, bags) | 3 |
| Furniture (couch, desk) | 2 |

---

## SERVER LOG READING GUIDE

### Session State Check (NEW)
```
============================================================
V3 MESSAGE: Screen cracked
Engine state: identifying
Product identified: True
Session keys: ['_version', 'engine_v3', 'current_field_v3']
engine_v3 in session: True        <-- KEY: Must be True in Phase 2!
============================================================
```

**Red flag:** If `engine_v3 in session: False` when the user is answering a question, the session cookie was dropped (overflow).

### Session Size Monitoring (NEW)
```
   SESSION SIZE after Phase 1 save: ~1200 bytes (29% of 4KB limit)
   SESSION SIZE after Phase 2 next-question save: ~1400 bytes (34% of 4KB limit)
```

If you see >90%, investigate what's growing in the session.

### Product Identification
```
PRODUCT IDENTIFIED: Apple iPhone 16 Pro
   Category: phone > electronics
   Question limit: 4
   IMEI device: True
   Auto-collected fields: ['storage', 'year']
   asked_fields (should be empty): set()    <-- KEY: Must be empty!
```

### Question Approval
```
APPROVE_QUESTIONS DEBUG:
   Proposed: ['condition', 'unlock_status', 'color']
   Mandatory: ['condition']
   Optional: ['unlock_status', 'color']
   Ordered: ['condition', 'unlock_status', 'color']
   asked_fields: set()
   collected_fields: ['storage', 'year']
   question_count: 0, limit: 4
   Skipping 'storage' - auto-collected from input
   Approved questions: ['condition', 'unlock_status', 'color']
```

### Question Validation
```
VALIDATE_AI_QUESTION DEBUG:
   Field: condition
   Is mandatory: True
   In asked_fields: False
   In collected_fields: False
   question_count: 0, limit: 4

   Question 1/4: condition
```

### Phase 1 Decision
```
PHASE 1 DECISION POINT:
   approved_questions: ['condition', 'unlock_status', 'color']
   engine.asked_fields: set()
   engine.collected_fields: ['storage', 'year']
   engine.question_count: 0
```

**Red flags to watch for:**
- `asked_fields (should be empty): {'storage', 'year'}` - Bug 1 has regressed
- `approved_questions: []` - No questions approved, will skip to calculation
- `Is mandatory: True` + `valid: False` - Bug 2 has regressed
- `engine_v3 in session: False` during Phase 2 - Session cookie overflow (Bug 6)
- `SESSION SIZE` >90% - Cookie approaching overflow

---

## DEBUGGING CHECKLIST

If questions are being skipped:

- [ ] Check `SESSION_VERSION` — has it been bumped since last deploy?
- [ ] Check server logs for `asked_fields (should be empty): set()` after product identification
- [ ] Check server logs for `APPROVE_QUESTIONS DEBUG` — are questions being approved?
- [ ] Check server logs for `VALIDATE_AI_QUESTION DEBUG` — is validation passing?
- [ ] Check server logs for `PHASE 1 DECISION POINT` — what's the approved list?
- [ ] Clear browser session / use incognito
- [ ] Test via API directly (see Test 1 above)

If engine loses context mid-conversation (Issue 6):

- [ ] Check server logs for `engine_v3 in session: True/False` — is it True on the second turn?
- [ ] Check server logs for `SESSION SIZE` — is it approaching 4KB?
- [ ] Verify `conversation_turns` is NOT in `to_dict()` output
- [ ] Verify `product_info_v3` is NOT being written to session
- [ ] Check that `Product identified: True` on second turn (not False)
- [ ] If `Product identified: False` on a turn where user is answering a question, session was lost

---

## TEST MATRIX

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

## ESCALATION

If fixes don't resolve the issue:

1. **Check Render logs** — All debug prints will show exact flow
2. **Compare logs to expected output** in "Server Log Reading Guide" above
3. **If `asked_fields` is not empty** after product identification - `set_product_info()` regression
4. **If approved_questions is empty** - Check `approve_questions()` logic, mandatory injection
5. **If validation fails** - Check `validate_ai_question()` mandatory exemption
6. **If session is stale** - Bump `SESSION_VERSION` and redeploy
7. **If `engine_v3 in session: False`** during Phase 2 - Session cookie overflow, check `to_dict()` isn't storing growing data
8. **If SESSION_SIZE >90%** - Consider switching to Flask-Session with server-side storage

---

**Last updated:** Session cookie overflow fix (Issue 6)
