import requests
from bs4 import BeautifulSoup
from config import Config
import re


class EbayScraper:
    """Scrapes eBay for international pricing data"""

    def __init__(self):
        self.base_url = "https://www.ebay.com"
        self.headers = {'User-Agent': Config.USER_AGENT}
        self.timeout = Config.SCRAPING_TIMEOUT

    def search_product(self, search_queries):
        """
        Search eBay for product prices

        Args:
            search_queries: List of search query strings

        Returns:
            List of price results in USD
        """
        results = []

        for query in search_queries[:3]:
            try:
                # eBay search URL - filter for used items
                search_url = f"{self.base_url}/sch/i.html?_nkw={query.replace(' ', '+')}&LH_ItemCondition=3000"

                response = requests.get(
                    search_url,
                    headers=self.headers,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # eBay uses specific classes for search results
                    listings = soup.find_all('div', class_='s-item__info')

                    for listing in listings[:10]:  # Top 10 results
                        try:
                            # Extract title
                            title_elem = listing.find('div', class_='s-item__title')
                            title = title_elem.get_text(strip=True) if title_elem else None

                            # Extract price
                            price_elem = listing.find('span', class_='s-item__price')
                            price_text = price_elem.get_text(strip=True) if price_elem else None

                            if title and price_text:
                                # Extract numeric price (in USD)
                                price_usd = self._extract_price(price_text)

                                if price_usd and price_usd > 0:
                                    # Check if it's a "Buy It Now" or sold listing
                                    condition = 'used'
                                    if listing.find(text=re.compile('Pre-Owned|Used', re.I)):
                                        condition = 'used'
                                    elif listing.find(text=re.compile('New', re.I)):
                                        condition = 'new'

                                    # Get item URL
                                    link = listing.find_parent('div', class_='s-item__wrapper').find('a')
                                    url = link['href'] if link else search_url

                                    results.append({
                                        'title': title,
                                        'price_usd': price_usd,
                                        'url': url,
                                        'condition': condition,
                                        'source': 'eBay'
                                    })

                        except Exception as e:
                            print(f"Error parsing eBay listing: {e}")
                            continue

            except Exception as e:
                print(f"Error searching eBay for '{query}': {e}")
                continue

        return results

    def search_sold_listings(self, search_queries):
        """
        Search eBay SOLD listings for more accurate market value

        Args:
            search_queries: List of search query strings

        Returns:
            List of sold prices in USD
        """
        results = []

        for query in search_queries[:2]:
            try:
                # eBay sold listings filter
                search_url = f"{self.base_url}/sch/i.html?_nkw={query.replace(' ', '+')}&LH_Sold=1&LH_Complete=1&LH_ItemCondition=3000"

                response = requests.get(
                    search_url,
                    headers=self.headers,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    listings = soup.find_all('div', class_='s-item__info')

                    for listing in listings[:10]:
                        try:
                            title_elem = listing.find('div', class_='s-item__title')
                            title = title_elem.get_text(strip=True) if title_elem else None

                            price_elem = listing.find('span', class_='s-item__price')
                            price_text = price_elem.get_text(strip=True) if price_elem else None

                            if title and price_text:
                                price_usd = self._extract_price(price_text)

                                if price_usd and price_usd > 0:
                                    results.append({
                                        'title': title,
                                        'price_usd': price_usd,
                                        'url': search_url,
                                        'condition': 'used',
                                        'source': 'eBay (Sold)',
                                        'sold': True
                                    })

                        except Exception as e:
                            continue

            except Exception as e:
                print(f"Error searching eBay sold listings: {e}")
                continue

        return results

    def _extract_price(self, price_text):
        """
        Extract numeric price from eBay price text
        Examples: "$123.45", "$1,234.56", "US $123.00"
        """
        try:
            # Remove currency symbols and commas
            clean_price = re.sub(r'[,$\s]', '', price_text)
            # Remove text like "US" or "to"
            clean_price = re.sub(r'[A-Za-z]+', '', clean_price)
            # Extract first number
            match = re.search(r'[\d.]+', clean_price)
            if match:
                price = float(match.group())
                # Sanity check - eBay prices should be reasonable
                if 0 < price < 100000:
                    return price
        except Exception:
            pass
        return None
