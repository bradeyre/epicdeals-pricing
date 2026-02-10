from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from config import Config
import os
import secrets
import sys
import traceback

print("=" * 60)
print("STARTING APPLICATION")
print("=" * 60)

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
CORS(app)  # Enable CORS for WordPress embedding

# Session version - forces all old sessions to reset on deployment
# Change this value (or it auto-changes via hash) to invalidate all existing sessions
SESSION_VERSION = "v3.1.8"


@app.before_request
def check_session_version():
    """Invalidate stale sessions from before this deployment"""
    if session.get('_version') != SESSION_VERSION:
        session.clear()
        session['_version'] = SESSION_VERSION

# Initialize services with error handling
ai_service = None
ai_service_v3 = None  # NEW: v3.0 architecture
offer_service = None
email_service = None

try:
    print("Importing AIService (v2.0)...")
    from services.ai_service import AIService
    print("✅ AIService v2.0 imported")

    print("Initializing AIService v2.0...")
    ai_service = AIService()
    print("✅ AIService v2.0 initialized")

    print("Importing AIServiceV3 (v3.0)...")
    from services.ai_service_v3 import AIServiceV3
    from services.guardrail_engine import GuardrailEngine
    print("✅ AIService v3.0 imported")

    print("Initializing AIService v3.0...")
    ai_service_v3 = AIServiceV3()
    print("✅ AIService v3.0 initialized")

    print("Importing OfferService...")
    from services.offer_service import OfferService
    print("✅ OfferService imported")

    print("Initializing OfferService...")
    offer_service = OfferService()
    print("✅ OfferService initialized")

    print("Importing EmailService...")
    from services.email_service import EmailService
    print("✅ EmailService imported")

    print("Initializing EmailService...")
    email_service = EmailService()
    print("✅ EmailService initialized")

    print("Importing utils...")
    from utils.validators import Validators
    from utils.courier_checker import is_courier_eligible, get_courier_rejection_message
    print("✅ Utils imported")

    print("\n" + "=" * 60)
    print("ALL SERVICES INITIALIZED SUCCESSFULLY (v2.0 + v3.0)")
    print("=" * 60 + "\n")

except Exception as e:
    print(f"\n{'='*60}")
    print(f"❌ INITIALIZATION ERROR:")
    print(f"{'='*60}")
    print(f"Error: {e}")
    print(f"\nFull traceback:")
    traceback.print_exc()
    print(f"{'='*60}\n")
    sys.exit(1)


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/start-conversation', methods=['POST'])
def start_conversation():
    """Initialize a new conversation"""
    try:
        if ai_service is None:
            return jsonify({
                'success': False,
                'error': 'AI service not initialized. Please contact support.'
            }), 500

        # Create new session
        session_id = secrets.token_urlsafe(16)
        session['conversation_id'] = session_id
        session['conversation_history'] = []
        session['product_info'] = {}
        session['courier_checked'] = False  # Reset courier check flag

        # Get initial question from AI
        next_question = ai_service.get_next_question([], {})

        return jsonify({
            'success': True,
            'session_id': session_id,
            'question': next_question
        })
    except Exception as e:
        print(f"❌ Error in start_conversation: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error starting conversation: {str(e)}'
        }), 500


