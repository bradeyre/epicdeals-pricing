# Enhanced Condition Assessment System

## Problem
Current system only asks "What is the physical condition?" which is too vague:
- Doesn't capture specific damage types
- Can't accurately adjust pricing for different issues
- Users might overstate condition
- No way to differentiate between "Good with minor scratches" vs "Good but cracked screen"

## Solution: Two-Stage Condition Assessment

### Stage 1: Overall Condition (Current)
Quick assessment to categorize the item:
- Excellent - Like new
- Good - Minor wear
- Fair - Visible scratches/wear
- Poor - Damaged/broken

### Stage 2: Specific Issues Check (NEW)
Follow-up question based on category to identify specific problems that affect value.

---

## Implementation Design

### 1. Category-Specific Damage Questions

#### For Phones/Tablets:
```
"Are there any of the following issues with your [iPhone 11]?"
(Multi-select checkboxes)

□ Screen cracked or scratched
□ Back glass cracked
□ Body dents or deep scratches
□ Battery health below 80%
□ Camera issues (blurry, not working)
□ Face ID / Touch ID not working
□ Buttons or ports damaged
□ Water damage
□ None - Everything works perfectly ✓

If "None" selected → Skip detailed questions
If any issues selected → Ask for details on each
```

#### For Laptops:
```
"Are there any of the following issues with your [MacBook Pro]?"
(Multi-select checkboxes)

□ Screen scratches, dead pixels, or cracks
□ Keyboard keys missing or sticky
□ Trackpad not working properly
□ Battery health below 80% / won't hold charge
□ Dents or cracks in body/chassis
□ Hinge loose or broken
□ Ports not working (USB, charging, etc.)
□ Overheating issues
□ None - Everything works perfectly ✓
```

#### For Cameras:
```
"Are there any of the following issues with your [Canon DSLR]?"
(Multi-select checkboxes)

□ Lens scratches or fungus
□ Sensor dust or spots
□ Shutter not working / high shutter count
□ Autofocus issues
□ Body scratches or dents
□ Missing parts (lens cap, battery, etc.)
□ Viewfinder scratches
□ None - Everything works perfectly ✓
```

#### For Appliances (Washing Machines, Fridges, etc.):
```
"Are there any of the following issues with your [Samsung Washing Machine]?"
(Multi-select checkboxes)

□ Doesn't start or complete cycles
□ Leaks water
□ Makes excessive noise
□ Door doesn't close properly
□ Visible rust or corrosion
□ Dents or scratches on exterior
□ Missing parts (drawer, filter, etc.)
□ None - Everything works perfectly ✓
```

#### For TVs:
```
"Are there any of the following issues with your [Samsung TV]?"
(Multi-select checkboxes)

□ Screen burn-in or dead pixels
□ Cracked screen
□ Lines or discoloration
□ HDMI ports not working
□ Smart features not working
□ Stand missing or broken
□ Remote missing
□ None - Everything works perfectly ✓
```

---

## Pricing Adjustment Logic

### Base Price Formula:
```python
Base Market Value = Median from research
Condition Multiplier = Based on overall condition
Issue Deductions = Sum of specific issue impacts
Repair Cost Estimate = From repair_cost_service

Final Adjusted Value = (Base Market Value × Condition Multiplier) - Issue Deductions - Repair Costs
```

### Condition Multipliers:

| Condition | Multiplier | Description |
|-----------|------------|-------------|
| Excellent | 0.95-1.00 | Like new, no visible wear |
| Good | 0.85-0.94 | Minor wear, fully functional |
| Fair | 0.70-0.84 | Visible wear, all features work |
| Poor | 0.50-0.69 | Major damage or functionality issues |
| Broken | 0.20-0.49 | Not working, parts value only |

### Issue Deductions (Phones - iPhone Example):

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Screen cracked | -R800 to -R1,500 | Major issue, expensive repair |
| Screen scratched | -R200 to -R400 | Cosmetic, less severe |
| Back glass cracked | -R600 to -R1,000 | Common issue |
| Body dents | -R200 to -R500 | Cosmetic |
| Battery <80% | -R500 to -R800 | Replacement needed |
| Camera issues | -R400 to -R1,200 | Depends on severity |
| Face/Touch ID broken | -R800 to -R1,500 | Major feature loss |
| Buttons/ports damaged | -R300 to -R600 | Repair needed |
| Water damage | -R1,000 to -R2,500 | High risk, unpredictable |

