# Project Structure - EpicDeals Pricing Tool

**Complete file organization and descriptions**

---

## 📁 Root Directory

```
Claude ED Price Research Tool - Jan 2026/
├── app.py                          # Main Flask application
├── config.py                       # Configuration and environment variables
├── requirements.txt                # Python dependencies
├── Procfile                        # For deployment (Heroku/Railway)
├── .env                           # Environment variables (create this)
├── .gitignore                     # Git ignore rules
│
├── services/                      # Backend services
│   ├── __init__.py
│   ├── ai_service.py             # Claude AI conversation logic
│   ├── perplexity_price_service.py  # Market price research
│   ├── intelligent_repair_cost_service.py  # Repair cost research
│   ├── condition_assessment_service.py  # Damage tracking
│   ├── depreciation_service.py   # ⭐ NEW: Age-based depreciation
│   ├── offer_service.py          # Offer calculation
│   └── email_service.py          # Email notifications
│
├── static/                        # Frontend assets
│   ├── css/
│   │   └── style.css             # All styling
│   └── js/
│       └── app.js                # Frontend logic
│
├── templates/                     # HTML templates
│   └── index.html                # Main page
│
└── docs/                          # Documentation (all .md files)
    ├── QUICKSTART.md             # ⭐ Start here for deployment
    ├── FINAL_UPDATE_SUMMARY.md   # ⭐ Complete summary
    ├── AGE_BASED_DEPRECIATION.md # ⭐ NEW: Age system docs
    ├── DEPLOYMENT_GUIDE.md       # Detailed hosting guide
    ├── COMPLETE_FEATURES_SUMMARY.md  # All features
    ├── NEW_FEATURES_IMPLEMENTATION.md  # Session 2 features
    ├── README_PRIORITY_1_2.md    # Original implementation
    └── TESTING_GUIDE.md          # Test scenarios
```

---

## 🔧 Core Application Files

### `app.py` (Main Application)
**Purpose:** Flask web server and API endpoints

**Key Routes:**
- `/` - Main page
- `/api/message` - AI conversation
- `/api/customer-info` - Submit customer details
- `/api/dispute-price` - Price dispute submission
- `/api/health` - Health check

**Session Management:**
- Tracks conversation history
- Stores product info
- Maintains customer data

### `config.py` (Configuration)
**Purpose:** Environment variables and settings

**Configuration:**
- API keys (Anthropic, Perplexity)
- SMTP email settings
- Flask secret key
- Server settings

---

## 🤖 Services (Backend Logic)

### `services/ai_service.py` ⭐ MODIFIED
**Purpose:** Claude AI conversation management

**Key Methods:**
- `get_next_question()` - Determines what to ask next
- `extract_product_details()` - Parses conversation into structured data
- `generate_search_queries()` - Creates search queries
- `assess_confidence()` - Evaluates offer confidence

**Changes:** Added age/year as essential information, smart year extraction

### `services/depreciation_service.py` ⭐ NEW
**Purpose:** Age-based depreciation calculations

**Key Methods:**
- `calculate_depreciation_factor()` - Gets % value remaining based on age
- `estimate_age_from_model()` - Extracts year from model name (iPhone 13 = 2021)
- `get_depreciation_info()` - Complete calculation with explanation
- `_get_curve_key()` - Determines which curve to use (iPhone vs Android, etc.)

**Depreciation Curves:**
- iPhone, Android, MacBook, Windows Laptop
- Gaming Consoles, Cameras, TVs, Appliances
- Each with 7-10 year curves

### `services/perplexity_price_service.py` ⭐ MODIFIED
**Purpose:** Real-time market price research via Perplexity API

**Key Methods:**
- `search_prices()` - Searches second-hand prices
- `_search_new_prices_fallback()` - Falls back to new prices
- `_estimate_secondhand_from_new()` - Uses age-based depreciation
- `_parse_perplexity_response()` - Extracts prices from AI response

**Changes:** Now uses DepreciationService for age-aware estimates

### `services/intelligent_repair_cost_service.py`
**Purpose:** Research actual repair costs via Perplexity

**Key Methods:**
- `estimate_repair_cost()` - Gets repair cost for specific damage
- `_build_repair_query()` - Creates targeted search queries
- `_parse_repair_response()` - Extracts costs from results

**Searches:** iStore, iFix, local SA repair shops

### `services/condition_assessment_service.py`
**Purpose:** Track damage and calculate deductions

**Key Methods:**
- `calculate_deduction()` - Gets deduction % for damage type
- `get_total_deductions()` - Sums all damage deductions
- `assess_condition_category()` - Categorizes overall condition

**Damage Types:** Screen, battery, body, water, functional issues

### `services/offer_service.py` ⭐ MODIFIED
**Purpose:** Calculate final offers (Sell Now vs Consignment)

**Key Methods:**
- `calculate_offer()` - Complete offer calculation
- `_format_offer_message()` - Creates user-facing offer text
- `_decide_offer_type()` - Instant vs Manual review

**Changes:** Updated "24 hours" to "2 working days"

**Business Models:**
- Sell Now: 65% of adjusted value
- Consignment: 85% of expected sale price

### `services/email_service.py` ⭐ MODIFIED
**Purpose:** Send email notifications

**Key Methods:**
- `send_manual_review_request()` - Notify Brad of new offer
- `send_offer_to_customer()` - Confirmation email
- `send_price_dispute_request()` - Price dispute alert

**Changes:** Updated timing messages to "2 working days"

---

## 🎨 Frontend Files

### `static/js/app.js` ⭐ MODIFIED
**Purpose:** Frontend application logic

**Key Features:**
- Message handling (text, buttons, checkboxes)
- Offer display with breakdown
- Price dispute form
- Customer info form
- Loading states

