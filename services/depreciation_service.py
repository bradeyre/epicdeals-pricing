"""
Age-Based Depreciation Service

Calculates second-hand value based on item age and category.
Different categories have different depreciation curves.
"""

from datetime import datetime
from typing import Dict, Optional


class DepreciationService:
    """
    Handles age-based depreciation calculations with category-specific curves
    """

    def __init__(self):
        # Depreciation curves: year -> percentage of new retail price remaining
        # Year 0 = brand new (100%), Year 1 = after 1 year, etc.

        self.depreciation_curves = {
            'iphone': {
                0: 1.00,   # Brand new
                1: 0.65,   # After 1 year: 65% of new price
                2: 0.50,   # After 2 years: 50%
                3: 0.38,   # After 3 years: 38%
                4: 0.28,   # After 4 years: 28%
                5: 0.20,   # After 5 years: 20%
                6: 0.15,   # After 6 years: 15%
                7: 0.10,   # After 7+ years: 10%
            },
            'phone': {  # Android and other smartphones
                0: 1.00,
                1: 0.55,   # Depreciate faster than iPhone
                2: 0.40,
                3: 0.28,
                4: 0.18,
                5: 0.12,
                6: 0.08,
                7: 0.05,
            },
            'samsung_phone': {  # Samsung flagship phones
                0: 1.00,
                1: 0.58,   # Hold value slightly better
                2: 0.43,
                3: 0.30,
                4: 0.20,
                5: 0.13,
                6: 0.09,
                7: 0.06,
            },
            'macbook': {
                0: 1.00,
                1: 0.70,   # MacBooks hold value well
                2: 0.58,
                3: 0.48,
                4: 0.38,
                5: 0.30,
                6: 0.23,
                7: 0.18,
                8: 0.15,
            },
            'laptop': {  # Windows laptops
                0: 1.00,
                1: 0.55,   # Faster depreciation
                2: 0.40,
                3: 0.30,
                4: 0.22,
                5: 0.15,
                6: 0.10,
                7: 0.07,
            },
            'ipad': {
                0: 1.00,
                1: 0.65,
                2: 0.52,
                3: 0.40,
                4: 0.30,
                5: 0.22,
                6: 0.16,
                7: 0.12,
            },
            'tablet': {  # Android tablets
                0: 1.00,
                1: 0.55,
                2: 0.40,
                3: 0.28,
                4: 0.18,
                5: 0.12,
                6: 0.08,
                7: 0.05,
            },
            'console': {  # Gaming consoles
                0: 1.00,
                1: 0.75,   # Hold value well when new gen
                2: 0.65,
                3: 0.55,
                4: 0.45,   # Drops when new generation releases
                5: 0.35,
                6: 0.25,
                7: 0.18,
                8: 0.12,
            },
            'camera': {
                0: 1.00,
                1: 0.65,
                2: 0.55,
                3: 0.45,
                4: 0.38,
                5: 0.32,
                6: 0.26,
                7: 0.22,
                8: 0.18,
            },
            'smartwatch': {
                0: 1.00,
                1: 0.50,   # Rapid depreciation
                2: 0.35,
                3: 0.25,
                4: 0.18,
                5: 0.12,
                6: 0.08,
                7: 0.05,
            },
            'tv': {
                0: 1.00,
                1: 0.55,
                2: 0.42,
                3: 0.32,
                4: 0.25,
                5: 0.20,
                6: 0.15,
                7: 0.12,
                8: 0.10,
            },
            'appliance': {
                0: 1.00,
                1: 0.60,
                2: 0.48,
                3: 0.38,
                4: 0.30,
                5: 0.24,
                6: 0.18,
                7: 0.14,
                8: 0.10,
                9: 0.08,
                10: 0.06,
            },
            'default': {
                0: 1.00,
                1: 0.60,
                2: 0.45,
                3: 0.35,
                4: 0.27,
                5: 0.20,
                6: 0.15,
                7: 0.12,
            }
        }

    def calculate_depreciation_factor(
        self,
        category: str,
        age_years: float,
        brand: Optional[str] = None,
        model: Optional[str] = None
    ) -> float:
        """
        Calculate the depreciation factor for an item based on age

        Args:
            category: Item category (phone, laptop, etc.)
            age_years: Age in years (can be decimal, e.g., 2.5 years)
            brand: Brand name (to detect special cases like iPhone, MacBook)
            model: Model name (to detect special cases)

        Returns:
            Float between 0 and 1 representing percentage of new value remaining
        """

        # Detect special categories based on brand/model
        curve_key = self._get_curve_key(category, brand, model)

        # Get the appropriate depreciation curve
        curve = self.depreciation_curves.get(curve_key, self.depreciation_curves['default'])

        # Get age as integer years for curve lookup
        age_int = int(age_years)

        # If age exceeds curve data, use the last value
        max_age = max(curve.keys())
        if age_int >= max_age:
            return curve[max_age]

        # Interpolate between two points if needed (for fractional years)
        if age_years == age_int:
            # Exact year match
            return curve[age_int]
        else:
            # Interpolate between age_int and age_int + 1
            lower_value = curve[age_int]
            upper_value = curve[age_int + 1]
            fraction = age_years - age_int
            interpolated = lower_value - (lower_value - upper_value) * fraction
            return interpolated

    def _get_curve_key(self, category: str, brand: Optional[str], model: Optional[str]) -> str:
        """
        Determine which depreciation curve to use based on category/brand/model
        """
        category_lower = category.lower() if category else ''
        brand_lower = brand.lower() if brand else ''
        model_lower = model.lower() if model else ''

        # iPhone detection
        if 'iphone' in model_lower or (brand_lower == 'apple' and 'phone' in category_lower):
            return 'iphone'

        # MacBook detection
        if 'macbook' in model_lower or (brand_lower == 'apple' and 'laptop' in category_lower):
            return 'macbook'

        # iPad detection
        if 'ipad' in model_lower or (brand_lower == 'apple' and 'tablet' in category_lower):
            return 'ipad'

        # Samsung phone detection
        if brand_lower == 'samsung' and ('phone' in category_lower or 'galaxy' in model_lower):
            return 'samsung_phone'

        # Apple Watch / Smart Watch
        if 'watch' in category_lower or 'watch' in model_lower:
            return 'smartwatch'

        # General categories
        if 'phone' in category_lower or 'smartphone' in category_lower:
            return 'phone'

        if 'laptop' in category_lower:
            return 'laptop'

        if 'tablet' in category_lower:
            return 'tablet'

        if 'console' in category_lower or 'playstation' in model_lower or 'xbox' in model_lower:
            return 'console'

        if 'camera' in category_lower:
            return 'camera'

        if 'tv' in category_lower or 'television' in category_lower:
            return 'tv'

        if 'appliance' in category_lower or 'washing' in model_lower or 'fridge' in model_lower:
            return 'appliance'

        return 'default'

    def estimate_age_from_model(self, brand: str, model: str) -> Optional[int]:
        """
        Try to extract release year from model name

        Args:
            brand: Brand name
            model: Model name

        Returns:
            Year as integer, or None if can't determine
        """
        import re

        model_lower = model.lower() if model else ''
        brand_lower = brand.lower() if brand else ''

        # Look for explicit years in model name (e.g., "MacBook Pro 2020")
        year_match = re.search(r'(20\d{2})', model)
        if year_match:
            return int(year_match.group(1))

        # iPhone model year mapping
        iphone_years = {
            'iphone 15': 2023,
            'iphone 14': 2022,
            'iphone 13': 2021,
            'iphone 12': 2020,
            'iphone 11': 2019,
            'iphone xs': 2018,
            'iphone xr': 2018,
            'iphone x': 2017,
            'iphone 8': 2017,
            'iphone 7': 2016,
            'iphone 6s': 2015,
            'iphone 6': 2014,
        }

        for iphone_model, year in iphone_years.items():
            if iphone_model in model_lower:
                return year

        # Samsung Galaxy model year mapping
        galaxy_years = {
            's24': 2024,
            's23': 2023,
            's22': 2022,
            's21': 2021,
            's20': 2020,
            's10': 2019,
            's9': 2018,
            's8': 2017,
        }

        for galaxy_model, year in galaxy_years.items():
            if galaxy_model in model_lower:
                return year

        # MacBook Pro/Air M-series
        if 'm3' in model_lower:
            return 2023
        if 'm2' in model_lower:
            return 2022
        if 'm1' in model_lower:
            return 2020

        # PlayStation
        if 'ps5' in model_lower or 'playstation 5' in model_lower:
            return 2020
        if 'ps4' in model_lower or 'playstation 4' in model_lower:
            return 2013

        # Xbox
        if 'series x' in model_lower or 'series s' in model_lower:
            return 2020
        if 'xbox one' in model_lower:
            return 2013

        return None

    def calculate_age_in_years(self, year_purchased_or_released: int) -> float:
        """
        Calculate age in years from purchase/release year

        Args:
            year_purchased_or_released: The year (e.g., 2020)

        Returns:
            Age in years (decimal, e.g., 3.5 years)
        """
        current_year = datetime.now().year
        current_month = datetime.now().month

        # Calculate whole years
        age_years = current_year - year_purchased_or_released

        # Add fractional year based on current month
        # Assume mid-year release (July) as average
        month_fraction = (current_month - 7) / 12.0

        return age_years + month_fraction

    def get_depreciation_info(
        self,
        category: str,
        age_years: float,
        new_price: float,
        condition: str,
        brand: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict:
        """
        Calculate depreciation and return detailed breakdown

        Args:
            category: Item category
            age_years: Age in years
            new_price: New retail price
            condition: Physical condition
            brand: Brand name
            model: Model name

        Returns:
            Dict with depreciation_factor, estimated_value, condition_adjusted_value, and explanation
        """

        # Get base depreciation from age
        depreciation_factor = self.calculate_depreciation_factor(
            category, age_years, brand, model
        )

        # Calculate base value after depreciation
        base_value = new_price * depreciation_factor

        # Adjust for condition
        condition_multiplier = self._get_condition_multiplier(condition)
        final_value = base_value * condition_multiplier

        # Get curve key for explanation
        curve_key = self._get_curve_key(category, brand, model)

        return {
            'depreciation_factor': depreciation_factor,
            'base_value': round(base_value, 2),
            'condition_multiplier': condition_multiplier,
            'final_value': round(final_value, 2),
            'age_years': age_years,
            'curve_used': curve_key,
            'explanation': self._generate_explanation(
                curve_key, age_years, depreciation_factor, condition, condition_multiplier
            )
        }

    def _get_condition_multiplier(self, condition: str) -> float:
        """Get multiplier based on physical condition"""
        condition_lower = condition.lower() if condition else 'good'

        if 'pristine' in condition_lower or 'mint' in condition_lower:
            return 1.10  # +10% for pristine
        elif 'excellent' in condition_lower or 'like new' in condition_lower:
            return 1.05  # +5% for excellent
        elif 'good' in condition_lower:
            return 1.0   # Standard
        elif 'fair' in condition_lower:
            return 0.85  # -15% for fair
        elif 'poor' in condition_lower:
            return 0.65  # -35% for poor
        else:
            return 1.0

    def _generate_explanation(
        self,
        curve_key: str,
        age_years: float,
        depreciation_factor: float,
        condition: str,
        condition_multiplier: float
    ) -> str:
        """Generate human-readable explanation of depreciation"""

        age_text = f"{age_years:.1f} years old" if age_years >= 1 else f"{int(age_years * 12)} months old"

        explanation = f"Based on the item being {age_text}, "

        if curve_key == 'iphone':
            explanation += f"iPhones typically retain {int(depreciation_factor * 100)}% of their value at this age. "
        elif curve_key == 'macbook':
            explanation += f"MacBooks typically retain {int(depreciation_factor * 100)}% of their value at this age. "
        elif curve_key == 'phone':
            explanation += f"smartphones typically retain {int(depreciation_factor * 100)}% of their value at this age. "
        else:
            explanation += f"items in this category typically retain {int(depreciation_factor * 100)}% of their value at this age. "

        if condition_multiplier != 1.0:
            if condition_multiplier > 1.0:
                explanation += f"The {condition} condition adds {int((condition_multiplier - 1) * 100)}% to the value."
            else:
                explanation += f"The {condition} condition reduces the value by {int((1 - condition_multiplier) * 100)}%."

        return explanation
