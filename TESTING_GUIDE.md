# Testing Guide - Priority 1 & 2 Features

## Overview
This guide helps you test the newly implemented features: intelligent repair costs (Priority 1) and frontend multi-select checkboxes with transparent pricing display (Priority 2).

---

## Pre-Testing Setup

### 1. Environment Variables
Ensure `.env` file has:
```bash
PERPLEXITY_API_KEY=your_perplexity_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 2. Start the Application
```bash
cd "/Users/Focus/Downloads/Claude ED Price Research Tool - Jan 2026"
python3 app.py
```

Should see:
```
 * Running on http://127.0.0.1:5000
```

### 3. Open in Browser
Navigate to: `http://localhost:5000`

---

## Test Case 1: Perfect Condition iPhone (No Damage)

**Purpose:** Test that items with no damage get accurate offers without repair deductions

### Steps:
1. Click "Start Now"
2. Enter: "iPhone 11 128GB"
3. Select condition: "Excellent - Like new"
4. Damage question appears with checkboxes
5. Select ONLY: "None - Everything works perfectly"
6. Click "Continue"

### Expected Result:
```
Market Value (Median): R5,000.00
Condition (Excellent) ×98%: R4,900.00

(No repair costs breakdown shown)

Adjusted Value: R4,900.00

OPTION 1: Sell Now
R3,185 (65%)

OPTION 2: Consignment
R4,165 (85%)
💰 That's R980 MORE!
```

### ✅ Checklist:
- [ ] Checkboxes render properly
- [ ] Can select "None - Everything works perfectly"
- [ ] No repair costs breakdown shown
- [ ] Market value around R5,000
- [ ] Condition multiplier applied (98%)
- [ ] No repair deductions
- [ ] Both offers displayed side-by-side
- [ ] Savings calculation correct

---

## Test Case 2: iPhone with Screen Damage Only

**Purpose:** Test single damage type with Perplexity research

### Steps:
1. Click "Start Now"
2. Enter: "iPhone 11 128GB"
3. Select condition: "Good - Minor wear"
4. Damage question appears
5. Select ONLY: "Screen cracked or scratched"
6. Click "Continue"

### Expected Result:
```
Market Value (Median): R5,000.00
Condition (Good) ×90%: R4,500.00

⚠️ Repair Costs Breakdown:
• Screen cracked or scratched: R1,200
  (Based on iStore, iFix - typical iPhone 11
   screen replacement including labor)

Total Deductions: R1,200

Adjusted Value: R3,300.00

OPTION 1: Sell Now - R2,145 (65%)
OPTION 2: Consignment - R2,805 (85%)
💰 That's R660 MORE!
```

### ✅ Checklist:
- [ ] Perplexity API called (check terminal logs)
- [ ] Repair cost around R1,200 (±R200)
- [ ] Repair explanation shows sources
- [ ] Repair breakdown has yellow background
- [ ] Adjusted value = (market × 0.9) - repair costs
- [ ] Both offers calculate correctly
- [ ] Savings = consignment - sell now

### Terminal Debug Output to Check:
```
============================================================
INTELLIGENT REPAIR COST RESEARCH
Product: Apple iPhone 11
Damages: ['Screen cracked or scratched']
============================================================

Researching: Screen cracked or scratched
  Perplexity response: [actual API response]
  → Found: R1,200 - typical screen replacement including labor

Total Repair Costs: R1,200
============================================================
```

---

## Test Case 3: iPhone with Multiple Damages

**Purpose:** Test multiple damage selections with cumulative repair costs

### Steps:
1. Click "Start Now"
2. Enter: "iPhone 11 128GB"
3. Select condition: "Fair - Visible scratches"
4. Damage question appears
5. Select MULTIPLE:
   - "Screen cracked or scratched"
   - "Battery health below 80%"
   - "Back glass cracked"
6. Click "Continue"

### Expected Result:
```
Market Value (Median): R5,000.00
Condition (Fair) ×75%: R3,750.00

⚠️ Repair Costs Breakdown:
• Screen cracked or scratched: R1,200
  (Based on iStore, iFix - typical screen replacement)
• Battery health below 80%: R650
  (Based on local repair shops - battery replacement)
• Back glass cracked: R800
  (Based on Apple service centers - back glass replacement)

Total Deductions: R2,650

Adjusted Value: R1,100.00

OPTION 1: Sell Now - R715 (65%)
OPTION 2: Consignment - R935 (85%)
💰 That's R220 MORE!
```