### Issue Deductions (Laptops - MacBook Example):

| Issue | Deduction | Notes |
|-------|-----------|-------|
| Screen cracked | -R2,000 to -R5,000 | Very expensive repair |
| Dead pixels | -R500 to -R1,500 | Depends on severity |
| Keyboard issues | -R1,000 to -R2,500 | Replacement costly |
| Battery <80% | -R800 to -R1,500 | Easy to replace |
| Body dents/cracks | -R500 to -R1,500 | Cosmetic to structural |
| Trackpad broken | -R800 to -R1,200 | Important feature |
| Ports not working | -R600 to -R1,500 | Critical for usability |

---

## Enhanced AI Service Logic

### Update `services/ai_service.py`:

```python
def get_next_question(self, conversation_history, product_info):
    """
    Enhanced flow:
    1. Extract product info from first message
    2. Ask for missing specs (storage, RAM, etc.)
    3. Ask for OVERALL condition
    4. Ask for SPECIFIC ISSUES (based on category) ← NEW
    5. Mark as completed
    """
```

### New System Prompt Addition:

```python
ENHANCED QUESTION FLOW:

After asking about overall condition, ALWAYS ask about specific issues:

For phones/tablets:
{
    "question": "Are there any of these issues with your [Product]? Select all that apply:",
    "field_name": "damage_details",
    "type": "multi_select",
    "options": [
        "Screen cracked or scratched",
        "Back glass cracked",
        "Body dents or deep scratches",
        "Battery health below 80%",
        "Camera issues",
        "Face ID / Touch ID not working",
        "Buttons or ports damaged",
        "Water damage",
        "None - Everything works perfectly"
    ],
    "completed": false
}

If user selects "None - Everything works perfectly" → Set completed: true
If user selects any issues → These will be used for pricing adjustments

For laptops:
{
    "question": "Are there any of these issues with your [Product]? Select all that apply:",
    "field_name": "damage_details",
    "type": "multi_select",
    "options": [
        "Screen scratches, dead pixels, or cracks",
        "Keyboard keys missing or sticky",
        "Trackpad not working properly",
        "Battery health below 80%",
        "Dents or cracks in body",
        "Hinge loose or broken",
        "Ports not working",
        "Overheating issues",
        "None - Everything works perfectly"
    ],
    "completed": false
}
```

---

## Updated Conversation Flow Examples

### Example 1: iPhone 11 128GB (Perfect Condition)

```
Turn 1:
User: "iPhone 11 128GB"
AI extracts: category=phone, brand=Apple, model=iPhone 11, capacity=128GB
AI asks: "What is the physical condition of your iPhone 11?"

Turn 2:
User: "Excellent - Like new"
AI extracts: condition=excellent
AI asks: "Are there any of these issues? (Screen cracked, Battery issues, etc.)"

Turn 3:
User: [Selects] "None - Everything works perfectly"
AI extracts: damage_details=none
AI responds: completed=true ✓

PRICING:
Base Market Value: R5,000
Condition Multiplier: 0.98 (Excellent, no issues)
Issue Deductions: R0
Repair Costs: R0
Final Value: R5,000 × 0.98 = R4,900

Sell Now Offer (65%): R3,185
Consignment (85%): R4,165
```

### Example 2: iPhone 11 128GB (Good but Cracked Screen)

```
Turn 1:
User: "iPhone 11 128GB"
AI asks: "What is the physical condition?"

Turn 2:
User: "Good - Minor wear"
AI asks: "Are there any of these issues? Select all that apply"

Turn 3:
User: [Selects] "Screen cracked or scratched"
AI extracts: damage_details=[screen_cracked]
AI responds: completed=true ✓

PRICING:
Base Market Value: R5,000
Condition Multiplier: 0.90 (Good)
Issue Deductions: -R1,200 (Cracked screen)
Repair Costs: R0 (already factored in deduction)
Adjusted Value: (R5,000 × 0.90) - R1,200 = R4,500 - R1,200 = R3,300

Sell Now Offer (65%): R2,145
Consignment (85%): R2,805
```

