# Current Status & Missing Features - January 21, 2026

## Your Questions

### 1. ❓ "Can we use Perplexity to find repair costs and show them in the calculation?"

**Answer:** YES! Great idea - we can absolutely do this.

### 2. ❓ "Do we have photo upload and email built already?"

**Answer:** Partially

- ✅ **Email Service EXISTS** (`services/email_service.py`)
- ❌ **Photo Upload NOT BUILT YET**

---

## What Exists vs What's Missing

### ✅ BUILT & WORKING

#### Backend Services:
1. **AI Service** (`services/ai_service.py`) - Conversation logic ✅
2. **Offer Service** (`services/offer_service.py`) - Calculate offers ✅
3. **Price Research Service** (`services/price_research_service.py`) - Market research ✅
4. **Perplexity Price Service** (`services/perplexity_price_service.py`) - Real-time pricing ✅
5. **Repair Cost Service** (`services/repair_cost_service.py`) - Basic repair estimates ✅
6. **Email Service** (`services/email_service.py`) - Send emails ✅
7. **Condition Assessment Service** (`services/condition_assessment_service.py`) - NEW! ✅

#### Core Features:
- Conversation flow (2-3 questions)
- Product info extraction
- Market value research (Perplexity)
- Dual business models (Sell Now 65% + Consignment 85%)
- Courier eligibility checking
- Condition assessment with specific damage tracking
- Email notifications

### ❌ NOT BUILT YET

#### Missing Features:
1. **Photo Upload** ❌
   - No upload endpoint in `app.py`
   - No Cloudinary integration
   - No frontend upload interface
   - No photo storage

2. **Intelligent Repair Cost Research** ❌
   - Current system uses static estimates
   - Perplexity NOT integrated for repair costs
   - No real-time repair pricing research
   - No transparent breakdown shown to users

3. **Frontend Multi-Select** ❌
   - Backend supports `multi_select` questions
   - Frontend doesn't have checkbox UI for damage options
   - Only text and multiple_choice work currently

4. **Pricing Breakdown Display** ❌
   - Backend calculates detailed breakdown
   - Frontend doesn't show "why" the offer is what it is
   - No transparent explanation to users

5. **Database** ❌
   - No PostgreSQL setup
   - No listings table
   - No seller tracking
   - No product_specs database

---

## Implementation Plan

### 🎯 Priority 1: Intelligent Repair Costs with Perplexity (HIGH IMPACT)

**Why This First:**
- Transparent pricing = trust
- Accurate costs = less risk
- Shows users exactly why offer is lower

**Implementation:**

#### Step 1: Enhance Repair Cost Service with Perplexity

Create `services/intelligent_repair_cost_service.py`:

```python
from services.perplexity_price_service import PerplexityPriceService

class IntelligentRepairCostService:
    """
    Uses Perplexity to research actual repair costs in South Africa
    """

    def __init__(self):
        self.perplexity = PerplexityPriceService()

    def research_repair_cost(self, product_info, damage_type):
        """
        Research actual repair cost for specific damage

        Example: iPhone 11 screen replacement cost in South Africa
        """

        brand = product_info.get('brand', '')
        model = product_info.get('model', '')
        category = product_info.get('category', '')

        # Build search query
        query = f"{brand} {model} {damage_type} repair cost South Africa 2026"

        # Use Perplexity to research
        result = self.perplexity.search_prices(query)

        # Extract repair cost from results
        repair_cost = self._extract_repair_cost(result)

        return {
            'damage_type': damage_type,
            'estimated_cost': repair_cost,
            'source': 'Perplexity real-time research',
            'confidence': result.get('confidence', 0.8),
            'details': f"Based on current {brand} {model} {damage_type} repair pricing"
        }

    def research_all_damages(self, product_info, damage_details):
        """
        Research costs for all reported damages

        Returns:
            {
                'screen_cracked': {'cost': 1200, 'source': '...', 'details': '...'},
                'battery_degraded': {'cost': 650, 'source': '...', 'details': '...'},
                'total': 1850,
                'breakdown_message': "Screen: R1,200 | Battery: R650"
            }
        """

        breakdown = {}
        total = 0

        for damage in damage_details:
            if 'none' in damage.lower() and 'works' in damage.lower():
                continue

            # Research this specific damage cost
            cost_info = self.research_repair_cost(product_info, damage)
            breakdown[damage] = cost_info
            total += cost_info['estimated_cost']

        return {
            'breakdown': breakdown,
            'total_repair_cost': total,
            'explanation': self._format_breakdown_message(breakdown)
        }

    def _format_breakdown_message(self, breakdown):
        """
        Format user-friendly message showing repair costs

        Example:
        "Repair Costs Breakdown:
        • Screen replacement: R1,200 (typical iPhone 11 screen repair)
        • Battery replacement: R650 (includes labor)
        Total Deductions: R1,850"
        """

        lines = ["**Repair Costs Breakdown:**"]
        for damage, info in breakdown.items():
            lines.append(f"• {damage}: R{info['estimated_cost']:,.0f} ({info['details']})")

        total = sum(info['estimated_cost'] for info in breakdown.values())
        lines.append(f"\n**Total Deductions: R{total:,.0f}**")

        return "\n".join(lines)
```