@app.route('/api/submit-answer', methods=['POST'])
def submit_answer():
    """Handle user's answer and get next question or final offer"""

    data = request.json
    user_answer = data.get('answer', '')

    # Get conversation state from session
    conversation_history = session.get('conversation_history', [])
    product_info = session.get('product_info', {})

    print(f"\n{'='*60}")
    print(f"DEBUG - BEFORE PROCESSING:")
    print(f"User answer: {user_answer}")
    print(f"Current product_info: {product_info}")
    print(f"Conversation history length: {len(conversation_history)}")
    print(f"{'='*60}\n")

    # Add user's answer to history
    conversation_history.append({
        'role': 'user',
        'content': user_answer
    })

    # Quick courier check on raw user input (before AI extraction)
    # This catches obvious non-courier items immediately
    if not session.get('courier_checked'):
        quick_check = is_courier_eligible({'category': user_answer.lower(), 'brand': '', 'model': user_answer.lower()})
        session['courier_checked'] = True  # Mark as checked regardless of result
        if not quick_check['eligible']:
            return jsonify({
                'success': True,
                'completed': False,
                'question': {
                    'question': quick_check['reason'],
                    'type': 'rejection',
                    'completed': True
                },
                'rejection': True,
                'rejection_reason': quick_check['reason']
            })

    # Extract information from the conversation so far and update product_info
    extracted_info = ai_service.extract_product_details(conversation_history)

    if extracted_info:  # Only update if extraction returned data
        # Merge extracted info with existing, but don't overwrite with None values
        for key, value in extracted_info.items():
            if value is not None:
                if key == 'specifications' and key in product_info:
                    # Merge specifications dict
                    print(f"   🔄 Merging specifications: existing={product_info[key]}, new={value}")
                    if product_info[key] is None:
                        product_info[key] = {}
                    product_info[key].update(value)
                    print(f"   ✅ After merge: {product_info[key]}")
                else:
                    product_info[key] = value

    print(f"\n{'='*60}")
    print(f"DEBUG - AFTER EXTRACTION:")
    print(f"Extracted info: {extracted_info}")
    print(f"Updated product_info: {product_info}")
    print(f"{'='*60}\n")

    # Check courier eligibility after getting category
    if product_info.get('category') and not session.get('courier_checked'):
        courier_check = is_courier_eligible(product_info)
        session['courier_checked'] = True

        if not courier_check['eligible']:
            # Return non-courier rejection
            return jsonify({
                'success': True,
                'completed': False,
                'question': {
                    'question': courier_check['reason'],
                    'type': 'rejection',
                    'completed': True
                },
                'rejection': True,
                'rejection_reason': courier_check['reason']
            })

    # Get next question from AI with updated product info
    next_question = ai_service.get_next_question(conversation_history, product_info)

    # Debug logging
    print(f"\n{'='*60}")
    print(f"DEBUG - AI RESPONSE:")
    print(f"AI returned question: {next_question}")
    print(f"{'='*60}\n")

    # Add assistant's question to history (so we can track what was asked)
    if not next_question.get('completed'):
        conversation_history.append({
            'role': 'assistant',
            'content': next_question.get('question', '')
        })

    # Update session with both history and product info
    session['conversation_history'] = conversation_history
    session['product_info'] = product_info

    # Check if conversation is complete
    if next_question.get('completed'):
        return jsonify({
            'success': True,
            'completed': True,
            'product_info': product_info,
            'message': 'Thank you! Now calculating your offer...'
        })

    return jsonify({
        'success': True,
        'completed': False,
        'question': next_question
    })


def _normalize_v3_product_info(product_info, collected_fields):
    """
    Normalize v3 collected_fields into product_info keys that the offer
    service expects. The offer service reads 'condition' and 'damage_details'
    directly from product_info, but the guardrail engine may store these
    under various field names (condition, damage, damage_details, etc.).
    """
    # Flatten collected_fields into product_info top level
    for key, value in collected_fields.items():
        product_info[key] = value

    # Normalize damage-related fields into 'damage_details' (list format)
    damage_keys = ['condition', 'damage', 'damage_details', 'condition_details']
    damage_items = []
    for key in damage_keys:
        val = collected_fields.get(key)
        if val and val != 'no_damage' and val != 'unknown':
            if isinstance(val, list):
                # Filter list items — only keep actual damage/issues
                for item in val:
                    item_lower = item.lower() if isinstance(item, str) else ''
                    if any(d in item_lower for d in ['crack', 'scratch', 'dent', 'water',
                            'broken', 'chip', 'damage', 'battery', 'dead', 'bent',
                            'burn', 'stain', 'tear', 'worn', 'fad', '85%', 'lens']):
                        damage_items.append(item)
            elif isinstance(val, str):
                # Skip generic "good"/"excellent" — only include actual damage
                lower_val = val.lower()
                if any(d in lower_val for d in ['crack', 'scratch', 'dent', 'water',
                        'broken', 'chip', 'damage', 'battery', 'dead', 'bent',
                        'burn', 'stain', 'tear', 'worn', 'fad', '85%', 'lens']):
                    damage_items.append(val)

    if damage_items:
        product_info['damage_details'] = damage_items
        print(f"   🔧 Normalized damage_details: {damage_items}")

    # Ensure 'condition' key exists for offer service
    if 'condition' not in product_info:
        product_info['condition'] = 'good'  # Default if not asked

    product_info['collected_fields'] = collected_fields
    return product_info


