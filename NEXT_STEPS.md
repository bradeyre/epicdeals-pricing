# EpicDeals Platform - Next Steps & Implementation Plan

## Current Status
✅ Perplexity API working (real-time pricing)
✅ Courier eligibility checking
✅ Dual business model (Buy Now vs Consignment)
✅ Gumtree scraper added
✅ Median price display
✅ **Duplicate question bug FIXED** (Jan 21, 2026)
✅ Conversation flow optimized (2-3 questions max)
✅ **Enhanced condition assessment system** (Jan 21, 2026)
✅ Category-specific damage questions with precise deductions

---

## Critical Issues to Fix First

### 1. ✅ Fix Duplicate Question Bug - FIXED (Jan 21, 2026)
**Issue**: In screenshot, "What is the physical condition..." appeared twice
**Root Cause**: AI wasn't tracking asked questions + assistant messages not in history
**Files Modified**:
- `app.py` - Added assistant message tracking, improved state management
- `services/ai_service.py` - Enhanced prompt with duplicate prevention rules
**Fix Status**: ✅ COMPLETE - See CONVERSATION_FLOW_FIXES.md for details

### 2. Implement AI Product Recognition
**Current**: User types "iPhone 14 Pro Max", AI asks basic questions
**Target**: AI automatically knows it's a phone, looks up specs, asks smart questions

**Implementation**:
```python
# New function in ai_service.py
def identify_and_enrich_product(user_input: str) -> dict:
    """
    User: "iPhone 14 Pro Max"

    AI Returns:
    {
        'brand': 'Apple',
        'model': 'iPhone 14 Pro Max',
        'category': 'smartphone',
        'storage_options': ['128GB', '256GB', '512GB', '1TB'],
        'color_options': ['Space Black', 'Silver', 'Gold', 'Deep Purple'],
        'year_released': 2022,
        'original_price_range': [16999, 26999],
        'current_market_value': 12499,
        'courier_eligible': True,
        'common_issues': ['Battery degradation', 'Camera lens scratches'],
        'key_questions': [
            {
                'field': 'storage',
                'question': 'What storage capacity does your iPhone 14 Pro Max have?',
                'type': 'multiple_choice',
                'options': ['128GB', '256GB', '512GB', '1TB']
            },
            {
                'field': 'color',
                'question': 'What color is it?',
                'type': 'multiple_choice',
                'options': ['Space Black', 'Silver', 'Gold', 'Deep Purple']
            },
            {
                'field': 'condition',
                'question': 'What is the physical condition?',
                'type': 'multiple_choice',
                'options': ['Excellent - Like new', 'Good - Minor wear', 'Fair - Scratches', 'Poor - Damaged']
            },
            {
                'field': 'included',
                'question': 'What is included in the box?',
                'type': 'checkboxes',
                'options': ['Original box', 'Charger', 'Cable', 'Receipt']
            }
        ]
    }
    """
    # Use Claude API to identify product and look up specs
    # If specs not in database, use Perplexity to research
    # Cache in product_specs table for future use
```

---

## Development Priorities

### **PHASE 1: Core Intelligence (Week 1)**

#### 1.1 Product Specs Database
- [ ] Create `product_specs` table (see PRODUCT_DESIGN.md)
- [ ] Seed with top 50 phones (iPhone 11-15, Samsung S20-S24, etc.)
- [ ] Add top 20 laptops (MacBook Air/Pro, Dell XPS, ThinkPad, etc.)
- [ ] Use AI to auto-populate from Perplexity research

#### 1.2 AI Product Recognition
- [ ] Build `identify_and_enrich_product()` function
- [ ] Connect to product_specs database
- [ ] Fall back to Perplexity for unknown products
- [ ] Auto-cache new products for future use

#### 1.3 Dynamic Question Generator
- [ ] Generate questions based on category
- [ ] Pull options from product_specs (storage, colors)
- [ ] Adjust questions based on previous answers
- [ ] Remove duplicate question bug

#### 1.4 SKU Generation System
- [ ] Create SKU generator function
- [ ] Format: `EPD-{PRODUCT}-{VARIANT}-{CONDITION}-{DATE}-{SEQ}`
- [ ] Ensure uniqueness in database
- [ ] Print on shipping labels

---

### **PHASE 2: Listing Creation System (Week 2)**

#### 2.1 AI Content Generation
- [ ] Generate professional listing titles
  - Example: "Apple iPhone 14 Pro Max 256GB Space Black - Excellent Condition [SKU: EPD-IPH14PM-256-SB-EXC-20260121-001]"
