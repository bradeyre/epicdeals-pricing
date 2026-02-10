# v3.0 Migration Status

**Date:** February 9, 2026
**Progress:** Steps 1-2 Complete (40% done)

---

## ✅ What's Been Completed

### Step 1: GuardrailEngine (DONE)
**File:** `services/guardrail_engine.py`

**What it does:**
- Enforces non-negotiable rules the AI cannot break
- Tracks `asked_fields` AND `collected_fields` separately
- Hard 4-question cap (guarantees fast experience)
- Validates every AI response before accepting
- Handles "I don't know" gracefully (marks as 'unknown', moves on)
- Guarantees every conversation reaches offer state
- Serializable to/from Flask session (JSON-safe)

**Key Methods:**
- `set_product_info()` - Initialize with identified product
- `approve_questions()` - Filter AI's proposed questions
- `validate_ai_question()` - Check if question is allowed
- `record_answer()` - Store user's response
- `should_calculate_offer()` - Decide when to trigger offer
- `get_state_for_prompt()` - Tell AI what's already collected
- `to_dict()` / `from_dict()` - Session serialization

**Tests Passed:**
- ✅ Basic flow (iPhone with 3 questions)
- ✅ Duplicate prevention (rejects re-asking)
- ✅ "I don't know" handling (marks as 'unknown')
- ✅ Auto-collection of specs from initial message
- ✅ Question cap enforcement

### Step 2: AI Service v3 (DONE)
**File:** `services/ai_service_v3.py`

**What it does:**
- Radically simplified from v2.0 (800 lines → 300 lines)
- NO flow logic (GuardrailEngine handles that)
- NO duplicate prevention (GuardrailEngine handles that)
- NO hardcoded categories
- Just: understand products + ask smart questions

**Key Methods:**
- `identify_product()` - Phase 1: Extract product info + propose questions
- `generate_question()` - Phase 2: Create friendly question with options
- `extract_answer()` - Parse natural language into structured data
- `generate_acknowledgment()` - Friendly response after identification

**Two-Phase Architecture:**
1. **Phase 1 (Identify):** User says "iPhone 14 128GB" → AI returns product_info + proposed_questions
2. **Phase 2 (Question):** AI generates friendly question for each approved field

**Tests Passed:**
- ✅ iPhone identification (extracts brand, model, storage, year)
- ✅ Car identification (extracts year from model name)
- ✅ Question generation with category-specific options
- ✅ Answer extraction (handles text, numbers, "don't know")
- ✅ Works universally (no hardcoded categories)

---

## 🚧 What's Next

### Step 3: Wire Up API Route (1-2 hours)
**File to modify:** `app.py`

**What needs to be done:**
1. Import GuardrailEngine and AIServiceV3
2. Initialize engine in session on first message
3. Update `/api/message` route:
   ```python
   # Get or create engine from session
   engine = GuardrailEngine.from_dict(session.get('engine_state', {}))

   # First message: identify product
   if not engine.product_identified:
       result = ai.identify_product(user_message)
       engine.set_product_info(result['product_info'])
       approved = engine.approve_questions(result['proposed_questions'])
       # Generate first question
       # ...

   # Subsequent messages: record answer, ask next
   else:
       engine.record_answer(current_field, user_message)
       if engine.should_calculate_offer():
           # Trigger offer calculation
       else:
           # Ask next question

   # Save engine state to session
   session['engine_state'] = engine.to_dict()
   ```

4. Add `ui_options` to API response for frontend
5. Keep existing offer calculation pipeline (no changes needed)

**Key Considerations:**
- Preserve backward compatibility during migration
- Test with v2.0 sessions to ensure no breaks
- Add version flag to session to track v2 vs v3

### Step 4: Frontend Quick-Select UI (2-3 hours)
**File to modify:** `static/js/app.js`

**What needs to be added:**
1. **Quick-Select Buttons:**
   ```javascript
   if (response.ui_options && response.ui_options.length > 0) {
       renderQuickSelectButtons(response.ui_options);
   }
   ```

2. **Condition Checklist:**
   ```javascript
   if (response.ui_type === 'checklist') {
       renderCheckboxList(response.ui_options);
   }
   ```

3. **Progress Indicator:**
   ```javascript
   updateProgressDots(response.question_count, response.total_questions);
   ```

4. **Calculation Animation:**
   ```javascript
   showCalculatingAnimation([
       "🔍 Researching current market prices...",
       "📊 Calculating fair value...",
       "✅ Your offer is ready!"
   ]);
   ```

**CSS needs:** `static/css/style.css`
- Button styles for quick-select
- Checkbox styles for condition list
- Progress dots styling
- Animation keyframes

### Step 5: Test Across 10 Product Types (2-3 hours)

**Test Matrix:**
| # | Product | Expected Questions | Key Validation |
|---|---------|-------------------|----------------|
| 1 | iPhone 14 128GB | 3 (cond, lock, contract) | Skips storage (given), auto year |
| 2 | MacBook Air M2 | 2-3 (specs, cond, lock) | No contract, asks RAM if not given |
| 3 | 2019 VW Polo 1.0 TSI | 3 (km, cond, service) | Car-specific, no lock/contract |
| 4 | Nike AJ4 Military Black | 1-2 (cond, colourway) | Fashion-specific, minimal |
| 5 | Dyson Airwrap | 2-3 (variant, cond, completeness) | Asks version, no lock |
| 6 | Samsung 65" QLED TV | 2 (cond, model year) | No lock/contract, size given |
| 7 | Canon EOS R5 | 2 (cond, lens included?) | Camera-specific, no lock |
| 8 | PS5 Slim Digital | 2 (cond, controllers) | Console-specific |
| 9 | Weylandts leather couch | 2-3 (age, cond, colour) | Furniture, unusual category |
| 10 | GHD hair straightener | 1-2 (cond, model) | Simple, fast |