@app.route('/api/message/v3', methods=['POST'])
def message_v3():
    """
    v3.0 Universal Pricing Architecture

    Uses GuardrailEngine + simplified AI for universal product coverage.
    Handles ANY product in 2-4 questions with no duplicates guaranteed.
    """
    try:
        if ai_service_v3 is None:
            return jsonify({
                'success': False,
                'error': 'AI service v3 not initialized'
            }), 500

        data = request.json
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty'
            }), 400

        # Get or create GuardrailEngine from session
        engine_state = session.get('engine_v3', {})
        if engine_state:
            engine = GuardrailEngine.from_dict(engine_state)
        else:
            engine = GuardrailEngine()

        print(f"\n{'='*60}")
        print(f"V3 MESSAGE: {user_message}")
        print(f"Engine state: {engine.state.value}")
        print(f"Product identified: {engine.product_identified}")
        print(f"{'='*60}\n")

        # Record user message
        engine.record_user_message(user_message)

        # PHASE 1: Product Identification
        if not engine.product_identified:
            print("📋 Phase 1: Identifying product...")

            # AI identifies the product and proposes questions
            identification = ai_service_v3.identify_product(user_message)

            # Set product info in engine
            engine.set_product_info(identification['product_info'])

            # Approve questions (engine filters out already-collected fields)
            approved_questions = engine.approve_questions(identification['proposed_questions'])

            print(f"\n🔑 PHASE 1 DECISION POINT:")
            print(f"   approved_questions: {approved_questions}")
            print(f"   engine.asked_fields: {engine.asked_fields}")
            print(f"   engine.collected_fields: {list(engine.collected_fields.keys())}")
            print(f"   engine.question_count: {engine.question_count}")

            if not approved_questions:
                # If no questions needed (enough info from initial message), calculate offer
                print("✅ No questions needed - enough info collected!")
                session['engine_v3'] = engine.to_dict()
                session['product_info_v3'] = identification['product_info']
                session['product_info'] = _normalize_v3_product_info(
                    identification['product_info'], engine.collected_fields
                )
                return jsonify({
                    'success': True,
                    'should_calculate': True,
                    'message': "Got it! Calculating your offer now..."
                })

            # Generate friendly acknowledgment
            acknowledgment = ai_service_v3.generate_acknowledgment(identification['product_info'])

            # Generate first question
            first_field = approved_questions[0]
            question_data = ai_service_v3.generate_question(
                first_field,
                identification['product_info'],
                engine.collected_fields
            )

            # Validate the question with engine
            validation = engine.validate_ai_question(
                first_field,
                question_data['question_text'],
                question_data.get('quick_options', [])
            )

            if not validation['valid']:
                # Should never happen, but safety check
                print(f"⚠️  Question validation failed: {validation['reason']}")
                return jsonify({
                    'success': False,
                    'error': 'Internal error - question validation failed'
                }), 500

            # Record AI message
            full_response = f"{acknowledgment}\n\n{question_data['question_text']}"
            engine.record_ai_message(full_response)

            # Save engine state to session
            session['engine_v3'] = engine.to_dict()
            session['current_field_v3'] = first_field  # Track which field we're asking about

            # Return response with UI options
            return jsonify({
                'success': True,
                'message': acknowledgment,
                'question': question_data['question_text'],
                'field_name': first_field,
                'ui_type': question_data.get('ui_type', 'text'),
                'quick_options': question_data.get('quick_options', []),
                'progress': engine.get_progress_info(),
                'should_calculate': False,
                'imei_warning': engine.imei_device
            })

        # PHASE 2: Answering Questions
        else:
            print("📋 Phase 2: Processing answer...")

            # SAFETY: Detect stale sessions where product was identified in a
            # PREVIOUS conversation but the user is starting fresh.
            # If question_count == 0 and no questions have been asked yet, the
            # engine state is stale. Reset and treat as Phase 1.
            if engine.question_count == 0 and not session.get('current_field_v3'):
                print("⚠️  STALE SESSION DETECTED: product_identified=True but no questions asked")
                print("   Resetting engine and treating as Phase 1...")
                engine = GuardrailEngine()
                session.pop('engine_v3', None)
                session.pop('current_field_v3', None)

                # Re-run Phase 1 with the new engine
                identification = ai_service_v3.identify_product(user_message)
                engine.set_product_info(identification['product_info'])
                approved_questions = engine.approve_questions(identification['proposed_questions'])

                print(f"\n🔑 PHASE 1 (RECOVERED) DECISION POINT:")
                print(f"   approved_questions: {approved_questions}")

                if not approved_questions:
                    session['engine_v3'] = engine.to_dict()
                    session['product_info_v3'] = identification['product_info']
                    session['product_info'] = _normalize_v3_product_info(
                        identification['product_info'], engine.collected_fields
                    )
                    return jsonify({
                        'success': True,
                        'should_calculate': True,
                        'message': "Got it! Calculating your offer now..."
                    })

                acknowledgment = ai_service_v3.generate_acknowledgment(identification['product_info'])
                first_field = approved_questions[0]
                question_data = ai_service_v3.generate_question(
                    first_field, identification['product_info'], engine.collected_fields
                )
                validation = engine.validate_ai_question(
                    first_field, question_data['question_text'],
                    question_data.get('quick_options', [])
                )
                if not validation['valid']:
                    print(f"⚠️  Recovered question validation failed: {validation['reason']}")
                    return jsonify({'success': False, 'error': 'Internal error'}), 500

                full_response = f"{acknowledgment}\n\n{question_data['question_text']}"
                engine.record_ai_message(full_response)
                session['engine_v3'] = engine.to_dict()
                session['current_field_v3'] = first_field

                return jsonify({
                    'success': True,
                    'message': acknowledgment,
                    'question': question_data['question_text'],
                    'field_name': first_field,
                    'ui_type': question_data.get('ui_type', 'text'),
                    'quick_options': question_data.get('quick_options', []),
                    'progress': engine.get_progress_info(),
                    'should_calculate': False,
                    'imei_warning': engine.imei_device
                })

            # Get current question context from last AI message
            last_question_field = session.get('current_field_v3', '')

            if not last_question_field:
                return jsonify({
                    'success': False,
                    'error': 'Session lost. Please start over.'
                }), 400

            # Extract answer from user message
            extracted_answer = ai_service_v3.extract_answer(
                user_message,
                last_question_field,
                engine.product_info
            )

            # Record the answer in engine
            engine.record_answer(last_question_field, extracted_answer)

            # Check if we should calculate offer now
            if engine.should_calculate_offer():
                print("✅ Enough info collected - triggering offer calculation!")
                session['engine_v3'] = engine.to_dict()
                session['product_info_v3'] = engine.product_info
                session['product_info'] = _normalize_v3_product_info(
                    dict(engine.product_info), dict(engine.collected_fields)
                )

                return jsonify({
                    'success': True,
                    'should_calculate': True,
                    'message': "That's everything! 🎉 Calculating your offer now...",
                    'progress': engine.get_progress_info()
                })

            # Get next question
            # Find next unanswered question from approved list
            next_field = None
            for field in engine.approved_questions:
                if field not in engine.collected_fields and field not in engine.asked_fields:
                    next_field = field
                    break

            if not next_field:
                # Shouldn't happen (engine should have triggered calculation), but safety
                print("⚠️  No next question but calculation not triggered - forcing calculation")
                session['engine_v3'] = engine.to_dict()
                session['product_info_v3'] = engine.product_info
                session['product_info'] = _normalize_v3_product_info(
                    dict(engine.product_info), dict(engine.collected_fields)
                )

                return jsonify({
                    'success': True,
                    'should_calculate': True,
                    'message': "Thanks! Calculating your offer...",
                    'progress': engine.get_progress_info()
                })

            # Generate next question
            question_data = ai_service_v3.generate_question(
                next_field,
                engine.product_info,
                engine.collected_fields
            )

            # Validate with engine
            validation = engine.validate_ai_question(
                next_field,
                question_data['question_text'],
                question_data.get('quick_options', [])
            )

            if not validation['valid']:
                print(f"⚠️  Question rejected: {validation['reason']}")
                # Force calculation since we can't ask more questions
                session['engine_v3'] = engine.to_dict()
                session['product_info_v3'] = engine.product_info
                session['product_info'] = _normalize_v3_product_info(
                    dict(engine.product_info), dict(engine.collected_fields)
                )

                return jsonify({
                    'success': True,
                    'should_calculate': True,
                    'message': "Thanks! Calculating your offer...",
                    'progress': engine.get_progress_info()
                })

            # Record AI message
            engine.record_ai_message(question_data['question_text'])

            # Save state
            session['engine_v3'] = engine.to_dict()
            session['current_field_v3'] = next_field

            # Return next question
            return jsonify({
                'success': True,
                'question': question_data['question_text'],
                'field_name': next_field,
                'ui_type': question_data.get('ui_type', 'text'),
                'quick_options': question_data.get('quick_options', []),
                'progress': engine.get_progress_info(),
                'should_calculate': False
            })

    except Exception as e:
        print(f"❌ Error in message_v3: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error processing message: {str(e)}'
        }), 500