### ✅ Checklist:
- [ ] Can select multiple checkboxes
- [ ] All selected items display in chat (bullet list)
- [ ] Perplexity researches ALL damages (3 API calls)
- [ ] Each repair cost has source attribution
- [ ] Total deductions = sum of all repairs
- [ ] Adjusted value = (market × condition) - total repairs
- [ ] Offers calculate correctly

### Terminal Debug Output:
```
Researching: Screen cracked or scratched
  → Found: R1,200

Researching: Battery health below 80%
  → Found: R650

Researching: Back glass cracked
  → Found: R800

Total Repair Costs: R2,650
```

---

## Test Case 4: MacBook with Different Category

**Purpose:** Test category-specific damage options and higher repair costs

### Steps:
1. Click "Start Now"
2. Enter: "MacBook Pro 2020 16GB 512GB"
3. Select condition: "Good - Minor wear"
4. Damage question shows LAPTOP options:
   - "Screen scratches, dead pixels, or cracks"
   - "Keyboard keys missing or sticky"
   - "Trackpad not working properly"
   - "Battery health below 80%"
   - etc.
5. Select: "Battery health below 80%"
6. Click "Continue"

### Expected Result:
```
Market Value (Median): R15,000.00
Condition (Good) ×90%: R13,500.00

⚠️ Repair Costs Breakdown:
• Battery health below 80%: R1,100
  (Based on Apple Store, iStore - typical MacBook Pro
   battery replacement)

Total Deductions: R1,100

Adjusted Value: R12,400.00

OPTION 1: Sell Now - R8,060 (65%)
OPTION 2: Consignment - R10,540 (85%)
💰 That's R2,480 MORE!
```

### ✅ Checklist:
- [ ] Laptop-specific damage options shown (not phone options)
- [ ] Battery repair cost HIGHER than iPhone (~R1,100 vs R650)
- [ ] Market value higher for MacBook
- [ ] All calculations correct

---

## Test Case 5: Perplexity API Failure (Fallback Test)

**Purpose:** Test that fallback estimates work when Perplexity fails

### Steps:
1. Temporarily set wrong Perplexity API key in `.env`
2. Restart app
3. Enter: "iPhone 11 128GB"
4. Select condition: "Good"
5. Select damage: "Screen cracked or scratched"
6. Click "Continue"

### Expected Result:
```
⚠️ Repair Costs Breakdown:
• Screen cracked or scratched: R1,500
  (Estimated repair cost - manual verification recommended)

Total Deductions: R1,500
```

### ✅ Checklist:
- [ ] No crash when API fails
- [ ] Fallback estimate used (~R1,500 for iPhone screen)
- [ ] User sees offer (not error message)
- [ ] Message indicates estimate vs research

### Terminal Debug Output:
```
Perplexity API Error: [error details]
Using fallback estimate for screen_cracked: R1,500
```

**Remember to restore correct API key after test!**

---

## Test Case 6: Frontend Checkbox UX

**Purpose:** Test checkbox visual feedback and interactions

### Steps:
1. Start conversation
2. Get to damage question
3. Test interactions:
   - Hover over checkbox options
   - Click checkboxes on/off
   - Try to submit with nothing selected
   - Select multiple items
   - Unselect items
   - Submit with valid selection

### ✅ Visual Checklist:
- [ ] Checkboxes have purple border on hover
- [ ] Background changes to light purple on hover
- [ ] Checked items have purple accent color
- [ ] Checked items text becomes bold
- [ ] Submit button is full-width purple
- [ ] Error shows if no selection made
- [ ] Multiple selections work smoothly
- [ ] Mobile responsive (if testing on phone)

---

## Test Case 7: Pricing Display Visual Check

**Purpose:** Ensure transparent pricing display looks professional

### Steps:
1. Complete any offer flow
2. Review final offer display

### ✅ Visual Checklist:
- [ ] Market value section has light purple background
- [ ] Repair breakdown has yellow/warning background
- [ ] Repair items are bullet points with proper indentation
- [ ] Source attribution is italicized/grayed
- [ ] Adjusted value is bold and highlighted
- [ ] Dual offers are side-by-side (desktop)
- [ ] Dual offers stack vertically (mobile)
- [ ] Consignment option has gradient background
- [ ] Savings amount is green and bold
- [ ] All numbers formatted correctly (commas, 2 decimals)

---

## Test Case 8: Complete End-to-End Flow

**Purpose:** Test entire user journey from start to customer info submission

### Steps:
1. Click "Start Now"
2. Enter: "Samsung Galaxy S21 128GB"
3. Select condition: "Good - Minor wear"
4. Select damages:
   - "Screen cracked or scratched"
   - "Battery health below 80%"
