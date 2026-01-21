import requests
from bs4 import BeautifulSoup
from config import Config
import re


class GumtreeScraper:
    """Scrapes Gumtree.co.za for product prices"""

    def __init__(self):
        self.base_url = 'https://www.gumtree.co.za'
        self.headers = {'User-Agent': Config.USER_AGENT}

    def search_product(self, search_queries):
        """
        Search for product on Gumtree.co.za

        Args:
            search_queries: List of search query strings

        Returns:
            List of dicts with 'title', 'price', 'url', 'condition'
        """
        results = []

        for query in search_queries[:2]:  # Limit to first 2 queries for speed
            try:
                # Gumtree search URL format
                formatted_query = query.replace(' ', '-').lower()
                search_url = f"{self.base_url}/s-{formatted_query}/v1q0p1"

                print(f"  Searching Gumtree: {search_url}")

                response = requests.get(
                    search_url,
                    headers=self.headers,
                    timeout=Config.SCRAPING_TIMEOUT
                )

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Gumtree uses various listing formats
                    products = soup.find_all('div', class_=lambda x: x and 'listing' in str(x).lower()) or \
                              soup.find_all('article') or \
                              soup.find_all('li', class_=lambda x: x and 'result' in str(x).lower())

                    print(f"  Found {len(products)} products on Gumtree")

                    for product in products[:10]:  # Top 10 results per query
                        try:
                            # Extract title - multiple fallbacks
                            title = ''
                            title_elem = product.find('h2') or \
                                       product.find('h3') or \
                                       product.find('a', class_=lambda x: x and 'title' in str(x).lower())

                            if title_elem:
                                title = title_elem.get_text(strip=True)
                            else:
                                link = product.find('a')
                                if link and link.get('title'):
                                    title = link['title']

                            # Extract price
                            price_elem = product.find('span', class_=lambda x: x and 'price' in str(x).lower()) or \
                                       product.find('div', class_=lambda x: x and 'price' in str(x).lower()) or \
                                       product.find('p', class_=lambda x: x and 'price' in str(x).lower())

                            price_text = ''
                            if price_elem:
                                price_text = price_elem.get_text(strip=True)

                            # Extract numeric price
                            price = self._extract_price(price_text)

                            if title and price and price > 0:
                                link = product.find('a')
                                url = link['href'] if link and link.get('href') else search_url
                                if url and not url.startswith('http'):
                                    url = self.base_url + url

                                # Extract condition from title
                                condition = 'Used'
                                title_lower = title.lower()
                                if 'new' in title_lower or 'sealed' in title_lower:
                                    condition = 'New'
                                elif 'excellent' in title_lower or 'mint' in title_lower:
                                    condition = 'Excellent'
                                elif 'good' in title_lower:
                                    condition = 'Good'

                                results.append({
                                    'title': title,
                                    'price': price,
                                    'url': url,
                                    'condition': condition,
                                    'source': 'Gumtree'
                                })
                                print(f"    Found: {title[:50]}... R{price}")
                        except Exception as e:
                            print(f"  Error parsing product: {e}")
                            continue

            except Exception as e:
                print(f"Error searching Gumtree for '{query}': {e}")
                continue

        return results

    def _extract_price(self, price_text):
        """Extract numeric price from text like 'R1,234' or 'R1234'"""
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