### Example 3: MacBook Pro 2020 (Fair, Multiple Issues)

```
Turn 1:
User: "MacBook Pro 2020"
AI asks: "What are the specs?"

Turn 2:
User: "16GB RAM, 512GB SSD, M1"
AI asks: "What is the physical condition?"

Turn 3:
User: "Fair - Visible scratches"
AI asks: "Are there any of these issues?"

Turn 4:
User: [Selects] "Battery health below 80%", "Body dents or cracks"
AI extracts: damage_details=[battery_degraded, body_dents]
AI responds: completed=true ✓

PRICING:
Base Market Value: R15,000
Condition Multiplier: 0.75 (Fair)
Issue Deductions: -R1,200 (Battery) - R800 (Dents) = -R2,000
Adjusted Value: (R15,000 × 0.75) - R2,000 = R11,250 - R2,000 = R9,250

Sell Now Offer (65%): R6,013
Consignment (85%): R7,863
```

---

## Implementation Files

### 1. Create `services/condition_assessment_service.py`

```python
class ConditionAssessmentService:
    """
    Handles condition assessment and pricing adjustments
    """

    # Condition multipliers
    CONDITION_MULTIPLIERS = {
        'excellent': 0.98,
        'pristine': 0.98,
        'good': 0.90,
        'fair': 0.75,
        'poor': 0.60,
        'broken': 0.35
    }

    # Issue deductions by category (in ZAR)
    PHONE_DEDUCTIONS = {
        'screen_cracked': 1200,
        'screen_scratched': 300,
        'back_glass_cracked': 800,
        'body_dents': 350,
        'battery_degraded': 650,
        'camera_issues': 800,
        'biometric_broken': 1200,
        'buttons_ports_damaged': 450,
        'water_damage': 1800
    }

    LAPTOP_DEDUCTIONS = {
        'screen_cracked': 3500,
        'dead_pixels': 1000,
        'keyboard_issues': 1750,
        'battery_degraded': 1100,
        'body_damage': 1000,
        'trackpad_broken': 1000,
        'ports_broken': 1000,
        'overheating': 800
    }

    def calculate_adjusted_value(self, base_value, condition, damage_details, category):
        """
        Calculate adjusted value based on condition and specific issues

        Args:
            base_value: Market value from research
            condition: Overall condition (excellent, good, fair, poor)
            damage_details: List of specific issues
            category: Product category (phone, laptop, etc.)

        Returns:
            Adjusted value after applying multipliers and deductions
        """

        # Apply condition multiplier
        multiplier = self.CONDITION_MULTIPLIERS.get(condition.lower(), 0.85)
        adjusted = base_value * multiplier

        # Apply issue deductions
        if damage_details and damage_details != ['none']:
            deductions = self._calculate_issue_deductions(damage_details, category)
            adjusted -= deductions

        # Never go below 20% of base value
        min_value = base_value * 0.20
        adjusted = max(adjusted, min_value)

        return adjusted

    def _calculate_issue_deductions(self, damage_details, category):
        """Calculate total deductions for specific issues"""

        deduction_table = {
            'phone': self.PHONE_DEDUCTIONS,
            'smartphone': self.PHONE_DEDUCTIONS,
            'tablet': self.PHONE_DEDUCTIONS,
            'laptop': self.LAPTOP_DEDUCTIONS,
            'notebook': self.LAPTOP_DEDUCTIONS
        }

        deductions = deduction_table.get(category.lower(), {})
        total = 0

        for issue in damage_details:
            issue_key = issue.lower().replace(' ', '_').replace('-', '_')
            total += deductions.get(issue_key, 0)

        return total

    def get_damage_options_for_category(self, category):
        """Return appropriate damage questions for category"""

        category = category.lower()

        if category in ['phone', 'smartphone', 'tablet']:
            return [
                "Screen cracked or scratched",
                "Back glass cracked",
                "Body dents or deep scratches",
                "Battery health below 80%",
                "Camera issues (blurry, not working)",
                "Face ID / Touch ID not working",
                "Buttons or ports damaged",
                "Water damage",
                "None - Everything works perfectly"
            ]

        elif category in ['laptop', 'notebook', 'macbook']:
            return [
                "Screen scratches, dead pixels, or cracks",
                "Keyboard keys missing or sticky",
                "Trackpad not working properly",
                "Battery health below 80%",
                "Dents or cracks in body",
                "Hinge loose or broken",
                "Ports not working",
                "Overheating issues",
                "None - Everything works perfectly"
            ]

        elif category in ['camera', 'dslr']:
            return [
                "Lens scratches or fungus",
                "Sensor dust or spots",
                "Shutter not working / high count",
                "Autofocus issues",
                "Body scratches or dents",
                "Missing parts",
                "Viewfinder scratches",
                "None - Everything works perfectly"
            ]

        elif category in ['tv', 'television']:
            return [
                "Screen burn-in or dead pixels",
                "Cracked screen",
                "Lines or discoloration",
                "HDMI ports not working",
                "Smart features not working",
                "Stand missing or broken",
                "Remote missing",
                "None - Everything works perfectly"
            ]

        else:
            # Generic for appliances, etc.
            return [
                "Doesn't work properly",
                "Leaks or drips",
                "Makes excessive noise",
                "Missing parts",
                "Visible damage or rust",
                "None - Everything works perfectly"
            ]
```