5. Click "Continue"
6. Review offer
7. Enter customer info:
   - Name: "Test User"
   - Email: "test@example.com"
   - Phone: "0821234567"
8. Click "Get My Offer"

### Expected Result:
```
✅ Offer Confirmed!

R[amount]

We've received your information and will contact you
within 24 hours to arrange collection or drop-off.

You've also received a confirmation email.
```

### ✅ Checklist:
- [ ] Entire flow works smoothly
- [ ] No JavaScript errors (check browser console)
- [ ] No Python errors (check terminal)
- [ ] Offer email sent successfully
- [ ] Confirmation message displays
- [ ] Session data persists throughout

---

## Browser Compatibility Tests

Test in multiple browsers:

### Chrome/Edge (Recommended)
- [ ] All features work
- [ ] Checkboxes render correctly
- [ ] Hover states work
- [ ] No console errors

### Safari (macOS/iOS)
- [ ] Checkboxes work
- [ ] Styling consistent
- [ ] No layout issues
- [ ] Mobile responsive

### Firefox
- [ ] All interactions work
- [ ] Visual styling matches
- [ ] No compatibility issues

---

## Mobile Testing

Test on actual mobile devices or responsive mode:

### Phone (Portrait)
- [ ] Checkboxes are tappable
- [ ] Text is readable
- [ ] Dual offers stack vertically
- [ ] No horizontal scrolling
- [ ] Buttons are large enough to tap

### Tablet
- [ ] Layout adjusts appropriately
- [ ] Offers side-by-side if space allows
- [ ] All text readable

---

## Performance Testing

### Check Terminal Logs:

**Look for:**
```
============================================================
INTELLIGENT REPAIR COST RESEARCH
Product: Apple iPhone 11
Damages: ['Screen cracked or scratched', 'Battery health below 80%']
============================================================

Researching: Screen cracked or scratched
  Perplexity response: [actual response]
  → Found: R1,200 - typical screen replacement including labor

Researching: Battery health below 80%
  Perplexity response: [actual response]
  → Found: R650 - typical battery replacement including parts

Total Repair Costs: R1,850
============================================================

Pricing Calculation:
- Market Value: R5,000.00
- Condition (good): 90% = R4,500.00
- Repair Costs: -R1,850.00
- Adjusted Value: R2,650.00
```

### Timing:
- [ ] Each Perplexity call: 2-5 seconds
- [ ] Total offer calculation: 5-15 seconds
- [ ] No timeouts
- [ ] User sees loading spinner

---

## Common Issues & Solutions

### Issue: "No checkbox options provided"
**Cause:** Backend not sending `multi_select` type
**Check:** ai_service.py line ~200 - ensure question type is set

### Issue: Repair costs show as R0
**Cause:** Perplexity API key missing or invalid
**Solution:** Check `.env` file, verify API key

### Issue: Checkboxes don't render
**Cause:** JavaScript error or missing HTML element
**Solution:** Check browser console, verify checkbox-area exists in HTML

### Issue: Selected items don't submit
**Cause:** Event listener not attached
**Solution:** Check browser console for errors

### Issue: Styling looks broken
**Cause:** CSS not loaded or cached old version
**Solution:** Hard refresh (Cmd+Shift+R / Ctrl+Shift+F5)

---

## Success Criteria

All tests pass when:

✅ Multi-select checkboxes work smoothly
✅ Perplexity research returns accurate costs
✅ Repair breakdown displays with sources
✅ Dual offers calculate correctly
✅ Savings amount is accurate
✅ Fallback estimates work when API fails
✅ Visual design is professional
✅ Mobile responsive
✅ No console errors
✅ No terminal errors
✅ End-to-end flow completes

---

## Reporting Issues

If you find bugs, note:

1. **Test case number**
2. **Browser/device**
3. **What you did** (steps)
4. **What happened** (actual result)
5. **What should happen** (expected result)
6. **Console errors** (if any)
7. **Terminal errors** (if any)

Example:
```
Test Case 2 - Chrome on macOS
Steps: Selected "Screen cracked", clicked Continue
Actual: Repair cost shows R0
Expected: Repair cost ~R1,200
Console: No errors
Terminal: "Perplexity API Error: Invalid API key"
```

---

## Next Steps After Testing

Once all tests pass:

1. Deploy to staging environment
2. Test with real Perplexity API calls
3. Monitor API usage and costs
4. Collect user feedback
5. Track accuracy metrics
6. Adjust repair cost estimates if needed

---

**Happy Testing!** 🧪✅
