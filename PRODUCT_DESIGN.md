# EpicDeals AI-Powered Consignment Platform - Product Design

## Vision
Build a platform that makes Facebook Marketplace, Gumtree, and BobShop obsolete by removing ALL the pain of selling while maximizing seller value.

## Core Value Proposition
- **For Sellers**: List in 2 minutes, ship and forget, get paid automatically
- **For EpicDeals**: Pre-created listings ready to go live when items arrive, professional SKU system, higher margins through efficiency

---

## Customer Journey - Reimagined

### Phase 1: AI-Powered Product Discovery (2 minutes)

**Step 1: What are you selling?**
- User types: "iPhone 14 Pro Max" or "Samsung Fridge"
- AI immediately:
  - Identifies product category
  - Checks courier eligibility
  - If non-courier: Shows rejection message with future expansion promise

**Step 2: AI-Generated Smart Questions**
- AI uses Claude/Anthropic API to generate context-aware questions
- Example for iPhone 14 Pro Max:
  ```
  Q1: "What storage capacity?"
     → Options: 128GB | 256GB | 512GB | 1TB (AI-generated from product specs)

  Q2: "What color is it?"
     → Options: Space Black | Silver | Gold | Deep Purple

  Q3: "What's the physical condition?"
     → Options: Excellent (like new) | Good (minor wear) | Fair (scratches) | Poor (damaged)

  Q4: "What's included in the box?"
     → Checkboxes: Original box | Charger | Cable | Earphones | Receipt

  Q5: "Any damage or issues?"
     → Checkboxes: Cracked screen | Battery issues | Camera problems | None
  ```

**Step 3: AI Price Research (happens in background)**
- Perplexity searches current market
- Shows seller:
  ```
  Market Value: R12,499 (median from 8 sources)

  YOUR OPTIONS:

  Option 1: SELL NOW - Get R8,749 today
  ✓ Money in your account within 24 hours
  ✓ We handle everything
  ✓ No waiting, no hassle

  Option 2: CONSIGNMENT - Get R9,899 after sale
  ✓ We list and sell for you
  ✓ Higher payout (80% - R100 courier)
  ✓ Paid 2 days after buyer receives item
  ✓ Typically sells within 7-14 days
  ```

### Phase 2: Pre-Listing Creation

**Step 4: Generate Listing Details (if they choose consignment or sell now)**

AI automatically creates:
1. **Product Title**: "Apple iPhone 14 Pro Max 256GB Space Black - Excellent Condition"
2. **Description**:
   ```
   Apple iPhone 14 Pro Max in Excellent condition

   Specifications:
   • Storage: 256GB
   • Color: Space Black
   • Condition: Excellent - Like new with minimal signs of use
   • Battery Health: Will be tested upon arrival
   • Accessories: Original box, charger, cable included

   What's Included:
   ✓ iPhone 14 Pro Max 256GB
   ✓ Original box
   ✓ Charging cable
   ✓ Power adapter

   Quality Guarantee:
   • Professionally inspected
   • 45-point quality check
   • 12-month warranty included
   • Fast, insured delivery
   ```

3. **Photos**: Request 4-6 photos
   - Front view
   - Back view
   - Side views
   - Any damage/wear
   - Serial number/IMEI

4. **Generate Unique SKU**: `EPD-IPH14PM-256-SB-EXC-20260121-001`
   - EPD = EpicDeals
   - IPH14PM = iPhone 14 Pro Max
   - 256 = Storage
   - SB = Space Black
   - EXC = Excellent
   - 20260121 = Date
   - 001 = Item number that day

### Phase 3: Seller Details & Shipping

**Step 5: Collect Seller Information**
- Full name
- Phone number
- Email address
- Pickup address
- Bank account details (for payout)
- ID number (for verification)

**Step 6: Shipping Arrangement**
- Show: "We'll collect from you on [date]"
- Send SMS: "EpicDeals courier arriving [day] [time]"
- Generate shipping label with SKU
- Courier collects item

### Phase 4: Quality Control & Listing

**Step 7: Item Arrives at EpicDeals**
- Scan SKU
- Pull up pre-created listing
- 45-point quality inspection
- Take professional photos
- Update condition if needed

**Step 8: Listing Goes Live**
- For "Sell Now": Mark as sold to EpicDeals, pay seller within 24h
- For "Consignment":
  - Publish to epicdeals.co.za
  - Publish to Facebook Marketplace (auto)
  - Publish to Gumtree (auto)
  - Status: "Available for Sale"

**Step 9: When Item Sells**
- Mark as sold
- Ship to buyer
- Track delivery
- 2 working days after delivery confirmation: Pay seller
- Send SMS: "Your iPhone 14 Pro Max sold for R12,499. Your payout of R9,899 has been deposited."

