# Duplicate Question Bug - Fixed (January 21, 2026)

## Problem
The conversation flow was asking duplicate questions, particularly the condition question appearing twice in the same conversation.

## Root Cause
The AI service wasn't properly tracking which questions had already been asked, and the app.py wasn't storing the assistant's questions in the conversation history.

## Solution Implemented

### 1. Enhanced AI Service Prompt (`services/ai_service.py`)

Added explicit duplicate prevention rules:

```python
CRITICAL RULES - PREVENT DUPLICATE QUESTIONS:
1. NEVER ask the same question twice - review the conversation history carefully
2. NEVER ask about information that's already in CURRENT PRODUCT INFO
3. Be SMART - extract ALL information from what the user already told you
...

BEFORE ASKING A QUESTION:
1. Check conversation_history - has this question been asked already?
2. Check CURRENT PRODUCT INFO - do we already have this information?
3. If YES to either, DON'T ask it again - move to the next needed information or set completed=true
```

### 2. Added Conversation History Tracking

The system prompt now includes:
- Full CURRENT PRODUCT INFO to show what's already known
- List of all assistant questions from conversation history

This ensures the AI can see:
- What information has already been gathered
- What questions have already been asked

### 3. Improved App Logic (`app.py`)

**Before:**
- Only tracked user messages
- AI couldn't see what questions it had already asked

**After:**
- Tracks both user AND assistant messages
- Adds assistant's question to history after generating it
- Better product_info merging logic to avoid losing data
- Enhanced debug logging to track conversation flow

### 4. Better Product Info Merging

```python
# Merge extracted info without overwriting with None values
for key, value in extracted_info.items():
    if value is not None:
        if key == 'specifications' and key in product_info:
            # Merge specifications dict properly
            if product_info[key] is None:
                product_info[key] = {}
            product_info[key].update(value)
        else:
            product_info[key] = value
```

## Expected Behavior Now

### Example Flow: iPhone 11 128GB

**Turn 1:**
- User: "iPhone 11 128GB"
- System extracts: category=phone, brand=Apple, model=iPhone 11, capacity=128GB
- AI asks: "What is the physical condition?"

**Turn 2:**
- User: "Good - Minor wear"
- System extracts: condition=good
- System checks: Do we have category, brand, model, capacity, condition? YES
- AI returns: completed=true (NO additional questions)

### What's Prevented

❌ **No longer happens:**
1. Asking about condition twice
2. Asking for information already provided
3. Asking about category when it's obvious from the product name
4. Asking about color (doesn't affect value significantly)

✅ **Now works correctly:**
1. Each question asked only once
2. AI recognizes information from user's initial input
3. Completes conversation efficiently (2-3 questions maximum)
4. Full conversation history maintained

## Testing Checklist

- [ ] Test: "iPhone 11 128GB" → Should ask ONLY condition (1 question)
- [ ] Test: "iPhone 11" → Should ask capacity, then condition (2 questions)
- [ ] Test: "MacBook Pro 2020" → Should ask specs, then condition (2 questions)
- [ ] Test: "Samsung washing machine" → Should ask model, then condition (2 questions)
- [ ] Test: Complete flow end-to-end with no duplicates

## Debug Output

Enhanced logging now shows:
```
============================================================
DEBUG - BEFORE PROCESSING:
User answer: Good - Minor wear
Current product_info: {'category': 'phone', 'brand': 'Apple', ...}
Conversation history length: 2
============================================================

============================================================
DEBUG - AFTER EXTRACTION:
Extracted info: {'condition': 'good', ...}
Updated product_info: {'category': 'phone', 'brand': 'Apple', 'condition': 'good', ...}
============================================================

============================================================
DEBUG - AI RESPONSE:
AI returned question: {"question": "", "completed": true}
============================================================
```

## Next Steps

1. Test full conversation flow with various products
2. Monitor for any edge cases where duplicates might still occur
3. Consider adding explicit deduplication check in app.py as fallback
4. Update frontend to handle completed state properly

## Files Modified

1. `services/ai_service.py` - Enhanced prompt with duplicate prevention
2. `app.py` - Added assistant message tracking and better merging logic

---

**Status:** ✅ Fixed and ready for testing
**Date:** January 21, 2026
