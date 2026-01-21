# Condition Assessment System - Implementation Complete

## Overview
Added comprehensive condition assessment system that captures both overall condition AND specific damage details for accurate pricing.

## What Was Implemented

### ✅ 1. New Service: `ConditionAssessmentService`
**File:** `services/condition_assessment_service.py`

**Features:**
- Condition multipliers (Excellent: 98%, Good: 90%, Fair: 75%, Poor: 60%)
- Category-specific issue deductions (phones, laptops, cameras, TVs, appliances)
- Smart damage detection and pricing adjustments
- Detailed breakdown formatting for users

**Example Deductions:**
| Issue | Phone | Laptop | Impact |
|-------|-------|--------|--------|
| Screen cracked | -R1,200 | -R3,500 | High |
| Battery <80% | -R650 | -R1,100 | Medium |
| Body dents | -R350 | -R1,000 | Low-Medium |
| Water damage | -R1,800 | N/A | Very High |

### ✅ 2. Enhanced AI Conversation Flow
**File:** `services/ai_service.py`

**New Question Flow:**
1. Extract product info
2. Ask for specs (if needed)
3. Ask for **overall condition**
4. Ask for **specific issues** (NEW!) ← Multi-select checkboxes
5. Complete

**Example Questions by Category:**

#### Phones/Tablets:
```
"Are there any of these issues with your iPhone 11? Select all that apply:"
- Screen cracked or scratched
- Back glass cracked
- Body dents or deep scratches
- Battery health below 80%
- Camera issues
- Face ID / Touch ID not working
- Buttons or ports damaged
- Water damage
- None - Everything works perfectly
```

#### Laptops:
```
"Are there any of these issues with your MacBook Pro? Select all that apply:"
- Screen scratches, dead pixels, or cracks
- Keyboard keys missing or sticky
- Trackpad not working properly
- Battery health below 80%
- Dents or cracks in body
- Hinge loose or broken
- Ports not working
- Overheating issues
- None - Everything works perfectly
```

###  ✅ 3. Integrated with Offer Calculation
**File:** `services/offer_service.py`

**Changes:**
- Added `ConditionAssessmentService` to imports
- Calculate adjusted value using condition + specific issues
- Maintains backward compatibility with legacy `damage_info`

**New Calculation Flow:**
```python
Base Market Value (from research)
    ↓
Apply Condition Multiplier (excellent/good/fair/poor)
    ↓
Subtract Issue Deductions (cracked screen, battery, etc.)
    ↓
Adjusted Value
    ↓
× 65% = Sell Now Offer
× 85% = Consignment Payout
```

---

## Example Pricing Scenarios

### Scenario 1: Perfect Condition iPhone
```
Product: iPhone 11 128GB
Condition: Excellent - Like new
Issues: None - Everything works perfectly

CALCULATION:
Base Market Value: R5,000
Condition Multiplier: 0.98 (Excellent)
Issue Deductions: R0
Adjusted Value: R5,000 × 0.98 = R4,900

OFFERS:
Sell Now (65%): R3,185
Consignment (85%): R4,165
```

### Scenario 2: Good Condition with Cracked Screen
```
Product: iPhone 11 128GB
Condition: Good - Minor wear
Issues: Screen cracked or scratched

CALCULATION:
Base Market Value: R5,000
Condition Multiplier: 0.90 (Good)
After condition: R5,000 × 0.90 = R4,500
Issue Deductions: -R1,200 (Cracked screen)
Adjusted Value: R4,500 - R1,200 = R3,300

OFFERS:
Sell Now (65%): R2,145
Consignment (85%): R2,805

DIFFERENCE: R1,380 less due to cracked screen
```

### Scenario 3: MacBook with Multiple Issues
```
Product: MacBook Pro 2020 16GB/512GB
Condition: Fair - Visible scratches
Issues: Battery health below 80%, Dents or cracks in body

CALCULATION:
Base Market Value: R15,000
Condition Multiplier: 0.75 (Fair)
After condition: R15,000 × 0.75 = R11,250
Issue Deductions:
  - Battery degraded: -R1,100
  - Body dents: -R1,000
  Total: -R2,100
Adjusted Value: R11,250 - R2,100 = R9,150

OFFERS:
Sell Now (65%): R5,948
Consignment (85%): R7,778

DIFFERENCE: R5,850 less due to condition + issues
```

---

## Updated Conversation Flow

### Example: iPhone 11 128GB

**Turn 1:**
```
User: "iPhone 11 128GB"
AI extracts: category=phone, brand=Apple, model=iPhone 11, capacity=128GB
AI asks: "What is the physical condition of your iPhone 11?"
```

**Turn 2:**
```
User: "Good - Minor wear"
AI extracts: condition=good
AI asks: "Are there any of these issues with your iPhone 11? Select all that apply:
  - Screen cracked or scratched
  - Back glass cracked
  - Body dents or deep scratches
  - Battery health below 80%
  - Camera issues
  - Face ID / Touch ID not working
  - Buttons or ports damaged
  - Water damage
  - None - Everything works perfectly"
```

**Turn 3:**
```
User: [Selects] "Battery health below 80%"
AI extracts: damage_details=['Battery health below 80%']
AI: Completed ✓
```

**Result:**
- Total questions: 2 (condition + issues)
- Accurate pricing based on specific problem
- User knows why offer is what it is
- EpicDeals knows what to expect

---

## Benefits

