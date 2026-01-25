# Design Principles - EpicDeals AI Tool

## Core Philosophy

This tool is built on **intelligent AI-driven logic** rather than hard-coded rules. The system should adapt and think, not rely on lists and static conditions.

---

## 1. NO HARD-CODED LISTS RULE

### ❌ What NOT to Do:
- Never create lists of specific items (pianos, guitars, elephants, fridges, BMWs, etc.)
- Never hard-code specific product names in logic
- Never use switch/case or if/else chains for specific item types
- Never add examples of specific items in AI prompts

### ✅ What TO Do Instead:
- Use **logic-based AI prompting** that applies universally
- Ask questions about characteristics: size, weight, portability
- Use reasoning that works for ANY item, regardless of what it is
- Create prompts that think through principles, not memorize examples

### Example - Courier Eligibility:

**WRONG APPROACH:**
```python
# Hard-coded list - DON'T DO THIS
non_courier_items = ['piano', 'guitar', 'elephant', 'fridge', 'couch', 'BMW']
if item.lower() in non_courier_items:
    return False
```

**CORRECT APPROACH:**
```python
# Logic-based AI prompting - DO THIS
prompt = """Can "{item}" be shipped in a courier bag or small parcel box?

ASK YOURSELF:
1. Can this item fit in a standard courier bag or small box?
2. Can one person carry it easily?
3. Does it weigh under 25kg?

If NO to any question → not eligible
If YES to all → eligible
"""
```

### Why This Matters:

> "If someone wants to ship an elephant, it should be the same as if they want to ship a fridge or a couch or a BMW."

The logic must be **universal and principle-based**, not item-specific. This means:
- Piano blocked for same reason as elephant (too large for courier bag)
- iPhone 15 treated same as Samsung Galaxy (both are phones)
- MacBook evaluated same as Dell laptop (both are laptops)

---

## 2. AI-FIRST ARCHITECTURE

### Principle:
Let AI do the heavy lifting through intelligent prompting, not through code logic.

### Application Areas:

**Courier Eligibility** (utils/courier_checker.py):
- AI determines if item fits in courier bag
- No lists of non-courier items
- Pure size/weight/portability logic

**Product Categorization** (services/ai_service.py):
- AI extracts category from conversation
- No hard-coded category mappings
- Understands synonyms and variations naturally

**Business Model Options** (utils/courier_checker.py):
- AI determines if item is consumer electronics
- No category whitelists
- Explains reasoning for classification

**Repair Cost Assessment** (services/condition_assessment_service.py):
- AI researches actual repair costs
- No hard-coded price tables
- Adapts to market changes automatically

---

## 3. LOGIC OVER LISTS

### Categories Are Descriptive, Not Prescriptive:

When we mention categories (phones, tablets, laptops), it's for:
- Documentation clarity
- Example scenarios
- Test case organization

**Never use categories as:**
- Gatekeepers in code logic
- Switch/case conditions
- Whitelist/blacklist filters

### Generic Rules Over Specific Cases:

Instead of:
```python
if category == 'piano':
    return "Pianos are too large"
elif category == 'guitar':
    return "Guitars cannot be shipped"
```

Use:
```python
# Let AI apply universal logic
if not fits_in_courier_bag(item):
    return ai_explain_why_not_courierable(item)
```

---

## 4. TRANSPARENT REASONING

### AI Should Explain Decisions:

Every AI-driven decision should return:
- **Result**: What was decided
- **Reason**: Why it was decided
- **Confidence**: How certain we are

Example:
```json
{
  "eligible": false,
  "reason": "Pianos are typically 4-5 feet long and weigh 200-600kg, which exceeds courier bag limits",
  "is_silly": false,
  "category_matched": "large_instrument"
}
```

This creates:
- Better user experience (explains rejections)
- Easier debugging (see AI reasoning)
- Trust in the system (transparent logic)

---

## 5. ADAPTIVE QUESTIONS

### Dynamic Conversation Flow:

Questions should adapt to what the user has already told us:
- Don't ask for brand if user said "iPhone 13" (brand is obvious)
- Don't ask for year if user mentioned "2023 model"
- Don't ask condition if user described damage

