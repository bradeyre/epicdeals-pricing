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

Respond with ONLY this JSON:
{{
  "product_info": {{
    "name": "Full product name",
    "brand": "Brand name",
    "model": "Model/version",
    "category": "phone|laptop|vehicle|shoes|appliance|furniture|etc",
    "specs": {{
      "storage": "if mentioned",
      "year": "if mentioned or inferable (iPhone 14 = 2022)",
      "size": "if mentioned",
      "color": "if mentioned"
    }}
  }},
  "proposed_questions": ["field1", "field2", "field3"]
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

Examples:
- Phone condition: ["☐ Screen cracked", "☐ Back glass cracked", "☐ Battery <80%", "☐ None ✔"]
- Car condition: ["☐ Body dents", "☐ Engine warning", "☐ Tyres worn", "☐ None ✔"]
- Shoes condition: ["☐ Sole worn", "☐ Scuffs/stains", "☐ Box missing", "☐ None ✔"]

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

        prompt = f"""Generate a SHORT, friendly acknowledgment for: {product_name} ({category})

Keep it to ONE sentence. Be encouraging. Use South African tone.

Examples:
- "Nice, an iPhone 14! Those hold their value pretty well 👍"
- "A 2019 Polo Comfortline — solid choice, those are always in demand! 🚗"
- "AJ4 Retros! 🔥 Those are hot right now."

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
