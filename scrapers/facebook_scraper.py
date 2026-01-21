from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import Config
import re
import time


class FacebookMarketplaceScraper:
    """
    Scrapes Facebook Marketplace for pricing data.

    Note: FB Marketplace is challenging to scrape and may violate their TOS.
    This is a best-effort implementation with no guarantees.
    Consider using this sparingly and implementing rate limiting.
    """

    def __init__(self):
        self.base_url = "https://www.facebook.com/marketplace/johannesburg/search"
        self.timeout = Config.SCRAPING_TIMEOUT

    def _init_driver(self):
        """Initialize headless Chrome driver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument(f'user-agent={Config.USER_AGENT}')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')

        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            print(f"Error initializing Chrome driver: {e}")
            return None

    def search_product(self, search_queries):
        """
        Search Facebook Marketplace

        Args:
            search_queries: List of search query strings

        Returns:
            List of price results
        """
        results = []
        driver = None

        try:
            driver = self._init_driver()
            if not driver:
                return results

            for query in search_queries[:2]:  # Limit queries
                try:
                    # Build search URL
                    search_url = f"{self.base_url}?query={query.replace(' ', '%20')}"

                    driver.get(search_url)
                    time.sleep(3)  # Wait for dynamic content

                    # Try to find product listings
                    # Note: FB's HTML structure changes frequently, these selectors may need updates
                    try:
                        listings = driver.find_elements(By.CSS_SELECTOR, '[data-testid="marketplace_feed_item"]')

                        for listing in listings[:5]:  # Top 5 results
                            try:
                                # Extract title
                                title_elem = listing.find_element(By.CSS_SELECTOR, 'span')
                                title = title_elem.text if title_elem else None

                                # Extract price - FB uses various formats
                                price_text = listing.text
                                price = self._extract_price(price_text)

                                if title and price:
                                    results.append({
                                        'title': title,
                                        'price': price,
                                        'url': search_url,
                                        'condition': 'used',
                                        'source': 'Facebook Marketplace'
                                    })

                            except NoSuchElementException:
                                continue

                    except Exception as e:
                        print(f"Error finding FB listings: {e}")

                except Exception as e:
                    print(f"Error searching Facebook for '{query}': {e}")
                    continue

        except Exception as e:
            print(f"Facebook scraper error: {e}")

        finally:
            if driver:
                driver.quit()

        return results

    def _extract_price(self, text):
        """
        Extract price from text.
        FB Marketplace shows prices in various formats: R1,234 or R1234 or R 1234
        """
        try:
            # Look for R followed by numbers
            match = re.search(r'R\s*([0-9,]+)', text)
            if match:
                price_str = match.group(1).replace(',', '')
                return float(price_str)
        except Exception:
            pass
        return None

    def search_product_simple(self, search_queries):
        """
        Simplified search without Selenium (less reliable but faster)
        Tries to fetch FB Marketplace via requests (likely to fail due to JS rendering)
        """
        import requests

        results = []
        headers = {'User-Agent': Config.USER_AGENT}

        for query in search_queries[:1]:
            try:
                search_url = f"{self.base_url}?query={query.replace(' ', '%20')}"
                response = requests.get(search_url, headers=headers, timeout=self.timeout)

                if response.status_code == 200:
                    # Try basic price extraction from HTML
                    prices = re.findall(r'R\s*([0-9,]+)', response.text)

                    for price_str in prices[:5]:
                        try:
                            price = float(price_str.replace(',', ''))
                            results.append({
                                'title': f"Item from {query}",
                                'price': price,
                                'url': search_url,
                                'condition': 'used',
                                'source': 'Facebook Marketplace'
                            })
                        except ValueError:
                            continue

            except Exception as e:
                print(f"Simple FB search error: {e}")

        return results
