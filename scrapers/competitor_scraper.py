import requests
from bs4 import BeautifulSoup
from config import Config
import re


class CompetitorScraper:
    """Scrapes competitor websites for pricing data"""

    def __init__(self):
        self.headers = {'User-Agent': Config.USER_AGENT}
        self.timeout = Config.SCRAPING_TIMEOUT

    def search_all_competitors(self, search_queries):
        """
        Search all competitor sites

        Returns:
            List of price results from all competitors
        """
        all_results = []

        # Search each competitor
        all_results.extend(self.search_bobshop(search_queries))
        all_results.extend(self.search_wefix(search_queries))
        all_results.extend(self.search_swopp(search_queries))
        all_results.extend(self.search_istore(search_queries))

        return all_results

    def search_bobshop(self, search_queries):
        """Search bobshop.co.za using Manus approach"""
        results = []

        for query in search_queries[:2]:
            try:
                search_url = f"https://www.bobshop.co.za/Browse/Search.aspx?q={query}"
                print(f"  Searching BobShop: {search_url}")

                response = requests.get(search_url, headers=self.headers, timeout=self.timeout)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Bob Shop uses various listing formats
                    products = soup.find_all(class_=lambda x: x and ('listing-item' in str(x) or 'product-card' in str(x) or 'item-card' in str(x)))

                    if not products:
                        # Try alternative selector
                        products = soup.find_all('a', href=lambda x: x and '/p/' in str(x))

                    print(f"  Found {len(products)} products on BobShop")

                    for idx, product in enumerate(products[:10]):
                        try:
                            # Extract title
                            title_elem = product.find(class_=lambda x: x and ('title' in str(x).lower() or 'product' in str(x).lower()))
                            if not title_elem:
                                title_elem = product.find(['h3', 'h4'])
                            if not title_elem and product.name == 'a':
                                title = product.get('title', '') or product.get_text(strip=True)
                            else:
                                title = title_elem.get_text(strip=True) if title_elem else ''

                            # Extract price
                            price_elem = product.find(class_=lambda x: x and 'price' in str(x).lower())
                            if not price_elem and product.name == 'a':
                                price_elem = product.parent.find(class_=lambda x: x and 'price' in str(x).lower())

                            price_text = price_elem.get_text(strip=True) if price_elem else ''
                            price = self._extract_price(price_text)

                            if title and len(title) > 3 and price and price > 0:
                                url = product.get('href', search_url) if product.name == 'a' else product.find('a').get('href', search_url) if product.find('a') else search_url
                                if url and not url.startswith('http'):
                                    url = f"https://www.bobshop.co.za{url}"

                                results.append({
                                    'title': title[:200],
                                    'price': price,
                                    'url': url,
                                    'condition': 'used',
                                    'source': 'BobShop'
                                })
                                print(f"    Found: {title[:50]}... R{price}")
                        except Exception as e:
                            print(f"  Error parsing BobShop product: {e}")
                            continue

            except Exception as e:
                print(f"Error searching BobShop: {e}")
                continue

        return results

    def search_wefix(self, search_queries):
        """Search wefix.co.za"""
        results = []
        base_url = Config.PRICE_SOURCES['wefix']

        for query in search_queries[:2]:
            try:
                search_url = f"{base_url}/?s={query}"
                response = requests.get(search_url, headers=self.headers, timeout=self.timeout)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Look for common e-commerce patterns
                    products = soup.find_all(['div', 'li'], class_=lambda x: x and ('product' in x.lower() or 'item' in x.lower()))

                    for product in products[:5]:
                        price = self._extract_price_from_element(product)
                        title = self._extract_title_from_element(product)

                        if price and title:
                            results.append({
                                'title': title,
                                'price': price,
                                'url': search_url,
                                'condition': 'used',
                                'source': 'WeFix'
                            })

            except Exception as e:
                print(f"Error searching WeFix: {e}")
                continue

        return results

    def search_swopp(self, search_queries):
        """Search swopp.co.za"""
        results = []
        base_url = Config.PRICE_SOURCES['swopp']

        for query in search_queries[:2]:
            try:
                search_url = f"{base_url}/search?q={query}"
                response = requests.get(search_url, headers=self.headers, timeout=self.timeout)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Swopp-specific selectors (adjust based on actual site structure)
                    products = soup.find_all(['div', 'article'], class_=lambda x: x and 'product' in x.lower())

                    for product in products[:5]:
                        price = self._extract_price_from_element(product)
                        title = self._extract_title_from_element(product)

                        if price and title:
                            results.append({
                                'title': title,
                                'price': price,
                                'url': search_url,
                                'condition': 'used',
                                'source': 'Swopp'
                            })

            except Exception as e:
                print(f"Error searching Swopp: {e}")
                continue

        return results

    def search_istore(self, search_queries):
        """Search istorepreowned.co.za"""
        results = []
        base_url = Config.PRICE_SOURCES['istore']

        for query in search_queries[:2]:
            try:
                search_url = f"{base_url}/?s={query}&post_type=product"
                response = requests.get(search_url, headers=self.headers, timeout=self.timeout)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # WooCommerce structure
                    products = soup.find_all('li', class_='product')

                    for product in products[:5]:
                        price_elem = product.find('span', class_='price')
                        title_elem = product.find('h2') or product.find('a', class_='woocommerce-LoopProduct-link')

                        if price_elem and title_elem:
                            price = self._extract_price(price_elem.get_text(strip=True))
                            title = title_elem.get_text(strip=True)

                            if price:
                                results.append({
                                    'title': title,
                                    'price': price,
                                    'url': search_url,
                                    'condition': 'preowned',
                                    'source': 'iStore Preowned'
                                })

            except Exception as e:
                print(f"Error searching iStore: {e}")
                continue

        return results

    def _extract_price_from_element(self, element):
        """Try to extract price from a product element"""
        # Look for common price class names and patterns
        price_classes = ['price', 'amount', 'cost', 'value']

        for class_name in price_classes:
            price_elem = element.find(['span', 'div', 'p'], class_=lambda x: x and class_name in x.lower())
            if price_elem:
                price = self._extract_price(price_elem.get_text(strip=True))
                if price:
                    return price

        # Fallback: search entire element text for price pattern
        text = element.get_text()
        price = self._extract_price(text)
        return price

    def _extract_title_from_element(self, element):
        """Try to extract product title from element"""
        # Look for common title elements
        title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'a'], class_=lambda x: x and ('title' in x.lower() or 'name' in x.lower()))

        if title_elem:
            return title_elem.get_text(strip=True)

        # Fallback: first link or heading
        link = element.find('a')
        if link:
            return link.get_text(strip=True)

        return None

    def _extract_price(self, price_text):
        """Extract numeric price from text"""
        try:
            clean_price = re.sub(r'[R,\s]', '', price_text)
            match = re.search(r'[\d.]+', clean_price)
            if match:
                return float(match.group())
        except Exception:
            pass
        return None
