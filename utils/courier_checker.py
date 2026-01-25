"""
Courier Eligibility Checker - AI-Powered
Determines if an item can be couriered using AI intelligence
Generates witty, adaptive responses for all scenarios
"""

import anthropic
from config import Config


def is_courier_eligible(product_info: dict) -> dict:
    """
    Check if a product can be couriered using AI intelligence

    Args:
        product_info: Dict with 'category', 'brand', 'model', etc.

    Returns:
        Dict with 'eligible' (bool), 'reason' (str), 'category_matched' (str), 'is_silly' (bool)
    """
    category = product_info.get('category', '').lower()
    brand = product_info.get('brand', '').lower()
    model = product_info.get('model', '').lower()

    # Combine all text for AI analysis
    full_text = f"{category} {brand} {model}".strip()

    if not full_text:
        return {
            'eligible': True,
            'reason': 'Item appears to be courier-eligible',
            'category_matched': 'unknown',
            'is_silly': False
        }

    # Use AI to determine courier eligibility
    try:
        print(f"\n🤖 AI COURIER CHECK: Analyzing '{full_text}'...")

        client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)

        prompt = f"""You are analyzing whether an item can be couriered for EpicDeals.co.za, a second-hand electronics buyer in South Africa.

ITEM DESCRIPTION: "{full_text}"

THE CORE RULE - USE YOUR INTELLIGENCE:
Ask yourself: "Can this item fit in a courier bag or small parcel box, and be safely shipped by a standard courier service?"

If YES → eligible: true
If NO → eligible: false

THINK ABOUT:
1. SIZE: Can it fit in a courier bag or box that one person can carry? (Roughly: smaller than 60cm x 40cm x 40cm)
2. WEIGHT: Can one person lift it? (Under ~25kg)
3. FRAGILITY: Is it robust enough to survive standard courier handling in a box?
4. PRACTICALITY: Would a normal courier service accept this item?

EXAMPLES OF YOUR THINKING PROCESS:

"Piano" → Think: Pianos are large, heavy instruments. Even small keyboards are bulky. Cannot fit in courier bag. NOT ELIGIBLE.

"Refrigerator" → Think: Large appliance, very heavy, requires special delivery. NOT ELIGIBLE.

"BMW" → Think: A car cannot be couriered. Absurd. NOT ELIGIBLE.

"Elephant" → Think: Living creature, massive, absurd to courier. SILLY and NOT ELIGIBLE.

"iPhone 11" → Think: Small phone, fits in hand, lightweight, can be safely packed in small box. ELIGIBLE.

"Laptop" → Think: Portable computer, designed to be carried, fits in courier box. ELIGIBLE.

"Couch" → Think: Large furniture, heavy, requires furniture movers. NOT ELIGIBLE.

"Guitar" → Think: Musical instrument, bulky, delicate neck, too large for standard courier box. NOT ELIGIBLE.

"Headphones" → Think: Small, lightweight, fits in bag. ELIGIBLE.

SILLY/IMPOSSIBLE ITEMS (use common sense):
- Living creatures (animals, people, plants)
- Fictional things (unicorns, dragons, lightsabers, magic wands)
- Illegal items (drugs, weapons, organs)
- Absurd things (buildings, vehicles, aircraft, boats, rockets)

RESPONSE TONE:
- For SILLY items: Be witty and playful, redirect to real electronics
- For LARGE items: Be friendly and apologetic, explain we only accept courier-friendly items
- For INAPPROPRIATE items: Be firm but brief
- Use emojis, keep responses 2-3 sentences max

OUTPUT FORMAT (respond with ONLY valid JSON):
{{
    "eligible": true/false,
    "is_silly": true/false,
    "category_matched": "brief descriptor",
    "reason": "Your message"
}}

EXAMPLES:

Input: "piano"
Output: {{"eligible": false, "is_silly": false, "category_matched": "large instrument", "reason": "🎹 Pianos are too large for courier delivery! We only accept items that fit in a courier bag or small box. We buy phones, laptops, tablets, cameras, and other small electronics. Please check back as we expand!"}}

Input: "washing machine"
Output: {{"eligible": false, "is_silly": false, "category_matched": "large appliance", "reason": "We only accept items that can be couriered in a bag or small box. Large appliances like washing machines require special delivery. We buy phones, laptops, cameras, and other small electronics!"}}

Input: "elephant"
Output: {{"eligible": false, "is_silly": true, "category_matched": "animal", "reason": "🐘 We definitely can't courier elephants! We buy small electronics like phones, laptops, and tablets. Got any of those instead?"}}

Input: "BMW"
Output: {{"eligible": false, "is_silly": true, "category_matched": "vehicle", "reason": "🚗 Cars can't be couriered! We buy small electronics like phones, laptops, cameras, and gaming consoles that fit in a box. Got something like that?"}}

Input: "iPhone 11"
Output: {{"eligible": true, "is_silly": false, "category_matched": "phone", "reason": "Item can be couriered"}}

Input: "MacBook Pro"
Output: {{"eligible": true, "is_silly": false, "category_matched": "laptop", "reason": "Item can be couriered"}}

Input: "unicorn"
Output: {{"eligible": false, "is_silly": true, "category_matched": "mythical creature", "reason": "🦄 Unfortunately, mythical creatures aren't real! We buy actual electronics like phones, laptops, and tablets. Got any of those?"}}

Now analyze this item and respond with ONLY valid JSON:"""

        print(f"   Calling Claude API...")
        response = client.messages.create(
            model=Config.ANTHROPIC_MODEL,
            max_tokens=512,
            timeout=10.0,  # 10 second timeout
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        print(f"   ✅ API call successful!")

        import json
        import re

        response_text = response.content[0].text.strip()

        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            response_text = json_match.group(0)

        result = json.loads(response_text)

        print(f"\n{'='*60}")
        print(f"AI COURIER CHECK RESULT for '{full_text}':")
        print(f"  eligible: {result.get('eligible')}")
        print(f"  is_silly: {result.get('is_silly')}")
        print(f"  category_matched: {result.get('category_matched')}")
        print(f"  reason: {result.get('reason')}")
        print(f"{'='*60}\n")

        # Ensure all required fields exist
        if 'eligible' not in result:
            result['eligible'] = True
        if 'is_silly' not in result:
            result['is_silly'] = False
        if 'category_matched' not in result:
            result['category_matched'] = 'unknown'
        if 'reason' not in result:
            result['reason'] = 'Item appears to be courier-eligible'

        return result

    except Exception as e:
        print(f"❌ ERROR in AI courier check: {e}")
        import traceback
        traceback.print_exc()

        # Fallback: For safety, reject unknown items during errors
        # This prevents accepting items we shouldn't when AI is down
        return {
            'eligible': False,
            'reason': 'We\'re experiencing technical difficulties. Please try again in a moment or contact us at brad@epicdeals.co.za',
            'category_matched': 'error',
            'is_silly': False
        }


def get_courier_rejection_message(product_info: dict) -> str:
    """
    Get a friendly rejection message for non-courier items

    Args:
        product_info: Dict with product information

    Returns:
        str: Rejection message or None if eligible
    """
    result = is_courier_eligible(product_info)

    if result['eligible']:
        return None

    return result['reason']


def get_business_model_options(product_info: dict) -> dict:
    """
    Determine which business models are available for this product
    Uses AI to intelligently classify electronics vs non-electronics

    Args:
        product_info: Dict with 'category', 'brand', 'model', etc.

    Returns:
        Dict with:
            - 'sell_now_available' (bool)
            - 'consignment_available' (bool)
            - 'reason' (str)
    """
    category = product_info.get('category', '').lower()
    brand = product_info.get('brand', '').lower()
    model = product_info.get('model', '').lower()

    # Combine all text for checking
    full_text = f"{category} {brand} {model}".strip()

    if not full_text:
        # Default to consignment only for unknown items
        return {
            'sell_now_available': False,
            'consignment_available': True,
            'reason': 'Unknown item - consignment only'
        }

    # Use AI to determine if it's electronics
    try:
        client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)

        prompt = f"""Is this item consumer electronics?

ITEM: "{full_text}"

Consumer electronics include: phones, smartphones, tablets, laptops, computers, watches, smartwatches, cameras, headphones, earbuds, speakers, gaming consoles, keyboards, mice, drones, routers, hard drives, graphics cards, processors, powerbanks, chargers, smart home devices, etc.

NOT consumer electronics: furniture, appliances, clothing, musical instruments (except electronic), books, toys (except electronic), etc.

Respond with ONLY valid JSON:
{{
    "is_electronics": true/false
}}"""

        response = client.messages.create(
            model=Config.ANTHROPIC_MODEL,
            max_tokens=128,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        import json
        import re

        response_text = response.content[0].text.strip()
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            response_text = json_match.group(0)

        result = json.loads(response_text)
        is_electronics = result.get('is_electronics', False)

        if is_electronics:
            return {
                'sell_now_available': True,
                'consignment_available': True,
                'reason': 'Electronics item - both models available'
            }
        else:
            return {
                'sell_now_available': False,
                'consignment_available': True,
                'reason': 'Non-electronics item - consignment only (harder to price accurately)'
            }

    except Exception as e:
        print(f"Error in business model classification: {e}")
        # Fallback: consignment only (conservative)
        return {
            'sell_now_available': False,
            'consignment_available': True,
            'reason': 'Item classification unclear - consignment only'
        }