- [ ] Generate detailed descriptions
  - Include specs, condition, what's included
  - Professional tone, SEO-optimized
  - Honest about condition/issues
- [ ] Create listing preview before seller confirms

#### 2.2 Photo Management
- [ ] Add photo upload step (4-6 photos required)
  - Front view
  - Back view
  - Sides
  - Any damage
  - Serial number/IMEI
- [ ] Integrate Cloudinary for storage
- [ ] Auto-resize and optimize images
- [ ] Generate professional product shots

#### 2.3 Database Implementation
- [ ] Create `listings` table (see schema in PRODUCT_DESIGN.md)
- [ ] Create `sellers` table
- [ ] Create `product_specs` table
- [ ] Set up proper indexes for performance
- [ ] Use PostgreSQL or MySQL

---

### **PHASE 3: Seller Experience (Week 3)**

#### 3.1 Seller Registration
- [ ] Full name, email, phone
- [ ] ID number for verification
- [ ] Bank account details
  - Bank name
  - Account holder name
  - Account number
  - Account type
  - Branch code
- [ ] Pickup address

#### 3.2 Shipping & Tracking
- [ ] Integrate courier service (Pargo, RAM, etc.)
- [ ] Generate shipping labels with SKU
- [ ] SMS notifications:
  - "Collection scheduled for [date]"
  - "Item collected, en route to EpicDeals"
  - "Item received, under inspection"
  - "Listed on epicdeals.co.za"
  - "Your item sold for R[amount]"
  - "Payment of R[payout] sent to your account"
- [ ] Tracking page for sellers

#### 3.3 Seller Dashboard
- [ ] View all listings (pending, live, sold)
- [ ] Track status of each item
- [ ] View earnings and payouts
- [ ] Update bank details
- [ ] View transaction history

---

### **PHASE 4: Admin & Operations (Week 4)**

#### 4.1 Admin Dashboard
- [ ] View incoming items (pending collection)
- [ ] Scan SKU when item arrives
- [ ] Pull up pre-created listing
- [ ] 45-point quality inspection checklist
- [ ] Upload professional photos
- [ ] Adjust condition if needed
- [ ] Approve and publish listing

#### 4.2 Quality Inspection System
- [ ] Standard checklist (45 points):
  - Power on/boot test
  - Screen condition (dead pixels, scratches)
  - Touch/input responsiveness
  - Cameras (all lenses)
  - Speakers & microphone
  - Buttons & ports
  - Battery health (for phones/laptops)
  - Network connectivity
  - Face ID / Touch ID (for Apple)
  - Physical condition grading
  - Serial number verification (not stolen)
  - Factory reset confirmation
- [ ] Photo capture step
- [ ] Condition adjustment if seller overstated
- [ ] Notes field for issues found

#### 4.3 Listing Management
- [ ] Approve/reject listings
- [ ] Edit titles/descriptions
- [ ] Set final pricing
- [ ] Manage inventory
- [ ] Mark as sold
- [ ] Track sales performance

---

### **PHASE 5: Multi-Platform Publishing (Week 5)**

#### 5.1 EpicDeals.co.za Integration
- [ ] Auto-publish approved listings
- [ ] WooCommerce integration or custom
- [ ] SEO optimization
- [ ] Rich snippets (schema markup)

#### 5.2 Facebook Marketplace
- [ ] Research Facebook Marketplace API
- [ ] Auto-publish listings
- [ ] Sync inventory (mark sold)
- [ ] Handle inquiries

#### 5.3 Gumtree Integration
- [ ] Gumtree API or automation (Selenium)
- [ ] Auto-publish listings
- [ ] Sync inventory
- [ ] Manage responses

#### 5.4 Optional: Takealot/BidOrBuy
- [ ] Evaluate marketplace fees
- [ ] API integration if worthwhile
- [ ] Multi-platform inventory sync

---

### **PHASE 6: Financial System (Week 6)**

#### 6.1 Payment Integration
- [ ] Integrate payment gateway (Yoco, PayFast, Ozow)
- [ ] Verify buyer payments
- [ ] Track transaction fees
- [ ] Handle refunds if needed

#### 6.2 Seller Payouts
- [ ] Bank account verification
- [ ] Automated payout system
- [ ] 2 working days after delivery confirmation
- [ ] Payment notifications
- [ ] Failed payment handling