### 2. Update `services/offer_service.py`

Add condition assessment integration:

```python
from services.condition_assessment_service import ConditionAssessmentService

class OfferService:
    def __init__(self):
        self.price_research_service = PriceResearchService()
        self.repair_cost_service = RepairCostService()
        self.condition_service = ConditionAssessmentService()  # NEW
        self.sell_now_percentage = Config.SELL_NOW_PERCENTAGE
        self.consignment_percentage = Config.CONSIGNMENT_PERCENTAGE

    def calculate_offer(self, product_info, damage_info=None):
        # ... existing code ...

        market_value = price_research.get('market_value')

        # NEW: Apply condition-based adjustments
        condition = product_info.get('condition', 'good')
        damage_details = product_info.get('damage_details', [])
        category = product_info.get('category', 'other')

        adjusted_value = self.condition_service.calculate_adjusted_value(
            market_value,
            condition,
            damage_details,
            category
        )

        # Continue with existing offer calculation using adjusted_value
        sell_now_offer = adjusted_value * self.sell_now_percentage
        # ... rest of logic ...
```

---

## Benefits

### For Accurate Pricing:
✅ Captures specific issues that affect value
✅ More granular pricing adjustments
✅ Reduces risk of overpaying
✅ Fair offers for sellers

### For Sellers:
✅ Transparent pricing breakdown
✅ Understand why offer is what it is
✅ No surprises during inspection
✅ Honest assessment upfront

### For EpicDeals:
✅ Accurate condition assessment before collection
✅ Fewer disputes about condition
✅ Better inventory management
✅ Reduced inspection surprises

---

## Next Steps

1. **Implement** `ConditionAssessmentService`
2. **Update** AI service to ask damage questions
3. **Integrate** with offer calculation
4. **Test** with various scenarios
5. **Add** pricing breakdown to offer message
6. **Monitor** accuracy vs actual inspections

---

## Testing Scenarios

### Test 1: Perfect Condition
- iPhone 11 128GB
- Excellent condition
- No issues selected
- Expected: Highest possible offer

### Test 2: Minor Issues
- iPhone 11 128GB
- Good condition
- Screen scratched + Battery <80%
- Expected: Moderate deductions

### Test 3: Major Issues
- iPhone 11 128GB
- Fair condition
- Screen cracked + Water damage
- Expected: Significant deductions

### Test 4: Laptop
- MacBook Pro 2020
- Good condition
- Battery degraded
- Expected: Laptop-specific deductions applied

---

**Status:** Design Complete - Ready for Implementation
**Priority:** High (improves pricing accuracy significantly)
**Estimated Time:** 4-6 hours implementation + testing
