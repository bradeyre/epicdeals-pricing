// EpicDeals AI Price Research Tool - Frontend

class EpicDealsApp {
    constructor() {
        this.sessionId = null;
        this.currentQuestion = null;
        this.init();
    }

    init() {
        // Event listeners
        document.getElementById('start-btn').addEventListener('click', () => this.startConversation());
        document.getElementById('send-btn').addEventListener('click', () => this.sendTextAnswer());
        document.getElementById('text-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendTextAnswer();
        });
        document.getElementById('contact-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitCustomerInfo();
        });

        // Terms & Conditions modal
        this.initTermsModal();

        // Set minimum date for collection date to tomorrow
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        const minDate = tomorrow.toISOString().split('T')[0];
        const collectionDateInput = document.getElementById('collection-date');
        if (collectionDateInput) {
            collectionDateInput.min = minDate;
        }
    }

    initTermsModal() {
        const modal = document.getElementById('terms-modal');
        const showTermsLink = document.getElementById('show-terms-link');
        const closeButtons = document.querySelectorAll('.close-modal, .close-modal-btn');

        // Delegate event for show terms link (since it's created dynamically)
        document.addEventListener('click', (e) => {
            if (e.target && e.target.id === 'show-terms-link') {
                e.preventDefault();
                modal.style.display = 'block';
            }
        });

        // Close modal when clicking X or Close button
        closeButtons.forEach(button => {
            button.addEventListener('click', () => {
                modal.style.display = 'none';
            });
        });

        // Close modal when clicking outside
        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    }

    async startConversation() {
        this.showLoading();

        try {
            const response = await fetch('/api/start-conversation', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            const data = await response.json();

            if (data.success) {
                this.sessionId = data.session_id;
                this.hideWelcome();
                this.displayQuestion(data.question);
            } else {
                this.showError('Failed to start. Please try again.');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showError('Connection error. Please check your internet and try again.');
        } finally {
            this.hideLoading();
        }
    }

    displayQuestion(question) {
        // Add bot message
        this.addMessage(question.question, 'bot');

        // Show appropriate input method
        if (question.type === 'multiple_choice') {
            this.showOptions(question.options);
            this.hideTextInput();
            this.hideCheckboxes();
        } else if (question.type === 'multi_select') {
            this.showCheckboxes(question.options);
            this.hideTextInput();
            this.hideOptions();
        } else {
            this.showTextInput();
            this.hideOptions();
            this.hideCheckboxes();
        }

        this.currentQuestion = question;
    }

    addMessage(text, sender) {
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.style.display = 'block';

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        bubbleDiv.textContent = text;

        messageDiv.appendChild(bubbleDiv);
        chatMessages.appendChild(messageDiv);

        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    showOptions(options) {
        console.log('=== showOptions called ===');
        console.log('Options received:', options);
        console.log('Options type:', typeof options);
        console.log('Options is array?', Array.isArray(options));

        const optionsArea = document.getElementById('options-area');
        console.log('optionsArea element:', optionsArea);

        if (!optionsArea) {
            console.error('CRITICAL: options-area element not found!');
            return;
        }

        optionsArea.innerHTML = '';
        optionsArea.style.display = 'flex';
        optionsArea.style.visibility = 'visible';
        optionsArea.style.opacity = '1';

        console.log('optionsArea display:', optionsArea.style.display);

        if (!options || options.length === 0) {
            console.error('No options provided or empty array');
            return;
        }

        console.log('Creating buttons for', options.length, 'options');
        options.forEach((option, index) => {
            console.log(`Creating button ${index}:`, option);
            const btn = document.createElement('button');
            btn.className = 'option-btn';
            btn.textContent = option;
            btn.style.display = 'block';
            btn.style.visibility = 'visible';
            btn.addEventListener('click', () => this.selectOption(option));
            optionsArea.appendChild(btn);
            console.log(`Button ${index} appended, children count:`, optionsArea.children.length);
        });

        console.log('Final optionsArea HTML:', optionsArea.innerHTML);
        console.log('=== showOptions complete ===');
    }

    async selectOption(option) {
        // Add user's selection to chat
        this.addMessage(option, 'user');
        this.hideOptions();
        this.showLoading();

        await this.submitAnswer(option);
    }

    async sendTextAnswer() {
        const input = document.getElementById('text-input');
        const answer = input.value.trim();

        if (!answer) return;

        // Add user's answer to chat
        this.addMessage(answer, 'user');
        input.value = '';
        this.hideTextInput();
        this.showLoading();

        await this.submitAnswer(answer);
    }

    async submitAnswer(answer) {
        try {
            const response = await fetch('/api/submit-answer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ answer })
            });

            const data = await response.json();

            if (data.success) {
                // Check for rejection (non-courier item)
                if (data.rejection) {
                    this.showRejection(data.rejection_reason);
                    return;
                }

                if (data.completed) {
                    // Conversation complete, calculate offer
                    this.addMessage(data.message, 'bot');
                    await this.calculateOffer();
                } else {
                    // Show next question
                    this.displayQuestion(data.question);
                }
            } else {
                this.showError('Something went wrong. Please try again.');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showError('Connection error. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    showRejection(reason) {
        // Hide chat and show rejection message
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.style.display = 'none';

        const offerDisplay = document.getElementById('offer-display');
        offerDisplay.style.display = 'block';

        offerDisplay.innerHTML = `
            <div class="rejection-message">
                <div class="icon">📦</div>
                <h2>We're Sorry</h2>
                <p style="color: #666; margin: 20px 0; line-height: 1.6;">
                    ${reason}
                </p>
                <p style="color: #999; font-size: 14px; margin-top: 30px;">
                    We're constantly expanding our services. Please check back soon or contact us at
                    <a href="mailto:brad@epicdeals.co.za" style="color: #2e88c9; text-decoration: none; font-weight: 600;">brad@epicdeals.co.za</a>
                </p>
                <button class="btn btn-primary" onclick="location.reload()" style="margin-top: 20px;">Start Over</button>
            </div>
        `;
    }

    async calculateOffer() {
        this.showLoading();

        try {
            const response = await fetch('/api/calculate-offer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            const data = await response.json();

            if (data.success) {
                // Store product info for later use
                this.productInfo = data.offer.price_research?.product_info || {};
                this.displayOffer(data.offer);
            } else {
                this.showError(data.error || 'Failed to calculate offer.');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showError('Failed to calculate offer. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    getProductSummary(offer) {
        // Get product info from offer (now included in backend response)
        const productInfo = offer.product_info || this.productInfo || {};

        const brand = productInfo.brand || 'Unknown Brand';
        const model = productInfo.model || 'Unknown Model';
        const category = productInfo.category || 'Item';
        const condition = productInfo.condition || 'Used';
        const year = productInfo.year || productInfo.specifications?.year || '';

        let summaryHTML = `
            <div class="product-summary">
                <h3>Item Summary</h3>
                <div class="summary-details">
                    <div class="summary-item">
                        <span class="summary-label">Product:</span>
                        <span class="summary-value">${brand} ${model}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Category:</span>
                        <span class="summary-value">${category}</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Condition:</span>
                        <span class="summary-value">${condition.charAt(0).toUpperCase() + condition.slice(1)}</span>
                    </div>
                    ${year ? `
                    <div class="summary-item">
                        <span class="summary-label">Year:</span>
                        <span class="summary-value">${year}</span>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;

        return summaryHTML;
    }

    displayOffer(offer) {
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.style.display = 'none';

        const offerDisplay = document.getElementById('offer-display');
        offerDisplay.style.display = 'block';

        // Store offer for later use
        this.currentOffer = offer;

        // Handle user estimate request
        if (offer.recommendation === 'user_estimate') {
            offerDisplay.innerHTML = `
                <div class="icon">💭</div>
                <h2>We need your help!</h2>
                <p style="color: #666; margin: 20px 0;">
                    We couldn't find enough pricing data for your item in the market.
                    Could you tell us what you think it's worth second-hand?
                </p>
                <div class="user-estimate-input">
                    <label for="user-estimate">Your estimate (ZAR):</label>
                    <input type="number" id="user-estimate" placeholder="e.g., 5000" min="0" step="50" />
                    <button id="submit-estimate-btn" class="btn btn-primary">Calculate My Offer</button>
                </div>
                <p style="color: #999; font-size: 0.9em; margin-top: 20px;">
                    We'll make you an offer at 70% of your estimate and contact you for manual assessment.
                </p>
            `;

            // Attach event listener to submit button
            document.getElementById('submit-estimate-btn').addEventListener('click', () => this.submitUserEstimate());
            return;
        }

        // Handle manual review offer (based on user estimate)
        if (offer.recommendation === 'manual_review' && offer.based_on_user_estimate) {
            offerDisplay.innerHTML = `
                <div class="icon">📋</div>
                <h2>Here's our preliminary offer</h2>
                <div class="offer-amount">R${this.formatNumber(offer.offer_amount)}</div>
                <div class="offer-breakdown">
                    <div class="breakdown-item">
                        <span>Your Estimate</span>
                        <span>R${this.formatNumber(offer.market_value)}</span>
                    </div>
                    ${offer.repair_costs > 0 ? `
                    <div class="breakdown-item">
                        <span>Repair Costs</span>
                        <span>-R${this.formatNumber(offer.repair_costs)}</span>
                    </div>
                    <div class="breakdown-item">
                        <span>Adjusted Value</span>
                        <span>R${this.formatNumber(offer.market_value - offer.repair_costs)}</span>
                    </div>
                    ` : ''}
                    <div class="breakdown-item">
                        <span>Our Offer (70%)</span>
                        <span>R${this.formatNumber(offer.offer_amount)}</span>
                    </div>
                </div>
                <p style="color: #666; margin: 20px 0;">
                    ⚠️ This offer is based on your estimate and requires manual assessment.
                    Our team will contact you within 2 working days to finalize the offer.
                </p>
            `;
            // Show customer form
            document.getElementById('customer-form').style.display = 'block';
            return;
        }

        if (offer.recommendation === 'instant_offer') {
            // Build repair costs breakdown HTML if available
            let repairBreakdownHTML = '';
            if (offer.repair_explanation) {
                // Convert markdown-style repair explanation to HTML
                repairBreakdownHTML = `
                    <div class="repair-explanation">
                        ${this.formatRepairExplanation(offer.repair_explanation)}
                    </div>
                `;
            }

            // Check if this is an estimate from new price
            let estimateNotice = '';
            if (offer.is_new_price_estimate) {
                let depreciationExplanation = '';
                if (offer.depreciation_info && offer.depreciation_info.explanation) {
                    depreciationExplanation = `<br><br>${offer.depreciation_info.explanation}`;
                }

                estimateNotice = `
                    <div class="estimate-notice">
                        <strong>ℹ️ Pricing Note:</strong> We couldn't find second-hand prices for this item, so we estimated based on new retail price (R${this.formatNumber(offer.new_price)}) and age-based depreciation for this category.${depreciationExplanation}
                    </div>
                `;
            }

            offerDisplay.innerHTML = `
                <div class="icon">🎉</div>
                <h2>Great news! We'd like to make you an offer</h2>

                ${this.getProductSummary(offer)}

                <div class="beta-notice">
                    <strong>🚀 New System!</strong> This is our new automated pricing tool. All offers require manual verification by our team before final confirmation. We'll contact you within 2 working days.
                </div>

                ${estimateNotice}

                <div class="offer-breakdown">
                    <div class="breakdown-item">
                        <span>Market Value (working condition)</span>
                        <span>R${this.formatNumber(offer.market_value)}</span>
                    </div>
                    ${offer.repair_costs > 0 ? `
                    <div class="breakdown-item negative">
                        <span>Less: Estimated Repair Costs</span>
                        <span>-R${this.formatNumber(offer.repair_costs)}</span>
                    </div>
                    <div class="breakdown-item adjusted-value">
                        <span>Value to Us</span>
                        <span>R${this.formatNumber(offer.adjusted_value)}</span>
                    </div>
                    ` : ''}
                </div>

                ${repairBreakdownHTML}

                <div class="vat-notice">
                    <p style="font-size: 0.9em; color: #666;">All prices include VAT</p>
                </div>

                <div class="offer-selection-prompt">
                    <h3 style="margin-bottom: 20px;">Choose your preferred option:</h3>
                </div>

                <div class="dual-offers">
                    <label class="offer-option sell-now" for="offer-sell-now">
                        <input type="radio" name="offer-choice" id="offer-sell-now" value="sell_now" />
                        <div class="offer-content">
                            <h3>OPTION 1: SELL NOW</h3>
                            <div class="option-amount">R${this.formatNumber(offer.sell_now_offer)}</div>
                            <p class="option-description">Immediate payment (65%)</p>
                        </div>
                    </label>

                    <label class="offer-option consignment" for="offer-consignment">
                        <input type="radio" name="offer-choice" id="offer-consignment" value="consignment" checked />
                        <div class="offer-content">
                            <h3>OPTION 2: CONSIGNMENT</h3>
                            <div class="option-amount highlight">R${this.formatNumber(offer.consignment_payout)}</div>
                            <p class="option-description">After sale (85%)</p>
                            <p class="savings">💰 That's R${this.formatNumber(offer.consignment_payout - offer.sell_now_offer)} MORE!</p>
                        </div>
                    </label>
                </div>

                <div class="pricing-dispute">
                    <p style="color: #999; font-size: 14px; margin: 20px 0 10px 0;">
                        Think our pricing is off? <a href="#" id="dispute-price-link">Let us know</a>
                    </p>
                </div>

                <p style="color: #666; margin: 20px 0;">
                    This preliminary offer requires manual verification. Enter your details below and we'll confirm within 2 working days.
                </p>
            `;

            // Add event listener for price dispute link
            const disputeLink = document.getElementById('dispute-price-link');
            if (disputeLink) {
                disputeLink.addEventListener('click', (e) => {
                    e.preventDefault();
                    // Pass adjusted value instead of market value for dispute form
                    this.showPriceDisputeForm(offer.adjusted_value || offer.market_value);
                });
            }
        } else {
            offerDisplay.innerHTML = `
                <div class="icon">📧</div>
                <h2>We'd like to review your item personally</h2>
                <p style="color: #666; margin: 20px 0;">
                    ${offer.reason}
                </p>
                <div class="offer-breakdown">
                    <div class="breakdown-item">
                        <span>Estimated Value Range</span>
                        <span>R${this.formatNumber(offer.market_value * 0.6)} - R${this.formatNumber(offer.market_value * 0.8)}</span>
                    </div>
                </div>
                <p style="color: #666; margin: 20px 0;">
                    Our team will contact you within 2 working days with a personalized offer.
                </p>
            `;
        }

        // Show customer form
        document.getElementById('customer-form').style.display = 'block';
    }

    async submitUserEstimate() {
        const estimateInput = document.getElementById('user-estimate');
        const estimate = parseFloat(estimateInput.value);

        if (!estimate || estimate <= 0) {
            this.showError('Please enter a valid estimate amount');
            return;
        }

        this.showLoading();

        try {
            const response = await fetch('/api/submit-user-estimate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ estimate })
            });

            const data = await response.json();

            if (data.success) {
                this.displayOffer(data.offer);
            } else {
                this.showError(data.error || 'Failed to calculate offer.');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showError('Failed to calculate offer. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    async submitCustomerInfo() {
        const name = document.getElementById('customer-name').value.trim();
        const email = document.getElementById('customer-email').value.trim();
        const phone = document.getElementById('customer-phone').value.trim();
        const address = document.getElementById('customer-address').value.trim();
        const collectionDate = document.getElementById('collection-date').value;
        const termsAgreed = document.getElementById('terms-agreement').checked;

        if (!name || !email || !phone || !address || !collectionDate) {
            this.showError('Please fill in all required fields');
            return;
        }

        if (!termsAgreed) {
            this.showError('Please agree to the Terms & Conditions');
            return;
        }

        this.showLoading();

        try {
            const response = await fetch('/api/submit-customer-info', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name,
                    email,
                    phone,
                    address,
                    collection_date: collectionDate,
                    terms_agreed: termsAgreed
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showSuccess(data);
            } else {
                this.showError(data.error || 'Failed to submit. Please try again.');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showError('Connection error. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    showSuccess(data) {
        const offerDisplay = document.getElementById('offer-display');
        document.getElementById('customer-form').style.display = 'none';

        if (data.type === 'instant_offer') {
            offerDisplay.innerHTML = `
                <div class="success-message">
                    <div class="icon">✅</div>
                    <h2>Offer Confirmed!</h2>
                    <div class="offer-amount">R${this.formatNumber(data.offer_amount)}</div>
                    <p>${data.message}</p>
                    <p style="margin-top: 20px;">We'll be in touch soon to arrange collection or drop-off.</p>
                </div>
            `;
        } else {
            offerDisplay.innerHTML = `
                <div class="success-message">
                    <div class="icon">✅</div>
                    <h2>Request Submitted!</h2>
                    <p>${data.message}</p>
                </div>
            `;
        }
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;

        const container = document.querySelector('.container');
        container.insertBefore(errorDiv, container.firstChild);

        setTimeout(() => errorDiv.remove(), 5000);
    }

    formatNumber(num) {
        if (num === null || num === undefined || isNaN(num)) {
            return '0.00';
        }
        return Number(num).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    formatRepairExplanation(explanation) {
        if (!explanation) return '';

        // Convert markdown-style formatting to HTML
        let html = explanation
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')  // Bold
            .replace(/^• (.+)$/gm, '<div class="repair-item">• $1</div>')  // Bullet points
            .replace(/\n\n/g, '<br><br>')  // Double line breaks
            .replace(/\n/g, '<br>');  // Single line breaks

        return html;
    }

    showLoading() {
        document.getElementById('loading').style.display = 'block';
    }

    hideLoading() {
        document.getElementById('loading').style.display = 'none';
    }

    showTextInput() {
        document.getElementById('input-area').style.display = 'flex';
        document.getElementById('text-input').focus();
    }

    hideTextInput() {
        document.getElementById('input-area').style.display = 'none';
    }

    hideOptions() {
        document.getElementById('options-area').style.display = 'none';
    }

    showCheckboxes(options) {
        const checkboxArea = document.getElementById('checkbox-area');
        checkboxArea.innerHTML = '';
        checkboxArea.style.display = 'block';

        if (!options || options.length === 0) {
            console.error('No checkbox options provided');
            return;
        }

        // Create checkbox container
        const checkboxContainer = document.createElement('div');
        checkboxContainer.className = 'checkbox-container';

        options.forEach((option, index) => {
            const label = document.createElement('label');
            label.className = 'checkbox-label';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = option;
            checkbox.id = `checkbox-${index}`;
            checkbox.className = 'damage-checkbox';

            const span = document.createElement('span');
            span.className = 'checkbox-text';
            span.textContent = option;

            label.appendChild(checkbox);
            label.appendChild(span);
            checkboxContainer.appendChild(label);
        });

        checkboxArea.appendChild(checkboxContainer);

        // Add submit button
        const submitBtn = document.createElement('button');
        submitBtn.id = 'submit-checkboxes-btn';
        submitBtn.className = 'btn btn-primary';
        submitBtn.textContent = 'Continue';
        submitBtn.addEventListener('click', () => this.submitCheckboxes());

        checkboxArea.appendChild(submitBtn);
    }

    hideCheckboxes() {
        const checkboxArea = document.getElementById('checkbox-area');
        if (checkboxArea) {
            checkboxArea.style.display = 'none';
        }
    }

    async submitCheckboxes() {
        const checkboxes = document.querySelectorAll('.damage-checkbox:checked');

        if (checkboxes.length === 0) {
            this.showError('Please select at least one option');
            return;
        }

        const selectedOptions = Array.from(checkboxes).map(cb => cb.value);
        const answer = selectedOptions.join(', ');

        // Add user's selection to chat
        this.addMessage(selectedOptions.join('\n• '), 'user');
        this.hideCheckboxes();
        this.showLoading();

        await this.submitAnswer(answer);
    }

    hideWelcome() {
        document.querySelector('.conversation-area').style.display = 'none';
    }

    showPriceDisputeForm(ourEstimate) {
        const offerDisplay = document.getElementById('offer-display');
        offerDisplay.innerHTML = `
            <div class="icon">💬</div>
            <h2>Help Us Get It Right</h2>
            <p style="color: #666; margin-bottom: 20px;">
                We appreciate your feedback! Let us know what you think the fair price should be.
            </p>

            <div class="dispute-form">
                <div class="form-group">
                    <label>Our Estimate:</label>
                    <div class="price-display">R${this.formatNumber(ourEstimate)}</div>
                </div>

                <div class="form-group">
                    <label for="user-estimate">Your Estimate (ZAR):</label>
                    <input type="number" id="user-estimate" placeholder="e.g., 8000" min="0" step="100" />
                </div>

                <div class="form-group">
                    <label for="justification">Why do you think it's worth more/less?</label>
                    <textarea id="justification" rows="4" placeholder="Please explain your reasoning..."></textarea>
                </div>

                <div class="form-group">
                    <label>Have links to similar items? (Optional)</label>
                    <input type="url" id="link1" placeholder="https://..." />
                    <input type="url" id="link2" placeholder="https://..." />
                    <input type="url" id="link3" placeholder="https://..." />
                </div>

                <button id="submit-dispute-btn" class="btn btn-primary">Submit Feedback</button>
                <button id="cancel-dispute-btn" class="btn btn-secondary">Cancel</button>
            </div>
        `;

        // Add event listeners
        document.getElementById('submit-dispute-btn').addEventListener('click', () => this.submitPriceDispute());
        document.getElementById('cancel-dispute-btn').addEventListener('click', () => {
            this.displayOffer(this.currentOffer);
        });
    }

    async submitPriceDispute() {
        const userEstimate = parseFloat(document.getElementById('user-estimate').value);
        const justification = document.getElementById('justification').value.trim();
        const link1 = document.getElementById('link1').value.trim();
        const link2 = document.getElementById('link2').value.trim();
        const link3 = document.getElementById('link3').value.trim();

        if (!userEstimate || userEstimate <= 0) {
            this.showError('Please enter your estimated value');
            return;
        }

        if (!justification) {
            this.showError('Please explain your reasoning');
            return;
        }

        const links = [link1, link2, link3].filter(link => link.length > 0);

        this.showLoading();

        try {
            const response = await fetch('/api/dispute-price', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_estimate: userEstimate,
                    justification: justification,
                    links: links
                })
            });

            const data = await response.json();

            if (data.success) {
                const offerDisplay = document.getElementById('offer-display');
                offerDisplay.innerHTML = `
                    <div class="success-message">
                        <div class="icon">✅</div>
                        <h2>Thank You!</h2>
                        <p>${data.message}</p>
                        <p style="margin-top: 20px;">We've received your feedback and will review it carefully. You'll hear from us within 2 working days.</p>
                    </div>
                `;
            } else {
                this.showError(data.error || 'Failed to submit feedback');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showError('Connection error. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    // ============================================================
    // V3.0 ARCHITECTURE METHODS
    // Universal pricing with GuardrailEngine
    // ============================================================

    async sendMessageV3(message) {
        /**
         * Send message to v3.0 endpoint
         * Returns: { success, question, quick_options, ui_type, progress, should_calculate }
         */
        this.showLoading();

        try {
            const response = await fetch('/api/message/v3', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });

            const data = await response.json();

            if (!data.success) {
                this.showError(data.error || 'Something went wrong');
                return null;
            }

            this.hideLoading();
            return data;

        } catch (error) {
            console.error('Error in sendMessageV3:', error);
            this.showError('Connection error. Please try again.');
            this.hideLoading();
            return null;
        }
    }

    async startConversationV3() {
        /**
         * Start v3.0 conversation flow
         * Replaces old start-conversation endpoint
         */
        this.hideWelcome();
        this.addMessage("Hey! 👋 What are you looking to sell today?", 'bot');
        this.showTextInput();
    }

    async handleV3Response(data) {
        /**
         * Handle response from v3 endpoint
         * Displays question, quick-select buttons, progress, etc.
         */

        // Display acknowledgment/message if present
        if (data.message) {
            this.addMessage(data.message, 'bot');
        }

        // Check if should calculate offer
        if (data.should_calculate) {
            this.showCalculatingAnimation();
            // Trigger offer calculation
            setTimeout(() => this.calculateOfferV3(), 1000);
            return;
        }

        // Display question
        if (data.question) {
            this.addMessage(data.question, 'bot');
        }

        // Update progress indicator
        if (data.progress) {
            this.updateProgressDots(data.progress.current, data.progress.total);
        }

        // Show appropriate UI based on type
        if (data.ui_type === 'checklist' && data.quick_options) {
            this.showChecklistV3(data.quick_options, data.field_name);
        } else if (data.quick_options && data.quick_options.length > 0) {
            this.showQuickSelectButtons(data.quick_options);
        } else {
            this.showTextInput();
        }
    }

    showQuickSelectButtons(options) {
        /**
         * Display quick-select buttons below the question
         * Tapping a button instantly sends that answer
         */
        this.hideTextInput();
        this.hideCheckboxes();
        this.hideOptions();

        const chatMessages = document.getElementById('chat-messages');

        // Create quick-select container
        const quickSelectDiv = document.createElement('div');
        quickSelectDiv.className = 'quick-select-buttons';
        quickSelectDiv.innerHTML = options.map(option =>
            `<button class="quick-select-btn" data-value="${this.escapeHtml(option)}">
                ${this.escapeHtml(option)}
            </button>`
        ).join('');

        chatMessages.appendChild(quickSelectDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Add click handlers
        quickSelectDiv.querySelectorAll('.quick-select-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const value = btn.dataset.value;

                // Disable all buttons
                quickSelectDiv.querySelectorAll('.quick-select-btn').forEach(b => {
                    b.disabled = true;
                    b.style.opacity = '0.5';
                });

                // Highlight selected button
                btn.classList.add('selected');

                // Add user message
                this.addMessage(value, 'user');

                // Send to v3 API
                const response = await this.sendMessageV3(value);
                if (response) {
                    // Remove quick-select buttons
                    quickSelectDiv.remove();
                    this.handleV3Response(response);
                }
            });
        });
    }

    showChecklistV3(options, fieldName) {
        /**
         * Display multi-select checklist for condition/damage questions
         * Product-specific options generated by AI
         */
        this.hideTextInput();
        this.hideOptions();

        const chatMessages = document.getElementById('chat-messages');

        const checklistDiv = document.createElement('div');
        checklistDiv.className = 'condition-checklist';
        checklistDiv.innerHTML = `
            <div class="checklist-items">
                ${options.map((option, idx) => `
                    <label class="checklist-item">
                        <input type="checkbox" name="${fieldName}" value="${this.escapeHtml(option)}" id="check-${idx}">
                        <span class="checkbox-custom"></span>
                        <span class="checkbox-label">${this.escapeHtml(option)}</span>
                    </label>
                `).join('')}
            </div>
            <button class="checklist-submit-btn" id="submit-checklist">Continue</button>
        `;

        chatMessages.appendChild(checklistDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Submit handler
        document.getElementById('submit-checklist').addEventListener('click', async () => {
            const checked = checklistDiv.querySelectorAll('input[type="checkbox"]:checked');
            const values = Array.from(checked).map(cb => cb.value);

            if (values.length === 0) {
                alert('Please select at least one option');
                return;
            }

            // Disable checklist
            checklistDiv.querySelectorAll('input, button').forEach(el => el.disabled = true);
            checklistDiv.style.opacity = '0.6';

            // Format answer
            const answer = values.join(', ');
            this.addMessage(answer, 'user');

            // Send to v3 API
            const response = await this.sendMessageV3(answer);
            if (response) {
                checklistDiv.remove();
                this.handleV3Response(response);
            }
        });
    }

    updateProgressDots(current, total) {
        /**
         * Show progress indicator (e.g., ●●○○ for 2/4)
         * Displayed at top of chat
         */
        let progressDiv = document.getElementById('progress-dots');

        if (!progressDiv) {
            progressDiv = document.createElement('div');
            progressDiv.id = 'progress-dots';
            progressDiv.className = 'progress-indicator';

            const chatContainer = document.querySelector('.chat-container');
            chatContainer.insertBefore(progressDiv, chatContainer.firstChild);
        }

        const dots = [];
        for (let i = 0; i < total; i++) {
            dots.push(`<span class="progress-dot ${i < current ? 'filled' : ''}"></span>`);
        }

        progressDiv.innerHTML = `
            <div class="progress-dots-container">
                ${dots.join('')}
                <span class="progress-text">${current}/${total}</span>
            </div>
        `;
    }

    showCalculatingAnimation() {
        /**
         * Display friendly animation while calculating offer
         * Shows status updates: researching → calculating → ready
         */
        const chatMessages = document.getElementById('chat-messages');

        const animDiv = document.createElement('div');
        animDiv.id = 'calculating-animation';
        animDiv.className = 'calculating-animation';
        animDiv.innerHTML = `
            <div class="calc-spinner"></div>
            <div class="calc-status" id="calc-status">🔍 Researching current market prices...</div>
        `;

        chatMessages.appendChild(animDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Animate status messages
        const statuses = [
            "🔍 Researching current market prices...",
            "📊 Calculating fair value...",
            "✅ Your offer is ready!"
        ];

        let statusIndex = 0;
        const statusEl = document.getElementById('calc-status');

        const interval = setInterval(() => {
            statusIndex++;
            if (statusIndex < statuses.length) {
                statusEl.textContent = statuses[statusIndex];
            } else {
                clearInterval(interval);
            }
        }, 2000);

        // Store interval for cleanup
        this.calcInterval = interval;
    }

    async calculateOfferV3() {
        /**
         * Trigger offer calculation using v3 collected data
         * Reuses existing calculate-offer endpoint
         */
        try {
            const response = await fetch('/api/calculate-offer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            const data = await response.json();

            // Clear animation
            if (this.calcInterval) {
                clearInterval(this.calcInterval);
            }
            const animDiv = document.getElementById('calculating-animation');
            if (animDiv) {
                animDiv.remove();
            }

            if (data.success) {
                this.displayOfferV3(data.offer);
            } else {
                this.showError(data.error || 'Failed to calculate offer');
            }

        } catch (error) {
            console.error('Error calculating offer:', error);
            this.showError('Error calculating offer. Please try again.');
        }
    }

    displayOfferV3(offer) {
        /**
         * Display offer using existing displayOffer method
         * v3 data structure compatible with v2 display
         */
        this.displayOffer(offer);
    }

    escapeHtml(text) {
        /**
         * Escape HTML to prevent XSS
         */
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Enable v3 mode (for testing/migration)
    enableV3Mode() {
        /**
         * Switch app to use v3 endpoint
         * Call this to migrate from v2 to v3
         */
        this.v3Enabled = true;
        console.log('✅ V3.0 Universal Pricing Mode Enabled');

        // Replace start button handler
        document.getElementById('start-btn').removeEventListener('click', () => this.startConversation());
        document.getElementById('start-btn').addEventListener('click', () => this.startConversationV3());
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const app = new EpicDealsApp();
    app.enableV3Mode();  // Enable v3.0 Universal Pricing
});
