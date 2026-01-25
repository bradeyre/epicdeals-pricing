from scrapers.epicdeals_scraper import EpicDealsScraper
from scrapers.competitor_scraper import CompetitorScraper
# from scrapers.facebook_scraper import FacebookMarketplaceScraper  # Disabled for production (requires Chrome)
from scrapers.ebay_scraper import EbayScraper
from scrapers.gumtree_scraper import GumtreeScraper
from utils.currency_converter import CurrencyConverter
from services.ai_service import AIService
from services.perplexity_price_service import PerplexityPriceService
import statistics


class PriceResearchService:
    """
    Orchestrates price research across multiple sources
    """

    def __init__(self):
        self.epicdeals_scraper = EpicDealsScraper()
        self.competitor_scraper = CompetitorScraper()
        # self.facebook_scraper = FacebookMarketplaceScraper()  # Disabled for production
        self.ebay_scraper = EbayScraper()
        self.gumtree_scraper = GumtreeScraper()
        self.currency_converter = CurrencyConverter()
        self.ai_service = AIService()
        self.perplexity_service = PerplexityPriceService()

    def research_prices(self, product_info):
        """
        Main method to research prices across all sources using layered approach

        Args:
            product_info: Dict with product details

        Returns:
            Dict with:
                - prices_found: List of all prices
                - market_value: Estimated market value in ZAR
                - confidence: Confidence score
                - sources_checked: List of sources
                - price_breakdown: Detailed breakdown
                - needs_user_estimate: True if no pricing data found
        """

        print("\n=== Starting Layered Price Research ===")
        print(f"Product Info: {product_info}")

        category = product_info.get('category', '').lower()
        all_prices = []
        sources_checked = []
        price_breakdown = {}

        # LAYER 1: Try Perplexity AI first (most accurate, real-time)
        print("\n[Layer 1] Trying Perplexity AI for real-time market data...")
        perplexity_result = self.perplexity_service.search_prices(product_info)

        if perplexity_result['ai_used'] and perplexity_result['prices_found']:
            all_prices.extend(perplexity_result['prices_found'])
            sources_checked.extend(perplexity_result['sources'])
            price_breakdown['Perplexity AI'] = [
                {'price': p, 'source': 'Perplexity AI', 'title': f"{product_info.get('brand', '')} {product_info.get('model', '')}"}
                for p in perplexity_result['prices_found']
            ]
            print(f"  ✓ Perplexity found {len(perplexity_result['prices_found'])} prices")

        # If Perplexity gave us good data (3+ prices), we can skip scraping
        if len(all_prices) >= 3:
            print(f"\n✓ Found {len(all_prices)} prices from Perplexity - skipping web scraping")
            market_value = self._calculate_market_value(all_prices)
            confidence = min(0.75 + (len(all_prices) * 0.05), 0.95)

            return {
                'prices_found': all_prices,
                'market_value': market_value,
                'confidence': confidence,
                'sources_checked': sources_checked,
                'price_breakdown': price_breakdown,
                'needs_user_estimate': False
            }

        # LAYER 2: Web scraping fallback
        print("\n[Layer 2] Perplexity didn't find enough data - trying web scraping...")

        # Determine which sources to check based on category
        sources_to_check = self._get_sources_for_category(category)
        print(f"Sources to check for category '{category}': {sources_to_check}")

        # Generate search queries using AI
        search_queries = self.ai_service.generate_search_queries(product_info)
        print(f"Search queries: {search_queries}")

        # REAL SCRAPING with parallel execution and timeout
        import concurrent.futures
        import time

        def scrape_source_with_timeout(source_name):
            """Scrape a single source with timeout"""
            try:
                start_time = time.time()
                results = []

                if source_name == 'EpicDeals':
                    results = self.epicdeals_scraper.search_product(search_queries)
                elif source_name == 'Facebook Marketplace':
                    # Disabled for production (requires Chrome/Selenium)
                    results = []
                elif source_name == 'Gumtree':
                    results = self.gumtree_scraper.search_product(search_queries)
                elif source_name in ['BobShop', 'Takealot', 'BidOrBuy', 'WeFix', 'Swopp', 'iStore']:
                    results = self.competitor_scraper.search_all_competitors(search_queries)

                elapsed = time.time() - start_time
                print(f"{source_name}: Found {len(results)} results in {elapsed:.2f}s")
                return source_name, results
            except Exception as e:
                print(f"{source_name}: Error - {str(e)}")
                return source_name, []

        # Use ThreadPoolExecutor for parallel scraping with 12s total timeout
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_source = {
                executor.submit(scrape_source_with_timeout, source): source
                for source in sources_to_check
            }

            try:
                for future in concurrent.futures.as_completed(future_to_source, timeout=12):
                    try:
                        source_name, results = future.result(timeout=1)

                        if results:
                            sources_checked.append(source_name)
                            prices_from_source = []

                            for item in results[:5]:  # Top 5 results per source
                                price = item.get('price')
                                if price and price > 0:
                                    all_prices.append(price)
                                    prices_from_source.append(item)

                            if prices_from_source:
                                price_breakdown[source_name] = prices_from_source
                                print(f"Found {len(prices_from_source)} prices on {source_name}")

                    except Exception as e:
                        print(f"Error processing source result: {e}")
                        continue
            except concurrent.futures.TimeoutError:
                print("Scraping timeout - proceeding with results found so far")

        # If no prices found, flag for user estimate
        if not all_prices:
            print("No pricing data found - will request user estimate")
            return {
                'prices_found': [],
                'market_value': None,
                'confidence': 0,
                'sources_checked': sources_checked,
                'price_breakdown': price_breakdown,
                'needs_user_estimate': True
            }

        # Calculate market value from found prices
        market_value = self._calculate_market_value(all_prices)

        # Calculate confidence based on number of sources
        confidence = min(0.5 + (len(sources_checked) * 0.2), 0.95)

        print(f"\n=== Price Research Complete ===")
        print(f"Prices found: {all_prices}")
        print(f"Market value: R{market_value}")
        print(f"Confidence: {confidence}")

        return {
            'prices_found': all_prices,
            'market_value': market_value,
            'confidence': confidence,
            'sources_checked': sources_checked,
            'price_breakdown': price_breakdown,
            'needs_user_estimate': False
        }

        # ORIGINAL CODE (commented out for demo):
        # Generate search queries using AI
        search_queries = self.ai_service.generate_search_queries(product_info)

        all_prices = []
        sources_checked = []
        price_breakdown = {
            'epicdeals': [],
            'competitors': [],
            'facebook': [],
            'ebay': [],
            'ebay_sold': []
        }

        # 1. Check EpicDeals.co.za
        print("Checking EpicDeals.co.za...")
        try:
            epicdeals_results = self.epicdeals_scraper.search_product(search_queries)
            if epicdeals_results:
                sources_checked.append('EpicDeals')
                price_breakdown['epicdeals'] = epicdeals_results
                all_prices.extend([r['price'] for r in epicdeals_results if r.get('price')])
        except Exception as e:
            print(f"EpicDeals search failed: {e}")

        # 2. Check Competitors
        print("Checking competitors...")
        try:
            competitor_results = self.competitor_scraper.search_all_competitors(search_queries)
            if competitor_results:
                sources_checked.append('Competitors')
                price_breakdown['competitors'] = competitor_results
                all_prices.extend([r['price'] for r in competitor_results if r.get('price')])
        except Exception as e:
            print(f"Competitor search failed: {e}")

        # 3. Check Facebook Marketplace (optional, can be slow)
        print("Checking Facebook Marketplace...")
        try:
            # Use simple method first (faster but less reliable)
            fb_results = self.facebook_scraper.search_product_simple(search_queries)
            if not fb_results:
                # Fallback to Selenium if needed and no results from simple
                fb_results = self.facebook_scraper.search_product(search_queries)

            if fb_results:
                sources_checked.append('Facebook')
                price_breakdown['facebook'] = fb_results
                all_prices.extend([r['price'] for r in fb_results if r.get('price')])
        except Exception as e:
            print(f"Facebook search failed: {e}")

        # 4. Check eBay (with USD to ZAR conversion)
        print("Checking eBay...")
        try:
            ebay_results = self.ebay_scraper.search_product(search_queries)
            ebay_sold_results = self.ebay_scraper.search_sold_listings(search_queries)

            usd_zar_rate = self.currency_converter.get_usd_to_zar_rate()

            # Convert eBay prices to ZAR
            if ebay_results:
                sources_checked.append('eBay')
                for result in ebay_results:
                    if result.get('price_usd'):
                        result['price'] = result['price_usd'] * usd_zar_rate
                        result['exchange_rate'] = usd_zar_rate
                price_breakdown['ebay'] = ebay_results
                all_prices.extend([r['price'] for r in ebay_results if r.get('price')])

            if ebay_sold_results:
                sources_checked.append('eBay Sold')
                for result in ebay_sold_results:
                    if result.get('price_usd'):
                        result['price'] = result['price_usd'] * usd_zar_rate
                        result['exchange_rate'] = usd_zar_rate
                price_breakdown['ebay_sold'] = ebay_sold_results
                all_prices.extend([r['price'] for r in ebay_sold_results if r.get('price')])

        except Exception as e:
            print(f"eBay search failed: {e}")

        # Calculate market value
        market_value = self._calculate_market_value(all_prices)

        # Assess confidence using AI
        confidence_data = {
            'prices_found': all_prices,
            'sources': sources_checked,
            'price_breakdown': price_breakdown
        }
        confidence, assessment = self.ai_service.assess_confidence(confidence_data, product_info)

        return {
            'prices_found': all_prices,
            'market_value': market_value,
            'confidence': confidence,
            'sources_checked': sources_checked,
            'price_breakdown': price_breakdown,
            'assessment': assessment,
            'total_listings': len(all_prices)
        }

    def _get_sources_for_category(self, category):
        """
        Determine which sources to check based on product category
        Returns list of source names in priority order
        """
        category = category.lower()

        # Category-specific source mapping
        if category in ['phone', 'smartphone', 'tablet', 'laptop', 'computer', 'macbook']:
            return ['EpicDeals', 'Gumtree', 'WeFix', 'Facebook Marketplace']
        elif category in ['tv', 'television', 'appliance', 'washing machine', 'fridge', 'console', 'playstation', 'xbox']:
            return ['Gumtree', 'WeFix', 'Swopp', 'Facebook Marketplace']
        elif category in ['camera', 'lens', 'photography']:
            return ['Gumtree', 'Facebook Marketplace', 'Swopp', 'EpicDeals']
        elif category in ['watch', 'smartwatch']:
            return ['EpicDeals', 'Gumtree', 'iStore', 'Facebook Marketplace']
        else:
            # Default sources for unknown categories
            return ['Gumtree', 'Facebook Marketplace', 'WeFix', 'Swopp']

    def _generate_mock_price(self, product_info):
        """
        Generate realistic mock price based on product info
        This is for demo purposes - in production, actual scraping happens
        """
        import random

        brand = str(product_info.get('brand', '')).lower()
        model = str(product_info.get('model', '')).lower()
        category = str(product_info.get('category', '')).lower()

        # Base prices by category and brand
        if 'iphone' in model or 'iphone' in brand:
            if '11' in model:
                base = 6500
            elif '12' in model:
                base = 8500
            elif '13' in model:
                base = 10500
            elif '14' in model or '15' in model:
                base = 13500
            else:
                base = 5000
        elif 'macbook' in model or 'macbook' in brand:
            base = 15000
        elif 'samsung' in brand:
            if 'tv' in category:
                base = 8000
            elif 'phone' in category:
                base = 5500
            else:
                base = 4000
        elif category in ['tv', 'television']:
            base = 7000
        elif category in ['laptop', 'computer']:
            base = 8000
        elif category in ['washing machine', 'fridge', 'appliance']:
            base = 3500
        else:
            base = 4000

        # Add realistic variance (+/- 15%)
        variance = random.uniform(-0.15, 0.15)
        price = int(base * (1 + variance))

        # Round to nearest 50
        return round(price / 50) * 50

    def _calculate_market_value(self, prices):
        """
        Calculate estimated market value from list of prices

        Uses median for robustness against outliers
        """
        if not prices:
            return None

        # Remove extreme outliers (prices more than 3x or less than 0.3x the median)
        if len(prices) >= 3:
            initial_median = statistics.median(prices)
            filtered_prices = [
                p for p in prices
                if 0.3 * initial_median <= p <= 3 * initial_median
            ]
            if filtered_prices:
                prices = filtered_prices

        # Use median as market value
        if len(prices) == 1:
            return prices[0]
        elif len(prices) == 2:
            return statistics.mean(prices)
        else:
            return statistics.median(prices)

    def calculate_price_statistics(self, prices):
        """Calculate useful statistics about prices found"""
        if not prices:
            return None

        return {
            'min': min(prices),
            'max': max(prices),
            'median': statistics.median(prices),
            'mean': statistics.mean(prices),
            'count': len(prices),
            'std_dev': statistics.stdev(prices) if len(prices) > 1 else 0
        }