---

## Data Architecture

### Database Tables

**1. listings**
```sql
CREATE TABLE listings (
  id UUID PRIMARY KEY,
  sku VARCHAR(50) UNIQUE NOT NULL,
  created_at TIMESTAMP,

  -- Product Info
  category VARCHAR(50),
  brand VARCHAR(100),
  model VARCHAR(200),
  storage VARCHAR(20),
  color VARCHAR(50),
  condition VARCHAR(20),

  -- AI Generated
  title TEXT,
  description TEXT,
  market_value DECIMAL(10,2),
  ai_confidence DECIMAL(3,2),

  -- Pricing
  sell_now_price DECIMAL(10,2),
  consignment_price DECIMAL(10,2),
  final_sale_price DECIMAL(10,2),

  -- Seller Choice
  listing_type VARCHAR(20), -- 'sell_now' or 'consignment'

  -- Status
  status VARCHAR(20), -- 'pending_collection', 'in_transit', 'received', 'inspecting', 'listed', 'sold', 'paid_out'

  -- Seller Info
  seller_id UUID REFERENCES sellers(id),

  -- Quality Control
  inspection_notes TEXT,
  inspection_date TIMESTAMP,
  actual_condition VARCHAR(20),
  battery_health INT,

  -- Photos
  photo_urls TEXT[], -- Array of Cloudinary URLs

  -- Tracking
  courier_tracking VARCHAR(100),
  collection_date DATE,
  received_date DATE,
  listed_date DATE,
  sold_date DATE,
  payout_date DATE,

  -- Buyer Info (when sold)
  buyer_name VARCHAR(200),
  buyer_email VARCHAR(200),
  buyer_phone VARCHAR(20),
  buyer_address TEXT,

  -- Financial
  platform_fee DECIMAL(10,2),
  courier_fee DECIMAL(10,2),
  seller_payout DECIMAL(10,2)
);
```

**2. sellers**
```sql
CREATE TABLE sellers (
  id UUID PRIMARY KEY,
  full_name VARCHAR(200) NOT NULL,
  email VARCHAR(200) UNIQUE NOT NULL,
  phone VARCHAR(20) NOT NULL,
  id_number VARCHAR(20),

  -- Banking
  bank_name VARCHAR(100),
  account_holder VARCHAR(200),
  account_number VARCHAR(20),
  account_type VARCHAR(20),
  branch_code VARCHAR(10),

  -- Address
  street_address TEXT,
  suburb VARCHAR(100),
  city VARCHAR(100),
  postal_code VARCHAR(10),

  -- Stats
  total_listings INT DEFAULT 0,
  total_sold INT DEFAULT 0,
  total_earnings DECIMAL(10,2) DEFAULT 0,

  -- Verification
  verified BOOLEAN DEFAULT FALSE,
  verification_date TIMESTAMP,

  created_at TIMESTAMP DEFAULT NOW()
);
```

**3. product_specs (AI-powered)**
```sql
CREATE TABLE product_specs (
  id UUID PRIMARY KEY,
  brand VARCHAR(100),
  model VARCHAR(200),
  category VARCHAR(50),

  -- Specs (JSON)
  storage_options TEXT[], -- ['128GB', '256GB', '512GB']
  color_options TEXT[],
  year_released INT,
  original_price DECIMAL(10,2),

  -- AI Context
  common_issues TEXT[], -- ['Battery degradation', 'Screen scratches']
  key_features TEXT[],

  -- Auto-updated from market research
  current_market_value DECIMAL(10,2),
  last_updated TIMESTAMP
);
```

---

## AI Intelligence Layer

### 1. Product Recognition & Spec Lookup
```python
def identify_product(user_input: str) -> dict:
    """
    User types: "iPhone 14 Pro Max"
    AI returns:
    {
        'brand': 'Apple',
        'model': 'iPhone 14 Pro Max',
        'category': 'smartphone',
        'storage_options': ['128GB', '256GB', '512GB', '1TB'],
        'color_options': ['Space Black', 'Silver', 'Gold', 'Deep Purple'],
        'year_released': 2022,
        'courier_eligible': True
    }
    """
    # Use Claude API to extract product info
    # Check against product_specs database
    # If not found, use AI to research and create entry
```

### 2. Dynamic Question Generation
```python
def generate_questions(product_info: dict) -> list:
    """
    Based on product category and specs, generate smart questions

    For phones: storage, color, condition, battery, screen, box contents
    For laptops: RAM, storage, processor, screen size, condition
    For cameras: lens included, sensor condition, shutter count
    """
    # Use Claude to generate context-aware questions
    # Return structured question format with options
```

