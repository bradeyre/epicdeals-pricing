"""
Courier Eligibility Checker
Determines if an item can be couriered based on category and characteristics
Also determines business model eligibility (Sell Now + Consignment vs Consignment-only)
"""

# Electronics categories - qualify for BOTH Sell Now and Consignment
ELECTRONICS_CATEGORIES = [
    'phone',
    'smartphone',
    'mobile',
    'iphone',
    'android',
    'laptop',
    'notebook',
    'macbook',
    'tablet',
    'ipad',
    'watch',
    'smartwatch',
    'apple watch',
    'camera',
    'dslr',
    'mirrorless',
    'headphones',
    'earbuds',
    'airpods',
    'speaker',
    'portable speaker',
    'keyboard',
    'mouse',
    'drone',
    'gaming console',
    'playstation',
    'ps4',
    'ps5',
    'xbox',
    'nintendo',
    'switch',
    'controller',
    'router',
    'modem',
    'hard drive',
    'ssd',
    'external drive',
    'graphics card',
    'gpu',
    'cpu',
    'processor',
    'ram',
    'memory',
    'powerbank',
    'power bank',
    'charger',
    'cable',
    'smart home',
    'echo',
    'alexa',
    'google home',
    'nest'
]

# Items that can be couriered (includes electronics + other items)
COURIER_ELIGIBLE_CATEGORIES = [
    'phone',
    'smartphone',
    'mobile',
    'laptop',
    'notebook',
    'tablet',
    'ipad',
    'watch',
    'smartwatch',
    'camera',
    'headphones',
    'earbuds',
    'airpods',
    'speaker',
    'portable speaker',
    'keyboard',
    'mouse',
    'drone',
    'gaming console',
    'playstation',
    'xbox',
    'nintendo',
    'controller',
    'router',
    'modem',
    'hard drive',
    'ssd',
    'graphics card',
    'gpu',
    'cpu',
    'processor',
    'ram',
    'memory',
    'powerbank',
    'charger',
    'cable'
]

# Items that CANNOT be couriered (too large/heavy)
NON_COURIER_CATEGORIES = [
    'fridge',
    'refrigerator',
    'freezer',
    'washing machine',
    'washer',
    'dryer',
    'dishwasher',
    'oven',
    'stove',
    'microwave',
    'tv',
    'television',
    'monitor',  # Large monitors
    'furniture',
    'couch',
    'sofa',
    'bed',
    'mattress',
    'table',
    'desk',
    'chair',
    'wardrobe',
    'cabinet',
    'treadmill',
    'exercise bike',
    'air conditioner',
    'ac unit',
    'heater',
    'geyser',
    'water heater',
    'lawnmower',
    'generator',
    'compressor',
    'toolbox',
    'safe'
]


def is_courier_eligible(product_info: dict) -> dict:
    """
    Check if a product can be couriered

    Args:
        product_info: Dict with 'category', 'brand', 'model', etc.

    Returns:
        Dict with 'eligible' (bool), 'reason' (str), 'category_matched' (str)
    """
    category = product_info.get('category', '').lower()
    brand = product_info.get('brand', '').lower()
    model = product_info.get('model', '').lower()

    # Combine all text for checking
    full_text = f"{category} {brand} {model}".lower()

    # Check if explicitly non-courier
    for non_courier_item in NON_COURIER_CATEGORIES:
        if non_courier_item in full_text:
            return {
                'eligible': False,
                'reason': f"Unfortunately, we currently only accept items that can be couriered. We're unable to process large items like {non_courier_item}s at this time. Please check back in the future as we expand our services!",
                'category_matched': non_courier_item
            }

    # Check if explicitly courier-eligible
    for eligible_item in COURIER_ELIGIBLE_CATEGORIES:
        if eligible_item in full_text:
            return {
                'eligible': True,
                'reason': 'Item can be couriered',
                'category_matched': eligible_item
            }

    # Check for size indicators in the text
    large_indicators = ['large screen', 'inches', '"', 'inch', '55', '65', '75', '85']
    for indicator in large_indicators:
        if indicator in full_text:
            # Check if it's a large TV/monitor
            if 'tv' in full_text or 'television' in full_text or ('monitor' in full_text and any(size in full_text for size in ['32', '40', '50', '55', '65'])):
                return {
                    'eligible': False,
                    'reason': "Unfortunately, we currently only accept items that can be couriered. Large TVs and monitors cannot be safely couriered at this time.",
                    'category_matched': 'large screen'
                }

    # Default: assume courier-eligible for electronics
    # (Most electronics that aren't explicitly large can be couriered)
    return {
        'eligible': True,
        'reason': 'Item appears to be courier-eligible',
        'category_matched': 'general electronics'
    }


def get_courier_rejection_message(product_info: dict) -> str:
    """
    Get a friendly rejection message for non-courier items

    Args:
        product_info: Dict with product information

    Returns:
        str: Rejection message
    """
    result = is_courier_eligible(product_info)

    if result['eligible']:
        return None

    return result['reason']


def get_business_model_options(product_info: dict) -> dict:
    """
    Determine which business models are available for this product

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
    full_text = f"{category} {brand} {model}".lower()

    # Check if it's electronics
    is_electronics = False
    for electronics_item in ELECTRONICS_CATEGORIES:
        if electronics_item in full_text:
            is_electronics = True
            break

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
