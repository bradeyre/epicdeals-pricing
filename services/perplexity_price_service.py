import os
import requests
import re
from typing import List, Dict, Optional
from services.depreciation_service import DepreciationService


class PerplexityPriceService:
    """
    Uses Perplexity AI to search for real-time pricing data
    More accurate than web scraping for South African second-hand markets
    """

    def __init__(self):
        self.api_key = os.getenv('PERPLEXITY_API_KEY')
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.depreciation_service = DepreciationService()

    def search_prices(self, product_info: Dict) -> Dict:
        """
        Use Perplexity to search for current market prices

        Args:
            product_info: Dict with brand, model, condition, etc.

        Returns:
            Dict with prices_found, market_value, confidence, sources
        """
        if not self.api_key:
            print("Perplexity API key not found - skipping AI search")
            return {
                'prices_found': [],
                'market_value': None,
                'confidence': 0,
                'sources': [],
                'ai_used': False
            }

        # Build search query for second-hand prices
        query = self._build_search_query(product_info)
        print(f"  Using Perplexity AI to search: {query}")

        try:
            # Call Perplexity API
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar-pro",  # Deep retrieval with follow-ups
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a South African SECOND-HAND market price expert. Search for current USED/SECOND-HAND prices ONLY and return ONLY a JSON object with this exact format: {\"prices\": [price1, price2, ...], \"sources\": [\"source1\", \"source2\", ...]}. Prices must be in ZAR (South African Rand). CRITICAL: Only include SECOND-HAND/USED prices from classifieds and resale sites like gumtree.co.za, facebook marketplace, carbonite.co.za, bobshop.co.za. Do NOT include new retail prices from takealot.com, incredible.co.za, makro.co.za or any other new-product retailer. We need what people are actually selling used items for, not what they cost new."
                        },
                        {
                            "role": "user",
                            "content": query
                        }
                    ],
                    "temperature": 0.2,
                    "max_tokens": 1000
                },
                timeout=15
            )

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']

                # Parse the response
                prices, sources = self._parse_perplexity_response(content)

                if prices:
                    market_value = self._calculate_market_value(prices)
                    print(f"  Perplexity found {len(prices)} prices: {prices}")

                    return {
                        'prices_found': prices,
                        'market_value': market_value,
                        'confidence': min(0.7 + (len(prices) * 0.05), 0.95),  # Higher confidence with Perplexity
                        'sources': sources,
                        'ai_used': True,
                        'method': 'Perplexity AI - Second-hand',
                        'is_new_price_estimate': False
                    }
                else:
                    # No second-hand prices found, try new prices
                    print(f"  No second-hand prices found, trying new prices...")
                    return self._search_new_prices_fallback(product_info)

        except Exception as e:
            print(f"  Perplexity search error: {e}")
            # Try new prices as fallback
            return self._search_new_prices_fallback(product_info)

        return {
            'prices_found': [],
            'market_value': None,
            'confidence': 0,
            'sources': [],
            'ai_used': False,
            'is_new_price_estimate': False
        }

    def _search_new_prices_fallback(self, product_info: Dict) -> Dict:
        """
        Fallback: Search for new product prices and estimate second-hand value
        """
        if not self.api_key:
            return {
                'prices_found': [],
                'market_value': None,
                'confidence': 0,
                'sources': [],
                'ai_used': False,
                'is_new_price_estimate': False
            }

        brand = product_info.get('brand', '')
        model = product_info.get('model', '')
        storage = product_info.get('storage', '')
        category = product_info.get('category', '').lower()

        # Build query for NEW prices
        query = f"Find current NEW retail prices in South Africa for {brand} {model}"
        if storage:
            query += f" {storage}"
        query += ". Search takealot.com, incredible.co.za, game.co.za, makro.co.za. Return actual NEW prices in ZAR."

        print(f"  Searching NEW prices as fallback: {query}")

        try:
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar-pro",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a South African retail price expert. Search for current NEW retail prices and return ONLY a JSON object: {\"prices\": [price1, price2, ...], \"sources\": [\"source1\", \"source2\", ...]}. Prices must be in ZAR."
                        },
                        {
                            "role": "user",
                            "content": query
                        }
                    ],
                    "temperature": 0.2,
                    "max_tokens": 1000
                },
                timeout=15
            )

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                new_prices, sources = self._parse_perplexity_response(content)

                if new_prices:
                    median_new_price = self._calculate_market_value(new_prices)

                    # Estimate second-hand value based on age, category, and condition
                    estimated_value, depreciation_info = self._estimate_secondhand_from_new(
                        median_new_price,
                        category,
                        product_info.get('condition', 'good'),
                        product_info
                    )

                    print(f"  Found NEW price: R{median_new_price:,.0f}")
                    print(f"  Estimated second-hand value: R{estimated_value:,.0f}")
                    print(f"  Depreciation: {depreciation_info['explanation']}")

                    return {
                        'prices_found': [estimated_value],
                        'market_value': estimated_value,
                        'confidence': 0.6,  # Lower confidence for estimates
                        'sources': sources,
                        'ai_used': True,
                        'method': 'Perplexity AI - Estimated from new price',
                        'is_new_price_estimate': True,
                        'new_price': median_new_price,
                        'depreciation_info': depreciation_info
                    }

        except Exception as e:
            print(f"  New price search error: {e}")

        return {
            'prices_found': [],
            'market_value': None,
            'confidence': 0,
            'sources': [],
            'ai_used': False,
            'is_new_price_estimate': False
        }

    def _estimate_secondhand_from_new(self, new_price: float, category: str, condition: str, product_info: Dict = None) -> tuple:
        """
        Estimate second-hand value from new retail price using age-based depreciation curves

        Args:
            new_price: New retail price
            category: Item category
            condition: Physical condition
            product_info: Full product information (for extracting age/brand/model)

        Returns:
            Tuple of (estimated_value, depreciation_info_dict)
        """
        if not product_info:
            product_info = {}

        brand = product_info.get('brand', '')
        model = product_info.get('model', '')
        year = product_info.get('specifications', {}).get('year')

        # Try to determine age
        age_years = None

        # First, check if we have explicit year information
        if year:
            try:
                year_int = int(year)
                age_years = self.depreciation_service.calculate_age_in_years(year_int)
            except (ValueError, TypeError):
                pass

        # If no explicit year, try to extract from model name
        if age_years is None:
            estimated_year = self.depreciation_service.estimate_age_from_model(brand, model)
            if estimated_year:
                age_years = self.depreciation_service.calculate_age_in_years(estimated_year)

        # If still no age, use conservative default based on category
        if age_years is None:
            # Default to 2-3 years for most items (mid-life estimate)
            age_years = 2.5
            print(f"  No age found - using default: {age_years} years")

        print(f"  Calculating depreciation for {age_years:.1f} year old {category}")

        # Get depreciation calculation with full breakdown
        depreciation_info = self.depreciation_service.get_depreciation_info(
            category=category,
            age_years=age_years,
            new_price=new_price,
            condition=condition,
            brand=brand,
            model=model
        )

        return depreciation_info['final_value'], depreciation_info

    def _build_search_query(self, product_info: Dict) -> str:
        """Build optimized search query for Perplexity"""
        brand = product_info.get('brand', '')
        model = product_info.get('model', '')
        condition = product_info.get('condition', '')
        storage = product_info.get('storage', '')
        category = product_info.get('category', '')

        query = f"Find current SECOND-HAND / USED prices in South Africa for {brand} {model}"

        if storage:
            query += f" {storage}"

        if condition and 'good' in condition.lower():
            query += " in good condition"
        elif condition and 'excellent' in condition.lower():
            query += " in excellent condition"

        query += ". Search gumtree.co.za, facebook marketplace, carbonite.co.za, bobshop.co.za for USED listings only. Do NOT include new retail prices from takealot or other retailers. Return actual second-hand asking prices in ZAR."

        return query

    def _parse_perplexity_response(self, content: str) -> tuple[List[float], List[str]]:
        """Parse Perplexity response to extract prices and sources"""
        prices = []
        sources = []

        try:
            # Try to parse as JSON first
            import json
            # Extract JSON from response (might have markdown formatting)
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                prices = [float(p) for p in data.get('prices', []) if p]
                sources = data.get('sources', [])
        except:
            # Fallback: extract prices using regex
            price_matches = re.findall(r'R[\s]?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', content)
            for match in price_matches:
                try:
                    price = float(match.replace(',', ''))
                    if 1000 <= price <= 50000:  # Reasonable range
                        prices.append(price)
                except:
                    continue

            # Extract source URLs
            source_matches = re.findall(r'(epicdeals\.co\.za|bobshop\.co\.za|takealot\.com|gumtree\.co\.za)', content)
            sources = list(set(source_matches))

        return prices[:10], sources[:5]  # Limit results

    def _calculate_market_value(self, prices: List[float]) -> float:
        """Calculate median market value from prices, filtering outliers"""
        if not prices:
            return None

        sorted_prices = sorted(prices)

        # If we have enough data points, remove extreme outliers
        if len(sorted_prices) >= 3:
            median = sorted_prices[len(sorted_prices) // 2]
            # Remove prices that are more than 2x or less than 0.3x the median
            # This helps filter out accidentally-included new retail prices
            filtered = [p for p in sorted_prices if 0.3 * median <= p <= 2.0 * median]
            if filtered:
                sorted_prices = sorted(filtered)

        n = len(sorted_prices)

        if n % 2 == 0:
            return (sorted_prices[n//2 - 1] + sorted_prices[n//2]) / 2
        else:
            return sorted_prices[n//2]
