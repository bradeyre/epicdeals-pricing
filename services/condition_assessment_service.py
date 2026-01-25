"""
Condition Assessment Service
Handles detailed condition evaluation and pricing adjustments based on specific issues
"""


class ConditionAssessmentService:
    """
    Calculates pricing adjustments based on:
    1. Overall condition (excellent, good, fair, poor)
    2. Specific damage/issues reported by seller
    """

    # Condition multipliers (applied to base market value)
    # Updated to match new 5-tier grading system with clearer distinctions
    CONDITION_MULTIPLIERS = {
        # New structured grading (exact matches from AI)
        'pristine': 0.975,  # 95-100% value - Like new, no visible wear
        'excellent': 0.90,  # 85-95% value - Very light use, barely noticeable marks
        'good': 0.775,      # 70-85% value - Normal use, minor scratches/scuffs
        'fair': 0.60,       # 50-70% value - Heavy use, obvious scratches/dents
        'poor': 0.40,       # 30-50% value - Significant damage or broken parts

        # Legacy support (partial matching)
        'like new': 0.975,
        'very light use': 0.90,
        'barely noticeable marks': 0.90,
        'normal use': 0.775,
        'minor wear': 0.775,
        'minor scratches': 0.775,
        'heavy use': 0.60,
        'visible scratches': 0.60,
        'obvious scratches': 0.60,
        'damaged': 0.40,
        'broken': 0.40,
        'significant damage': 0.40,
        'not working': 0.30
    }

    # Issue deductions for PHONES/TABLETS (in ZAR)
    PHONE_DEDUCTIONS = {
        'screen_cracked': 1200,
        'screen_scratched': 300,
        'back_glass_cracked': 800,
        'body_dents': 350,
        'battery_degraded': 650,
        'battery_health_below_80': 650,
        'camera_issues': 800,
        'face_id_not_working': 1200,
        'touch_id_not_working': 1200,
        'biometric_broken': 1200,
        'buttons_damaged': 450,
        'ports_damaged': 450,
        'buttons_ports_damaged': 450,
        'water_damage': 1800
    }

    # Issue deductions for LAPTOPS (in ZAR)
    LAPTOP_DEDUCTIONS = {
        'screen_cracked': 3500,
        'screen_scratched': 800,
        'dead_pixels': 1000,
        'keyboard_issues': 1750,
        'keyboard_keys_missing': 1750,
        'trackpad_not_working': 1000,
        'trackpad_broken': 1000,
        'battery_degraded': 1100,
        'battery_health_below_80': 1100,
        'body_damage': 1000,
        'body_dents': 1000,
        'hinge_loose': 800,
        'hinge_broken': 1500,
        'ports_not_working': 1000,
        'ports_broken': 1000,
        'overheating': 800,
        'overheating_issues': 800
    }

    # Issue deductions for CAMERAS (in ZAR)
    CAMERA_DEDUCTIONS = {
        'lens_scratches': 800,
        'lens_fungus': 1200,
        'sensor_dust': 600,
        'sensor_spots': 600,
        'shutter_not_working': 2000,
        'high_shutter_count': 1000,
        'autofocus_issues': 1500,
        'body_scratches': 400,
        'body_dents': 600,
        'missing_parts': 500,
        'viewfinder_scratches': 300
    }

    # Issue deductions for TVs (in ZAR)
    TV_DEDUCTIONS = {
        'screen_burn_in': 2500,
        'dead_pixels': 1200,
        'cracked_screen': 4000,
        'lines_discoloration': 2000,
        'hdmi_ports_not_working': 800,
        'smart_features_not_working': 600,
        'stand_missing': 300,
        'stand_broken': 300,
        'remote_missing': 150
    }

    # Issue deductions for APPLIANCES (in ZAR)
    APPLIANCE_DEDUCTIONS = {
        'doesnt_work_properly': 2000,
        'leaks': 1500,
        'excessive_noise': 800,
        'missing_parts': 600,
        'visible_damage': 500,
        'rust': 800
    }

    def calculate_adjusted_value(self, base_value, condition, damage_details, category):
        """
        Calculate adjusted value based on condition and specific issues

        Args:
            base_value (float): Market value from research
            condition (str): Overall condition (excellent, good, fair, poor)
            damage_details (list): List of specific issues
            category (str): Product category (phone, laptop, etc.)

        Returns:
            float: Adjusted value after applying multipliers and deductions
        """

        if not base_value or base_value <= 0:
            return 0

        # Step 1: Apply condition multiplier
        condition_normalized = condition.lower() if condition else 'good'
        multiplier = self.CONDITION_MULTIPLIERS.get(condition_normalized, 0.85)
        adjusted = base_value * multiplier

        print(f"\nCondition Assessment:")
        print(f"- Base Market Value: R{base_value:,.2f}")
        print(f"- Condition: {condition} (multiplier: {multiplier})")
        print(f"- After condition adjustment: R{adjusted:,.2f}")

        # Step 2: Apply issue deductions
        total_deductions = 0
        if damage_details and damage_details != ['none']:
            # Check if "None - Everything works perfectly" is selected
            none_selected = any('none' in str(issue).lower() and 'works' in str(issue).lower()
                              for issue in damage_details)

            if not none_selected:
                total_deductions = self._calculate_issue_deductions(damage_details, category)
                adjusted -= total_deductions
                print(f"- Issue deductions: -R{total_deductions:,.2f}")
                print(f"- After deductions: R{adjusted:,.2f}")

        # Step 3: Never go below 20% of base value (parts value)
        min_value = base_value * 0.20
        adjusted = max(adjusted, min_value)

        if adjusted == min_value:
            print(f"- Applied minimum floor: R{min_value:,.2f}")

        print(f"- Final Adjusted Value: R{adjusted:,.2f}\n")

        return round(adjusted, 2)

    def _calculate_issue_deductions(self, damage_details, category):
        """
        Calculate total deductions for specific issues

        Args:
            damage_details (list): List of damage issues
            category (str): Product category

        Returns:
            float: Total deduction amount in ZAR
        """

        # Select appropriate deduction table
        deduction_table = self._get_deduction_table(category)

        total = 0
        print(f"\n  Damage Details:")

        for issue in damage_details:
            # Normalize issue string to match keys
            issue_key = self._normalize_issue_key(issue)

            # Look up deduction
            deduction = deduction_table.get(issue_key, 0)

            if deduction > 0:
                print(f"  - {issue}: -R{deduction:,.2f}")
                total += deduction
            else:
                # Try partial matching
                matched = False
                for key, value in deduction_table.items():
                    if key in issue_key or issue_key in key:
                        print(f"  - {issue}: -R{value:,.2f}")
                        total += value
                        matched = True
                        break

                if not matched:
                    print(f"  - {issue}: (no deduction found)")

        return total

    def _get_deduction_table(self, category):
        """Get appropriate deduction table for category"""

        category_lower = category.lower()

        if category_lower in ['phone', 'smartphone', 'mobile', 'iphone', 'android', 'tablet', 'ipad']:
            return self.PHONE_DEDUCTIONS

        elif category_lower in ['laptop', 'notebook', 'macbook', 'computer']:
            return self.LAPTOP_DEDUCTIONS

        elif category_lower in ['camera', 'dslr', 'mirrorless']:
            return self.CAMERA_DEDUCTIONS

        elif category_lower in ['tv', 'television']:
            return self.TV_DEDUCTIONS

        elif category_lower in ['appliance', 'washing machine', 'fridge', 'refrigerator', 'dishwasher']:
            return self.APPLIANCE_DEDUCTIONS

        else:
            # Generic deductions for unknown categories
            return {
                'broken': 1000,
                'damaged': 800,
                'missing_parts': 500,
                'scratched': 300
            }

    def _normalize_issue_key(self, issue):
        """Normalize issue string to match deduction table keys"""

        if not issue:
            return ''

        # Convert to lowercase
        normalized = issue.lower()

        # Remove common prefixes/suffixes
        normalized = normalized.replace('- ', '')
        normalized = normalized.replace(' or ', '_')
        normalized = normalized.replace('/', '_')
        normalized = normalized.replace(' ', '_')
        normalized = normalized.replace('-', '_')
        normalized = normalized.replace('(', '')
        normalized = normalized.replace(')', '')
        normalized = normalized.replace(',', '')

        # Handle common variations
        normalized = normalized.replace('cracked_or_scratched', 'cracked')
        normalized = normalized.replace('blurry', 'issues')
        normalized = normalized.replace('not_working', 'broken')

        return normalized

    def get_damage_options_for_category(self, category):
        """
        Return appropriate damage questions for category

        Args:
            category (str): Product category

        Returns:
            list: List of damage options to present to user
        """

        category_lower = category.lower() if category else ''

        if category_lower in ['phone', 'smartphone', 'mobile', 'iphone', 'android', 'tablet', 'ipad']:
            return [
                "Screen cracked or scratched",
                "Back glass cracked",
                "Body dents or deep scratches",
                "Battery health below 80%",
                "Camera issues (blurry, not working)",
                "Face ID / Touch ID not working",
                "Buttons or ports damaged",
                "Water damage",
                "None - Everything works perfectly"
            ]

        elif category_lower in ['laptop', 'notebook', 'macbook', 'computer']:
            return [
                "Screen scratches, dead pixels, or cracks",
                "Keyboard keys missing or sticky",
                "Trackpad not working properly",
                "Battery health below 80%",
                "Dents or cracks in body",
                "Hinge loose or broken",
                "Ports not working",
                "Overheating issues",
                "None - Everything works perfectly"
            ]

        elif category_lower in ['camera', 'dslr', 'mirrorless']:
            return [
                "Lens scratches or fungus",
                "Sensor dust or spots",
                "Shutter not working / high count",
                "Autofocus issues",
                "Body scratches or dents",
                "Missing parts",
                "Viewfinder scratches",
                "None - Everything works perfectly"
            ]

        elif category_lower in ['tv', 'television']:
            return [
                "Screen burn-in or dead pixels",
                "Cracked screen",
                "Lines or discoloration",
                "HDMI ports not working",
                "Smart features not working",
                "Stand missing or broken",
                "Remote missing",
                "None - Everything works perfectly"
            ]

        elif category_lower in ['appliance', 'washing machine', 'fridge', 'refrigerator', 'dishwasher', 'dryer']:
            return [
                "Doesn't work properly",
                "Leaks or drips",
                "Makes excessive noise",
                "Missing parts",
                "Visible damage or rust",
                "None - Everything works perfectly"
            ]

        elif category_lower in ['console', 'playstation', 'xbox', 'nintendo', 'switch']:
            return [
                "Doesn't power on",
                "Disc drive not working",
                "Controller issues",
                "HDMI port damaged",
                "Overheating or loud fan",
                "Body scratches or dents",
                "Missing cables or controllers",
                "None - Everything works perfectly"
            ]

        else:
            # Generic options for unknown categories
            return [
                "Doesn't work properly",
                "Visible damage or scratches",
                "Missing parts or accessories",
                "Cosmetic wear",
                "None - Everything works perfectly"
            ]

    def format_condition_breakdown(self, base_value, condition, damage_details, category, adjusted_value):
        """
        Format a detailed breakdown of condition adjustments for display

        Args:
            base_value: Original market value
            condition: Overall condition
            damage_details: List of issues
            category: Product category
            adjusted_value: Final adjusted value

        Returns:
            str: Formatted breakdown message
        """

        multiplier = self.CONDITION_MULTIPLIERS.get(condition.lower() if condition else 'good', 0.85)
        after_condition = base_value * multiplier

        breakdown = f"\n**Condition Assessment Breakdown:**\n"
        breakdown += f"- Market Value: R{base_value:,.2f}\n"
        breakdown += f"- Condition ({condition}): {multiplier*100:.0f}% = R{after_condition:,.2f}\n"

        if damage_details and damage_details != ['none']:
            none_selected = any('none' in str(issue).lower() and 'works' in str(issue).lower()
                              for issue in damage_details)

            if not none_selected:
                deductions = self._calculate_issue_deductions(damage_details, category)
                if deductions > 0:
                    breakdown += f"\n**Issue Deductions:**\n"
                    for issue in damage_details:
                        issue_key = self._normalize_issue_key(issue)
                        deduction_table = self._get_deduction_table(category)
                        deduction = deduction_table.get(issue_key, 0)
                        if deduction > 0:
                            breakdown += f"  - {issue}: -R{deduction:,.2f}\n"

        breakdown += f"\n**Final Adjusted Value: R{adjusted_value:,.2f}**\n"

        return breakdown