@app.route('/api/reset-session', methods=['POST'])
def reset_session():
    """Force clear session for testing/debugging"""
    session.clear()
    session['_version'] = SESSION_VERSION
    return jsonify({'success': True, 'message': 'Session cleared', 'version': SESSION_VERSION})


@app.route('/api/calculate-offer', methods=['POST'])
def calculate_offer():
    """Calculate and return offer"""

    # Get product info from session
    product_info = session.get('product_info', {})

    if not product_info:
        return jsonify({
            'success': False,
            'error': 'No product information found. Please start over.'
        }), 400

    # Validate product info
    is_valid, error_msg = Validators.validate_product_info(product_info)
    if not is_valid:
        return jsonify({
            'success': False,
            'error': error_msg
        }), 400

    # Extract damage info if present
    damage_info = product_info.get('damage', {})

    # Calculate offer
    try:
        offer_data = offer_service.calculate_offer(product_info, damage_info)

        # Store offer in session for later use
        session['offer_data'] = offer_data

        # Add product_info to the response so frontend can display it
        offer_data['product_info'] = product_info

        return jsonify({
            'success': True,
            'offer': offer_data
        })

    except Exception as e:
        print(f"Error calculating offer: {e}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while calculating your offer. Please try again.'
        }), 500


@app.route('/api/submit-user-estimate', methods=['POST'])
def submit_user_estimate():
    """Handle user's price estimate when no market data found"""

    data = request.json
    user_estimate = data.get('estimate')

    if not user_estimate:
        return jsonify({
            'success': False,
            'error': 'Please provide an estimate'
        }), 400

    # Get product info from session
    product_info = session.get('product_info', {})
    damage_info = product_info.get('damage', {})

    try:
        # Calculate offer based on user estimate
        offer_data = offer_service.calculate_offer_from_user_estimate(
            product_info,
            user_estimate,
            damage_info
        )

        if not offer_data.get('success', True):
            return jsonify(offer_data), 400

        # Store offer in session
        session['offer_data'] = offer_data

        return jsonify({
            'success': True,
            'offer': offer_data
        })

    except Exception as e:
        print(f"Error calculating offer from user estimate: {e}")
        return jsonify({
            'success': False,
            'error': 'An error occurred while calculating your offer. Please try again.'
        }), 500


