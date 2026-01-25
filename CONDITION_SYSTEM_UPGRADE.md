# Condition Assessment & Pricing System Upgrade

## Overview
Complete overhaul of the condition assessment and pricing system to eliminate calculation errors, implement intelligent BER (Beyond Economic Repair) detection, and add consignment-only flows for unrepairable items.

---

## Key Problems Fixed

### 1. ❌ Double-Dipping Bug (CRITICAL)
**Problem:** System was applying BOTH condition penalty AND repair cost deduction
```
WRONG: (Market Value × 0.40) - Repair Cost = Double penalty
RIGHT: Market Value - Repair Cost = Correct value
```

**Example:**
- iPhone 16 Pro Max: R8,000 market value
- Screen cracked: R1,800 repair
- **OLD (Wrong):** R8,000 × 0.40 - R1,800 = R1,400 ❌
- **NEW (Correct):** R8,000 - R1,800 = R6,200 → Offer: R4,030 ✅

**Fix:** New `calculate_value_with_repairs()` method in `condition_assessment_service.py:484`

---

### 2. ❌ "Cracked" Under "Good" Condition
**Problem:** Mixing cosmetic issues with structural damage in checklist

**Solution:** Reorganized damage options by severity:
- **Structural Damage** (Poor): Screen cracked, back glass cracked, water damage
- **Functional Failures** (Poor/Fair): Camera not working, Face ID broken
- **Repairable Issues** (Fair): Battery degraded, buttons damaged
- **Cosmetic Only** (Good/Excellent): Scratches, scuffs, minor dents

**Files Updated:**
- `services/condition_assessment_service.py:279-350`
- `services/ai_service.py:327-367`

---

## New Features Implemented

### 3. ✅ Universal BER (Beyond Economic Repair) Detection

**What it does:** Automatically identifies items that cost more to repair than they're worth

**Universal Rules (applies to ANY product):**
1. **Repair cost percentage threshold:**
   - Low value (<R2,000): 50%
   - Mid value (R2,000-R10,000): 35%
   - High value (>R10,000): 25%

2. **Multiple major issues:** 3+ structural/functional failures = BER

3. **Unreliable repairs:** Water damage, fungus, mold, won't turn on = BER

4. **Age + damage:** >5 years old + repair cost >30% = BER

**Example BER Scenarios:**
- TV with cracked screen (repair = 75% of value) → BER
- iPhone with screen + back glass + water damage → BER
- 6-year-old laptop with broken hinge (repair = R3,500) → BER

**Implementation:** `condition_assessment_service.py:465-533`

---

### 4. ✅ Device Lock Verification (Phones/Tablets/Laptops/Watches)

**New Questions Added:**
1. "Is your device unlocked from all accounts (iCloud/Google/Samsung/Microsoft)?"
2. "Is it free from contracts or payment plans?"
3. "Do you have proof of purchase?" (optional)

**Penalty Policy (HARSH):**
If device arrives locked:
- **Option 1:** Unlock remotely + pay R550 verification fee
- **Option 2:** Return device + pay R550 return fee (labor + courier)

**Auto-decline if:**
- User selects "No" to unlocked question
- User selects "Still under contract"

**Implementation:** `services/ai_service.py:310-365`

---

### 5. ✅ Consignment-Only Flow for BER Items

**When BER detected:**
- No direct purchase offer
- Automatic consignment offer
- Listed as "For Parts/Repair" or "As-Is"
- Seller keeps item until sold
- Shipping deducted from payout (R100-150)

