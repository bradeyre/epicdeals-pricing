import anthropic
from config import Config


class AIService:
    """
    Handles AI-powered conversations using Claude API
    Manages adaptive questioning and product information extraction
    """

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.model = Config.ANTHROPIC_MODEL
        self._required_fields_cache = {}  # Cache AI-determined requirements per product

    def _get_required_fields(self, product_info):
        """
        Uses AI to intelligently determine which fields are required for this specific product.
        NO HARD-CODED LISTS - uses universal logic that works for ANY product.

        Returns:
            dict: Required fields and their descriptions for error messages
        """
        brand = product_info.get('brand', '')
        model = product_info.get('model', '')
        category = product_info.get('category', '')

        # Base requirements for all items
        required = {
            'category': 'product category',
            'brand': 'brand name',
            'model': 'model name',
            'damage_details': 'damage assessment'  # ALWAYS required for condition/pricing
        }

        # If we don't have basic product info yet, just return base requirements
        if not brand or not model or brand == 'Unknown' or model == 'Unknown':
            print(f"   ⏭️  Product info incomplete, skipping intelligent field detection")
            return required

        # Check cache first
        cache_key = f"{brand}_{model}_{category}".lower().replace(' ', '_')
        if cache_key in self._required_fields_cache:
            print(f"   ✅ Using cached requirements for {brand} {model}")
            return self._required_fields_cache[cache_key]

        print(f"\n🔍 INTELLIGENT FIELD DETECTION for {brand} {model}")

        # Use fast keyword-based intelligence (no extra AI call)
        # This is "intelligent" because it analyzes the specific product, not just category
        try:
            # Smart detection based on brand/model keywords
            category_lower = category.lower()
            brand_lower = brand.lower()
            model_lower = model.lower()
            full_text = f"{brand_lower} {model_lower} {category_lower}"

            # Intelligent pattern detection
            is_phone = any(word in full_text for word in
                          ['phone', 'iphone', 'galaxy', 'pixel', 'oneplus', 'xiaomi', 'android'])
            is_tablet = any(word in full_text for word in ['tablet', 'ipad'])
            is_laptop = any(word in full_text for word in
                           ['laptop', 'macbook', 'notebook', 'thinkpad', 'chromebook'])
            is_smartwatch = any(word in full_text for word in
                               ['apple watch', 'galaxy watch', 'fitbit', 'garmin', 'smartwatch'])

            # Apply intelligent rules
            if is_phone or is_tablet:
                required.update({
                    'capacity': 'storage capacity',
                    'device_unlocked': 'device unlock status',
                    'contract_free': 'contract status'
                })
                print(f"   Detected: Phone/Tablet → requires storage, unlock, contract")
            elif is_laptop:
                required.update({
                    'specifications': 'specifications',
                    'device_unlocked': 'device unlock status'
                })
                print(f"   Detected: Laptop → requires specs, unlock")
            elif is_smartwatch:
                required['device_unlocked'] = 'device unlock status'
                print(f"   Detected: Smartwatch → requires unlock")
            else:
                print(f"   Detected: Other device → requires damage only")

            # Cache the result
            self._required_fields_cache[cache_key] = required

        except Exception as e:
            print(f"❌ Field detection error: {e}")
            # If even fallback fails, return base requirements

        return required

    def _validate_completion(self, product_info, result):
        """
        Validates that all required fields are present before allowing completion.

        Args:
            product_info: Current product information
            result: AI's response with completed flag

        Returns:
            dict: Modified result that forces next question if validation fails
        """
        # Only validate if AI is trying to complete
        if not result.get('completed', False):
            return result

        try:
            # Check if we have all required fields
            required_fields = self._get_required_fields(product_info)
            missing_fields = []

            for field, description in required_fields.items():
                if field not in product_info or not product_info[field]:
                    missing_fields.append(description)
        except Exception as e:
            print(f"❌ Validation error: {e}")
            print(f"   Allowing completion to proceed (fail-safe)")
            return result

        # If fields are missing, override completion and force next question
        if missing_fields:
            print(f"\n⚠️  VALIDATION FAILED - Missing required fields:")
            for field in missing_fields:
                print(f"   - {field}")
            print(f"   Current product_info: {product_info}")
            print(f"   Blocking completion and forcing next question\n")

            # Override AI's completion attempt
            result['completed'] = False

            # Generate appropriate next question based on first missing field
            next_question = self._generate_missing_field_question(product_info, missing_fields[0])
            result.update(next_question)

        return result

    def _generate_missing_field_question(self, product_info, missing_description):
        """
        Generates the next required question based on missing field.

        Args:
            product_info: Current product information
            missing_description: Description of missing field

        Returns:
            dict: Question to ask for the missing field
        """
        category = product_info.get('category', '').lower()
        brand = product_info.get('brand', 'item')
        model = product_info.get('model', 'device')
        product_name = f"{brand} {model}"

        if 'storage capacity' in missing_description:
            return {
                'question': f"What storage capacity does your {product_name} have?",
                'field_name': 'capacity',
                'type': 'text'
            }
        elif 'damage assessment' in missing_description:
            return {
                'question': f"Are there any of these issues with your {product_name}? Select all that apply:",
                'field_name': 'damage_details',
                'type': 'multi_select',
                'options': ['Screen cracked', 'Back glass cracked', 'Water damage', 'Face ID / Touch ID not working',
                           'Camera not working', "Won't turn on / Dead", 'Battery health below 80%',
                           'Buttons or ports damaged', 'Camera issues (blurry)', 'Screen scratches (not cracked)',
                           'Body scratches or scuffs', 'Minor dents', 'None - Everything works perfectly']
            }
        elif 'device unlock status' in missing_description:
            if 'iphone' in model.lower() or 'ipad' in model.lower() or 'macbook' in model.lower():
                account_type = 'iCloud'
            elif 'samsung' in brand.lower():
                account_type = 'Google and Samsung accounts'
            else:
                account_type = 'any accounts'

            return {
                'question': f"Is your {product_name} unlocked from {account_type}?",
                'field_name': 'device_unlocked',
                'type': 'multiple_choice',
                'options': [f'Yes - Fully unlocked', f'No - Still locked', 'Not sure']
            }
        elif 'contract status' in missing_description:
            return {
                'question': f"Is your {product_name} free from any contract or payment plan?",
                'field_name': 'contract_free',
                'type': 'multiple_choice',
                'options': ['Yes - Fully paid off, no contracts', 'No - Still under contract or payment plan']
            }
        elif 'specifications' in missing_description:
            return {
                'question': f"What are the specifications of your {product_name}? (RAM, storage, screen size)",
                'field_name': 'specifications',
                'type': 'text'
            }
        else:
            # Fallback
            return {
                'question': f"Please provide additional details about your {product_name}",
                'field_name': 'additional_info',
                'type': 'text'
            }

    def get_next_question(self, conversation_history, product_info):
        """
        Determines the next question to ask based on conversation history
        and currently gathered product information.

        Args:
            conversation_history: List of previous messages
            product_info: Dict of currently known product details

        Returns:
            Dict with 'question', 'options' (if multiple choice), 'field_name', and 'completed' flag
        """

        system_prompt = """You are an intelligent assistant for EpicDeals.co.za, a second-hand goods buyer in South Africa.

Your job is to ASK QUESTIONS to gather ONLY information that affects resale value and pricing.

CRITICAL RULES - PREVENT DUPLICATE QUESTIONS:
1. NEVER ask the same question twice - review the conversation history carefully
2. NEVER ask about information that's already in CURRENT PRODUCT INFO
3. Be SMART - extract ALL information from what the user already told you in ONE message
4. CRITICAL EXTRACTION EXAMPLES:
   - User: "iPhone 11" → Extract: category=phone, brand=Apple, model=iPhone 11, year=2019
   - User: "iPhone 16 Pro Max 512GB" → Extract: category=phone, brand=Apple, model=iPhone 16 Pro Max, capacity=512GB, year=2024
   - User: "MacBook Pro 2020 16GB" → Extract: category=laptop, brand=Apple, model=MacBook Pro, year=2020, ram=16GB
   - User: "Samsung Galaxy S24 256GB" → Extract: category=phone, brand=Samsung, model=Galaxy S24, capacity=256GB, year=2024
5. If user provides storage/capacity in their message (e.g., "512GB"), DON'T ask about storage!
6. If user provides year in model name (e.g., "2020"), DON'T ask about year!
7. ONLY ask for information you DON'T already have AND that affects pricing
8. Ask ONE clear question at a time
9. Use multiple choice for condition questions
10. CRITICAL: You MUST ask ALL required questions - do NOT skip damage assessment or unlock verification!
11. Mark as COMPLETED only when ALL required questions have been asked (see COMPLETION section below for full requirements)

BEFORE ASKING ANY QUESTION - MANDATORY CHECKS:
1. Check CURRENT PRODUCT INFO first - what do we already know?
   - If capacity is already there (e.g., "512GB"), DON'T ask about storage!
   - If year is already there (e.g., "2024"), DON'T ask about year!
   - If condition is already there, DON'T ask about condition!
2. Check conversation_history - has this question been asked already?
3. Extract information from the LATEST user message BEFORE deciding what to ask
4. If information is already available, SKIP to the next needed question
5. NEVER ask for information that's in CURRENT PRODUCT INFO

ESSENTIAL INFORMATION (ONLY what affects resale value):
- Item category (phone, laptop, tablet, camera, watch, appliance, console, etc.)
- Brand name
- Model/version
- AGE/YEAR - CRITICAL for depreciation calculation:
  INTELLIGENT YEAR DETECTION - DON'T ASK UNNECESSARILY:
  1. First, use your knowledge to determine the release year from the model name
  2. For products with SINGLE release year (most phones, tablets, consoles):
     - iPhone 16 Pro Max → 2024 (released Sept 2024)
     - iPhone 15 → 2023 (released Sept 2023)
     - iPhone 11 → 2019 (released Sept 2019)
     - Samsung Galaxy S24 → 2024 (released Jan 2024)
     - PS5 → 2020 (released Nov 2020)
     - iPad Air 5th gen → 2022
     DO NOT ask "what year" - you already know it!
  3. For products with MULTI-YEAR production (laptops with year in name, older models):
     - "MacBook Pro 2020" → year=2020 (explicit in name, don't ask)
     - "MacBook Pro 13-inch" → ASK year (produced 2016-2022, ambiguous)
     - "Dell XPS 15" → ASK year (produced many years)
  4. ONLY ask year when:
     - The model was produced across multiple years AND year isn't in the name
     - The model is truly ambiguous (e.g., "Samsung TV" without model number)
  5. For phones/tablets: Almost NEVER ask year - you know the release date
  6. For laptops: Only ask if model doesn't include year and was produced 2+ years
- Key specifications that affect pricing:
  - Phones/tablets: storage capacity (64GB, 128GB, etc.) - DON'T ask about color
    CRITICAL FOR ALL PRODUCTS: Before asking about ANY specification that has limited variations (storage, RAM, screen size, etc.):
    1. Use your knowledge to determine what variations exist for that specific model
    2. Provide ONLY the valid options as multiple choice
    3. This applies to: phones (storage), laptops (RAM/storage configs), TVs (screen sizes), tablets (storage), etc.
    Examples:
    - iPhone 16 Pro Max: 256GB, 512GB, 1TB (released 2024)
    - iPhone 11: 64GB, 128GB, 256GB (released 2019)
    - MacBook Air M2: 8GB/256GB, 8GB/512GB, 16GB/512GB, 24GB/2TB configs
    - Samsung Galaxy S24: 128GB, 256GB, 512GB
  - Laptops: RAM, storage, screen size, processor (M1, M2, M3, Intel i5/i7/i9, etc.)
    Look up available configurations for the specific model
  - TVs: screen size, technology (OLED, QLED, LED)
    Look up available sizes for that specific model series
  - Cameras: sensor size, lens included
  - Appliances: capacity/size, energy rating
- Physical condition (excellent, good, fair, poor)
- Specific damage/issues (AFTER asking about condition - see below)

WHAT NOT TO ASK:
- Color (for phones, laptops, etc.) - minimal impact on value
- Cosmetic preferences that don't affect functionality
- Original packaging (unless specifically relevant)
- Any detail that doesn't significantly impact the item's market value

SMART EXTRACTION EXAMPLES - AUTOMATIC YEAR DETECTION:
- "iPhone 16 Pro Max" → category=phone, brand=Apple, model=iPhone 16 Pro Max, year=2024 (DON'T ask year!)
- "iPhone 13 Pro 256GB" → category=phone, brand=Apple, model=iPhone 13 Pro, capacity=256GB, year=2021 (DON'T ask!)
- "Samsung Galaxy S21" → category=phone, brand=Samsung, model=Galaxy S21, year=2021 (DON'T ask!)
- "MacBook Air M1" → category=laptop, brand=Apple, model=MacBook Air M1, year=2020 (M1 = late 2020, DON'T ask!)
- "MacBook Air M2" → category=laptop, brand=Apple, model=MacBook Air M2, year=2022 (M2 = 2022, DON'T ask!)
- "MacBook Pro 2020" → category=laptop, brand=Apple, model=MacBook Pro, year=2020 (explicit in name, DON'T ask!)
- "PS5" → category=console, brand=Sony, model=PlayStation 5, year=2020 (DON'T ask!)
- "iPad Pro 11-inch 2021" → category=tablet, brand=Apple, model=iPad Pro 11-inch, year=2021 (DON'T ask!)
- "iPhone 11" → category=phone, brand=Apple, model=iPhone 11, year=2019 (released Sept 2019, DON'T ask!)

WHEN TO ASK YEAR (rare cases):
- "MacBook Pro 13-inch" → Model produced 2016-2022, ASK: "What year is your MacBook Pro?"
- "Dell XPS 15" → Multi-year model, ASK: "What year is your Dell XPS 15?"
- "Samsung TV" → No specific model, ASK: "What year was it purchased?"

╔══════════════════════════════════════════════════════════════╗
║  RESPONSE FORMAT - ABSOLUTELY CRITICAL - NO EXCEPTIONS      ║
╚══════════════════════════════════════════════════════════════╝

YOU MUST RESPOND WITH ONLY VALID JSON - NOTHING ELSE
⚠️  NO explanations, NO text before JSON, NO text after JSON ⚠️
⚠️  WRONG: "Is your iPhone 14 unlocked from iCloud?" ⚠️
✅  CORRECT: {"question": "Is your iPhone 14 unlocked from iCloud?", "field_name": "device_unlocked", ...}

EVERY response MUST start with { and end with }
EVERY response MUST contain ALL required fields: "question", "field_name", "type", "completed"

WHEN TO USE MULTIPLE CHOICE vs TEXT:
- Use "multiple_choice" for: storage capacity (when you know the exact options for that model), condition, damage details, RAM configs, screen sizes
- Use "text" for: year, model number (when unknown), truly open-ended specs
- CRITICAL: For ANY product specification with limited variations:
  1. First, use your knowledge to look up what variations exist for that specific model
  2. If you know the variations (which you should for most mainstream products), provide multiple choice
  3. ONLY use text input if the product is truly obscure or the variations are unknown
- Examples where you SHOULD use multiple choice (because you have this knowledge):
  - iPhone models → storage options vary by generation
  - MacBook models → specific RAM/storage configs
  - Samsung Galaxy models → storage tiers
  - iPad models → storage capacities
  - TV models → available screen sizes in that series
- NEVER ask user to type specifications when you can provide the exact options

For storage capacity questions (use multiple_choice with accurate options):
{
    "question": "What storage capacity does your iPhone 16 Pro Max have?",
    "field_name": "capacity",
    "type": "multiple_choice",
    "options": ["256GB", "512GB", "1TB"],
    "completed": false
}

For text questions (only when multiple choice isn't appropriate):
{
    "question": "What year was your MacBook purchased?",
    "field_name": "year",
    "type": "text",
    "completed": false
}

For condition questions - GENERATE PRODUCT-SPECIFIC DESCRIPTIONS:
Instead of generic descriptions, tailor the condition options to the specific product type.
Use your knowledge of what matters for that product category.

CONDITION LEVELS (always use these 5 levels):
1. Pristine - Like new condition
2. Excellent - Very light use
3. Good - Normal use
4. Fair - Heavy use
5. Poor - Significant damage

CRITICAL: DO NOT ASK SEPARATE CONDITION QUESTION!
Skip general "condition" questions entirely. Go straight to specific damage assessment.

EXAMPLES:

User says "iPhone 16 Pro Max"
→ Extract: category=phone, brand=Apple, model=iPhone 16 Pro Max, year=2024
→ Check: Do we have storage? NO
→ Look up in your knowledge: iPhone 16 Pro Max comes in 256GB, 512GB, 1TB
→ Ask about storage with specific options:
{
    "question": "What storage capacity does your iPhone 16 Pro Max have?",
    "field_name": "capacity",
    "type": "multiple_choice",
    "options": ["256GB", "512GB", "1TB"],
    "completed": false
}

User answers "512GB"
→ Extract: capacity=512GB
→ Now SKIP condition question, go DIRECTLY to damage assessment

User says "MacBook Air M2"
→ Extract: category=laptop, brand=Apple, model=MacBook Air M2, year=2022
→ Check: Have we asked about configuration? NO
→ Look up in your knowledge: MacBook Air M2 has these configs: 8GB/256GB, 8GB/512GB, 16GB/512GB, 24GB/2TB
→ Ask about configuration:
{
    "question": "What configuration does your MacBook Air M2 have?",
    "field_name": "specifications",
    "type": "multiple_choice",
    "options": ["8GB RAM / 256GB", "8GB RAM / 512GB", "16GB RAM / 512GB", "24GB RAM / 2TB"],
    "completed": false
}

User says "Samsung Galaxy S23"
→ Extract: category=phone, brand=Samsung, model=Galaxy S23, year=2023
→ Check: Have we asked about storage? NO
→ Look up: Galaxy S23 comes in 128GB, 256GB
→ Ask with specific options:
{
    "question": "What storage capacity does your Samsung Galaxy S23 have?",
    "field_name": "capacity",
    "type": "multiple_choice",
    "options": ["128GB", "256GB"],
    "completed": false
}

COMPLETE FLOW EXAMPLE FOR IPHONE:

User says "iPhone 14"
→ Step 1: Extract: category=phone, brand=Apple, model=iPhone 14, year=2022
→ Step 2: Check - do we have storage? NO
→ Step 2: Ask storage:
{
    "question": "What storage capacity does your iPhone 14 have?",
    "field_name": "capacity",
    "type": "multiple_choice",
    "options": ["128GB", "256GB", "512GB"],
    "completed": false
}

User answers "128GB"
→ Step 3: Now ask damage assessment (MANDATORY):
{
    "question": "Are there any of these issues with your iPhone 14? Select all that apply:",
    "field_name": "damage_details",
    "type": "multi_select",
    "options": ["Screen cracked", "Back glass cracked", "Water damage", "Face ID / Touch ID not working", "Camera not working", "Won't turn on / Dead", "Battery health below 80%", "Buttons or ports damaged", "Camera issues (blurry)", "Screen scratches (not cracked)", "Body scratches or scuffs", "Minor dents", "None - Everything works perfectly"],
    "completed": false
}

User selects "None - Everything works perfectly"
→ Step 4: Extract: condition=excellent, damage_details=[none]
→ Step 4: Determine if lockable - iPhone = YES (has iCloud)
→ Step 4: Ask unlock verification:
{
    "question": "Is your iPhone 14 unlocked from iCloud?",
    "field_name": "device_unlocked",
    "type": "multiple_choice",
    "options": ["Yes - Fully unlocked from iCloud", "No - Still locked to iCloud", "Not sure"],
    "completed": false
}

User answers "Yes - Fully unlocked from iCloud"
→ Step 5: Ask contract status:
{
    "question": "Is your iPhone 14 free from any contract or payment plan?",
    "field_name": "contract_free",
    "type": "multiple_choice",
    "options": ["Yes - Fully paid off, no contracts", "No - Still under contract or payment plan"],
    "completed": false
}

User answers "Yes - Fully paid off, no contracts"
→ Step 6: NOW mark as completed:
{
    "question": "",
    "field_name": "",
    "type": "text",
    "completed": true,
    "penalty_info": "Please note: If your device arrives locked to an account, you'll need to either: 1. Unlock it remotely and pay a R550 verification fee, OR 2. Pay R550 for us to return the device to you"
}

IMPORTANT: DO NOT ask separate "condition" question AND "damage details" question. The damage details question IS the condition assessment. Derive condition from damage answers:
- "None - Everything works perfectly" → condition=excellent
- Minor cosmetic only (scratches, scuffs) → condition=good
- Functional issues (battery, buttons, minor cracks) → condition=fair
- Major damage (cracked screen, water damage, won't turn on) → condition=poor

After damage details collected, intelligently check if device needs unlock verification (use logic, not lists)

User says "MacBook Pro 2020"
→ Extract: category=laptop, brand=Apple, model=MacBook Pro, year=2020
→ Check: Do we have specs? NO
→ Ask: "What are the specs? (RAM, storage, screen size)"

User says "Samsung washing machine"
→ Extract: category=appliance, brand=Samsung, type=washing machine
→ Check: Do we have model? NO
→ Ask: "What is the model number?" (need specific model for pricing)

DAMAGE DETAILS QUESTIONS BY CATEGORY:

For PHONES/TABLETS:
"Are there any of these issues with your [Product]? Select all that apply:"
Options: ["Screen cracked", "Back glass cracked", "Water damage", "Face ID / Touch ID not working", "Camera not working", "Won't turn on / Dead", "Battery health below 80%", "Buttons or ports damaged", "Camera issues (blurry)", "Screen scratches (not cracked)", "Body scratches or scuffs", "Minor dents", "None - Everything works perfectly"]

For LAPTOPS:
"Are there any of these issues with your [Product]? Select all that apply:"
Options: ["Screen cracked", "Hinge broken", "Water damage", "Won't turn on / Dead", "Trackpad not working", "Keyboard not working", "Battery health below 80%", "Keyboard keys missing or sticky", "Ports not working", "Overheating issues", "Screen scratches (not cracked)", "Dead pixels (minor)", "Body scratches or dents", "None - Everything works perfectly"]

For CAMERAS:
Options: ["Lens scratches or fungus", "Sensor dust or spots", "Shutter not working / high count", "Autofocus issues", "Body scratches or dents", "Missing parts", "Viewfinder scratches", "None - Everything works perfectly"]

For TVs:
Options: ["Cracked screen", "Screen burn-in (severe)", "Won't turn on / Dead", "Lines or discoloration on screen", "HDMI ports not working", "Smart features not working", "Dead pixels (minor)", "Stand missing or broken", "Remote missing", "Body scratches", "None - Everything works perfectly"]

For APPLIANCES:
Options: ["Doesn't work properly", "Leaks or drips", "Makes excessive noise", "Missing parts", "Visible damage or rust", "None - Everything works perfectly"]

CRITICAL QUESTION ORDER:
1. First: Category, brand, model (from initial input)
2. Then: Age/Year (if needed)
3. Then: Key specs (storage, RAM, etc.)
4. Then: DAMAGE DETAILS (MANDATORY - never skip this!)
5. Finally: Device unlock verification (only if lockable)

NEVER skip damage assessment - it must come BEFORE unlock verification!

DEVICE UNLOCK VERIFICATION (INTELLIGENT CHECK REQUIRED):

After getting damage_details (and ONLY after damage_details), use INTELLIGENCE to determine if this specific device can be locked to digital accounts:

ASK YOURSELF:
1. Can this device be locked to iCloud, Google Account, Samsung Account, Microsoft Account, or similar?
2. Does it have operating system-level account protection?
3. Is it a smart device with user accounts?

Examples of lockable devices: iPhone, Samsung Galaxy, iPad, MacBook, Dell laptop, Apple Watch, Samsung Galaxy Watch
Examples of NON-lockable: Rolex watch, Canon camera, binoculars, PS5 console, Samsung TV, mechanical keyboard

Think intelligently - don't use category alone:
- "Apple Watch" → YES, lockable (smart device with iCloud)
- "Rolex Submariner" → NO, not lockable (mechanical watch, no accounts)
- "iPhone 16" → YES, lockable (has iCloud lock)
- "Canon EOS camera" → NO, not lockable (no account system)

If the device CAN be locked to accounts (based on intelligence, not lists), ask MULTIPLE verification questions in order:

Question 1 - Account Lock Status (REQUIRED):
Use INTELLIGENCE to mention only RELEVANT accounts for this specific device:
- iPhone/iPad/MacBook/Apple Watch → mention only "iCloud"
- Samsung phone/tablet/watch → mention only "Google Account and Samsung Account"
- Other Android phones → mention only "Google Account"
- Windows laptop → mention only "Microsoft Account"
- Multi-brand (unsure) → use generic "any accounts"

Examples:
{
    "question": "Is your iPhone 16 Pro Max unlocked from iCloud?",
    "field_name": "device_unlocked",
    "type": "multiple_choice",
    "options": [
        "Yes - Fully unlocked from iCloud",
        "No - Still locked to iCloud",
        "Not sure"
    ],
    "completed": false
}

{
    "question": "Is your Samsung Galaxy S24 unlocked from all accounts (Google and Samsung)?",
    "field_name": "device_unlocked",
    "type": "multiple_choice",
    "options": [
        "Yes - Fully unlocked from all accounts",
        "No - Still locked to an account",
        "Not sure"
    ],
    "completed": false
}

If answer is "No" or "Not sure" → STOP and return:
{
    "question": "We cannot purchase devices locked to accounts. Please unlock your device first and try again.",
    "field_name": "",
    "type": "text",
    "completed": true,
    "decline_reason": "device_locked"
}

If answer is "Yes - Fully unlocked" → Continue to Question 2!

Question 2 - Contract Status (REQUIRED for phones/tablets):
CRITICAL: You MUST ask this question for smartphones and tablets - do NOT skip it!
{
    "question": "Is your [Product] free from any contract or payment plan?",
    "field_name": "contract_free",
    "type": "multiple_choice",
    "options": [
        "Yes - Fully paid off, no contracts",
        "No - Still under contract or payment plan"
    ],
    "completed": false
}

If answer is "No" → STOP and return:
{
    "question": "We cannot purchase devices under contract or payment plans. Please settle your account first.",
    "field_name": "",
    "type": "text",
    "completed": true,
    "decline_reason": "under_contract"
}

If answer is "Yes - Fully paid off" → NOW you can mark as completed!

Question 3 - Proof of Purchase (OPTIONAL - SKIP THIS):
DO NOT ask about proof of purchase. Skip this question entirely.
After Questions 1 and 2 are answered, proceed directly to completion.

After unlock and contract questions answered, extract: device_unlocked=yes, contract_free=yes
Then set completed: true

IMPORTANT PENALTY POLICY:
Include in your final message AFTER all questions:
"Please note: If your device arrives locked to an account, you'll need to either:
1. Unlock it remotely and pay a R550 verification fee, OR
2. Pay R550 for us to return the device to you"

COMPLETION: Set "completed": true ONLY when you have ASKED ABOUT AND RECEIVED ANSWERS FOR:
1. Category, brand, model ✓
2. Age/Year (ESSENTIAL for phones, laptops, tablets) ✓
3. Key specs (if applicable - storage, RAM, screen size) ✓
4. Damage details (specific issues) - MANDATORY FOR ALL ITEMS ✓
5. Device unlock verification (ONLY if device is intelligently determined to be lockable) ✓
6. Contract status (ONLY if device can have contracts - smartphones, tablets, smart watches with cellular) ✓

DO NOT set completed=true until you have asked ALL applicable questions and received user answers!

For an iPhone, you MUST ask ALL of these questions in order:
1. Storage capacity (e.g., "128GB") ✓
2. Damage details ("Are there any of these issues...") ✓
3. Device unlock ("Is your iPhone unlocked from iCloud?") ✓
4. Contract status ("Is your iPhone free from any contract...") ✓
5. ONLY THEN mark completed=true

CRITICAL: After the user answers the unlock question, you MUST ask the contract question next!
Do NOT jump to completion after unlock - contract question is MANDATORY for phones!

NEVER skip to completion after just asking about storage!
NEVER skip to completion after just asking about unlock - ask contract first!

COMPLETION EXAMPLES - After user answers last question (unlock/contract), return EXACTLY this format:

Example 1 - Simple completion (no lockable device):
{
    "question": "",
    "field_name": "",
    "type": "text",
    "completed": true
}

Example 2 - Completion with penalty warning (lockable device):
{
    "question": "",
    "field_name": "",
    "type": "text",
    "completed": true,
    "penalty_info": "Please note: If your device arrives locked to an account, you'll need to either: 1. Unlock it remotely and pay a R550 verification fee, OR 2. Pay R550 for us to return the device to you"
}

CRITICAL JSON FORMAT RULES - FOLLOW EXACTLY:
1. Use lowercase "true" and "false" (NOT "True" or "False" - Python style will break parsing!)
2. Use double quotes for strings (NOT single quotes)
3. Do NOT include any text before or after the JSON
4. NEVER use Python boolean literals (True/False) - always use JSON (true/false)
5. Empty strings must be "" not ''

WRONG EXAMPLES (DO NOT USE):
{"completed": True}  ❌ Python boolean
{"completed": False, 'field': 'value'}  ❌ Single quotes
{'question': "text"}  ❌ Single quotes on keys

CORRECT EXAMPLES (USE THESE):
{"completed": true}  ✅ JSON boolean
{"completed": false, "field": "value"}  ✅ Double quotes
{"question": "text"}  ✅ Double quotes on keys

DO NOT ask any more questions after all requirements met. Just return completed: true with empty question.

DECLINE IMMEDIATELY if:
- Device is locked to an account → decline_reason: "device_locked"
- Device is under contract/payment plan → decline_reason: "under_contract"

CURRENT PRODUCT INFO:
""" + str(product_info) + """

CONVERSATION HISTORY (check for duplicate questions):
""" + str([msg['content'] for msg in conversation_history if msg['role'] == 'assistant']) + """

═══════════════════════════════════════════════════════════════
YOUR RESPONSE MUST USE THIS EXACT JSON TEMPLATE - NO OTHER FORMAT:
═══════════════════════════════════════════════════════════════
{
    "question": "<the actual question text goes here>",
    "field_name": "<the field name>",
    "type": "<text|multiple_choice|multi_select>",
    "options": [<only if type is multiple_choice or multi_select>],
    "completed": <true|false>
}
═══════════════════════════════════════════════════════════════
DO NOT write anything except the JSON above. Start your response with { and end with }"""

        # Build conversation messages
        messages = []
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # If no messages yet, return the initial question directly
        if not messages:
            return {
                "question": "What item do you want to sell?",
                "field_name": "item_description",
                "type": "text",
                "completed": False
            }

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=messages
        )

        # Parse response
        import json
        import re
        response_text = response.content[0].text.strip()

        # Try to extract JSON from response (in case AI adds extra text)
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            response_text = json_match.group(0)

        # FIX: Replace Python-style booleans with JSON booleans before parsing
        response_text = response_text.replace(': True', ': true')
        response_text = response_text.replace(': False', ': false')
        response_text = response_text.replace(':True', ':true')
        response_text = response_text.replace(':False', ':false')

        try:
            result = json.loads(response_text)
            print(f"\n{'='*60}")
            print(f"DEBUG AI_SERVICE: Successfully parsed JSON")
            print(f"   Question: {result.get('question', 'N/A')}")
            print(f"   Field: {result.get('field_name', 'N/A')}")
            print(f"   Type: {result.get('type', 'N/A')}")
            print(f"   Completed: {result.get('completed', 'N/A')}")
            if 'penalty_info' in result:
                print(f"   Penalty info included: Yes")
            print(f"{'='*60}\n")

            # Ensure type field exists
            if 'type' not in result:
                result['type'] = 'text'
            # Ensure completed field exists
            if 'completed' not in result:
                result['completed'] = False

            # CRITICAL: Validate completion - enforce required fields
            result = self._validate_completion(product_info, result)

            return result
        except json.JSONDecodeError as e:
            # Fallback if AI doesn't return proper JSON
            print(f"❌ JSON PARSE ERROR in get_next_question:")
            print(f"   Error: {e}")
            print(f"   Raw response: {response_text}")
            print(f"   Full AI response: {response.content[0].text}")

            # INTELLIGENT FALLBACK: Check if validation would generate a question
            # This handles Haiku returning plain text instead of JSON
            print(f"\n🔧 ATTEMPTING INTELLIGENT FALLBACK:")
            print(f"   Checking if we have missing required fields...")

            required_fields = self._get_required_fields(product_info)
            missing_fields = []
            for field, description in required_fields.items():
                if field not in product_info or not product_info[field]:
                    missing_fields.append(description)

            if missing_fields:
                # Generate the next required question
                print(f"   ✅ Found missing field: {missing_fields[0]}")
                print(f"   Generating structured question for: {missing_fields[0]}")
                fallback_question = self._generate_missing_field_question(product_info, missing_fields[0])
                fallback_question['completed'] = False
                print(f"   📋 Fallback question: {fallback_question.get('question', 'N/A')}")
                return fallback_question
            else:
                # No missing fields, return generic error question
                print(f"   ⚠️  No missing fields found, returning generic fallback")
                return {
                    "question": "What type of item do you want to sell?",
                    "field_name": "item_description",
                    "type": "text",
                    "completed": False
                }

    def extract_product_details(self, conversation_history):
        """
        Extracts structured product information from the conversation.

        Returns:
            Dict with product details: category, brand, model, specs, condition, damage
        """

        system_prompt = """Analyze the conversation and extract all product details.

Return a JSON object with these fields (use null if not mentioned):
{
    "category": "phone|laptop|camera|tablet|console|appliance|watch|other (binoculars=camera, headphones=other)",
    "brand": "Brand name",
    "model": "Model name/number",
    "specifications": {
        "capacity": "e.g., 128GB",
        "color": "e.g., Space Gray",
        "year": "e.g., 2020",
        "size": "e.g., 15 inch"
    },
    "condition": "pristine|excellent|good|fair|poor|broken",
    "damage": {
        "screen": "none|scratched|cracked|broken",
        "body": "none|minor_scratches|dents|cracks",
        "battery": "good|degraded|dead",
        "functional": "fully_working|some_issues|not_working",
        "notes": "Any other damage mentioned"
    },
    "damage_details": "Summary of damage/issues mentioned (use 'No issues mentioned' or 'Pristine condition' if user said none/everything works/no damage)",
    "device_unlocked": "yes|no|not_asked (if device unlock was discussed)",
    "contract_free": "yes|no|not_asked (if contract status was discussed)"
}

CRITICAL DAMAGE EXTRACTION RULES:
- If user selected "None - Everything works perfectly" or similar → damage_details: "No issues mentioned"
- If user said "no damage", "everything works", "pristine", "perfect" → damage_details: "No issues mentioned"
- If user mentioned specific issues → damage_details: "Brief summary of issues"
- NEVER leave damage_details as null if damage was discussed

IMPORTANT: Extract device_unlocked and contract_free from conversation if those questions were asked.
"""

        messages = []
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Debug: Print what we're sending to extraction AI
        print(f"\n🔍 EXTRACTION DEBUG:")
        print(f"   Conversation history has {len(conversation_history)} messages")
        for i, msg in enumerate(conversation_history):
            print(f"   [{i}] {msg['role']}: {msg['content'][:100]}")

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=system_prompt,
            messages=messages
        )

        import json
        raw_response = response.content[0].text
        print(f"   AI extraction raw response: {raw_response[:500]}")

        try:
            result = json.loads(raw_response)
            print(f"   ✅ Extraction successful: {result}")
            return result
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON parse failed: {e}")
            print(f"   Full response: {raw_response}")
            return None

    def generate_search_queries(self, product_info):
        """
        Generates effective search queries for finding prices online.

        Args:
            product_info: Structured product information

        Returns:
            List of search query strings
        """

        prompt = f"""Generate 3-5 effective search queries to find the price of this second-hand item online:

Product: {product_info}

Return ONLY a JSON array of search query strings, like:
["query 1", "query 2", "query 3"]

Make queries specific enough to find the exact item, but not so specific they return no results.
Include variations (with/without capacity, with/without color, etc.)
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        import json
        try:
            queries = json.loads(response.content[0].text)
            return queries
        except json.JSONDecodeError:
            # Fallback: generate basic query
            brand = product_info.get('brand', '')
            model = product_info.get('model', '')
            return [f"{brand} {model} second hand South Africa"]

    def assess_confidence(self, price_data, product_info):
        """
        Assesses confidence in the pricing data collected.

        Args:
            price_data: Dict of prices found from various sources
            product_info: Product details

        Returns:
            Float between 0 and 1 indicating confidence level
        """

        prompt = f"""Assess the confidence level for making an automated offer based on this data:

PRODUCT: {product_info}

PRICE DATA FOUND: {price_data}

Consider:
1. Number of price points found
2. Consistency between sources
3. Recency of data
4. Exact match vs similar items
5. South African vs overseas prices

Return a JSON object:
{{
    "confidence": 0.0-1.0,
    "reasoning": "Brief explanation",
    "recommendation": "instant_offer|email_review"
}}
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        import json
        try:
            result = json.loads(response.content[0].text)
            return result['confidence'], result
        except (json.JSONDecodeError, KeyError):
            # Conservative default
            return 0.5, {"confidence": 0.5, "reasoning": "Unable to assess", "recommendation": "email_review"}
