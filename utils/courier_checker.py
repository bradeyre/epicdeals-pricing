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

Your task is to determine:
1. Can this item be safely couriered? (Consider size, weight, fragility, practicality)
2. Is this a silly/impossible/inappropriate item?
3. Generate a witty, engaging response message

COURIER ELIGIBILITY RULES:
- ✅ YES: Small electronics (phones, laptops, tablets, cameras, watches, headphones, gaming consoles, small appliances that fit in a box)
- ✅ YES: Items that can fit in a standard courier box and weigh under ~25kg
- ❌ NO: Large appliances (fridges, washing machines, ovens, dishwashers, geysers)
- ❌ NO: Furniture (sofas, beds, tables, wardrobes, desks)
- ❌ NO: Large musical instruments (pianos, organs, drum kits, harps, tubas)
- ❌ NO: Vehicles (cars, boats, motorcycles)
- ❌ NO: Large fitness equipment (treadmills, exercise bikes)
- ❌ NO: TVs larger than 50 inches (too fragile for courier)

SILLY/IMPOSSIBLE ITEMS (requires witty response):
- Living creatures (animals, people, etc.)
- Fictional items (unicorns, dragons, lightsabers, time machines, etc.)
- Illegal/inappropriate items (weapons, drugs, organs, etc.)
- Absurd items (spaceships, submarines, tanks, nuclear anything, etc.)
- Real estate (houses, buildings, land)

RESPONSE TONE:
- For SILLY items: Be witty, humorous, and playful while redirecting to actual electronics
- For NON-COURIER items: Be friendly, apologetic, and professional
- For INAPPROPRIATE items: Be firm but not preachy
- Always use emojis to make responses engaging
- Keep responses concise (2-3 sentences max)

OUTPUT FORMAT (respond with ONLY valid JSON):
{{
    "eligible": true/false,
    "is_silly": true/false,
    "category_matched": "brief descriptor of what was detected",
    "reason": "Your witty/friendly message here"
}}

EXAMPLES:

Input: "grand piano"
Output: {{"eligible": false, "is_silly": false, "category_matched": "large instrument", "reason": "🎹 Grand pianos are a bit too grand for our courier service! These magnificent instruments are too large and delicate to ship safely. We focus on electronics like phones, laptops, and gaming consoles that can be couriered. Check back as we expand our services!"}}

Input: "penguin"
Output: {{"eligible": false, "is_silly": true, "category_matched": "animal", "reason": "🐧 While we admire your entrepreneurial spirit, we can't accept live animals! Penguins belong in the wild (or a zoo with proper permits). How about something electronic instead? Got a phone or laptop to sell?"}}

Input: "iPhone 11"
Output: {{"eligible": true, "is_silly": false, "category_matched": "phone", "reason": "Item can be couriered"}}

Input: "unicorn"
Output: {{"eligible": false, "is_silly": true, "category_matched": "mythical creature", "reason": "🦄 If you actually have a unicorn, you should probably contact a mythical creature preservation society! For now, we only buy real-world electronics and gadgets. Got an iPhone or gaming console instead?"}}

Input: "washing machine"
Output: {{"eligible": false, "is_silly": false, "category_matched": "large appliance", "reason": "Unfortunately, we currently only accept items that can be couriered. We're unable to process large appliances like washing machines at this time. We buy phones, laptops, cameras, and other electronics that fit in a box. Please check back in the future as we expand our services!"}}

Input: "time machine"
Output: {{"eligible": false, "is_silly": true, "category_matched": "fictional device", "reason": "⏰ If you had a working time machine, you could go back and get a better price! For now, we only buy electronics from this timeline. How about a phone, tablet, or gaming console?"}}

Input: "kidney"
Output: {{"eligible": false, "is_silly": true, "category_matched": "human organ", "reason": "🏥 We're definitely not buying organs! That's highly illegal and extremely concerning. We buy phones, laptops, cameras, and other electronics only. Please contact appropriate authorities if you need help."}}

Input: "MacBook Pro"
Output: {{"eligible": true, "is_silly": false, "category_matched": "laptop", "reason": "Item can be couriered"}}

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
