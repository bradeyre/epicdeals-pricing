"""
AI Service for EpicDeals v3.0

Radically simplified from v2.0. The AI's job is simple:
1. Understand what the product is
2. Know what affects its resale value
3. Ask friendly questions
4. Extract structured answers

All the flow control, duplicate prevention, and rules enforcement
happens in GuardrailEngine. The AI just needs to be smart about products.
"""

import anthropic
import json
import re
from typing import Dict, List, Any, Optional
from config import Config


class AIServiceV3:
    """
    Simplified AI service for universal product pricing.

    Key differences from v2.0:
    - No flow logic in prompts (engine handles that)
    - No duplicate prevention rules (engine handles that)
    - No hardcoded product categories
    - Just: understand product + ask smart questions
    """

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        self.model_sonnet = "claude-sonnet-4-20250514"  # For conversations
        self.model_haiku = "claude-3-5-haiku-20241022"  # For fast parsing

    def identify_product(self, user_message: str) -> Dict[str, Any]:
        """
        Phase 1: Identify what the user wants to sell.

        Returns: {
            'product_info': {
                'name': str,
                'brand': str,
                'model': str,
                'category': str,
                'specs': dict  # Any specs mentioned (storage, year, size, etc.)
            },
            'proposed_questions': [field_name, field_name, ...]  # What to ask
        }
        """
        prompt = f"""You are a South African product pricing expert for EpicDeals.

The user wants to sell: "{user_message}"

Your job: Identify the product and propose 1-4 questions that would affect its resale price.

Think about what makes THIS specific product more or less valuable:
- Phones: storage, condition, unlock status, contract status
- Cars: mileage, condition, service history
- Shoes: size, condition, colorway, authenticity
- Appliances: age, condition, completeness (all attachments?)
- Furniture: age, condition, material/color
- Electronics: age, condition, included accessories

IMPORTANT:
- Extract any specs already mentioned (if user said "iPhone 14 128GB", storage is 128GB - don't ask again!)
- Only propose questions about things NOT mentioned
- Condition/damage is almost always relevant
- Keep it to 1-4 questions max

MODEL CONFIRMATION:
If the user's description is AMBIGUOUS about the exact model or variant, set "needs_model_confirmation" to true and provide a list of likely models in "model_options". Examples of when this is needed:
- "Sony headphones" → could be WH-1000XM3, XM4, or XM5 (very different prices)
- "MacBook" → could be Air or Pro, M1/M2/M3
- "Samsung Galaxy" → could be S23, S24, A series, etc.
- "iPhone" without a number → which generation?
- "VW Polo" → which year/engine variant?
- "Nike Dunks" → which colorway?

When the user IS specific enough (e.g. "iPhone 16 Pro 256GB", "Sony WH-1000XM4"), set "needs_model_confirmation" to false.

Respond with ONLY this JSON:
{{
  "product_info": {{
    "name": "Full product name",
    "brand": "Brand name",
    "model": "Model/version (your best guess if ambiguous)",
    "category": "phone|laptop|vehicle|shoes|appliance|furniture|etc",
    "specs": {{
      "storage": "if mentioned",
      "year": "if mentioned or inferable (iPhone 14 = 2022)",
      "size": "if mentioned",
      "color": "if mentioned"
    }}
  }},
  "proposed_questions": ["field1", "field2", "field3"],
  "needs_model_confirmation": false,
  "model_options": ["Model A", "Model B", "Model C"]
}}

Be smart about years: iPhone 16 = 2024, iPhone 15 = 2023, PS5 = 2020, etc.
"""

        try:
            response = self.client.messages.create(
                model=self.model_sonnet,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract JSON from response
            response_text = response.content[0].text.strip()
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                response_text = json_match.group(0)

            result = json.loads(response_text)

            print(f"\n🤖 AI IDENTIFICATION:")
            print(f"   Product: {result['product_info'].get('brand', '')} {result['product_info'].get('model', '')}")
            print(f"   Category: {result['product_info'].get('category', '')}")
            print(f"   Specs extracted: {result['product_info'].get('specs', {})}")
            print(f"   Proposed questions: {result['proposed_questions']}")

            return result

        except Exception as e:
            print(f"❌ Error identifying product: {e}")
            # Fallback: basic extraction
            return {
                'product_info': {
                    'name': user_message,
                    'brand': 'Unknown',
                    'model': user_message,
                    'category': 'general',
                    'specs': {}
                },
                'proposed_questions': ['condition', 'age']
            }

    def generate_question(self, field_name: str, product_info: Dict[str, Any],
                         collected_fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 2: Generate a friendly question for a specific field.

        Returns: {
            'question_text': str,  # Friendly, natural question
            'quick_options': list,  # Quick-select buttons
            'ui_type': 'quick_select' | 'checklist' | 'text'
        }
        """
        product_name = f"{product_info.get('brand', '')} {product_info.get('model', '')}".strip()
        category = product_info.get('category', 'item')

        prompt = f"""You are asking the seller a question about their {product_name} ({category}).

Field to ask about: {field_name}

Product details: {json.dumps(product_info, indent=2)}
Already collected: {json.dumps(collected_fields, indent=2)}

Generate a friendly, natural question with quick-select options.

PERSONALITY:
- Friendly South African tone
- Use emojis sparingly (👍, 🚗, ✅)
- Keep it conversational
- Be encouraging ("No stress - we factor that in fairly")

For CONDITION/DAMAGE questions, generate a checklist of common issues for THIS specific product type.

IMPORTANT: For iPhones, always include "Battery health under 85%" as an option in the condition checklist.
We need to know about battery health because under 85% means a battery replacement is needed before resale.

Examples:
- iPhone condition: ["Screen cracked/scratched", "Back glass cracked", "Camera lens damaged", "Battery health under 85%", "Water damage", "None - excellent condition ✅"]
- Other phone condition: ["Screen cracked/scratched", "Back glass cracked", "Camera lens damaged", "Battery issues", "Water damage", "None - excellent condition ✅"]
- Car condition: ["Body dents", "Engine warning", "Tyres worn", "None ✔"]
- Shoes condition: ["Sole worn", "Scuffs/stains", "Box missing", "None ✔"]

For DAMAGE_SEVERITY questions (follow-up after user reported damage):
- The user already told us WHAT damage exists (see "Already collected" above for their condition answer)
- Now ask HOW BAD it is for EACH reported issue
- Be specific to the damage they reported. Examples:
  - If "Screen cracked/scratched": ask "How would you describe the screen damage?" with options like ["Hairline scratches only", "Deep scratches (can feel with fingernail)", "Cracked but display works", "Cracked and display has issues"]
  - If "Back glass cracked": ["Small chip/crack", "Spider-web cracks", "Shattered"]
  - If "Dents": ["Small barely visible dents", "Noticeable dents", "Large dents affecting function"]
  - If "Sole worn": ["Light wear, plenty of life left", "Moderate wear, some tread left", "Heavy wear, needs resoling"]
- Use ui_type "quick_select" (NOT checklist - they pick the ONE that best describes it)
- If multiple damage items were reported, ask about the MOST significant one and include "Also describe: [other items]" as a text prompt
- Keep it friendly: "Just so we can factor this in accurately..."

For BATTERY_HEALTH questions (iPhones only):
- Ask what their iPhone battery health percentage is (Settings > Battery > Battery Health)
- Provide options: ["95-100%", "85-94%", "75-84%", "Under 75%", "Not sure"]
- Use ui_type "quick_select"
- Mention they can check in Settings > Battery > Battery Health

For other questions, provide 3-6 tap-able options.

Respond with ONLY this JSON:
{{
  "question_text": "Your friendly question here",
  "quick_options": ["Option 1", "Option 2", "Option 3"],
  "ui_type": "quick_select"  // or "checklist" for condition questions
}}
"""

        try:
            response = self.client.messages.create(
                model=self.model_sonnet,
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text.strip()
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                response_text = json_match.group(0)

            result = json.loads(response_text)

            print(f"\n💬 AI QUESTION:")
            print(f"   Field: {field_name}")
            print(f"   Text: {result['question_text'][:80]}...")
            print(f"   Options: {len(result.get('quick_options', []))} provided")

            return result

        except Exception as e:
            print(f"❌ Error generating question: {e}")
            # Fallback: basic question
            return {
                'question_text': f"Tell me about the {field_name} of your {product_name}",
                'quick_options': [],
                'ui_type': 'text'
            }

    def extract_answer(self, user_answer: str, field_name: str,
                      context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Extract structured value from user's natural language answer.

        Handles:
        - Direct answers: "128GB" -> "128GB"
        - Multiple items: "Screen cracked, battery issues" -> ["screen_cracked", "battery_issues"]
        - Uncertain: "not sure" -> "unknown"
        - Natural language: "about 85,000" -> 85000
        """
        user_answer = user_answer.strip()

        # Handle uncertain answers
        uncertain_phrases = ['not sure', "don't know", 'unsure', 'idk']
        if any(phrase in user_answer.lower() for phrase in uncertain_phrases):
            return 'unknown'

        # For condition/damage, might have multiple items
        if 'condition' in field_name.lower() or 'damage' in field_name.lower():
            # Check for "none" or "no issues"
            if any(phrase in user_answer.lower() for phrase in ['none', 'no issues', 'perfect', 'excellent']):
                return 'no_damage'

            # Extract multiple issues
            # This is simplified - in production, use AI to parse complex answers
            return user_answer

        # For numeric fields (mileage, year), extract numbers
        if 'mileage' in field_name.lower() or 'km' in field_name.lower():
            numbers = re.findall(r'\d+', user_answer.replace(',', ''))
            if numbers:
                return int(numbers[0])

        if 'year' in field_name.lower():
            numbers = re.findall(r'20\d{2}|19\d{2}', user_answer)
            if numbers:
                return int(numbers[0])

        # Default: return as-is
        return user_answer

    def generate_acknowledgment(self, product_info: Dict[str, Any]) -> str:
        """
        Generate a friendly acknowledgment after product identification.

        Examples:
        - "Nice, an iPhone 14! Those hold their value pretty well 👍"
        - "A 2019 Polo Comfortline — solid choice, those are always in demand! 🚗"
        - "AJ4 Retros! 🔥 Those are hot right now."
        """
        product_name = f"{product_info.get('brand', '')} {product_info.get('model', '')}".strip()
        category = product_info.get('category', '')

        prompt = f"""The user wants to SELL their {product_name} ({category}) through our second-hand marketplace.

Generate a SHORT, friendly acknowledgment. ONE sentence only. South African tone.

IMPORTANT: The user is SELLING this item, not buying it. Focus on how well the item sells, its demand, or its resale value.

Good examples (seller context):
- "Nice, an iPhone 14! Those hold their value really well 👍"
- "A 2019 Polo — always in demand on the second-hand market! 🚗"
- "AJ4 Retros! 🔥 Those sell fast."
- "Sharp choice to sell now — Dyson Airwraps are hot right now!"

BAD examples (sounds like buying — DO NOT do this):
- "You'll be sorted with this gadget!" ← wrong, they're selling it
- "Great pickup!" ← wrong, they're not buying

Just the acknowledgment, no extra text:"""

        try:
            response = self.client.messages.create(
                model=self.model_haiku,  # Fast for this
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )

            ack = response.content[0].text.strip()
            # Remove quotes if AI added them
            ack = ack.strip('"\'')
            return ack

        except:
            return f"Great, a {product_name}!"