**For each test:**
- Record question flow
- Verify no duplicates
- Check question count ≤ 4
- Confirm offer reached
- Validate UI options provided

---

## 📝 Documentation Updates Needed

### BUILD_DOCUMENT.md
Add new section after current content:

```markdown
## v3.0 Architecture Upgrade (Feb 2026)

### The Problem v3.0 Solves
v2.0 was built for electronics. v3.0 is built for EVERYTHING.

The breakthrough: We don't need different flows for each product type.
We need an AI that understands what affects price + an engine that
keeps it disciplined.

### Hybrid Architecture: AI Brain + Code Guardrails

**AI (Claude):**
- Understands what the product IS
- Knows what affects its resale value
- Generates natural, friendly questions
- Extracts structured data from answers

**Engine (Python):**
- Tracks what's been asked and answered
- Enforces max 4 questions (hard cap)
- Validates AI responses (rejects duplicates)
- Decides when to calculate offer
- Guarantees progression to offer

### Key Benefits

**Universal Coverage:**
- Works for phones, cars, shoes, furniture, anything
- No hardcoded product lists
- AI adapts questions per product type

**Faster Experience:**
- Hard 4-question cap (was often 6-8 in v2.0)
- Questions combined when natural
- Specs extracted from initial message

**More Reliable:**
- Duplicate prevention at code level (not prompt)
- "I don't know" handled gracefully
- Guaranteed offer (no infinite loops)
- Testable, predictable rules

**Better UX:**
- Quick-select buttons for every question
- Category-specific condition checklists
- Progress indicator
- Calculation animation
```

---

## 🔄 Migration Strategy

### Phase 1: Parallel Deployment (Recommended)
Run v2.0 and v3.0 side-by-side:
1. Add route `/api/message/v3` for new architecture
2. Frontend detects v3 availability
3. A/B test with 10% traffic
4. Monitor metrics (completion rate, time, satisfaction)
5. Gradual rollout to 100%

### Phase 2: Full Migration
Once v3 proven stable:
1. Make v3 the default
2. Keep v2 as fallback for 2 weeks
3. Full cutover after validation

### Rollback Plan
If issues discovered:
- Revert to v2.0 AI service
- Engine stays (it's additive, doesn't break v2)
- No data loss (sessions compatible)

---

## 📊 Success Metrics to Track

**Speed:**
- [ ] Average questions per conversation (target: ≤ 3)
- [ ] Time to offer (target: < 45 seconds)

**Accuracy:**
- [ ] Duplicate question rate (target: 0%)
- [ ] Conversations reaching offer (target: 100%)

**Coverage:**
- [ ] Product categories successfully priced (target: 10+ categories)
- [ ] Unusual items priced (track edge cases)

**User Satisfaction:**
- [ ] Completion rate (target: > 90%)
- [ ] "Questions felt relevant" (survey)

---

## 🐛 Known Issues to Watch

1. **AI Prompt Brittleness**
   - AI might still propose irrelevant questions
   - Engine catches this, but log for improvement

2. **Category Edge Cases**
   - Truly unusual items ("vintage typewriter", "kayak")
   - Monitor how AI handles these

3. **Multi-Language**
   - Current prompts are English-only
   - Afrikaans support needed for SA market

4. **Complex Answers**
   - User writes paragraph instead of selecting option
   - Extract_answer() is simplified, needs enhancement

---

## 🚀 Quick Start for Next Session

```bash
cd "/Users/Focus/Downloads/Claude ED Price Research Tool - Jan 2026"

# Test the core modules
python3 -c "from services.guardrail_engine import GuardrailEngine; print('✅ Engine works')"
python3 -c "from services.ai_service_v3 import AIServiceV3; print('✅ AI works')"

# Next: Integrate with Flask
# Edit app.py and add /api/message/v3 route
```

---

## 📞 Context for Future Sessions

**What we're building:** Universal pricing engine that can price ANY product in 2-4 questions

**Why it's different:** AI understands products + Python engine enforces discipline

**What's working:** Core architecture tested and proven

**What's next:** Wire it into Flask + build frontend UI

**End goal:** Seller types "2019 VW Polo" or "Nike AJ4" and gets fair offer in 60 seconds

---

## 💾 Files Modified So Far

- ✅ NEW: `services/guardrail_engine.py` (345 lines)
- ✅ NEW: `services/ai_service_v3.py` (307 lines)
- ⏳ PENDING: `app.py` (needs v3 route)
- ⏳ PENDING: `static/js/app.js` (needs quick-select UI)
- ⏳ PENDING: `static/css/style.css` (needs new styles)

**Total Progress:** 40% complete (2/5 steps done)
**Estimated Time Remaining:** 6-10 hours
**Status:** On track, architecture solid

---

Last Updated: February 9, 2026, 17:45 SAST
Next Session: Continue with Step 3 (API integration)
