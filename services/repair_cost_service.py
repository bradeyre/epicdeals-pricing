from services.ai_service import AIService
import anthropic
from config import Config


class RepairCostService:
    """
    Estimates repair costs for damaged items using AI research
    """

    def __init__(self):
        self.ai_service = AIService()
        self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)

    def estimate_repair_costs(self, product_info, damage_info):
        """
        Estimate repair costs for damaged items

        Args:
            product_info: Dict with product details (category, brand, model, etc.)
            damage_info: Dict with damage details (screen, body, battery, functional, notes)

        Returns:
            Dict with:
                - total_repair_cost: Estimated total in ZAR
                - breakdown: Dict of individual repair costs
                - confidence: How confident we are in the estimate
                - notes: Any additional information
        """

        # If no damage reported, no repair costs
        if not damage_info or self._no_damage(damage_info):
            return {
                'total_repair_cost': 0,
                'breakdown': {},
                'confidence': 1.0,
                'notes': 'No damage reported'
            }

        # Use AI to research and estimate repair costs
        repair_estimate = self._research_repair_costs(product_info, damage_info)

        return repair_estimate

    def _no_damage(self, damage_info):
        """Check if there's actually no damage"""
        if not damage_info:
            return True

        # Check if all damage fields are "none" or "good"
        no_damage_values = ['none', 'good', 'fully_working', None, '']

        for key, value in damage_info.items():
            if key == 'notes':
                continue
            if value not in no_damage_values:
                return False

        return True

    def _research_repair_costs(self, product_info, damage_info):
        """Use AI to research repair costs online"""

        prompt = f"""You are a repair cost estimation expert in South Africa.

PRODUCT INFORMATION:
{product_info}

DAMAGE INFORMATION:
{damage_info}

Your task:
1. Research typical repair costs for these specific damages in South Africa (ZAR)
2. Consider brand-specific costs (Apple vs generic, etc.)
3. Factor in labor costs typical in SA
4. Provide conservative (higher) estimates to be safe

Common SA repair costs reference:
- iPhone screen replacement: R800-R2500 (depends on model)
- Android screen replacement: R500-R1800
- Battery replacement iPhone: R600-R1200
- Battery replacement Android: R400-R800
- MacBook screen: R3000-R8000
- Laptop screen generic: R1500-R4000
- Water damage repairs: R800-R3000
- Back glass iPhone: R600-R1500

Respond in JSON format:
{{
    "breakdown": {{
        "screen": 0,
        "battery": 0,
        "body": 0,
        "water_damage": 0,
        "functionality": 0,
        "other": 0
    }},
    "total_repair_cost": 0,
    "confidence": 0.0-1.0,
    "notes": "Explanation of estimates and sources",
    "recommendation": "repair|replace - if repair cost exceeds 50% of value"
}}

Be realistic and conservative with estimates. If unsure, estimate higher.
"""

        try:
            response = self.client.messages.create(
                model=Config.ANTHROPIC_MODEL,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            result = json.loads(response.content[0].text)

            # Ensure total is calculated
            if 'breakdown' in result:
                total = sum(result['breakdown'].values())
                result['total_repair_cost'] = total

            return result

        except Exception as e:
            print(f"Error estimating repair costs: {e}")
            # Return conservative fallback estimate
            return self._fallback_estimate(product_info, damage_info)

    def _fallback_estimate(self, product_info, damage_info):
        """Fallback repair cost estimates if AI fails"""

        total = 0
        breakdown = {}

        # Screen damage
        if damage_info.get('screen') in ['cracked', 'broken']:
            category = product_info.get('category', '').lower()
            if 'iphone' in str(product_info.get('brand', '')).lower():
                breakdown['screen'] = 1500
            elif 'phone' in category or 'mobile' in category:
                breakdown['screen'] = 1000
            elif 'laptop' in category:
                breakdown['screen'] = 3000
            elif 'tablet' in category:
                breakdown['screen'] = 1200
            else:
                breakdown['screen'] = 1000

        # Battery issues
        if damage_info.get('battery') in ['degraded', 'dead']:
            if 'iphone' in str(product_info.get('brand', '')).lower():
                breakdown['battery'] = 900
            elif 'laptop' in product_info.get('category', '').lower():
                breakdown['battery'] = 1500
            else:
                breakdown['battery'] = 600

        # Body damage
        if damage_info.get('body') in ['dents', 'cracks']:
            breakdown['body'] = 500

        # Functional issues
        if damage_info.get('functional') in ['some_issues', 'not_working']:
            breakdown['functionality'] = 1000

        total = sum(breakdown.values())

        return {
            'total_repair_cost': total,
            'breakdown': breakdown,
            'confidence': 0.6,
            'notes': 'Fallback estimate based on typical SA repair costs'
        }
