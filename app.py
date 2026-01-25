from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from config import Config
from services.ai_service import AIService
from services.offer_service import OfferService
from services.email_service import EmailService
from utils.validators import Validators
from utils.courier_checker import is_courier_eligible, get_courier_rejection_message
import os
import secrets

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
CORS(app)  # Enable CORS for WordPress embedding

# Initialize services
ai_service = AIService()
offer_service = OfferService()
email_service = EmailService()


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/start-conversation', methods=['POST'])
def start_conversation():
    """Initialize a new conversation"""

    # Create new session
    session_id = secrets.token_urlsafe(16)
    session['conversation_id'] = session_id
    session['conversation_history'] = []
    session['product_info'] = {}

    # Get initial question from AI
    next_question = ai_service.get_next_question([], {})

    return jsonify({
        'success': True,
        'session_id': session_id,
        'question': next_question
    })


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
        if not quick_check['eligible']:
            session['courier_checked'] = True
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
                    if product_info[key] is None:
                        product_info[key] = {}
                    product_info[key].update(value)
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