@app.route('/api/submit-customer-info', methods=['POST'])
def submit_customer_info():
    """Handle customer contact information submission"""

    data = request.json
    customer_info = {
        'name': Validators.sanitize_input(data.get('name', '')),
        'email': Validators.sanitize_input(data.get('email', '')),
        'phone': Validators.sanitize_input(data.get('phone', '')),
        'address': Validators.sanitize_input(data.get('address', '')),
        'collection_date': Validators.sanitize_input(data.get('collection_date', '')),
        'terms_agreed': data.get('terms_agreed', False)
    }

    # Validate email
    if not Validators.validate_email(customer_info['email']):
        return jsonify({
            'success': False,
            'error': 'Please provide a valid email address'
        }), 400

    # Validate required fields
    if not customer_info['address'] or not customer_info['collection_date']:
        return jsonify({
            'success': False,
            'error': 'Please provide collection address and date'
        }), 400

    # Validate terms agreement
    if not customer_info['terms_agreed']:
        return jsonify({
            'success': False,
            'error': 'Please agree to the Terms & Conditions'
        }), 400

    # Store customer info in session for potential price dispute
    session['customer_info'] = customer_info

    # Get offer and product info from session
    offer_data = session.get('offer_data', {})
    product_info = session.get('product_info', {})
    damage_info = product_info.get('damage', {})

    if not offer_data:
        return jsonify({
            'success': False,
            'error': 'No offer data found. Please restart the process.'
        }), 400

    try:
        # Check recommendation type
        if offer_data['recommendation'] == 'instant_offer':
            # Send offer email to customer
            email_service.send_offer_to_customer(
                customer_info['email'],
                offer_data,
                product_info
            )

            return jsonify({
                'success': True,
                'type': 'instant_offer',
                'message': 'Offer sent to your email!',
                'offer_amount': offer_data['offer_amount']
            })

        else:
            # Send review request to Brad
            email_service.send_manual_review_request(
                product_info,
                damage_info,
                offer_data,
                customer_info
            )

            return jsonify({
                'success': True,
                'type': 'manual_review',
                'message': 'Thank you! Our team will contact you within 2 working days with a personalized offer.'
            })

    except Exception as e:
        print(f"Error processing customer info: {e}")
        return jsonify({
            'success': False,
            'error': 'An error occurred. Please contact us directly at brad@epicdeals.co.za'
        }), 500


