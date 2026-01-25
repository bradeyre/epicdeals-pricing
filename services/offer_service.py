from config import Config
from services.price_research_service import PriceResearchService
from services.repair_cost_service import RepairCostService
from services.condition_assessment_service import ConditionAssessmentService
from services.intelligent_repair_cost_service import IntelligentRepairCostService
from utils.courier_checker import is_courier_eligible, get_courier_rejection_message, get_business_model_options


class OfferService:
    """
    Calculates purchase offers based on market value and repair costs
    - Sell Now: 65% of market value
    - Consignment: 85% of sale price (free collection included)
    - Enhanced with condition assessment for accurate pricing
    - NEW: Intelligent repair cost research using Perplexity
    """

    def __init__(self):
        self.price_research_service = PriceResearchService()
        self.repair_cost_service = RepairCostService()  # Legacy fallback
        self.condition_service = ConditionAssessmentService()
        self.intelligent_repair_service = IntelligentRepairCostService()  # NEW!
        self.sell_now_percentage = Config.SELL_NOW_PERCENTAGE
        self.consignment_percentage = Config.CONSIGNMENT_PERCENTAGE

    def calculate_offer(self, product_info, damage_info=None):
        """
        Calculate offer for a product

        Args:
            product_info: Dict with product details
            damage_info: Dict with damage details (optional)

        Returns:
            Dict with:
                - offer_amount: Final offer in ZAR
                - market_value: Estimated market value
                - repair_costs: Estimated repair costs
                - calculation_breakdown: Step-by-step calculation
                - confidence: Overall confidence score
                - recommendation: instant_offer or email_review
                - reason: Why this recommendation
                - courier_eligible: True/False
                - consignment_option: Dict with consignment model details
        """

        # Step 0: Check courier eligibility
        print("Checking courier eligibility...")
        courier_check = is_courier_eligible(product_info)

        if not courier_check['eligible']:
            return {
                'offer_amount': None,
                'market_value': None,
                'repair_costs': 0,
                'calculation_breakdown': {},
                'confidence': 0,
                'recommendation': 'non_courier_item',
                'reason': courier_check['reason'],
                'courier_eligible': False,
                'consignment_option': None
            }

        # Step 1: Research market prices
        print("Researching market prices...")
        price_research = self.price_research_service.research_prices(product_info)

        # If no prices found, ask user for estimate
        if price_research.get('needs_user_estimate'):
            return {
                'offer_amount': None,
                'market_value': None,
                'repair_costs': 0,
                'calculation_breakdown': {},
                'confidence': 0,
                'recommendation': 'user_estimate',
                'reason': 'No market prices found - requesting user estimate',
                'price_research': price_research
            }

        market_value = price_research.get('market_value')

        # If no market value but not flagged for user estimate, return email review
        if not market_value:
            return {
                'offer_amount': None,
                'market_value': None,
                'repair_costs': 0,
                'calculation_breakdown': {},
                'confidence': 0,
                'recommendation': 'email_review',
                'reason': 'No market prices found',
                'price_research': price_research
            }

        # Step 2: Research intelligent repair costs (NEW - Perplexity powered!)
        print("Researching intelligent repair costs...")
        condition = product_info.get('condition', 'good')
        damage_details = product_info.get('damage_details', [])
        category = product_info.get('category', 'other')

        # Use intelligent repair service to research actual costs
        repair_research = self.intelligent_repair_service.research_all_damages(
            product_info,
            damage_details
        )

        repair_costs = repair_research.get('total_repair_cost', 0)
        repair_explanation = repair_research.get('explanation', '')

        # Step 3: Apply condition multiplier
        print("Applying condition multiplier...")
        # Parse condition from new format: "Pristine - Like new, no visible wear (95-100% value)"
        # Extract just the first word (pristine, excellent, good, fair, poor)
        condition_key = (condition.lower().split('-')[0].split('(')[0].strip() if condition else 'good')

        condition_multiplier = self.condition_service.CONDITION_MULTIPLIERS.get(
            condition_key,
            0.775  # Default to "good" multiplier
        )

        print(f"Condition: {condition} → Key: {condition_key} → Multiplier: {condition_multiplier}")

        # Calculate adjusted value
        # Formula: (Market Value × Condition Multiplier) - Repair Costs
        after_condition = market_value * condition_multiplier
        adjusted_value = max(0, after_condition - repair_costs)

        print(f"\nPricing Calculation:")
        print(f"- Market Value: R{market_value:,.2f}")
        print(f"- Condition ({condition}): {condition_multiplier * 100:.0f}% = R{after_condition:,.2f}")
        print(f"- Repair Costs: -R{repair_costs:,.2f}")
        print(f"- Adjusted Value: R{adjusted_value:,.2f}\n")

        # Step 4: Legacy support for old damage_info format
        if damage_info and not damage_details:
            print("Using legacy repair cost estimate...")
            legacy_repair = self.repair_cost_service.estimate_repair_costs(product_info, damage_info)
            legacy_costs = legacy_repair.get('total_repair_cost', 0)
            if legacy_costs > 0:
                adjusted_value = max(0, adjusted_value - legacy_costs)
                repair_costs += legacy_costs

        # Step 5: Calculate offers for both models
        # Sell Now: Adjusted Value × 65%
        # Consignment: Adjusted Value × 85% (free collection)
        adjusted_value = max(0, adjusted_value)

        sell_now_offer = adjusted_value * self.sell_now_percentage
        sell_now_offer = round(sell_now_offer / 10) * 10  # Round to nearest R10

        # For backward compatibility, use sell_now as default offer_amount
        offer_amount = sell_now_offer

        # Step 4: Validate offer is within acceptable range
        if offer_amount < Config.MIN_ITEM_VALUE:
            return {
                'offer_amount': offer_amount,
                'market_value': market_value,
                'repair_costs': repair_costs,
                'calculation_breakdown': {
                    'market_value': market_value,
                    'repair_costs': repair_costs,
                    'adjusted_value': adjusted_value,
                    'sell_now_percentage': self.sell_now_percentage,
                    'final_offer': offer_amount
                },
                'confidence': price_research.get('confidence', 0),
                'recommendation': 'email_review',
                'reason': f'Offer amount (R{offer_amount:,.2f}) below minimum threshold (R{Config.MIN_ITEM_VALUE:,})',
                'price_research': price_research,
                'repair_estimate': repair_research
            }

        if offer_amount > Config.MAX_ITEM_VALUE * self.sell_now_percentage:
            return {
                'offer_amount': offer_amount,
                'market_value': market_value,
                'repair_costs': repair_costs,
                'calculation_breakdown': {
                    'market_value': market_value,
                    'repair_costs': repair_costs,
                    'adjusted_value': adjusted_value,
                    'sell_now_percentage': self.sell_now_percentage,
                    'final_offer': offer_amount
                },
                'confidence': price_research.get('confidence', 0),
                'recommendation': 'email_review',
                'reason': f'Offer amount (R{offer_amount:,.2f}) above maximum threshold',
                'price_research': price_research,
                'repair_estimate': repair_research
            }

        # Step 5: Calculate consignment option
        # Consignment model: Seller gets 85% of sale price (free collection)
        # Assume sale price = adjusted_value (market_value - repair_costs)
        consignment_payout = adjusted_value * self.consignment_percentage
        consignment_payout = max(0, round(consignment_payout / 10) * 10)  # Round to nearest R10

        # Check business model eligibility
        model_options = get_business_model_options(product_info)

        consignment_option = {
            'expected_sale_price': adjusted_value,
            'commission_rate': 1 - self.consignment_percentage,  # 15%
            'commission_amount': adjusted_value * (1 - self.consignment_percentage),
            'courier_fee': 0,  # Free collection for customer
            'courier_cost_internal': Config.COURIER_COST_INTERNAL,  # What we pay
            'seller_payout': consignment_payout,
            'payment_terms': 'Paid 2 working days after buyer receives the item',
            'consignment_period': f'{Config.CONSIGNMENT_PERIOD_DAYS} days',
            'insurance': 'Fully insured while in our possession'
        }

        # Step 6: Determine if we should make instant offer or email for review
        overall_confidence = self._calculate_overall_confidence(
            price_research.get('confidence', 0),
            repair_research.get('confidence', 1.0),
            len(price_research.get('prices_found', []))
        )

        if overall_confidence >= Config.CONFIDENCE_THRESHOLD:
            recommendation = 'instant_offer'
            reason = 'High confidence in pricing and repair cost estimates'
        else:
            recommendation = 'email_review'
            reason = self._determine_review_reason(price_research, repair_research, overall_confidence)

        return {
            'offer_amount': offer_amount,
            'market_value': market_value,
            'repair_costs': repair_costs,
            'repair_explanation': repair_explanation,  # NEW: Transparent breakdown!
            'after_condition': after_condition,  # Value after condition multiplier
            'adjusted_value': adjusted_value,  # Final value after repairs
            'sell_now_offer': sell_now_offer,  # For frontend display
            'consignment_payout': consignment_payout,  # For frontend display
            'calculation_breakdown': {
                'market_value': market_value,
                'condition': condition,
                'condition_multiplier': condition_multiplier,
                'after_condition': after_condition,
                'repair_costs': repair_costs,
                'adjusted_value': adjusted_value,
                'sell_now_percentage': self.sell_now_percentage,
                'sell_now_offer': sell_now_offer,
                'consignment_percentage': self.consignment_percentage,
                'final_offer': offer_amount
            },
            'confidence': overall_confidence,
            'recommendation': recommendation,
            'reason': reason,
            'price_research': price_research,
            'repair_estimate': repair_research,  # NEW: Intelligent research results
            'courier_eligible': True,
            'consignment_option': consignment_option,
            'model_options': model_options  # Which models are available
        }

    def _calculate_overall_confidence(self, price_confidence, repair_confidence, listing_count):
        """
        Calculate overall confidence score

        Factors:
        - Price research confidence (AI assessment)
        - Repair cost confidence
        - Number of listings found
        """

        # Weight by number of listings
        listing_factor = min(1.0, listing_count / 5)  # Max out at 5 listings

        # Combine confidences
        overall = (
            price_confidence * 0.5 +
            repair_confidence * 0.3 +
            listing_factor * 0.2
        )

        return overall

    def _determine_review_reason(self, price_research, repair_estimate, confidence):
        """Determine why manual review is needed"""

        reasons = []

        if price_research.get('total_listings', 0) < 3:
            reasons.append('Few comparable listings found')

        if price_research.get('confidence', 0) < 0.6:
            reasons.append('Inconsistent pricing data')

        if repair_estimate.get('total_repair_cost', 0) > 0 and repair_estimate.get('confidence', 1.0) < 0.7:
            reasons.append('Uncertain repair cost estimates')

        if not reasons:
            reasons.append(f'Confidence score ({confidence:.0%}) below threshold')

        return '; '.join(reasons)

    def calculate_offer_from_user_estimate(self, product_info, user_estimate, damage_info=None):
        """
        Calculate offer based on user's estimate when no market data found

        Args:
            product_info: Dict with product details
            user_estimate: User's estimated value (float/int)
            damage_info: Dict with damage details (optional)

        Returns:
            Dict with offer details (always requires manual review)
        """

        # Convert user estimate to float
        try:
            user_estimate = float(user_estimate)
        except (ValueError, TypeError):
            return {
                'success': False,
                'error': 'Invalid estimate amount'
            }

        # Estimate repair costs if damaged
        repair_estimate = self.repair_cost_service.estimate_repair_costs(product_info, damage_info)
        repair_costs = repair_estimate.get('total_repair_cost', 0)

        # Calculate offer: (User Estimate - Repair Costs) × 70%
        adjusted_value = max(0, user_estimate - repair_costs)
        offer_amount = adjusted_value * self.offer_percentage

        # Round to nearest R10
        offer_amount = round(offer_amount / 10) * 10

        return {
            'offer_amount': offer_amount,
            'market_value': user_estimate,
            'repair_costs': repair_costs,
            'calculation_breakdown': {
                'user_estimate': user_estimate,
                'repair_costs': repair_costs,
                'adjusted_value': adjusted_value,
                'offer_percentage': self.offer_percentage,
                'final_offer': offer_amount
            },
            'confidence': 0.3,  # Low confidence - based on user estimate
            'recommendation': 'manual_review',
            'reason': 'Offer based on your estimate - manual assessment needed',
            'repair_estimate': repair_estimate,
            'based_on_user_estimate': True
        }

    def format_offer_message(self, offer_data, customer_info=None):
        """
        Format a friendly offer message for the customer

        Args:
            offer_data: Output from calculate_offer()
            customer_info: Optional customer information

        Returns:
            String with formatted offer message
        """

        # Check for non-courier items
        if offer_data['recommendation'] == 'non_courier_item':
            return f"""Thank you for your interest in EpicDeals!

{offer_data['reason']}

We're constantly expanding our services, so please check back in the future!"""

        if offer_data['recommendation'] == 'instant_offer':
            consignment = offer_data.get('consignment_option', {})
            model_options = offer_data.get('model_options', {})
            sell_now_available = model_options.get('sell_now_available', True)

            message = f"""Thank you for your interest in selling to EpicDeals!

Based on our market research, we have {'TWO options' if sell_now_available else 'an option'} for you:

**Market Value (Median): R{offer_data['market_value']:,.2f}**

"""

            # Show transparent repair cost breakdown if any
            repair_explanation = offer_data.get('repair_explanation', '')
            if repair_explanation:
                message += repair_explanation
                message += f"**Adjusted Value: R{offer_data.get('adjusted_value', offer_data['market_value']):,.2f}**\n\n"

            message += "---\n\n"

            # Show Sell Now option only if available (electronics)
            if sell_now_available:
                message += f"""**OPTION 1: Sell to us NOW**
💰 **Immediate Payment: R{offer_data['offer_amount']:,.2f}**

How we calculated this:
- Market Value: R{offer_data['market_value']:,.2f}
"""

                if offer_data['repair_costs'] > 0:
                    message += f"- Repair Costs: R{offer_data['repair_costs']:,.2f}\n"
                    message += f"- Adjusted Value: R{offer_data['market_value'] - offer_data['repair_costs']:,.2f}\n"

                message += f"- Our Offer (65%): R{offer_data['offer_amount']:,.2f}\n\n"
                message += "✓ Get paid within 2 working days\n"
                message += "✓ FREE collection from your door\n"
                message += "✓ No waiting, no hassle\n\n"
                message += "---\n\n"

            # Always show consignment option
            option_number = "2" if sell_now_available else ""
            payout_difference = consignment.get('seller_payout', 0) - offer_data.get('offer_amount', 0)

            message += f"""**OPTION {option_number}: List on Consignment**
💰 **You Get: R{consignment.get('seller_payout', 0):,.2f}** (after sale)"""

            if sell_now_available and payout_difference > 0:
                message += f"""
🎯 **That's R{payout_difference:,.0f} MORE than Sell Now!**

"""

            message += f"""

How it works:
- We list your item for R{consignment.get('expected_sale_price', 0):,.2f}
- Our commission (15%): R{consignment.get('commission_amount', 0):,.2f}
- Collection: FREE (normally R100)
- Your payout: R{consignment.get('seller_payout', 0):,.2f}
- Payment: {consignment.get('payment_terms', '')}
- Consignment period: {consignment.get('consignment_period', '60 days')}

✓ Earn more (85% vs 65%)
✓ FREE collection from your door
✓ Fully insured while with us
✓ We handle ALL buyer interactions
✓ Professional photos & listing
✓ No returns to you (we handle any issues)
✓ Typically sells within 14 days

"""

            message += """---

**Important Terms:**
• Items fully insured while in our possession
• Unsold after 60 days? We return it at our cost
• Price too high? We'll suggest adjustments after 21 days
• You can request price changes anytime

Both offers valid for 48 hours. Which option works best for you?"""

        else:
            message = f"""Thank you for your interest in selling to EpicDeals!

We've gathered information about your item, but we'd like to review it personally to give you the best offer.

**Estimated Market Value (Median): R{offer_data['market_value']:,.2f}**

Reason for manual review: {offer_data['reason']}

We offer two models:
1. **Buy Outright**: Immediate payment (~70% of market value)
2. **Consignment**: List and sell on your behalf (~80% minus fees after sale)

Our team will contact you within 2 working days with personalized offers for both options.
"""

        return message
