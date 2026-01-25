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
3. Be SMART - extract ALL information from what the user already told you
4. If user says "iPhone 11" - you already know: category=phone, brand=Apple, model=iPhone 11. DON'T ask for category!
5. If user says "MacBook Pro 2020" - you know: category=laptop, brand=Apple, model=MacBook Pro, year=2020
6. ONLY ask for information you DON'T already have AND that affects pricing
7. Ask ONE clear question at a time
8. Use multiple choice for condition questions
9. Be efficient - aim for 2-3 questions maximum
10. Mark as COMPLETED once you have: category, brand, model, key specs that affect value, and condition

BEFORE ASKING A QUESTION:
1. Check conversation_history - has this question been asked already?
2. Check CURRENT PRODUCT INFO - do we already have this information?
3. If YES to either, DON'T ask it again - move to the next needed information or set completed=true

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

RESPONSE FORMAT - CRITICAL:
You MUST respond with ONLY valid JSON, nothing else. No explanations, no text before or after.
EVERY response MUST contain a "question" field with the actual question text to ask the user.

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

For multiple choice questions (condition) - USE THESE EXACT OPTIONS:
{
    "question": "What is the physical condition of your iPhone 16 Pro Max?",
    "field_name": "condition",
    "type": "multiple_choice",
    "options": [
        "Pristine - Like new, no visible wear (95-100% value)",
        "Excellent - Very light use, barely noticeable marks (85-95% value)",
        "Good - Normal use, minor scratches/scuffs (70-85% value)",
        "Fair - Heavy use, obvious scratches/dents (50-70% value)",
        "Poor - Significant damage or broken parts (30-50% value)"
    ],
    "completed": false
}

When conversation is complete:
{
    "question": "",
    "field_name": "",
    "type": "text",
    "completed": true
}

EXAMPLES:

User says "iPhone 16 Pro Max"
→ Extract: category=phone, brand=Apple, model=iPhone 16 Pro Max, year=2024
→ Check: Have we asked about storage? NO
→ Look up in your knowledge: iPhone 16 Pro Max comes in 256GB, 512GB, 1TB
→ Ask about storage with specific options:
{
    "question": "What storage capacity does your iPhone 16 Pro Max have?",
    "field_name": "capacity",
    "type": "multiple_choice",
    "options": ["256GB", "512GB", "1TB"],
    "completed": false
}

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

User says "iPhone 11 128GB"
→ Extract: category=phone, brand=Apple, model=iPhone 11, capacity=128GB, year=2019
→ Check: Have we asked about condition? NO
→ Ask about condition using the EXACT options format:
{
    "question": "What is the physical condition of your iPhone 11?",
    "field_name": "condition",
    "type": "multiple_choice",
    "options": [
        "Pristine - Like new, no visible wear (95-100% value)",
        "Excellent - Very light use, barely noticeable marks (85-95% value)",
        "Good - Normal use, minor scratches/scuffs (70-85% value)",
        "Fair - Heavy use, obvious scratches/dents (50-70% value)",
        "Poor - Significant damage or broken parts (30-50% value)"
    ],
    "completed": false
}

User answers "Good - Minor wear"
→ Extract: condition=good
→ Check: Have we asked about damage details? NO
→ Ask about specific issues:
{
    "question": "Are there any of these issues with your iPhone 11? Select all that apply:",
    "field_name": "damage_details",
    "type": "multi_select",
    "options": ["Screen cracked or scratched", "Back glass cracked", "Body dents or deep scratches", "Battery health below 80%", "Camera issues", "Face ID / Touch ID not working", "Buttons or ports damaged", "Water damage", "None - Everything works perfectly"],
    "completed": false
}

User selects "None - Everything works perfectly"
→ Extract: damage_details=[none]
→ You now have: category, brand, model, capacity, condition, damage_details
→ Set completed: true

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
Options: ["Screen cracked or scratched", "Back glass cracked", "Body dents or deep scratches", "Battery health below 80%", "Camera issues", "Face ID / Touch ID not working", "Buttons or ports damaged", "Water damage", "None - Everything works perfectly"]

For LAPTOPS:
"Are there any of these issues with your [Product]? Select all that apply:"
Options: ["Screen scratches, dead pixels, or cracks", "Keyboard keys missing or sticky", "Trackpad not working properly", "Battery health below 80%", "Dents or cracks in body", "Hinge loose or broken", "Ports not working", "Overheating issues", "None - Everything works perfectly"]

For CAMERAS:
Options: ["Lens scratches or fungus", "Sensor dust or spots", "Shutter not working / high count", "Autofocus issues", "Body scratches or dents", "Missing parts", "Viewfinder scratches", "None - Everything works perfectly"]

For TVs:
Options: ["Screen burn-in or dead pixels", "Cracked screen", "Lines or discoloration", "HDMI ports not working", "Smart features not working", "Stand missing or broken", "Remote missing", "None - Everything works perfectly"]

For APPLIANCES:
Options: ["Doesn't work properly", "Leaks or drips", "Makes excessive noise", "Missing parts", "Visible damage or rust", "None - Everything works perfectly"]

COMPLETION: Set "completed": true when you have:
1. Category, brand, model
2. Age/Year (ESSENTIAL for phones, laptops, tablets)
3. Key specs (if applicable)
4. Overall condition
5. Damage details (specific issues)

CURRENT PRODUCT INFO:
""" + str(product_info) + """

CONVERSATION HISTORY (check for duplicate questions):
""" + str([msg['content'] for msg in conversation_history if msg['role'] == 'assistant'])

        # Build conversation messages
        messages = []
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # If no messages yet, start with a user message to begin the conversation
        if not messages:
            messages.append({
                "role": "user",
                "content": "I want to sell an item. Please ask me the first question to gather information."
            })

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

        try:
            result = json.loads(response_text)
            print(f"DEBUG AI_SERVICE: Raw AI response: {result}")

            # Ensure type field exists
            if 'type' not in result:
                result['type'] = 'text'
            # Ensure completed field exists
            if 'completed' not in result:
                result['completed'] = False

            print(f"DEBUG AI_SERVICE: Processed result: {result}")
            return result
        except json.JSONDecodeError as e:
            # Fallback if AI doesn't return proper JSON
            return {
                "question": "What type of item do you want to sell? (e.g., iPhone 11, MacBook Pro, Samsung TV)",
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
    "category": "phone|laptop|camera|tablet|console|appliance|watch|other",
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
    }
}
"""

        messages = []
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=system_prompt,
            messages=messages
        )

        import json
        try:
            result = json.loads(response.content[0].text)
            return result
        except json.JSONDecodeError:
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
