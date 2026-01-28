"""
Intelligent Repair Cost Service
Uses Perplexity API to research real-time repair costs in South Africa
"""

import os
import requests
from config import Config


class IntelligentRepairCostService:
    """
    Research actual repair costs using Perplexity API
    Provides transparent breakdown for users
    """

    def __init__(self):
        self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')
        self.perplexity_url = "https://api.perplexity.ai/chat/completions"

    def research_all_damages(self, product_info, damage_details):
        """
        Research repair costs for all reported damages

        Args:
            product_info: Dict with brand, model, category
            damage_details: List of damage issues selected by user

        Returns:
            Dict with:
                - breakdown: Dict of {damage: cost_info}
                - total_repair_cost: Total cost in ZAR
                - explanation: User-friendly formatted message
                - confidence: Overall confidence score
        """

        if not damage_details or self._no_damage(damage_details):
            return {
                'breakdown': {},
                'total_repair_cost': 0,
                'explanation': '',
                'confidence': 1.0
            }

        # Handle string input (convert to list)
        if isinstance(damage_details, str):
            damage_details = [damage_details]

        print(f"\n{'='*60}")
        print(f"INTELLIGENT REPAIR COST RESEARCH")
        print(f"Product: {product_info.get('brand')} {product_info.get('model')}")
        print(f"Damages: {damage_details}")
        print(f"{'='*60}\n")

        breakdown = {}
        total_cost = 0

        for damage in damage_details:
            # Skip "None - Everything works perfectly"
            if 'none' in damage.lower() and ('works' in damage.lower() or 'perfect' in damage.lower()):
                continue

            print(f"Researching: {damage}")

            # Research this specific damage
            cost_info = self._research_single_damage(product_info, damage)

            if cost_info['estimated_cost'] > 0:
                breakdown[damage] = cost_info
                total_cost += cost_info['estimated_cost']

                print(f"  → Found: R{cost_info['estimated_cost']:,.0f} - {cost_info['details']}")

        explanation = self._format_breakdown_message(breakdown, total_cost)

        print(f"\nTotal Repair Costs: R{total_cost:,.0f}")
        print(f"{'='*60}\n")

        return {
            'breakdown': breakdown,
            'total_repair_cost': total_cost,
            'explanation': explanation,
            'confidence': self._calculate_confidence(breakdown)
        }

    def _no_damage(self, damage_details):
        """Check if no actual damage reported"""
        if not damage_details:
            return True

        # Handle string input (convert to list)
        if isinstance(damage_details, str):
            damage_details = [damage_details]

        for damage in damage_details:
            damage_str = str(damage).lower()
            # Check for "no damage" indicators
            if any(phrase in damage_str for phrase in ['no issues', 'no damage', 'pristine', 'perfect condition', 'everything works']):
                continue
            # If we find actual damage, return False
            if damage_str and damage_str not in ['none', 'no']:
                return False

        return True

    def _research_single_damage(self, product_info, damage_type):
        """
        Research repair cost for a single damage type using Perplexity

        Args:
            product_info: Product details
            damage_type: Specific damage (e.g., "Screen cracked or scratched")

        Returns:
            Dict with estimated_cost, source, details, confidence
        """

        brand = product_info.get('brand', '')
        model = product_info.get('model', '')
        category = product_info.get('category', '')

        # Build search query for South African repair costs
        query = self._build_repair_query(brand, model, category, damage_type)

        try:
            # Use Perplexity to research repair costs
            result = self._query_perplexity(query)

            # Extract repair cost from Perplexity response
            cost_info = self._extract_repair_cost(result, damage_type, brand, category)

            return cost_info

        except Exception as e:
            print(f"Error researching repair cost: {e}")
            # Fallback to reasonable estimate
            return self._fallback_estimate(damage_type, brand, category)

    def _build_repair_query(self, brand, model, category, damage_type):
        """
        Build an effective search query for repair costs

        Examples:
        - "iPhone 11 screen replacement cost South Africa 2026"
        - "Samsung Galaxy S21 battery replacement price Johannesburg Cape Town"
        - "MacBook Pro M1 keyboard repair cost South Africa"
        """

        # Simplify damage type for search
        damage_simplified = self._simplify_damage_type(damage_type)

        # Build query with South African context
        query = f"{brand} {model} {damage_simplified} repair cost South Africa 2026"

        # Add major cities for more local results
        query += " Johannesburg Cape Town Durban Pretoria"

        return query

    def _simplify_damage_type(self, damage_type):
        """
        Simplify damage description for better search results

        "Screen cracked or scratched" → "screen replacement"
        "Battery health below 80%" → "battery replacement"
        """

        damage_lower = damage_type.lower()

        if 'screen' in damage_lower:
            if 'crack' in damage_lower:
                return 'screen replacement'
            else:
                return 'screen repair'

        elif 'battery' in damage_lower:
            return 'battery replacement'

        elif 'back glass' in damage_lower:
            return 'back glass replacement'

        elif 'camera' in damage_lower:
            return 'camera repair'

        elif 'keyboard' in damage_lower:
            return 'keyboard replacement'

        elif 'trackpad' in damage_lower:
            return 'trackpad repair'

        elif 'water damage' in damage_lower:
            return 'water damage repair'

        elif 'ports' in damage_lower or 'buttons' in damage_lower:
            return 'port button repair'

        elif 'hinge' in damage_lower:
            return 'hinge repair replacement'

        else:
            return damage_type  # Use as-is

    def _query_perplexity(self, query):
        """
        Query Perplexity API for repair cost information

        Args:
            query: Search query string

        Returns:
            API response with repair cost information
        """

        headers = {
            "Authorization": f"Bearer {self.perplexity_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "sonar-pro",  # Latest Perplexity model
            "messages": [
                {
                    "role": "system",
                    "content": """You are a repair cost research expert for South Africa.

When asked about repair costs:
1. Research current 2026 prices from South African repair shops
2. Provide prices in South African Rand (ZAR)
3. Give a realistic range (min-max)
4. Cite specific sources (iStore, iFix, repair shops, etc.)
5. Consider labor + parts

Format your response as:
"Typical cost: R[amount] (Range: R[min] - R[max])
Source: [shop/website names]
Details: [brief explanation]"
"""
                },
                {
                    "role": "user",
                    "content": f"What is the current {query}? Provide specific South African repair shop prices in Rand."
                }
            ],
            "temperature": 0.2,  # Low temperature for factual responses
            "max_tokens": 500
        }

        response = requests.post(
            self.perplexity_url,
            json=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Perplexity API error: {response.status_code} - {response.text}")

    def _extract_repair_cost(self, perplexity_result, damage_type, brand, category):
        """
        Extract repair cost from Perplexity API response

        Args:
            perplexity_result: Response from Perplexity
            damage_type: Original damage description
            brand: Product brand
            category: Product category

        Returns:
            Dict with estimated_cost, source, details, confidence
        """

        try:
            # Get the response text
            content = perplexity_result['choices'][0]['message']['content']

            print(f"  Perplexity response: {content[:200]}...")

            # Extract cost using simple parsing
            # Look for patterns like "R1,200" or "R 1200" or "R1200"
            import re

            # Find all ZAR amounts
            amounts = re.findall(r'R\s*([0-9,]+)', content)

            if amounts:
                # Parse amounts and get average/median
                parsed_amounts = []
                for amt in amounts:
                    try:
                        cleaned = amt.replace(',', '')
                        value = int(cleaned)
                        # Filter out unrealistic values
                        if 100 <= value <= 50000:
                            parsed_amounts.append(value)
                    except:
                        continue

                if parsed_amounts:
                    # Use median as estimate
                    import statistics
                    estimated_cost = statistics.median(parsed_amounts)

                    # Extract source and details from content
                    source = self._extract_source(content)
                    details = self._extract_details(content, damage_type)

                    return {
                        'estimated_cost': estimated_cost,
                        'source': source,
                        'details': details,
                        'confidence': 0.85,  # High confidence from Perplexity
                        'research_used': True
                    }

            # If no amounts found, use fallback
            return self._fallback_estimate(damage_type, brand, category)

        except Exception as e:
            print(f"  Error extracting cost: {e}")
            return self._fallback_estimate(damage_type, brand, category)

    def _extract_source(self, content):
        """Extract source information from Perplexity response"""

        content_lower = content.lower()

        sources = []
        if 'istore' in content_lower:
            sources.append('iStore')
        if 'ifix' in content_lower:
            sources.append('iFix')
        if 'repair' in content_lower and 'shop' in content_lower:
            sources.append('local repair shops')

        if sources:
            return f"Based on {', '.join(sources)}"
        else:
            return "Based on South African repair market research"

    def _extract_details(self, content, damage_type):
        """Extract relevant details from Perplexity response"""

        # Keep it short and relevant
        if 'labor' in content.lower():
            return f"Typical {damage_type.lower()} cost including labor"
        elif 'parts' in content.lower():
            return f"Typical {damage_type.lower()} including parts"
        else:
            return f"Current market rate for {damage_type.lower()}"

    def _fallback_estimate(self, damage_type, brand, category):
        """
        Provide reasonable fallback estimate when Perplexity fails

        Uses static estimates based on damage type and product category
        """

        damage_lower = damage_type.lower()
        brand_lower = brand.lower() if brand else ''
        category_lower = category.lower() if category else ''

        # iPhone/Apple premium pricing
        is_apple = 'apple' in brand_lower or 'iphone' in brand_lower or 'macbook' in brand_lower

        if 'screen' in damage_lower and 'crack' in damage_lower:
            if is_apple:
                if 'phone' in category_lower:
                    cost = 1500  # iPhone screen
                else:
                    cost = 4000  # MacBook screen
            else:
                if 'phone' in category_lower:
                    cost = 1000  # Android screen
                elif 'laptop' in category_lower:
                    cost = 2500  # Generic laptop screen
                else:
                    cost = 1200

        elif 'battery' in damage_lower:
            if is_apple:
                if 'phone' in category_lower:
                    cost = 800  # iPhone battery
                else:
                    cost = 1500  # MacBook battery
            else:
                if 'phone' in category_lower:
                    cost = 600
                elif 'laptop' in category_lower:
                    cost = 1200
                else:
                    cost = 700

        elif 'back glass' in damage_lower:
            cost = 800 if is_apple else 500

        elif 'camera' in damage_lower:
            cost = 1000 if is_apple else 700

        elif 'keyboard' in damage_lower:
            cost = 2000 if is_apple else 1500

        elif 'water damage' in damage_lower:
            cost = 2000  # High risk repair

        elif 'port' in damage_lower or 'button' in damage_lower:
            cost = 500

        elif 'hinge' in damage_lower:
            cost = 1500

        else:
            cost = 800  # Generic repair estimate

        return {
            'estimated_cost': cost,
            'source': 'Industry standard estimates',
            'details': f'Typical cost for {damage_type.lower()}',
            'confidence': 0.7,  # Lower confidence for fallback
            'research_used': False
        }

    def _format_breakdown_message(self, breakdown, total_cost):
        """
        Format user-friendly repair cost breakdown

        Example output:
        "**Repair Costs Breakdown:**
        • Screen cracked: R1,200 (Based on iStore - typical screen replacement including labor)
        • Battery degraded: R650 (Based on local repair shops - typical battery replacement including parts)

        **Total Deductions: R1,850**

        These are current market rates from South African repair shops. We deduct these costs
        to ensure we can properly refurbish your item before resale."
        """

        if not breakdown or total_cost == 0:
            return ""

        lines = ["\n**Why is the offer adjusted?**\n"]
        lines.append("**Repair Costs Breakdown:**")

        for damage, info in breakdown.items():
            cost = info['estimated_cost']
            source = info['source']
            details = info['details']

            lines.append(f"• {damage}: **R{cost:,.0f}** ({source} - {details})")

        lines.append(f"\n**Total Deductions: R{total_cost:,.0f}**\n")

        lines.append("_These are current market rates from South African repair shops. "
                    "We deduct these costs to ensure we can properly refurbish your item before resale._\n")

        return "\n".join(lines)

    def _calculate_confidence(self, breakdown):
        """Calculate overall confidence based on research results"""

        if not breakdown:
            return 1.0  # No repairs needed = high confidence

        confidences = [info['confidence'] for info in breakdown.values()]

        if confidences:
            import statistics
            return statistics.mean(confidences)
        else:
            return 0.7
