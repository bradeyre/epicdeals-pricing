import requests
from config import Config


class CurrencyConverter:
    """Handles USD to ZAR currency conversion"""

    def __init__(self):
        self.cache = {}  # Simple in-memory cache
        self.fallback_rate = Config.FALLBACK_USD_ZAR_RATE

    def get_usd_to_zar_rate(self):
        """
        Gets current USD to ZAR exchange rate.
        Tries multiple sources with fallbacks.

        Returns:
            Float: Current USD/ZAR exchange rate
        """

        # Try multiple free APIs
        sources = [
            self._get_rate_from_exchangerate_api,
            self._get_rate_from_reserve_bank,
            self._get_rate_from_fallback
        ]

        for source in sources:
            try:
                rate = source()
                if rate and rate > 0:
                    return rate
            except Exception as e:
                print(f"Error fetching exchange rate: {e}")
                continue

        # Ultimate fallback
        return Config.FALLBACK_USD_ZAR_RATE

    def _get_rate_from_api(self):
        """Try to get rate from exchangerate-api.com (free tier available)"""
        import requests

        try:
            response = requests.get(
                'https://api.exchangerate-api.com/v4/latest/USD',
                timeout=5
            )
            data = response.json()
            return data['rates']['ZAR']
        except Exception:
            return None

    def _get_rate_from_backup(self):
        """Try alternative sources for exchange rate"""
        try:
            import requests
            # Try exchangerate-api.com (free tier available)
            response = requests.get('https://open.er-api.com/v6/latest/USD', timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data['rates']['ZAR']
        except Exception:
            pass

        return None

    def format_zar(self, amount):
        """Format amount as South African Rand"""
        return f"R{amount:,.2f}"
