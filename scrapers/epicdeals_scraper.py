import requests
from bs4 import BeautifulSoup
from config import Config
import re


class EpicDealsScraper:
    """Scrapes EpicDeals.co.za for product prices"""

    def __init__(self):
        self.base_url = Config.PRICE_SOURCES['epicdeals']
        self.headers = {'User-Agent': Config.USER_AGENT}

    def search_product(self, search_queries):
        """
        Search for product on EpicDeals.co.za

        Args:
            search_queries: List of search query strings

        Returns:
            List of dicts with 'title', 'price', 'url', 'condition'
        """
        results = []

        for query in search_queries[:2]:  # Limit to first 2 queries for speed
            try:
                # EpicDeals uses WooCommerce with DGWT WCAS search
                search_url = f"{self.base_url}/?s={query}&post_type=product&dgwt_wcas=1"

                print(f"  Searching EpicDeals: {search_url}")

                response = requests.get(
                    search_url,
                    headers=self.headers,
                    timeout=Config.SCRAPING_TIMEOUT
                )

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # WooCommerce product listings - try multiple selectors
                    products = soup.find_all('li', class_='product') or \
                              soup.find_all('li', class_='type-product') or \
                              soup.find_all(class_='product')

                    print(f"  Found {len(products)} products on EpicDeals")

                    for product in products[:10]:  # Top 10 results per query
                        try:
                            # Extract title - multiple fallbacks
                            title = ''
                            title_elem = product.find('h2', class_='woocommerce-loop-product__title') or \
                                       product.find('h2', class_='product-title') or \
                                       product.find('h2') or \
                                       product.find('h3')

                            if title_elem:
                                title = title_elem.get_text(strip=True)
                            else:
                                link = product.find('a')
                                if link and link.get('title'):
                                    title = link['title']

                            # Extract price - get current price (may have sale price)
                            price_elem = product.find('span', class_='price')
                            if price_elem:
                                # Try to get sale price first
                                ins_price = price_elem.find('ins')
                                if ins_price:
                                    price_text = ins_price.get_text(strip=True)
                                else:
                                    price_text = price_elem.get_text(strip=True)
                            else:
                                price_text = ''

                            # Extract numeric price
                            price = self._extract_price(price_text)

                            if title and price and price > 0:
                                link = product.find('a', class_='woocommerce-LoopProduct-link') or product.find('a')
                                url = link['href'] if link and link.get('href') else search_url

                                # Extract condition from title
                                condition = 'Refurbished'
                                title_lower = title.lower()
                                if 'grade a' in title_lower:
                                    condition = 'Grade A'
                                elif 'grade b' in title_lower:
                                    condition = 'Grade B'
                                elif 'grade c' in title_lower:
                                    condition = 'Grade C'
                                elif 'sealed' in title_lower or 'new' in title_lower:
                                    condition = 'New'

                                results.append({
                                    'title': title,
                                    'price': price,
                                    'url': url,
                                    'condition': condition,
                                    'source': 'EpicDeals'
                                })
                                print(f"    Found: {title[:50]}... R{price}")
                        except Exception as e:
                            print(f"  Error parsing product: {e}")
                            continue

            except Exception as e:
                print(f"Error searching EpicDeals for '{query}': {e}")
                continue

        return results

    def _extract_price(self, price_text):
        """Extract numeric price from text like 'R1,234.00' or 'R1234'"""
        try:
            # Remove currency symbol and commas
            clean_price = re.sub(r'[R,\s]', '', price_text)
            # Extract first number found
            match = re.search(r'[\d.]+', clean_price)
            if match:
                return float(match.group())
        except Exception:
            pass
        return None
