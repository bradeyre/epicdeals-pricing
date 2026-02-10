"""
Guardrail Engine for EpicDeals v3.0

The engine that keeps AI honest. Enforces non-negotiable rules:
- Never re-ask questions
- Max 4 questions per conversation
- Always advance to offer
- Handle "I don't know" gracefully

This is the discipline layer. Intelligence lives in Claude, discipline lives here.
"""

from typing import Dict, List, Set, Optional, Any
from enum import Enum
import json


class ConversationState(Enum):
    """States the conversation can be in"""
    IDENTIFYING = "identifying"  # User just said what they want to sell
    QUESTIONING = "questioning"  # Asking clarifying questions
    CALCULATING = "calculating"  # Generating offer
    OFFER_READY = "offer_ready"  # Offer calculated, showing to user
    COLLECTING_INFO = "collecting_info"  # Collecting customer details after acceptance


class GuardrailEngine:
    """
    Manages conversation state and enforces rules the AI cannot break.

    Key Responsibilities:
    - Track what's been asked and answered
    - Validate AI responses (reject duplicates)
    - Enforce category-specific question caps
    - Decide when to calculate offer
    - Provide UI options for frontend
    """

    # Category normalization map - maps AI's raw categories to super-categories
    CATEGORY_MAP = {
        'electronics': [
            'phone', 'smartphone', 'iphone', 'android', 'samsung', 'mobile', 'cellphone',
            'tablet', 'ipad', 'laptop', 'macbook', 'computer', 'notebook',
            'camera', 'dslr', 'mirrorless', 'lens',
            'console', 'playstation', 'xbox', 'nintendo', 'switch',
            'tv', 'television', 'monitor',
            'smartwatch', 'watch', 'apple watch',
            'earbuds', 'headphones', 'speaker', 'airpods', 'beats',
            'drone', 'gopro'
        ],
        'vehicle': [
            'car', 'vehicle', 'motorcycle', 'motorbike', 'scooter',
            'bakkie', 'truck', 'suv', 'sedan', 'hatchback'
        ],
        'appliance': [
            'appliance', 'vacuum', 'dyson', 'hairdryer', 'straightener', 'ghd',
            'airwrap', 'kitchen', 'mixer', 'blender', 'microwave',
            'fridge', 'refrigerator', 'washing machine', 'dishwasher', 'dryer', 'oven'
        ],
        'fashion': [
            'shoes', 'sneakers', 'nike', 'adidas', 'jordan', 'puma',
            'bag', 'handbag', 'purse', 'backpack',
            'clothing', 'jacket', 'dress', 'shirt'
        ],
        'furniture': [
            'furniture', 'couch', 'sofa', 'table', 'chair',
            'desk', 'bed', 'mattress', 'shelf', 'cabinet', 'drawer'
        ],
    }

    # Super-category to question limit mapping
    CATEGORY_LIMITS = {
        'electronics': 4,    # Storage, condition, unlock, contract
        'vehicle': 6,        # Mileage, year, service, accident, condition, features
        'appliance': 3,      # Age, condition, completeness
        'fashion': 3,        # Size, condition, authenticity
        'furniture': 2,      # Age, condition
    }

    DEFAULT_QUESTION_LIMIT = 4  # Fallback for unknown categories

    def __init__(self):
        # Product identification
        self.product_identified: bool = False
        self.product_info: Dict[str, Any] = {}
        self.question_limit: int = self.DEFAULT_QUESTION_LIMIT  # Dynamic limit based on category

        # Question tracking
        self.approved_questions: List[str] = []  # Questions AI proposed and we approved
        self.collected_fields: Dict[str, Any] = {}  # field_name -> value for answered questions
        self.asked_fields: Set[str] = set()  # Fields that have been ASKED (even if "not sure")
        self.question_count: int = 0  # Number of questions asked so far

        # State management
        self.state: ConversationState = ConversationState.IDENTIFYING
        self.ui_options: List[Dict[str, Any]] = []  # Quick-select buttons/checklist for current question

        # Conversation history for context
        self.conversation_turns: List[Dict[str, str]] = []

    def record_user_message(self, message: str) -> None:
        """Record a message from the user"""
        self.conversation_turns.append({
            'role': 'user',
            'content': message
        })

    def record_ai_message(self, message: str) -> None:
        """Record a message from the AI"""
        self.conversation_turns.append({
            'role': 'assistant',
            'content': message
        })

    def _normalise_category(self, raw_category: str) -> str:
        """
        Normalise AI's raw category string to a super-category.
        Uses fuzzy keyword matching to handle variations.

        Args:
            raw_category: Category string from AI (e.g., 'smartphone', 'Samsung Galaxy', 'car')

        Returns:
            Super-category string ('electronics', 'vehicle', etc.) or 'general'
        """
        if not raw_category:
            return 'general'

        lower = raw_category.lower().strip()

        # Check each super-category's keywords
        for super_cat, keywords in self.CATEGORY_MAP.items():
            # Exact match or fuzzy keyword match
            if lower in keywords or any(kw in lower for kw in keywords):
                return super_cat

        return 'general'

    def set_product_info(self, product_info: Dict[str, Any]) -> None:
        """
        Set the identified product information.
        ENHANCED: Flattens ALL nested specs, auto-collects everything meaningful.

        Args:
            product_info: Product data from AI with possible nested 'specs' dict
        """
        # Flatten ALL nested specs to top level (v3.1 corrected approach)
        specs = product_info.pop('specs', {})
        if isinstance(specs, dict):
            for key, value in specs.items():
                # Only promote if value is meaningful
                if value and str(value).strip():
                    # Filter out placeholder/junk values
                    value_str = str(value).lower()
                    if value_str not in ('unknown', 'not specified', 'if mentioned', 'n/a', 'none'):
                        # Don't overwrite explicit top-level values
                        if key not in product_info or not product_info[key]:
                            product_info[key] = value

        # Auto-collect EVERY field that has a meaningful value
        # (except metadata fields like name, brand, category)
        metadata_fields = {'name', 'brand', 'category', 'model'}
        for key, value in product_info.items():
            if key not in metadata_fields and value and str(value).strip():
                value_str = str(value).lower()
                if value_str not in ('unknown', 'not specified', 'if mentioned', 'n/a'):
                    self.collected_fields[key] = value
                    self.asked_fields.add(key)

        self.product_info = product_info
        self.product_identified = True

        # Normalise category and set question limit
        raw_category = product_info.get('category', 'general')
        normalised_category = self._normalise_category(raw_category)
        self.question_limit = self.CATEGORY_LIMITS.get(normalised_category, self.DEFAULT_QUESTION_LIMIT)

        print(f"\n🎯 PRODUCT IDENTIFIED: {product_info.get('brand', '')} {product_info.get('model', '')}")
        print(f"   Category: {raw_category} → {normalised_category}")
        print(f"   Question limit: {self.question_limit}")
        print(f"   Auto-collected fields: {list(self.collected_fields.keys())}")

    # Fields that ALWAYS require user input (never auto-skip from extraction)
    MANDATORY_QUESTION_FIELDS = {'condition', 'damage', 'damage_details', 'condition_details'}

    def approve_questions(self, proposed_questions: List[str]) -> List[str]:
        """
        Review AI's proposed questions and approve only valid ones.

        Rules:
        - Condition/damage is ALWAYS asked FIRST (mandatory, highest priority)
        - Skip fields already collected from user input (auto-extracted specs)
        - Respect the category-specific question cap

        Returns: List of approved question field names
        """
        approved = []

        # STEP 1: Separate mandatory fields (condition) from optional ones
        mandatory = []
        optional = []

        for field in proposed_questions:
            if field in self.MANDATORY_QUESTION_FIELDS:
                mandatory.append(field)
            else:
                optional.append(field)

        # Ensure condition is always included — inject if AI didn't propose it
        if not mandatory:
            mandatory = ['condition']

        # STEP 2: Build final ordered list — mandatory FIRST, then optional
        ordered = mandatory + optional

        for field in ordered:
            # Already asked by the USER? Skip (not just auto-collected)
            if field in self.asked_fields and field not in self.MANDATORY_QUESTION_FIELDS:
                print(f"   ⏭️  Skipping '{field}' - already asked/answered")
                continue

            # Auto-collected spec? Skip UNLESS it's a mandatory user-input field
            if field in self.collected_fields and field not in self.MANDATORY_QUESTION_FIELDS:
                print(f"   ⏭️  Skipping '{field}' - auto-collected from input")
                continue

            # Already approved? Skip duplicates
            if field in approved:
                continue

            # Would exceed cap? Stop approving
            if len(approved) + self.question_count >= self.question_limit:
                print(f"   🛑 Reached {self.question_limit}-question cap, stopping approvals")
                break

            approved.append(field)

        self.approved_questions = approved
        print(f"   ✅ Approved questions: {approved}")
        return approved

    def validate_ai_question(self, question_field: str, question_text: str,
                            quick_options: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Validate that the AI's proposed question is allowed.

        Returns: {
            'valid': bool,
            'reason': str (if invalid),
            'ui_options': list (if valid)
        }
        """
        # Rule 1: NEVER RE-ASK
        if question_field in self.asked_fields:
            return {
                'valid': False,
                'reason': f"Field '{question_field}' already asked"
            }

        if question_field in self.collected_fields:
            return {
                'valid': False,
                'reason': f"Field '{question_field}' already collected"
            }

        # Rule 2: MAX QUESTIONS (category-specific)
        if self.question_count >= self.question_limit:
            return {
                'valid': False,
                'reason': f'Maximum {self.question_limit} questions reached'
            }

        # Valid! Record it
        self.asked_fields.add(question_field)
        self.question_count += 1

        # Store UI options for frontend
        if quick_options:
            self.ui_options = [{
                'type': 'quick_select',
                'options': quick_options
            }]
        else:
            self.ui_options = []

        print(f"\n   ❓ Question {self.question_count}/4: {question_field}")
        print(f"   📋 Asked fields: {self.asked_fields}")

        return {
            'valid': True,
            'ui_options': self.ui_options
        }

    def record_answer(self, field_name: str, value: Any) -> None:
        """
        Record the user's answer to a question.

        Handles:
        - Direct answers ("128GB", "Screen cracked")
        - Uncertain answers ("I don't know" -> marks as 'unknown')
        - Multiple values (checkboxes -> list)
        - "No damage" normalization (v3.1 Fix 4)
        """
        # Handle uncertain answers
        if isinstance(value, str):
            uncertain_phrases = ['not sure', "don't know", 'unsure', 'unknown', 'idk']
            if any(phrase in value.lower() for phrase in uncertain_phrases):
                value = 'unknown'
                print(f"   ⚠️  Uncertain answer for '{field_name}' - marking as 'unknown'")

        # Normalise 'no damage' answers (v3.1 Fix 4)
        # If user selects "✅ No issues" from checklist, record as 'no_damage' not the emoji string
        if field_name in ('condition', 'damage', 'damage_details') and isinstance(value, list):
            no_damage_indicators = [
                v for v in value
                if any(phrase in v.lower() for phrase in ['no issue', 'no damage', 'none', 'like new', '✅'])
            ]
            if no_damage_indicators:
                value = 'no_damage'
                print(f"   ✅ Normalized 'no damage' selection to 'no_damage'")

        self.collected_fields[field_name] = value
        self.asked_fields.add(field_name)  # Mark as both asked AND answered

        print(f"   ✅ Recorded: {field_name} = {value}")
        print(f"   📦 Collected fields: {len(self.collected_fields)}/{self.question_count}")

    def should_calculate_offer(self) -> bool:
        """
        Decide if we have enough information to calculate an offer.

        Returns True if:
        - Question cap reached (category-specific)
        - All approved questions have been asked AND answered
        - At least one question has been asked (never skip questioning entirely)
        """
        # SAFETY: Never trigger before at least one question has been asked
        if self.question_count == 0:
            print(f"\n   ⏳ NOT YET: No questions asked yet (question_count=0)")
            return False

        # Hit the cap? Always calculate
        if self.question_count >= self.question_limit:
            print(f"\n   🎯 TRIGGER CALCULATION: Question cap reached ({self.question_count}/{self.question_limit})")
            return True

        # All approved questions asked AND answered?
        # Count only USER-ANSWERED fields (fields in approved_questions that now have answers)
        if self.approved_questions:
            answered_approved = [f for f in self.approved_questions if f in self.collected_fields]
            if len(answered_approved) >= len(self.approved_questions):
                print(f"\n   🎯 TRIGGER CALCULATION: All {len(self.approved_questions)} approved questions answered")
                return True

        return False

    def get_state_for_prompt(self) -> str:
        """
        Generate a summary of current state for the AI prompt.
        This tells the AI what's already been collected so it never re-asks.
        """
        state = []

        state.append(f"PRODUCT: {self.product_info.get('name', 'Unknown')}")
        state.append(f"CATEGORY: {self.product_info.get('category', 'Unknown')}")

        if self.collected_fields:
            state.append("\nALREADY COLLECTED:")
            for field, value in self.collected_fields.items():
                state.append(f"  ✓ {field}: {value}")

        if self.asked_fields:
            state.append("\nALREADY ASKED (do not ask again):")
            for field in self.asked_fields:
                if field not in self.collected_fields:
                    state.append(f"  ⏭️  {field} (user was unsure)")

        state.append(f"\nQUESTIONS USED: {self.question_count}/{self.question_limit}")

        return "\n".join(state)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for Flask session storage (v3.1 Fix 5)"""
        return {
            'product_identified': self.product_identified,
            'product_info': self.product_info,
            'question_limit': self.question_limit,  # NEW: Include dynamic limit
            'approved_questions': self.approved_questions,
            'collected_fields': self.collected_fields,
            'asked_fields': list(self.asked_fields),  # Convert set to list for JSON
            'question_count': self.question_count,
            'state': self.state.value,
            'ui_options': self.ui_options,
            'conversation_turns': self.conversation_turns
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GuardrailEngine':
        """Deserialize from dict (Flask session) (v3.1 Fix 5)"""
        engine = cls()
        engine.product_identified = data.get('product_identified', False)
        engine.product_info = data.get('product_info', {})
        engine.question_limit = data.get('question_limit', cls.DEFAULT_QUESTION_LIMIT)  # NEW: Restore limit
        engine.approved_questions = data.get('approved_questions', [])
        engine.collected_fields = data.get('collected_fields', {})
        engine.asked_fields = set(data.get('asked_fields', []))  # Convert list back to set
        engine.question_count = data.get('question_count', 0)
        engine.state = ConversationState(data.get('state', 'identifying'))
        engine.ui_options = data.get('ui_options', [])
        engine.conversation_turns = data.get('conversation_turns', [])
        return engine

    def get_progress_info(self) -> Dict[str, Any]:
        """Get progress information for frontend display"""
        total_questions = min(len(self.approved_questions), self.question_limit)
        return {
            'current': self.question_count,
            'total': total_questions if total_questions > 0 else self.question_limit,
            'percentage': int((self.question_count / self.question_limit) * 100) if self.question_count > 0 else 0
        }

    def reset(self) -> None:
        """Reset the engine for a new conversation"""
        self.__init__()