#### 6.3 Financial Tracking
- [ ] Revenue per listing
- [ ] Platform fees collected
- [ ] Courier costs
- [ ] Net profit per item
- [ ] Monthly financial reports
- [ ] Tax reporting (for accountant)

---

## Key Technical Decisions

### Database Choice
**Recommendation**: PostgreSQL
- JSON field support for flexible product specs
- JSONB for fast queries
- UUID primary keys for SKUs
- Excellent for scaling

### File Storage
**Recommendation**: Cloudinary
- Fast image optimization
- CDN for quick loading
- Automatic resizing
- Generous free tier

### Courier Service
**Options**:
1. **Pargo**: R65 per collection, widespread pickup points
2. **RAM Couriers**: R75-120 door-to-door
3. **The Courier Guy**: R100+ door-to-door
**Recommendation**: Start with Pargo (cheapest, reliable)

### Multi-Platform Publishing
**Approach**:
1. EpicDeals.co.za: Direct WooCommerce API
2. Facebook Marketplace: Official API (if available) or browser automation
3. Gumtree: Likely need Selenium automation (no public API)

---

## Immediate Action Items (This Week)

### **Today**
1. [x] ✅ Fix duplicate question bug in conversation flow - COMPLETE
2. [ ] Test full conversation flow end-to-end with iPhone 14 Pro Max
   - Test: "iPhone 11 128GB" → Should ask ONLY condition (1 question)
   - Test: "iPhone 11" → Should ask capacity, then condition (2 questions)
   - Test: "MacBook Pro 2020" → Should ask specs, then condition (2 questions)
3. [ ] Design database schema (use PRODUCT_DESIGN.md)

### **This Week**
1. [ ] Set up PostgreSQL database
2. [ ] Create database tables (listings, sellers, product_specs)
3. [ ] Seed product_specs with top 20 phones
4. [ ] Build `identify_and_enrich_product()` AI function
5. [ ] Implement dynamic question generation
6. [ ] Add photo upload to conversation flow

---

## Success Metrics (6 Month Goals)

### Volume
- 100 listings per month
- 60% sell-through rate
- Average 10 days to sale

### Financial
- Average item value: R8,000
- Average commission: R1,700 (21% on consignment)
- Monthly revenue target: R170,000
- Net profit margin: 15-18% (after courier, operations)

### Customer Satisfaction
- 4.8+ star rating
- 90%+ seller satisfaction
- <5% return rate
- <2% disputes

---

## Questions to Resolve

1. **Courier Collection**: Do we offer free collection, or charge R100?
   - **Recommendation**: Charge R100, included in consignment fee

2. **Listing Photos**: Seller-provided or professional?
   - **Recommendation**: Seller provides 4-6 basic photos, we take professional shots when item arrives

3. **Item Inspection**: What if item condition worse than stated?
   - **Recommendation**: Contact seller, offer adjusted payout, or return item (seller pays return courier)

4. **Consignment Period**: How long before we return unsold items?
   - **Recommendation**: 60 days, then contact seller to either buy at 50% or return (seller pays courier)

5. **Buy Now vs Consignment**: What % should choose each?
   - **Target**: Push 70% to consignment (higher margin for everyone)
   - Use messaging: "Typically earn R2,000 more with consignment"

---

## Technology Stack Recommendation

### Backend
- **Framework**: Flask (current) or FastAPI (for scaling)
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy
- **Task Queue**: Celery + Redis (for async jobs like Perplexity searches)

### Frontend
- **Current**: Vanilla JS (keep it simple for now)
- **Future**: Consider React for admin dashboard

### AI & APIs
- **Claude API**: Product recognition, content generation, Q&A
- **Perplexity API**: Real-time market research
- **Cloudinary**: Image hosting and optimization

### Deployment
- **Hosting**: DigitalOcean, AWS, or Hetzner
- **Server**: Ubuntu 22.04 LTS
- **Web Server**: Nginx + Gunicorn
- **SSL**: Let's Encrypt
- **Monitoring**: Sentry for errors, Google Analytics for usage

---

## Next Conversation with Me

When we chat next, please have ready:
1. Confirmation on database choice (PostgreSQL recommended)
2. List of top 20-50 products to seed database with
3. Decision on courier service and fees
4. Thoughts on seller vs professional photos
5. Any other questions from PRODUCT_DESIGN.md

Let's build something that makes selling second-hand items RIDICULOUSLY easy!