### 3. Listing Content Generation
```python
def generate_listing(product_info: dict, answers: dict) -> dict:
    """
    Create professional listing with:
    - SEO-optimized title
    - Detailed description
    - Key features highlighted
    - Honest condition assessment
    - Professional tone
    """
    # Use Claude API to generate compelling copy
```

### 4. SKU Generation System
```python
def generate_sku(product_info: dict, date: str) -> str:
    """
    Format: EPD-{PRODUCT_CODE}-{VARIANT}-{CONDITION}-{DATE}-{SEQUENCE}

    Examples:
    - EPD-IPH14PM-256-SB-EXC-20260121-001
    - EPD-SAMGS23-128-BK-GOOD-20260121-002
    - EPD-MBAM2-512-SG-FAIR-20260121-003

    Product codes database:
    - iPhone 14 Pro Max = IPH14PM
    - Samsung Galaxy S23 = SAMGS23
    - MacBook Air M2 = MBAM2
    """
    # Generate unique, readable SKU
    # Check for conflicts
    # Store in database
```

---

## Competitive Advantages vs Facebook/Gumtree/BobShop

### What Makes This Better?

**For Sellers:**
1. **Zero Effort**: List in 2 mins, we do everything else
2. **No Haggling**: Professional pricing, no tire-kickers
3. **No Meetups**: We collect, we ship to buyers
4. **No Scams**: Professional platform, verified buyers
5. **Guaranteed Payment**: Money in bank, no cash/EFT risk
6. **Better Prices**: 80% of market value (vs 60-70% on BobShop)
7. **Fast Process**: Listed within 48 hours of collection

**For Buyers:**
1. **12-Month Warranty**: vs none on FB/Gumtree
2. **45-Point Inspection**: Guaranteed quality
3. **Professional Photos**: Clear product view
4. **Return Policy**: 7-day returns
5. **Insured Shipping**: Safe delivery
6. **Verified Products**: No fakes/stolen goods

**For EpicDeals:**
1. **Higher Margins**: 20% + R100 vs buying at 70%
2. **Pre-Created Listings**: Zero work when item arrives
3. **Professional Inventory**: SKU system, tracking
4. **Scalable**: Can handle 100+ items/day
5. **Multi-Platform**: Auto-post to FB, Gumtree, website
6. **Brand Trust**: Professional operation vs individual sellers

---

## Next Steps - Development Priorities

### Priority 1: Fix Current Issues
- [ ] Fix duplicate question bug in conversation flow
- [ ] Add photo upload capability
- [ ] Test full flow end-to-end

### Priority 2: AI Intelligence
- [ ] Build product_specs database (start with top 50 phones)
- [ ] Implement AI product recognition
- [ ] Build dynamic question generator
- [ ] Implement listing content generator
- [ ] Build SKU generation system

### Priority 3: Seller Management
- [ ] Create seller registration flow
- [ ] Add bank account capture
- [ ] Build seller dashboard
- [ ] Add photo upload interface

### Priority 4: Listing Management
- [ ] Build admin listing review interface
- [ ] Add quality inspection checklist
- [ ] Implement photo upload/management (Cloudinary)
- [ ] Create listing publishing system

### Priority 5: Multi-Platform Publishing
- [ ] Auto-publish to epicdeals.co.za
- [ ] Facebook Marketplace API integration
- [ ] Gumtree API/automation
- [ ] Consider: Takealot, Bidorbuy

### Priority 6: Financial System
- [ ] Seller payout automation
- [ ] Bank verification (via Yoco/PayFast)
- [ ] Transaction tracking
- [ ] Commission calculation

---

## Key Metrics to Track

1. **Conversion Rate**: % of visitors who complete listing
2. **Average Listing Time**: Target < 2 minutes
3. **Sell-Through Rate**: % of consignment items that sell
4. **Average Days to Sale**: Target < 14 days
5. **Seller Payout**: Average amount paid to sellers
6. **Platform Revenue**: Commission earned per item
7. **Customer Satisfaction**: NPS score

---

## Pricing Strategy

### Consignment Model (Recommended Push)
- **Seller Gets**: 80% of sale price - R100 courier
- **EpicDeals Gets**: 20% + R100
- **Example**: Item sells for R10,000
  - Seller: R7,900
  - EpicDeals: R2,100 (21% margin)

### Buy Now Model
- **Seller Gets**: 70% of market value immediately
- **EpicDeals Risk**: Must resell at profit
- **Example**: Market value R10,000
  - Seller: R7,000
  - EpicDeals must sell for R10,000+ to profit R3,000+

**Push Strategy**: Emphasize consignment with messaging like:
- "Typically get R2,000 more with consignment"
- "Items usually sell within 7-14 days"
- "We handle all the work - you just ship and wait"
