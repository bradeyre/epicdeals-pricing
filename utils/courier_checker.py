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

    # Combine all text for AI analysis, removing empty/duplicate parts
    parts = [p for p in [category, brand, model] if p]
    full_text = " ".join(parts).strip()

    # Remove duplicates (e.g., "piano piano" becomes "piano")
    words = full_text.split()
    if len(words) > 1 and all(w == words[0] for w in words):
        full_text = words[0]

    if not full_text:
        return {
            'eligible': True,
            'reason': 'Item appears to be courier-eligible',
            'category_matched': 'unknown',
            'is_silly': False
        }

    # Check for explicit multiple item indicators
    import re
    multiple_indicators = [
        r'\b\d+\s*x\b',  # "2x", "5 x"
        r'\bx\s*\d+\b',  # "x2", "x 5"
        r'\b(two|three|four|five|six|seven|eight|nine|ten)\s+(iphone|samsung|macbook|ipad|gopro|laptop|phone|tablet|camera)',
        r'\bmultiple\b',
        r'\bseveral\b',
        r'\bbunch of\b'
    ]

    full_text_lower = full_text.lower()
    for pattern in multiple_indicators:
        if re.search(pattern, full_text_lower):
            return {
                'eligible': False,
                'reason': 'We appreciate your interest! For multiple items, please submit each one separately for the most accurate pricing. This ensures we can properly evaluate the condition and specifications of each device.',
                'category_matched': 'multiple_items',
                'is_silly': False
            }

    # Use AI to determine courier eligibility
    try:
        print(f"\n🤖 AI COURIER CHECK: Analyzing '{full_text}'...")

        client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)

        prompt = f"""The user wants to sell ONE (1) single item: "{full_text}"

Can this SINGLE ITEM be shipped in a courier bag or small parcel box?

CRITICAL: This is ONE item, not multiple items. Numbers in the model name (like "iPhone 14", "iPhone 16", "Galaxy S21") are just the model version, NOT the quantity.

ASK YOURSELF:
1. Can this ONE item fit in a standard courier bag or small box?
2. Can one person carry this ONE item easily?
3. Does this ONE item weigh under 25kg?
4. Is it SAFE to ship? (Not hazardous, chemical, food, liquid, perishable, or restricted)
5. Is it USED ELECTRONICS? (We only buy used electronics - phones, laptops, tablets, cameras, watches, etc.)

If NO to ANY question → {{"eligible": false}}
If YES to ALL → {{"eligible": true}}

Is it a living thing, vehicle, furniture, large appliance, or fictional item? → {{"is_silly": true}}

IMPORTANT FOR ELIGIBLE ITEMS: Generate a friendly, welcoming message explaining how we'll ship this item.
IMPORTANT FOR NON-ELIGIBLE ITEMS: Generate a witty, friendly rejection message. Be creative and humorous while staying professional.

Output ONLY JSON:
{{"eligible": true/false, "is_silly": true/false, "category_matched": "type", "reason": "message"}}

Example thinking:
- "iPhone 16" → ONE phone (model 16) → used electronics → fits in bag → ELIGIBLE
- "iPhone 14" → ONE phone (model 14) → used electronics → fits in bag → ELIGIBLE
- "Galaxy S21" → ONE phone (model S21) → used electronics → fits in bag → ELIGIBLE
- Piano, couch, fridge → too large → not eligible, witty message
- Drain cleaner, chemicals, food → not electronics OR hazardous → not eligible
- Animals, vehicles → absurd → not eligible, is_silly, humorous message
- Clothing, books, toys → not electronics → not eligible

Analyze ONE (1) item: "{full_text}":"""

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
