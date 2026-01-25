# Quick Reference Guide - New Condition System

## TL;DR - What Changed?

### The Big Fix
**BEFORE:** iPhone with cracked screen = R1,400 offer ❌
**AFTER:** iPhone with cracked screen = R4,030 offer ✅

**Why?** We were double-penalizing (condition penalty + repair cost). Now we just subtract repair cost from market value.

---

## Decision Tree

```
Item submitted
    │
    ├─ Lockable device (phone/tablet/laptop/watch)?
    │   ├─ YES → Ask unlock questions
    │   │   ├─ Locked/Under contract? → DECLINE
    │   │   └─ Unlocked & contract-free → Continue
    │   └─ NO → Continue
    │
    ├─ Has damage/issues?
    │   ├─ NO → Offer 65% of market value
    │   └─ YES → Research repair costs
    │       │
    │       ├─ Repair cost confidence < 65%?
    │       │   └─ YES → Add to research queue (2 days)
    │       │
    │       ├─ Is it BER? (Check all rules)
    │       │   ├─ Water damage → BER
    │       │   ├─ Multiple (3+) major issues → BER
    │       │   ├─ Repair cost > threshold → BER
    │       │   ├─ TV with cracked screen → BER
    │       │   └─ If BER → Consignment only
    │       │
    │       └─ Economically repairable
    │           └─ Offer = (Market Value - Repair Cost) × 65%
```

---

## BER Thresholds (Quick Check)

| Item Value | Repair Cost Threshold | Example |
|------------|----------------------|---------|
| < R2,000 | 50% | R1,500 item, R800 repair = OK |
| R2,000 - R10,000 | 35% | R5,000 item, R2,000 repair = BER |
| > R10,000 | 25% | R15,000 item, R4,000 repair = BER |

---

## Auto-BER Items (Always Consignment Only)

- ❌ Water damage (any category)
- ❌ Liquid damage
- ❌ Fungus/mold
- ❌ Won't turn on / Dead
- ❌ Motherboard/logic board issues
- ❌ TV with cracked screen
- ❌ 3+ major issues combined
- ❌ Old (5+ years) + expensive repair (>30%)

---

## Device Lock Policy (Phones/Tablets/Laptops/Watches)

### Questions Asked:
1. Unlocked from all accounts?
2. Free from contracts/payment plans?
3. Have proof of purchase? (optional)

### If Locked Device Arrives:
- **Option 1:** Unlock remotely → Pay R550 fee → We continue purchase
- **Option 2:** Can't unlock → Pay R550 → We return device

### Auto-Decline If:
- User says "No" to unlocked
- User says "Yes" to under contract

---

## Offer Calculation (New Method)

### No Damage:
```
Offer = Market Value × 65%
Example: R10,000 × 0.65 = R6,500
```

### With Repairable Damage:
```
Offer = (Market Value - Repair Costs) × 65%
Example: (R10,000 - R1,800) × 0.65 = R5,330
```

### BER (Consignment Only):
```
Estimated sale price (as-is) × 85% - Shipping
Example: R2,000 × 0.85 - R150 = R1,550 to seller
```

---

## Damage Categories (How We Classify)

| Category | Examples | Outcome |
|----------|----------|---------|
| **Structural** | Screen cracked, back glass cracked, hinge broken | Usually BER or Poor |
| **Functional Failure** | Camera dead, Face ID broken, won't turn on | Poor condition |
| **Repairable** | Battery degraded, buttons damaged, ports broken | Fair condition |
| **Cosmetic** | Scratches, scuffs, minor dents | Good/Excellent |

---

## Research Queue (Low Confidence Repairs)

### When It Happens:
- Repair cost found BUT confidence < 65%
- Unusual damage needing expert assessment

### What User Sees:
- Preliminary offer shown
- "We'll get back to you in 2 working days"
- Final offer sent via email/SMS
- 48 hours to accept final offer

### Queue Management:
- File: `data/research_queue.json`
- SLA: 2 working days (skips weekends)
- Auto-tracks overdue items

