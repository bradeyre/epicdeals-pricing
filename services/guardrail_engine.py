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
    - Enforce 4-question cap
    - Decide when to calculate offer
    - Provide UI options for frontend
    """

    def __init__(self):
        # Product identification
        self.product_identified: bool = False
        self.product_info: Dict[str, Any] = {}

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

    def set_product_info(self, product_info: Dict[str, Any]) -> None:
        """
        Set the identified product information.
        This is called after the AI extracts product details from the initial message.
        """
        self.product_info = product_info
        self.product_identified = True

        # Auto-collect any specs that came with the initial message
        if 'storage' in product_info:
            self.collected_fields['storage'] = product_info['storage']
            self.asked_fields.add('storage')

        if 'year' in product_info and product_info['year'] != 'unknown':
            self.collected_fields['year'] = product_info['year']
            self.asked_fields.add('year')

        if 'size' in product_info:
            self.collected_fields['size'] = product_info['size']
            self.asked_fields.add('size')

        print(f"\n🎯 PRODUCT IDENTIFIED: {product_info.get('brand', '')} {product_info.get('model', '')}")
        print(f"   Auto-collected fields: {list(self.collected_fields.keys())}")

    def approve_questions(self, proposed_questions: List[str]) -> List[str]:
        """
        Review AI's proposed questions and approve only valid ones.

        Removes:
        - Questions about fields already asked
        - Questions about fields already collected
        - Questions beyond the 4-question cap

        Returns: List of approved question field names
        """
        approved = []

        for field in proposed_questions:
            # Already asked or collected? Skip
            if field in self.asked_fields or field in self.collected_fields:
                print(f"   ⏭️  Skipping '{field}' - already asked/answered")
                continue

            # Would exceed cap? Stop approving
            if len(approved) + self.question_count >= 4:
                print(f"   🛑 Reached 4-question cap, stopping approvals")
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

        # Rule 2: MAX 4 QUESTIONS
        if self.question_count >= 4:
            return {
                'valid': False,
                'reason': 'Maximum 4 questions reached'
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
        """
        # Handle uncertain answers
        if isinstance(value, str):
            uncertain_phrases = ['not sure', "don't know", 'unsure', 'unknown', 'idk']
            if any(phrase in value.lower() for phrase in uncertain_phrases):
                value = 'unknown'
                print(f"   ⚠️  Uncertain answer for '{field_name}' - marking as 'unknown'")

        self.collected_fields[field_name] = value
        self.asked_fields.add(field_name)  # Mark as both asked AND answered

        print(f"   ✅ Recorded: {field_name} = {value}")
        print(f"   📦 Collected fields: {len(self.collected_fields)}/{self.question_count}")

    def should_calculate_offer(self) -> bool:
        """
        Decide if we have enough information to calculate an offer.

        Returns True if:
        - Question cap reached (4 questions)
        - All approved questions answered
        - Minimum required fields collected (product + condition)
        """
        # Hit the cap? Always calculate
        if self.question_count >= 4:
            print(f"\n   🎯 TRIGGER CALCULATION: Question cap reached (4/4)")
            return True

        # All approved questions answered?
        if self.approved_questions and len(self.collected_fields) >= len(self.approved_questions):
            print(f"\n   🎯 TRIGGER CALCULATION: All approved questions answered")
            return True

        # Minimum fields: must have condition/damage info
        if 'condition' in self.collected_fields or 'damage' in self.collected_fields:
            if len(self.collected_fields) >= 2:  # At least product + condition + 1 more
                print(f"\n   🎯 TRIGGER CALCULATION: Sufficient fields collected")
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

        state.append(f"\nQUESTIONS USED: {self.question_count}/4")

        return "\n".join(state)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for Flask session storage"""
        return {
            'product_identified': self.product_identified,
            'product_info': self.product_info,
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
        """Deserialize from dict (Flask session)"""
        engine = cls()
        engine.product_identified = data.get('product_identified', False)
        engine.product_info = data.get('product_info', {})
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
        total_questions = min(len(self.approved_questions), 4)
        return {
            'current': self.question_count,
            'total': total_questions if total_questions > 0 else 4,
            'percentage': int((self.question_count / 4) * 100) if self.question_count > 0 else 0
        }

    def reset(self) -> None:
        """Reset the engine for a new conversation"""
        self.__init__()