### For Pricing Accuracy:
✅ **Granular adjustments** - Specific deductions per issue
✅ **Category-specific** - Different deductions for phones vs laptops
✅ **Fair pricing** - Both parties know what affects value
✅ **Reduced risk** - No surprises during inspection

### For Users:
✅ **Transparent** - See exactly why offer is X amount
✅ **Honest assessment** - Encourages accurate reporting
✅ **Fair offers** - Not penalized for minor issues
✅ **Quick process** - Just checkboxes, no typing

### For EpicDeals:
✅ **Accurate expectations** - Know condition before collection
✅ **Fewer disputes** - Condition agreed upfront
✅ **Better inventory** - Pre-assess items accurately
✅ **Reduced inspection surprises** - Less adjustment needed

---

## Debug Output Example

When running, you'll see detailed logging:

```
Applying condition assessment...

Condition Assessment:
- Base Market Value: R5,000.00
- Condition: good (multiplier: 0.9)
- After condition adjustment: R4,500.00

  Damage Details:
  - Battery health below 80%: -R650.00

- Issue deductions: -R650.00
- After deductions: R3,850.00
- Final Adjusted Value: R3,850.00
```

This helps verify:
- Condition multiplier is applied correctly
- Issue deductions are working
- Final value makes sense

---

## Testing Scenarios

### Test 1: Perfect Condition
```
Product: iPhone 11 128GB
Condition: Excellent
Issues: None - Everything works perfectly
Expected: Highest possible offer (98% of market value)
```

### Test 2: Single Issue
```
Product: iPhone 11 128GB
Condition: Good
Issues: Screen cracked or scratched
Expected: R1,200 deduction from base offer
```

### Test 3: Multiple Issues
```
Product: iPhone 11 128GB
Condition: Fair
Issues: Screen cracked, Battery <80%, Water damage
Expected: Multiple deductions stack (-R3,250 total)
```

### Test 4: Laptop Different Deductions
```
Product: MacBook Pro 2020
Condition: Good
Issues: Battery health below 80%
Expected: R1,100 deduction (laptop rate, not phone rate)
```

### Test 5: Appliance
```
Product: Samsung Washing Machine
Condition: Fair
Issues: Leaks or drips
Expected: R1,500 deduction + fair condition multiplier
```

---

## Files Modified

| File | Changes | Purpose |
|------|---------|---------|
| `services/condition_assessment_service.py` | Created | Core assessment logic |
| `services/ai_service.py` | Enhanced prompt | Ask damage details question |
| `services/offer_service.py` | Integrated service | Use for pricing calculations |
| `CONDITION_ASSESSMENT_DESIGN.md` | Documentation | Full design spec |

---

## Next Steps

### Phase 1: Testing (This Week)
- [ ] Test perfect condition items
- [ ] Test single issue items
- [ ] Test multiple issues
- [ ] Test different categories (phones, laptops, etc.)
- [ ] Verify deductions match expected amounts

### Phase 2: Frontend Integration (Next Week)
- [ ] Update frontend to handle `multi_select` question type
- [ ] Add checkboxes for damage options
- [ ] Show selected issues in confirmation
- [ ] Display pricing breakdown in offer

### Phase 3: Refinement (Week 3)
- [ ] Collect real-world data on accuracy
- [ ] Adjust deduction amounts if needed
- [ ] Add more categories (consoles, watches, etc.)
- [ ] Fine-tune condition multipliers

### Phase 4: Advanced Features (Week 4+)
- [ ] Photo upload for visual verification
- [ ] AI image analysis for automatic damage detection
- [ ] Severity levels (minor scratch vs major crack)
- [ ] Regional pricing variations

---

## Configuration

All deduction amounts are centralized in `ConditionAssessmentService`:

```python
# Easy to adjust based on real data
PHONE_DEDUCTIONS = {
    'screen_cracked': 1200,      # Can adjust if too high/low
    'battery_degraded': 650,     # Based on replacement cost
    'water_damage': 1800,        # High risk, reflects that
    # ... etc
}
```

To adjust deductions:
1. Edit values in `services/condition_assessment_service.py`
2. Restart Flask app
3. Test with new values
4. Monitor accuracy vs actual inspections

---

## Success Metrics

Track these to measure improvement:

### Pricing Accuracy:
- **Offer vs Inspection Match**: Target >85% within R500
- **Dispute Rate**: Target <5%
- **Return Rate**: Target <3%

### User Experience:
- **Completion Rate**: Target >85%
- **Time to Complete**: Target <2 minutes
- **User Satisfaction**: Target 4.5+ / 5

### Business Impact:
- **Overpayment Rate**: Track how often we pay too much
- **Underpayment Rate**: Track fair offers
- **Inspection Surprises**: Reduce by 60%+

---

## Status

🟢 **COMPLETE** - Ready for testing

**Implemented:** January 21, 2026
**Files Created:** 2 (condition_assessment_service.py, CONDITION_ASSESSMENT_DESIGN.md)
**Files Modified:** 2 (ai_service.py, offer_service.py)
**Lines of Code:** ~400
**Next:** Test with real products + integrate frontend checkboxes

---

## Summary

✅ **Two-stage condition assessment** (overall + specific issues)
✅ **Category-specific deductions** (phones vs laptops vs cameras)
✅ **Accurate pricing** (condition multipliers + issue deductions)
✅ **User transparency** (see exactly why offer is X)
✅ **EpicDeals protection** (know condition before collection)

**Result:** Much more accurate pricing that reflects actual item condition and specific issues, reducing risk for EpicDeals and providing fair, transparent offers for sellers.