---

## Consignment Requirements (BER Items)

### What User Must Do:
1. ✅ Upload 3-5 clear photos
2. ✅ Photos show all damage
3. ✅ AI verifies photos match description
4. ✅ Sign commitment (won't sell elsewhere)
5. ✅ Ship within 48hrs if sold

### What They Get:
- Listed as "For Parts/Repair" or "As-Is"
- 85% of sale price
- Shipping deducted from payout
- Payment 2 days after buyer receives
- Can request removal if not sold

---

## Common Scenarios

### Scenario 1: Clean iPhone
- Condition: Excellent
- Damage: None
- **Offer:** R8,000 × 0.65 = **R5,200**

### Scenario 2: iPhone with Battery Issue
- Market Value: R8,000
- Battery repair: R650
- **Offer:** (R8,000 - R650) × 0.65 = **R4,778**

### Scenario 3: iPhone with Cracked Screen
- Market Value: R8,000
- Screen repair: R1,800
- **Offer:** (R8,000 - R1,800) × 0.65 = **R4,030**

### Scenario 4: iPhone with Screen + Back Glass + Water Damage
- BER detected (multiple major issues)
- **No purchase offer**
- **Consignment:** List for R1,600 (parts), seller gets R1,210

### Scenario 5: TV with Cracked Screen
- BER detected (repair = 75% of value)
- **No purchase offer**
- **Consignment only** or decline

### Scenario 6: Locked iPhone
- User says "No" to unlocked question
- **Auto-decline**
- "Please unlock your device first"

---

## New API Response Fields

```javascript
{
  recommendation: 'ber_consignment_only',  // NEW: No purchase, consignment only
  ber_check: {                             // NEW: BER analysis
    is_ber: true,
    reason: 'Repair cost (75%) exceeds threshold (25%)',
    recommendation: 'consignment'
  },
  damage_classification: {                 // NEW: Severity breakdown
    structural: ['Screen cracked'],
    functional_failure: [],
    repairable: [],
    cosmetic_only: [],
    ber_flags: []
  },
  needs_manual_research: true,             // NEW: Low confidence
  preliminary_offer: 3500,                 // NEW: Before research
  research_sla: '2 working days'           // NEW: When final offer ready
}
```

---

## Configuration (If You Need to Adjust)

```python
# services/offer_service.py
repair_confidence_threshold = 0.65  # Min confidence for auto-offer

# services/condition_assessment_service.py (in is_beyond_economic_repair)
BER_THRESHOLD_LOW_VALUE = 0.50      # <R2,000 items
BER_THRESHOLD_MID_VALUE = 0.35      # R2,000-R10,000
BER_THRESHOLD_HIGH_VALUE = 0.25     # >R10,000

# Device lock fee
DEVICE_LOCK_FEE = 550  # R550 penalty

# Commission rates
SELL_NOW_PERCENTAGE = 0.65         # 65% offer
CONSIGNMENT_PERCENTAGE = 0.85      # 85% to seller
```

---

## Files to Know

| File | What It Does |
|------|--------------|
| `services/condition_assessment_service.py` | BER detection, damage classification, new calculation |
| `services/offer_service.py` | Main offer logic, integrates everything |
| `services/ai_service.py` | Asks questions, device unlock verification |
| `services/research_queue_service.py` | 2-day research queue management |
| `CONDITION_SYSTEM_UPGRADE.md` | Full technical documentation |
| `QUICK_REFERENCE.md` | This file! |

---

## Troubleshooting

### "Offer seems too low"
→ Check if double-dipping bug returned (should use `calculate_value_with_repairs()`)

### "Item should be BER but got purchase offer"
→ Check BER thresholds, verify damage classification

### "Device unlock questions not showing"
→ Check category in `requires_device_unlock_check()` - Line 560

### "Research queue not triggering"
→ Check `repair_confidence_threshold` in offer_service.py - Line 27

---

**Pro Tip:** Read `CONDITION_SYSTEM_UPGRADE.md` for full technical details. This is just the quick reference!