**Consignment Requirements:**
1. Upload 3-5 clear photos
2. AI verification of photos vs. description
3. Commitment agreement (won't sell elsewhere)
4. Ship within 48 hours if sold

**Payout Calculation:**
```
Estimated sale price (as-is) × 85% - Shipping = Seller payout
Commission: 15%
```

**Implementation:**
- `services/offer_service.py:124-171` (BER detection)
- `services/offer_service.py:485-525` (Consignment message)

---

### 6. ✅ 2-Day Repair Cost Research Queue

**When triggered:** Repair cost confidence < 65%

**What happens:**
1. System calculates preliminary offer
2. Adds to research queue with 2 working day SLA
3. Manual team researches actual costs
4. Final offer sent via email/SMS
5. User has 48 hours to accept

**Features:**
- Automatic SLA calculation (skips weekends)
- Unique queue ID (e.g., RQ20260125143022)
- Overdue tracking
- Stats dashboard

**Implementation:** `services/research_queue_service.py` (new file)

---

## File Changes Summary

### Modified Files:

1. **services/condition_assessment_service.py**
   - Added `classify_damage_severity()` - Line 403
   - Added `is_beyond_economic_repair()` - Line 465
   - Added `calculate_value_with_repairs()` - Line 535 (NEW CORRECT METHOD)
   - Added `requires_device_unlock_check()` - Line 560
   - Reorganized damage options by severity - Lines 279-350
   - Deprecated old `calculate_adjusted_value()` - Line 117

2. **services/offer_service.py**
   - Integrated BER detection - Lines 124-171
   - Fixed double-dipping calculation - Lines 193-201
   - Added repair research queue integration - Lines 110-142
   - Added BER consignment offer message - Lines 485-525
   - Added repair research needed message - Lines 528-552
   - Imported `ResearchQueueService` - Line 6

3. **services/ai_service.py**
   - Added device lock verification questions - Lines 310-365
   - Added penalty policy warning - Lines 361-364
   - Updated damage options for phones/tablets/laptops/TVs - Lines 327-367
   - Updated completion criteria - Lines 373-381

4. **services/research_queue_service.py** (NEW FILE)
   - Complete queue management system
   - 2 working day SLA calculation
   - Pending/overdue tracking
   - Stats dashboard

---

## Business Logic Flows

### Flow 1: Clean Item (No Repairs)
```
User describes item → No damage selected → Market value research
→ Offer = Market Value × 0.65
```

### Flow 2: Repairable Item
```
User describes item → Selects "Battery degraded"
→ Research repair cost: R650
→ Value to us: R8,000 - R650 = R7,350
→ Offer: R7,350 × 0.65 = R4,778
```

### Flow 3: BER Item (Consignment Only)
```
User describes TV → Selects "Cracked screen"
→ BER detected (repair cost 75% of value)
→ No purchase offer
→ Consignment option: List as-is for R1,200 (parts value)
→ Seller gets: R1,200 × 0.85 - shipping = R870
```

### Flow 4: Locked Device (Auto-Decline)
```
User describes iPhone → Unlocked? "No"
→ Auto-decline with message:
   "We cannot purchase locked devices. Please unlock first."
```

### Flow 5: Low Confidence Repairs (Research Queue)
```
User describes item → Repair cost found but low confidence (55%)
→ Preliminary offer: R3,500
→ Added to research queue
→ "We'll get back to you in 2 working days"
→ Manual research → Final offer sent
```

---

## Testing Checklist

### Test Scenarios:

- [ ] iPhone with cracked screen → Should offer R4,030 (not R1,400)
- [ ] TV with cracked screen → Should decline purchase, offer consignment only
- [ ] Locked iPhone → Should auto-decline immediately
- [ ] iPhone under contract → Should auto-decline immediately
- [ ] Item with water damage → Should trigger BER, consignment only
- [ ] Item with low repair confidence → Should add to research queue
- [ ] Clean item (no damage) → Should offer 65% of market value
- [ ] Item with battery issue only → Should deduct R650 and offer 65%
- [ ] Multiple major issues → Should trigger BER if >3 issues

---

## Configuration Constants

```python
# Thresholds (can be adjusted)
REPAIR_CONFIDENCE_THRESHOLD = 0.65  # Minimum for auto-offer
BER_THRESHOLD_LOW_VALUE = 0.50      # <R2,000 items
BER_THRESHOLD_MID_VALUE = 0.35      # R2,000-R10,000
BER_THRESHOLD_HIGH_VALUE = 0.25     # >R10,000

# Penalties
DEVICE_LOCK_FEE = 550  # R550 for locked devices

# SLA
REPAIR_RESEARCH_SLA_DAYS = 2  # Working days

# Commission
CONSIGNMENT_COMMISSION = 0.15  # 15%
SELLER_PAYOUT = 0.85           # 85%
```

---

## API Response Changes

### New Fields in offer_data:

```python
{
    'recommendation': 'ber_consignment_only',  # NEW
    'ber_check': {                             # NEW
        'is_ber': True,
        'reason': '...',
        'recommendation': 'consignment'
    },
    'damage_classification': {                 # NEW
        'structural': [...],
        'functional_failure': [...],
        'repairable': [...],
        'cosmetic_only': [...],
        'ber_flags': [...]
    },
    'needs_manual_research': True,             # NEW
    'research_sla': '2 working days',          # NEW
    'preliminary_offer': 3500,                 # NEW
}
```

### New recommendation values:
- `'ber_consignment_only'` - Item is BER, consignment only
- `'repair_research_needed'` - Low confidence, needs manual research
- `'device_locked'` - Device locked (decline)
- `'under_contract'` - Under contract (decline)

---

## Migration Notes

### Backward Compatibility:
- Old `calculate_adjusted_value()` method deprecated but kept for legacy support
- New method `calculate_value_with_repairs()` is the correct one to use
- Frontend should check for new `recommendation` values

### Breaking Changes:
- Condition multipliers NO LONGER applied when repair costs exist
- Device lock questions now REQUIRED for phones/tablets/laptops/watches
- BER items no longer receive direct purchase offers

---

## Future Enhancements

1. **Photo Upload & AI Verification** (consignment)
2. **Consignment Commitment Agreement** (legal binding)
3. **Admin Dashboard** for research queue
4. **Automated Repair Cost Updates** from repair shop APIs
5. **ML Model** to predict BER based on historical data

---

## Support & Questions

For questions about this upgrade:
- Review this document first
- Check implementation in referenced files
- Test with example scenarios above

**Last Updated:** 2026-01-25
**Version:** 2.0
**Author:** Claude Sonnet 4.5
