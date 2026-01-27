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
        DEPRECATED - This method uses the old double-dipping logic
        Use calculate_value_with_repairs() instead

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
                # Structural damage (Poor condition)
                "Screen cracked",
                "Back glass cracked",
                "Water damage",

                # Functional failures (Poor/Fair condition)
                "Face ID / Touch ID not working",
                "Camera not working",
                "Won't turn on / Dead",

                # Repairable issues (Fair condition)
                "Battery health below 80%",
                "Buttons or ports damaged",
                "Camera issues (blurry)",

                # Cosmetic only (Good/Excellent condition)
                "Screen scratches (not cracked)",
                "Body scratches or scuffs",
                "Minor dents",

                "None - Everything works perfectly"
            ]

        elif category_lower in ['laptop', 'notebook', 'macbook', 'computer']:
            return [
                # Structural damage (Poor condition)
                "Screen cracked",
                "Hinge broken",
                "Water damage",

                # Functional failures (Poor/Fair condition)
                "Won't turn on / Dead",
                "Trackpad not working",
                "Keyboard not working",

                # Repairable issues (Fair condition)
                "Battery health below 80%",
                "Keyboard keys missing or sticky",
                "Ports not working",
                "Overheating issues",

                # Cosmetic only (Good/Excellent condition)
                "Screen scratches (not cracked)",
                "Dead pixels (minor)",
                "Body scratches or dents",

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
                # Beyond Economic Repair (Decline/Consignment only)
                "Cracked screen",
                "Screen burn-in (severe)",

                # Functional failures (Poor/Fair)
                "Won't turn on / Dead",
                "Lines or discoloration on screen",
                "HDMI ports not working",

                # Repairable issues (Fair)
                "Smart features not working",
                "Dead pixels (minor)",

                # Cosmetic/Missing parts (Good)
                "Stand missing or broken",
                "Remote missing",
                "Body scratches",

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

    def classify_damage_severity(self, damage_details, category):
        """
        Classify damage into severity levels

        Args:
            damage_details (list): List of damage issues
            category (str): Product category

        Returns:
            dict: {
                'cosmetic_only': [...],
                'repairable': [...],
                'structural': [...],
                'functional_failure': [...],
                'ber_flags': [...]  # Beyond Economic Repair flags
            }
        """

        classification = {
            'cosmetic_only': [],
            'repairable': [],
            'structural': [],
            'functional_failure': [],
            'ber_flags': []
        }

        if not damage_details:
            return classification

        # Handle string input (convert to list)
        if isinstance(damage_details, str):
            damage_details = [damage_details]

        # Check for "None - Everything works perfectly" or "No issues mentioned"
        for issue in damage_details:
            issue_str = str(issue).lower()
            if any(phrase in issue_str for phrase in ['no issues', 'no damage', 'pristine', 'perfect', 'everything works']):
                return classification

        # If we only have "None" or similar, skip
        if all(str(issue).strip().lower() in ['none', 'no', ''] for issue in damage_details):
            return classification

        # Universal BER keywords (category-agnostic)
        ber_keywords = [
            'water damage', 'liquid damage', 'moisture',
            'fungus', 'mold', 'corrosion', 'rust' if category == 'appliance' else None,
            'won\'t turn on', 'won\'t power on', 'doesn\'t turn on', 'dead',
            'motherboard', 'logic board', 'main board'
        ]
        ber_keywords = [k for k in ber_keywords if k]  # Remove None values

        for issue in damage_details:
            issue_lower = issue.lower()

            # Check for BER flags first
            if any(keyword in issue_lower for keyword in ber_keywords):
                classification['ber_flags'].append(issue)
                continue

            # Structural damage (requires professional repair)
            if any(keyword in issue_lower for keyword in [
                'cracked screen', 'screen cracked', 'screen crack',
                'back glass cracked', 'back cracked',
                'hinge broken', 'hinge loose',
                'shutter not working', 'shutter broken'
            ]):
                classification['structural'].append(issue)
                continue

            # Functional failures (major component not working)
            if any(keyword in issue_lower for keyword in [
                'camera issues', 'camera not working', 'camera broken',
                'face id not working', 'touch id not working', 'biometric',
                'trackpad not working', 'trackpad broken',
                'autofocus issues',
                'ports not working', 'hdmi not working',
                'doesn\'t work properly', 'won\'t start',
                'disc drive not working',
                'motor', 'compressor', 'leaks', 'leaking'
            ]):
                classification['functional_failure'].append(issue)
                continue

            # Repairable issues (can be fixed at reasonable cost)
            if any(keyword in issue_lower for keyword in [
                'battery', 'button', 'port damaged',
                'keyboard', 'keys missing', 'sticky',
                'sensor dust', 'sensor spots',
                'overheating', 'excessive noise',
                'missing parts', 'missing accessories'
            ]):
                classification['repairable'].append(issue)
                continue

            # Everything else is cosmetic
            classification['cosmetic_only'].append(issue)

        return classification

    def is_beyond_economic_repair(self, product_info, repair_cost, market_value, damage_classification):
        """
        Universal BER (Beyond Economic Repair) detection
        Works for ANY product category

        Args:
            product_info (dict): Product details
            repair_cost (float): Total estimated repair cost
            market_value (float): Market value in working condition
            damage_classification (dict): Output from classify_damage_severity

        Returns:
            dict: {
                'is_ber': bool,
                'reason': str,
                'recommendation': 'decline' or 'consignment'
            }
        """

        # Rule 1: BER flags (water damage, fungus, etc.)
        if damage_classification['ber_flags']:
            return {
                'is_ber': True,
                'reason': f"Unreliable repair: {', '.join(damage_classification['ber_flags'])}",
                'recommendation': 'consignment'
            }

        # Rule 2: Multiple major issues (compounding risk)
        major_count = (
            len(damage_classification['structural']) +
            len(damage_classification['functional_failure'])
        )

        if major_count >= 3:
            return {
                'is_ber': True,
                'reason': f"Multiple major issues ({major_count}) create compounding risk",
                'recommendation': 'consignment'
            }

        # Rule 3: Repair cost percentage threshold (dynamic)
        if repair_cost > 0 and market_value > 0:
            repair_percentage = (repair_cost / market_value) * 100

            # Dynamic threshold based on product value
            if market_value < 2000:
                threshold = 50  # Low-value items: more tolerance
            elif market_value < 10000:
                threshold = 35  # Mid-value: moderate
            else:
                threshold = 25  # High-value: strict

            if repair_percentage > threshold:
                return {
                    'is_ber': True,
                    'reason': f"Repair cost ({repair_percentage:.0f}%) exceeds economic threshold ({threshold}%)",
                    'recommendation': 'consignment'
                }

        # Rule 4: Age + damage combination
        year = product_info.get('year')
        if year:
            from datetime import datetime
            age = datetime.now().year - int(year)

            if age > 5 and repair_cost > (market_value * 0.3):
                return {
                    'is_ber': True,
                    'reason': f"Old product ({age} years) + high repair cost ({(repair_cost/market_value)*100:.0f}%) = poor investment",
                    'recommendation': 'consignment'
                }

        # Not BER - economically repairable
        return {
            'is_ber': False,
            'reason': 'Economically repairable',
            'recommendation': 'purchase'
        }

    def calculate_value_with_repairs(self, market_value, repair_cost, category):
        """
        NEW CORRECT CALCULATION - No double-dipping!

        When we're buying to repair:
        - Start from market value of REPAIRED item
        - Subtract repair costs
        - This gives us the value we can offer

        Args:
            market_value (float): Market value in WORKING, GOOD condition
            repair_cost (float): Cost to repair all issues
            category (str): Product category

        Returns:
            float: Value after accounting for repairs
        """

        if not market_value or market_value <= 0:
            return 0

        # Simple math: Value after repair - Cost to repair = Our value
        value_to_us = market_value - repair_cost

        # Never go below 20% of market value (parts value floor)
        min_value = market_value * 0.20
        value_to_us = max(value_to_us, min_value)

        print(f"\nRepair-Based Valuation:")
        print(f"- Market Value (working condition): R{market_value:,.2f}")
        print(f"- Repair Costs: -R{repair_cost:,.2f}")
        print(f"- Value to Us: R{value_to_us:,.2f}")
        print(f"- Minimum Floor (20%): R{min_value:,.2f}\n")

        return round(value_to_us, 2)

    def requires_device_unlock_check(self, category):
        """
        Check if this product type requires device unlock verification

        Args:
            category (str): Product category

        Returns:
            bool: True if device lock check is needed
        """

        lockable_categories = [
            'phone', 'smartphone', 'mobile', 'iphone', 'android',
            'tablet', 'ipad',
            'laptop', 'notebook', 'macbook', 'computer',
            'watch', 'smartwatch', 'apple watch'
        ]

        return category.lower() in lockable_categories
