import os
from dotenv import load_dotenv

load_dotenv(override=True)


class Config:
    """Application configuration"""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    # Anthropic AI
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    ANTHROPIC_MODEL = 'claude-3-haiku-20240307'  # Using Haiku - Sonnet causes OOM on free Render tier

    # Perplexity AI
    PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')

    # Email
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL', 'brad@epicdeals.co.za')

    # Business Rules - Updated Jan 21, 2026
    SELL_NOW_PERCENTAGE = float(os.getenv('SELL_NOW_PERCENTAGE', 0.65))  # Seller gets 65% immediately
    CONSIGNMENT_PERCENTAGE = float(os.getenv('CONSIGNMENT_PERCENTAGE', 0.85))  # Seller gets 85% after sale
    CONSIGNMENT_PERIOD_DAYS = int(os.getenv('CONSIGNMENT_PERIOD_DAYS', 60))  # 60 days to sell
    PRICE_DROP_THRESHOLD_DAYS = int(os.getenv('PRICE_DROP_THRESHOLD_DAYS', 21))  # Suggest price drop after 21 days
    MIN_PRICE_FLOOR_PERCENTAGE = float(os.getenv('MIN_PRICE_FLOOR_PERCENTAGE', 0.70))  # Never drop below 70% of original

    MIN_ITEM_VALUE = int(os.getenv('MIN_ITEM_VALUE', 1500))
    MAX_ITEM_VALUE = int(os.getenv('MAX_ITEM_VALUE', 25000))
    CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.75))

    # Courier (free for customers, absorbed in commission)
    COURIER_COST_INTERNAL = 100  # What we pay courier service
    COLLECTION_FREE = True  # Free collection for customers

    # Legacy (keep for backward compatibility)
    OFFER_PERCENTAGE = SELL_NOW_PERCENTAGE

    # Price Research Sources
    PRICE_SOURCES = {
        'epicdeals': 'https://epicdeals.co.za',
        'wefix': 'https://wefix.co.za',
        'swopp': 'https://swopp.co.za',
        'istore': 'https://istorepreowned.co.za',
        'facebook': 'https://www.facebook.com/marketplace',
        'ebay': 'https://www.ebay.com'
    }

    # Scraping Configuration
    SCRAPING_TIMEOUT = 10  # seconds
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

    # Currency
    EXCHANGE_RATE_API_KEY = os.getenv('EXCHANGE_RATE_API_KEY')
    FALLBACK_USD_ZAR_RATE = 18.5  # Fallback if API fails

    # Validation
    @staticmethod
    def validate():
        """Validate required configuration"""
        errors = []

        if not Config.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY is required")

        if not Config.SMTP_USERNAME or not Config.SMTP_PASSWORD:
            errors.append("SMTP credentials are required for email functionality")

        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")

        return True