#### Step 2: Update Offer Service to Show Breakdown

Modify `services/offer_service.py`:

```python
def format_offer_message(self, offer_data, customer_info=None):
    """
    Enhanced to show repair cost breakdown
    """

    if offer_data['recommendation'] == 'instant_offer':
        message = f"""Thank you for your interest in selling to EpicDeals!

**Market Value (Median): R{offer_data['market_value']:,.2f}**

"""

        # Show repair costs breakdown if any
        if offer_data.get('repair_costs', 0) > 0:
            message += f"""
**Why the adjusted price?**

{offer_data.get('repair_breakdown_message', '')}

These are typical repair costs in South Africa based on current market rates.
We deduct these to ensure we can refurbish the item properly.

**Adjusted Value: R{offer_data['adjusted_value']:,.2f}**

---

"""

        # Continue with sell now and consignment options...
```

#### Step 3: Test with Real Example

```
Product: iPhone 11 128GB
Condition: Good
Damage: Screen cracked

PERPLEXITY RESEARCH:
Query: "iPhone 11 screen replacement cost South Africa 2026"
Result: R1,200 - R1,500 typical cost

SHOWN TO USER:
"Market Value: R5,000

Why the adjusted price?

Repair Costs Breakdown:
• Screen cracked: R1,200 (typical iPhone 11 screen repair at iStore or iFix)

Total Deductions: R1,200

Adjusted Value: R3,800

OPTION 1: Sell Now
You Get: R2,470 (65% of adjusted value)

OPTION 2: Consignment
You Get: R3,230 (85% of adjusted value)
That's R760 MORE!"
```

**Benefits:**
- ✅ Real-time accurate repair costs
- ✅ Transparent pricing (users see WHY)
- ✅ Trust building (not arbitrary deductions)
- ✅ Reduces disputes

**Time to Implement:** 2-3 hours

---

### 🎯 Priority 2: Photo Upload (MEDIUM-HIGH IMPACT)

**Status:** NOT BUILT

**Why Important:**
- Visual verification of condition
- Reduces inspection surprises
- Professional listings ready

**Implementation:**

#### Step 1: Add Cloudinary Integration

Create `utils/photo_upload.py`:

```python
import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config(
    cloud_name = "your_cloud_name",
    api_key = "your_api_key",
    api_secret = "your_api_secret"
)

def upload_product_photo(file, product_info):
    """
    Upload photo to Cloudinary

    Returns:
        {
            'url': 'https://cloudinary.com/...',
            'public_id': 'epicdeals/iphone11_001',
            'format': 'jpg'
        }
    """

    # Generate unique filename
    sku = f"{product_info['brand']}_{product_info['model']}_{timestamp}"

    result = cloudinary.uploader.upload(
        file,
        folder="epicdeals/products",
        public_id=sku,
        overwrite=True,
        resource_type="image"
    )

    return {
        'url': result['secure_url'],
        'public_id': result['public_id'],
        'format': result['format']
    }
```

#### Step 2: Add Upload Endpoint to app.py

```python
@app.route('/api/upload-photos', methods=['POST'])
def upload_photos():
    """Handle photo uploads"""

    if 'photos' not in request.files:
        return jsonify({'error': 'No photos provided'}), 400

    files = request.files.getlist('photos')
    product_info = session.get('product_info', {})

    if len(files) < 4:
        return jsonify({'error': 'Please upload at least 4 photos'}), 400

    photo_urls = []
    for file in files:
        result = upload_product_photo(file, product_info)
        photo_urls.append(result['url'])

    # Save to product_info
    product_info['photo_urls'] = photo_urls
    session['product_info'] = product_info

    return jsonify({
        'success': True,
        'photo_urls': photo_urls
    })
```

#### Step 3: Add Frontend Upload UI

Update `templates/index.html` and `static/js/app.js`:

```html
<!-- Photo upload step (after damage details) -->
<div id="photo-upload-section" style="display: none;">
    <h3>Upload Photos</h3>
    <p>Please upload 4-6 clear photos:</p>
    <ul>
        <li>Front view</li>
        <li>Back view</li>
        <li>Side views</li>
        <li>Any damage/wear</li>
        <li>Serial number/IMEI (if visible)</li>
    </ul>

    <input type="file" id="photo-input" multiple accept="image/*" max="6">
    <div id="photo-preview"></div>
    <button id="upload-photos-btn">Upload Photos</button>
</div>
```

```javascript
// Handle photo upload
document.getElementById('upload-photos-btn').addEventListener('click', async () => {
    const files = document.getElementById('photo-input').files;

    if (files.length < 4) {
        alert('Please upload at least 4 photos');
        return;
    }

    const formData = new FormData();
    for (let file of files) {
        formData.append('photos', file);
    }

    const response = await fetch('/api/upload-photos', {
        method: 'POST',
        body: formData
    });

    const data = await response.json();
    if (data.success) {
        // Show success and move to offer
        calculateOffer();
    }
});
```

