from config import Config


class Validators:
    """Input validation utilities"""

    @staticmethod
    def validate_email(email):
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_phone(phone):
        """Validate South African phone number"""
        import re
        # Remove spaces and dashes
        cleaned = re.sub(r'[\s\-]', '', phone)
        # South African numbers: +27 or 0 followed by 9 digits
        pattern = r'^(\+27|0)[0-9]{9}$'
        return re.match(pattern, cleaned) is not None

    @staticmethod
    def validate_item_value(value):
        """Check if item value is within acceptable range"""
        try:
            val = float(value)
            return Config.MIN_ITEM_VALUE <= val <= Config.MAX_ITEM_VALUE
        except (ValueError, TypeError):
            return False

    @staticmethod
    def sanitize_input(text):
        """Basic input sanitization"""
        if not text:
            return ""
        # Remove potentially dangerous characters
        import re
        # Keep alphanumeric, spaces, basic punctuation
        sanitized = re.sub(r'[^\w\s\-.,@+()\/]', '', str(text))
        return sanitized.strip()

    @staticmethod
    def validate_product_info(product_info):
        """
        Validate that product info has minimum required fields

        Returns:
            (bool, str): (is_valid, error_message)
        """
        required_fields = ['category', 'brand', 'model']

        for field in required_fields:
            if not product_info.get(field):
                return False, f"Missing required field: {field}"

        return True, ""