**Implementation:**
- AI analyzes conversation history
- Extracts known information
- Asks only for missing details

See: `services/ai_service.py` - `get_next_question()`

---

## 6. FAIL-SAFE DEFAULTS

### When AI Fails or Times Out:

Always default to the **safest option**:
- Courier check fails → Reject item (don't accept unknown items)
- Price research fails → Email review (don't make blind offers)
- Repair cost unclear → Manual research queue

**Never fail open** (accepting risky items when unsure).

Example (utils/courier_checker.py):
```python
except Exception as e:
    # Fallback: REJECT unknown items during errors
    return {
        'eligible': False,
        'reason': 'Technical difficulties...',
        'category_matched': 'error'
    }
```

---

## 7. CONFIGURATION OVER CODE

### Business Rules Should Be Configurable:

Hard-code logic patterns, not business values.

**In config.py (Good):**
```python
SELL_NOW_PERCENTAGE = 0.65
CONSIGNMENT_PERCENTAGE = 0.85
COURIER_COST_INTERNAL = 100
MIN_ITEM_VALUE = 3000
```

**Not in code (Bad):**
```python
# Don't do this
offer = price * 0.65  # Magic number!
```

This allows:
- Business to adjust rates without code changes
- A/B testing different percentages
- Environment-specific settings (dev vs prod)

---

## 8. MINIMAL UI EXAMPLES

### Don't Over-Explain to Users:

**First question:**
```
What item do you want to sell?
```

**Not:**
```
What item do you want to sell? (e.g., iPhone 11, MacBook Pro, Samsung TV, Piano)
```

Users know what they want to sell. Examples clutter the UI and can bias responses.

---

## 9. TESTING WITH EDGE CASES

### Test the Logic, Not Just Happy Paths:

Always test with:
- **Silly items**: Elephant, penguin, unicorn (should handle gracefully)
- **Large items**: Piano, fridge, couch (courier should reject)
- **Ambiguous items**: "Phone" without brand (should ask follow-ups)
- **Damaged items**: Cracked screen + water damage (BER detection)

See: Test scenarios in conversation history (Piano, Elephant, Penguin, Jetski)

---

## 10. DOCUMENTATION FOLLOWS REALITY

### Keep Docs in Sync:

When code changes:
1. Update the relevant .md file
2. Add entry to DESIGN_PRINCIPLES.md if it's a pattern
3. Update QUICK_REFERENCE.md for user-facing impact

**Documentation files:**
- `DESIGN_PRINCIPLES.md` - This file (architecture rules)
- `QUICK_REFERENCE.md` - User-facing guide
- `CONDITION_SYSTEM_UPGRADE.md` - Technical deep dive
- `README.md` - Getting started guide

---

## Common Pitfalls to Avoid

### 1. "Just This One Exception"
Adding one hard-coded item seems harmless, but it breaks the pattern. Soon you have 50 exceptions.

### 2. "AI Is Too Slow"
Don't optimize prematurely by replacing AI with hard-coded rules. Add caching or improve prompts instead.

### 3. "Users Might Enter X"
Don't try to anticipate every possible input with special cases. Let AI handle the variety.

### 4. "This Category Needs Special Logic"
If you're adding category-specific code, you're breaking the design principle. Find the universal logic instead.

---

## Enforcement Checklist

Before committing code, verify:

- [ ] No hard-coded item lists (grep for `['piano'`, `'guitar'`, etc.)
- [ ] No category-based if/else chains
- [ ] AI prompts use logic, not examples
- [ ] Error handling defaults to safest option
- [ ] Business values in config.py, not code
- [ ] Documentation updated if patterns changed

---

## Philosophy Summary

**Single Source of Truth:** AI reasoning, not code rules
**Universal Logic:** Works for ANY item
**Transparent Decisions:** Always explain why
**Fail Safe:** Conservative defaults when uncertain
**Adapt, Don't Hard-Code:** Let AI handle variety

---

**Last Updated:** January 25, 2026
**Maintainer:** Focus/Brad
**Related Files:** `utils/courier_checker.py`, `services/ai_service.py`, `services/offer_service.py`