**Changes:**
- Display depreciation explanations
- All "24 hours" → "2 working days"

### `static/css/style.css`
**Purpose:** All styling and responsive design

**Key Styles:**
- Chat interface
- Message bubbles
- Offer breakdown
- Multi-select checkboxes
- Price dispute form
- Beta notices
- Mobile responsive

### `templates/index.html`
**Purpose:** Main HTML structure

**Sections:**
- Chat container
- Message area
- Input area
- Offer display
- Forms

---

## 📚 Documentation Files

### ⭐ `QUICKSTART.md` (NEW)
**For:** Quick deployment (30 mins to live)
**Contains:** Step-by-step Railway deployment, API key setup, testing

### ⭐ `FINAL_UPDATE_SUMMARY.md` (NEW)
**For:** Complete overview of latest changes
**Contains:** What was implemented, files modified, testing checklist, management demo tips

### ⭐ `AGE_BASED_DEPRECIATION.md` (NEW)
**For:** Technical documentation of age system
**Contains:** Implementation details, depreciation curves, user examples, testing scenarios

### `DEPLOYMENT_GUIDE.md` (NEW)
**For:** Detailed hosting instructions
**Contains:** 5 hosting options, environment variables, cost estimates, troubleshooting

### `COMPLETE_FEATURES_SUMMARY.md`
**For:** Overview of all features
**Contains:** Full feature list, user journey, competitive advantages, metrics

### `NEW_FEATURES_IMPLEMENTATION.md`
**For:** Session 2 features (price dispute, new price fallback, disclaimers)
**Contains:** Technical implementation, user experience examples, benefits

### `README_PRIORITY_1_2.md`
**For:** Original Priority 1 & 2 implementation
**Contains:** Intelligent repair costs, multi-select checkboxes, transparent pricing

### `TESTING_GUIDE.md`
**For:** Comprehensive testing
**Contains:** 8 test cases, expected results, edge cases

---

## 🔑 Environment Variables (.env)

Create this file yourself - DO NOT commit to git:

```bash
# AI APIs
ANTHROPIC_API_KEY=sk-ant-xxxxx
PERPLEXITY_API_KEY=pplx-xxxxx

# Flask
SECRET_KEY=your_secret_key_here

# Email (Gmail example)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
NOTIFICATION_EMAIL=brad@epicdeals.co.za
```

---

## 📦 Dependencies (requirements.txt)

```
flask==3.0.0
python-dotenv==1.0.0
anthropic==0.8.0
requests==2.31.0
gunicorn==21.2.0
```

---

## 🚀 Deployment Files

### `Procfile`
For Heroku/Railway deployment:
```
web: gunicorn app:app
```

### `.gitignore`
Ignore sensitive files:
```
.env
__pycache__/
*.pyc
.DS_Store
```

---

## 📊 File Statistics

**Total Files:** 25+
**Python Files:** 8 services + 2 main
**JavaScript:** 1 (app.js)
**CSS:** 1 (style.css)
**HTML:** 1 (index.html)
**Documentation:** 9 markdown files

**Total Lines of Code:**
- Python: ~2,800 lines
- JavaScript: ~850 lines
- CSS: ~600 lines
- Total: ~4,250 lines

---

## 🎯 Key Files for Each Task

### Want to understand the system?
Start with: `COMPLETE_FEATURES_SUMMARY.md`

### Want to deploy quickly?
Start with: `QUICKSTART.md`

### Want to understand age depreciation?
Read: `AGE_BASED_DEPRECIATION.md`

### Want to modify AI questions?
Edit: `services/ai_service.py`

### Want to adjust depreciation curves?
Edit: `services/depreciation_service.py` (lines 15-150)

### Want to change styling?
Edit: `static/css/style.css`

### Want to modify offer display?
Edit: `static/js/app.js` (displayOffer function)

---

## 🔍 Code Navigation Tips

### Find where prices are researched:
`services/perplexity_price_service.py` → `search_prices()`

### Find where depreciation is calculated:
`services/depreciation_service.py` → `get_depreciation_info()`

### Find where AI asks questions:
`services/ai_service.py` → `get_next_question()`

### Find where offers are displayed:
`static/js/app.js` → `displayOffer()`

### Find where emails are sent:
`services/email_service.py` → `send_*` methods

---

## 🛠️ Development Workflow

### 1. Make Changes
```bash
# Edit files
code services/depreciation_service.py

# Test syntax
python3 -m py_compile services/depreciation_service.py
```

### 2. Test Locally
```bash
python3 app.py
# Visit http://localhost:5000
```

### 3. Deploy
```bash
git add .
git commit -m "Your changes"
git push origin main
# Auto-deploys to Railway/Heroku
```

---

## 📈 Future Additions

**If you add photo upload:**
- Create `services/image_service.py`
- Add Cloudinary integration
- Update `app.py` with upload endpoint

**If you add database:**
- Create `models/` directory
- Add SQLAlchemy models
- Update `app.py` with database config

**If you add analytics:**
- Create `services/analytics_service.py`
- Track user behavior
- Generate reports

---

## 🎉 Summary

**Core Files (Must Understand):**
- ✅ `app.py` - Main application
- ✅ `services/ai_service.py` - AI logic
- ✅ `services/depreciation_service.py` - Age depreciation
- ✅ `static/js/app.js` - Frontend

**Documentation (Must Read):**
- ✅ `QUICKSTART.md` - For deployment
- ✅ `FINAL_UPDATE_SUMMARY.md` - For overview
- ✅ `AGE_BASED_DEPRECIATION.md` - For age system

**Status:** 🟢 All files documented and ready

**Next:** Deploy using `QUICKSTART.md`!