**Time to Implement:** 3-4 hours

---

### 🎯 Priority 3: Frontend Multi-Select & Pricing Breakdown (HIGH IMPACT)

**Status:** Backend ready, frontend missing

#### Step 1: Add Multi-Select Checkbox UI

Update `static/js/app.js`:

```javascript
function displayQuestion(questionData) {
    if (questionData.type === 'multi_select') {
        // Create checkboxes
        let html = `<p>${questionData.question}</p>`;
        html += '<div class="checkbox-group">';

        for (let option of questionData.options) {
            html += `
                <label class="checkbox-label">
                    <input type="checkbox" value="${option}" name="damage_option">
                    <span>${option}</span>
                </label>
            `;
        }

        html += '</div>';
        html += '<button id="submit-checkboxes">Continue</button>';

        document.getElementById('question-container').innerHTML = html;

        // Handle submission
        document.getElementById('submit-checkboxes').addEventListener('click', () => {
            const selected = [];
            document.querySelectorAll('input[name="damage_option"]:checked').forEach(cb => {
                selected.push(cb.value);
            });

            submitAnswer(selected.join(', '));
        });
    }
}
```

#### Step 2: Show Pricing Breakdown in Offer

```javascript
function displayOffer(offerData) {
    let html = `
        <h2>Your Offer</h2>
        <div class="offer-breakdown">
            <h3>Market Value: R${offerData.market_value.toFixed(2)}</h3>
    `;

    if (offerData.repair_breakdown_message) {
        html += `
            <div class="repair-costs">
                ${offerData.repair_breakdown_message}
            </div>
        `;
    }

    html += `
        <h3>Adjusted Value: R${offerData.adjusted_value.toFixed(2)}</h3>

        <div class="sell-now-option">
            <h4>OPTION 1: Sell Now</h4>
            <p class="offer-amount">R${offerData.sell_now_offer.toFixed(2)}</p>
        </div>

        <div class="consignment-option">
            <h4>OPTION 2: Consignment</h4>
            <p class="offer-amount">R${offerData.consignment_payout.toFixed(2)}</p>
        </div>
    `;
}
```

**Time to Implement:** 2-3 hours

---

## Summary: What to Build Next

### Recommended Order:

**Week 1: Intelligent Pricing & Transparency**
1. ✅ Intelligent repair costs with Perplexity (2-3 hours)
2. ✅ Show pricing breakdown to users (1-2 hours)
3. ✅ Frontend multi-select checkboxes (2-3 hours)

**Week 2: Photo Upload**
4. ⏳ Cloudinary setup & integration (3-4 hours)
5. ⏳ Photo upload endpoint (1-2 hours)
6. ⏳ Frontend upload UI (2-3 hours)

**Week 3: Testing & Refinement**
7. ⏳ Test full flow with real products
8. ⏳ Adjust repair costs based on data
9. ⏳ Refine user messaging

---

## Current File Status

### ✅ WORKING:
- `app.py` - Main Flask app with conversation endpoints
- `services/ai_service.py` - Conversation logic
- `services/offer_service.py` - Offer calculation
- `services/price_research_service.py` - Market research
- `services/perplexity_price_service.py` - Real-time pricing
- `services/email_service.py` - Email notifications
- `services/condition_assessment_service.py` - Damage tracking
- `config.py` - Configuration (65% sell now, 85% consignment)

### ❌ MISSING:
- `utils/photo_upload.py` - NOT BUILT
- `services/intelligent_repair_cost_service.py` - NOT BUILT
- Frontend multi-select UI - NOT BUILT
- Cloudinary integration - NOT SET UP
- Database tables - NOT CREATED

---

## Quick Wins (Do These First!)

### 1. Transparent Repair Costs (2-3 hours)
**Impact:** HIGH - Users understand pricing
**Effort:** LOW - Just integrate Perplexity research

### 2. Show Pricing Breakdown (1 hour)
**Impact:** HIGH - Builds trust
**Effort:** LOW - Just format output differently

### 3. Multi-Select Checkboxes (2 hours)
**Impact:** MEDIUM - Better UX
**Effort:** LOW - Frontend only

**Total Time:** 5-6 hours for massive improvement!

---

## Status Summary

| Feature | Backend | Frontend | Status |
|---------|---------|----------|--------|
| Conversation Flow | ✅ | ✅ | Working |
| Market Research | ✅ | ✅ | Working |
| Condition Assessment | ✅ | ❌ | Backend ready |
| Repair Cost Research | ❌ | ❌ | Static only |
| Pricing Breakdown | ✅ | ❌ | Backend ready |
| Multi-Select | ✅ | ❌ | Backend ready |
| Photo Upload | ❌ | ❌ | Not built |
| Email Notifications | ✅ | N/A | Working |
| Database | ❌ | ❌ | Not built |

**Next Action:** Implement intelligent repair costs with Perplexity!
