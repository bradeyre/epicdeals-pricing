# How to Enable v3.0 Universal Pricing

The v3.0 architecture is fully built and ready to test! Here's how to enable it:

## Quick Enable (In Browser Console)

1. Start the app: `python3 app.py`
2. Open http://localhost:5000 in your browser
3. Open browser console (F12 or Cmd+Option+I)
4. Before clicking "Get Started", run:
   ```javascript
   // Find the app instance and enable v3
   window.epicDealsApp = document.querySelector('.container').__vue__ || window.app;

   // Or directly enable on page load by adding to index.html:
   document.addEventListener('DOMContentLoaded', () => {
       const app = new EpicDealsApp();
       app.enableV3Mode();  // <-- This switches to v3
   });
   ```

## Permanent Enable (Modify index.html)

Edit `templates/index.html`, find the script initialization at the bottom:

**Change from:**
```javascript
document.addEventListener('DOMContentLoaded', () => {
    new EpicDealsApp();
});
```

**Change to:**
```javascript
document.addEventListener('DOMContentLoaded', () => {
    const app = new EpicDealsApp();
    app.enableV3Mode();  // Enable v3.0 Universal Pricing
});
```

## What Happens When v3 is Enabled?

✅ **"Get Started" button** triggers v3 conversation flow
✅ **All messages** route through `/api/message/v3`
✅ **Quick-select buttons** appear for every question
✅ **Progress dots** show at top (●●○○)
✅ **Condition checklists** dynamically generated per product
✅ **Calculating animation** with status updates
✅ **Works for ANY product** (not just electronics)

## Test Products

Try these to validate universal coverage:

1. **Phone:** "iPhone 14 128GB"
2. **Car:** "2019 VW Polo 1.0 TSI"
3. **Shoes:** "Nike Air Jordan 4 Retro size 10"
4. **Appliance:** "Dyson Airwrap Complete Long"
5. **Laptop:** "MacBook Air M2"
6. **TV:** "Samsung 65 inch QLED"
7. **Camera:** "Canon EOS R5"
8. **Console:** "PS5 Slim Digital"
9. **Furniture:** "Weylandts leather couch 3 seater"
10. **Beauty:** "GHD hair straightener"

## Expected Behavior

- **2-4 questions max** (enforced by GuardrailEngine)
- **No duplicate questions** (validated at code level)
- **"I don't know" handled** (marks as unknown, moves on)
- **Product-specific questions** (car asks mileage, phone asks storage)
- **Always reaches offer** (guaranteed by engine)

## A/B Testing (Run Both v2 and v3)

To run both versions simultaneously:

1. Keep v2 as default (current behavior)
2. Add a "Try v3 Beta" button that calls `app.enableV3Mode()`
3. Track metrics:
   - Questions per conversation (target: ≤3)
   - Time to offer (target: <45 seconds)
   - Completion rate (target: >90%)
   - Duplicate question rate (target: 0%)

## Rollback Plan

If issues found:
1. Comment out `app.enableV3Mode()` line
2. App reverts to v2.0 automatically
3. No data loss (v2 routes still active)

## Architecture Comparison

### v2.0 (Current)
- AI controls everything (flow, duplicates, rules)
- 800-line complex prompt
- Electronics-focused
- 6-8 questions typical
- Duplicates possible

### v3.0 (New)
- **AI + Python guardrails**
- 300-line simple prompt
- **Universal (ANY product)**
- **2-4 questions max**
- **Zero duplicates** (code-enforced)

---

Ready to test! Just add `app.enableV3Mode()` and experience the new universal pricing engine.