@app.route('/api/dispute-price', methods=['POST'])
def dispute_price():
    """Handle user disputing the pricing with their own estimate and links"""

    data = request.json
    user_estimate = data.get('user_estimate')
    justification = data.get('justification', '')
    links = data.get('links', [])

    if not user_estimate:
        return jsonify({
            'success': False,
            'error': 'Please provide your estimated value'
        }), 400

    # Get session data
    product_info = session.get('product_info', {})
    offer_data = session.get('offer_data', {})
    customer_info = session.get('customer_info', {})

    if not product_info:
        return jsonify({
            'success': False,
            'error': 'Session expired. Please start over.'
        }), 400

    try:
        # Send price dispute email to Brad
        email_service.send_price_dispute_request(
            product_info=product_info,
            our_estimate=offer_data.get('market_value', 0),
            user_estimate=user_estimate,
            justification=justification,
            links=links,
            customer_info=customer_info
        )

        return jsonify({
            'success': True,
            'message': 'Thank you for your feedback! Our team will review your estimate and get back to you within 2 working days.'
        })

    except Exception as e:
        print(f"Error processing price dispute: {e}")
        return jsonify({
            'success': False,
            'error': 'An error occurred. Please contact us at brad@epicdeals.co.za'
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'EpicDeals Price Research Tool'
    })


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Validate configuration
    try:
        Config.validate()
        print("✓ Configuration validated successfully")
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        print("\nPlease check your .env file and ensure all required values are set.")
        exit(1)

    print("\n" + "="*60)
    print("EpicDeals AI Price Research Tool")
    print("="*60)
    print(f"Server starting on http://localhost:5000")
    print(f"Press CTRL+C to stop")
    print("="*60 + "\n")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.DEBUG
    )
