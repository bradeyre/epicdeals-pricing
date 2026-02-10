// EpicDeals v3.1 - Dark Theme Chat UI
// Three screens: Landing → Chat → Offer
// Uses v3.0 GuardrailEngine backend exclusively

class EpicDealsApp {
    constructor() {
        this.currentField = null;
        this.currentOffer = null;
        this.productInfo = {};
        this.init();
    }

    init() {
        // Landing → Start
        document.getElementById('start-btn').addEventListener('click', () => this.startChat());

        // Chat input
        document.getElementById('send-btn').addEventListener('click', () => this.sendTextAnswer());
        document.getElementById('text-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendTextAnswer();
        });

        // Customer form
        document.getElementById('contact-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitCustomerInfo();
        });

        // Terms modal
        this.initTermsModal();

        // Set min date for collection
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        const collectionDate = document.getElementById('collection-date');
        if (collectionDate) {
            collectionDate.min = tomorrow.toISOString().split('T')[0];
        }

        console.log('EpicDeals v3.1 initialized');
    }

    initTermsModal() {
        const modal = document.getElementById('terms-modal');
        document.addEventListener('click', (e) => {
            if (e.target && e.target.id === 'show-terms-link') {
                e.preventDefault();
                modal.classList.remove('hidden');
            }
        });
        document.querySelectorAll('.close-modal, .close-modal-btn').forEach(btn => {
            btn.addEventListener('click', () => modal.classList.add('hidden'));
        });
        window.addEventListener('click', (e) => {
            if (e.target === modal) modal.classList.add('hidden');
        });
    }

    // ============================================
    // SCREEN NAVIGATION
    // ============================================

    showScreen(screenId) {
        ['landing-screen', 'chat-screen', 'offer-screen'].forEach(id => {
            document.getElementById(id).classList.add('hidden');
        });
        document.getElementById(screenId).classList.remove('hidden');
        // Also hide customer form when switching screens
        document.getElementById('customer-form').classList.add('hidden');
    }

    async startChat() {
        this.showScreen('chat-screen');

        // Always reset server session on new chat to prevent stale state
        try {
            await fetch('/api/reset-session', { method: 'POST' });
            console.log('Session reset for fresh start');
        } catch (e) {
            console.warn('Session reset failed:', e);
        }

        this.addMessage("Hey! What are you looking to sell today?", 'bot');
        this.showTextInput();
    }

    // ============================================
    // MESSAGING
    // ============================================

    addMessage(text, sender) {
        const container = document.getElementById('chat-messages');
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender} fade-in`;

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.textContent = text;

        msgDiv.appendChild(bubble);
        container.appendChild(msgDiv);
        this.scrollToBottom();
    }

    scrollToBottom() {
        const area = document.querySelector('.messages-area');
        if (area) area.scrollTop = area.scrollHeight;
    }

    // ============================================
    // TYPING INDICATOR
    // ============================================

    showTypingIndicator() {
        const container = document.getElementById('chat-messages');
        const typing = document.createElement('div');
        typing.id = 'typing-indicator';
        typing.className = 'typing-indicator';
        typing.innerHTML = `
            <div class="typing-bubble">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        container.appendChild(typing);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const el = document.getElementById('typing-indicator');
        if (el) el.remove();
    }

    // ============================================
    // INPUT CONTROLS
    // ============================================

    showTextInput() {
        document.getElementById('input-bar').style.display = 'block';
        document.getElementById('text-input').focus();
    }

    hideTextInput() {
        document.getElementById('input-bar').style.display = 'none';
    }

    // ============================================
    // PROGRESS BAR
    // ============================================

    updateProgress(progress) {
        if (!progress) return;
        const pct = progress.percentage || 0;
        document.getElementById('progress-fill').style.width = `${pct}%`;
        document.getElementById('progress-text').textContent = `${progress.current}/${progress.total}`;
    }

    // ============================================
    // v3 API COMMUNICATION
    // ============================================

    async sendMessageV3(message) {
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
            return data;
        } catch (error) {
            console.error('API error:', error);
            this.showError('Connection error. Please try again.');
            return null;
        }
    }

    async sendTextAnswer() {
        const input = document.getElementById('text-input');
        const answer = input.value.trim();
        if (!answer) return;

        // Show user message
        this.addMessage(answer, 'user');
        input.value = '';
        this.hideTextInput();

        // Show typing
        this.showTypingIndicator();

        // Send to backend
        const data = await this.sendMessageV3(answer);
        this.hideTypingIndicator();

        if (data) {
            this.handleV3Response(data);
        }
    }

    // ============================================
    // RESPONSE HANDLER
    // ============================================

    handleV3Response(data) {
        // Show acknowledgment message
        if (data.message) {
            this.addMessage(data.message, 'bot');
        }

        // Track IMEI device status (warning shown on offer screen, not in chat)
        if (data.imei_warning) {
            this.isImeiDevice = true;
        }

        // Update progress
        if (data.progress) {
            this.updateProgress(data.progress);
        }

        // Should calculate offer?
        if (data.should_calculate) {
            this.showCalculationAnimation();
            return;
        }

        // Show question
        if (data.question) {
            this.addMessage(data.question, 'bot');
        }

        // Track current field
        this.currentField = data.field_name;

        // Show appropriate UI
        if (data.ui_type === 'checklist' && data.quick_options) {
            this.showChecklist(data.quick_options, data.field_name);
        } else if (data.quick_options && data.quick_options.length > 0) {
            this.showQuickSelect(data.quick_options);
        } else {
            this.showTextInput();
        }
    }

    // ============================================
    // IMEI / ACCOUNT LOCK NOTICE
    // ============================================

    showImeiNotice() {
        const container = document.getElementById('chat-messages');
        const notice = document.createElement('div');
        notice.className = 'imei-notice fade-in';
        notice.innerHTML = `
            <div class="imei-notice-icon">🔒</div>
            <div class="imei-notice-text">
                <strong>Important:</strong> This device must arrive without an iCloud, Google, or Samsung account lock.
                If locked on arrival, there's a <strong>R550 fee</strong> to unlock it remotely with your help — or R550 return shipping.
            </div>
        `;
        container.appendChild(notice);
        this.scrollToBottom();
    }

    // ============================================
    // QUICK-SELECT BUTTONS
    // ============================================

    showQuickSelect(options) {
        this.hideTextInput();
        const container = document.getElementById('chat-messages');

        const wrapper = document.createElement('div');
        wrapper.className = 'quick-select-buttons fade-in';

        options.forEach(option => {
            const btn = document.createElement('button');
            btn.className = 'quick-select-btn';
            btn.textContent = option;
            btn.addEventListener('click', async () => {
                // Disable all
                wrapper.querySelectorAll('.quick-select-btn').forEach(b => {
                    b.disabled = true;
                    b.style.opacity = '0.4';
                });
                btn.style.opacity = '1';
                btn.style.borderColor = 'var(--accent)';
                btn.style.color = 'var(--accent)';

                this.addMessage(option, 'user');
                this.showTypingIndicator();

                const data = await this.sendMessageV3(option);
                this.hideTypingIndicator();
                wrapper.remove();

                if (data) this.handleV3Response(data);
            });
            wrapper.appendChild(btn);
        });

        // Also show text input for custom answers
        this.showTextInput();
        container.appendChild(wrapper);
        this.scrollToBottom();
    }

    // ============================================
    // CHECKLIST (condition/damage)
    // ============================================

    showChecklist(options, fieldName) {
        this.hideTextInput();
        const container = document.getElementById('chat-messages');

        const wrapper = document.createElement('div');
        wrapper.className = 'checklist-container fade-in';

        const itemsDiv = document.createElement('div');
        itemsDiv.className = 'checklist-items';

        const selected = new Set();

        options.forEach((option, idx) => {
            const item = document.createElement('button');
            item.className = 'checklist-item';
            item.textContent = option;
            item.dataset.value = option;

            const isPositive = option.includes('None') || option.includes('no issue') ||
                               option.includes('Like new') || option.includes('No damage');

            item.addEventListener('click', () => {
                if (selected.has(option)) {
                    selected.delete(option);
                    item.className = 'checklist-item';
                } else {
                    // If selecting "No issues", clear others
                    if (isPositive) {
                        selected.clear();
                        itemsDiv.querySelectorAll('.checklist-item').forEach(el => {
                            el.className = 'checklist-item';
                        });
                    } else {
                        // If selecting a damage item, deselect "no issues"
                        options.forEach(opt => {
                            if (opt.includes('None') || opt.includes('no issue') ||
                                opt.includes('Like new') || opt.includes('No damage')) {
                                selected.delete(opt);
                            }
                        });
                        itemsDiv.querySelectorAll('.checklist-item').forEach(el => {
                            const val = el.dataset.value;
                            if (val.includes('None') || val.includes('no issue') ||
                                val.includes('Like new') || val.includes('No damage')) {
                                el.className = 'checklist-item';
                            }
                        });
                    }
                    selected.add(option);
                    item.className = isPositive
                        ? 'checklist-item selected positive'
                        : 'checklist-item selected negative';
                }
            });

            itemsDiv.appendChild(item);
        });

        const submitBtn = document.createElement('button');
        submitBtn.className = 'checklist-submit';
        submitBtn.textContent = 'Continue';
        submitBtn.addEventListener('click', async () => {
            if (selected.size === 0) {
                this.showError('Please select at least one option');
                return;
            }

            const values = Array.from(selected);
            const answer = values.join(', ');

            // Disable
            wrapper.querySelectorAll('button').forEach(b => b.disabled = true);
            wrapper.style.opacity = '0.6';

            this.addMessage(answer, 'user');
            this.showTypingIndicator();

            const data = await this.sendMessageV3(answer);
            this.hideTypingIndicator();
            wrapper.remove();

            if (data) this.handleV3Response(data);
        });

        wrapper.appendChild(itemsDiv);
        wrapper.appendChild(submitBtn);
        container.appendChild(wrapper);
        this.scrollToBottom();
    }

    // ============================================
    // CALCULATION ANIMATION
    // ============================================

    showCalculationAnimation() {
        this.hideTextInput();
        const container = document.getElementById('chat-messages');

        const steps = [
            { icon: '1', label: 'Researching SA market prices...' },
            { icon: '2', label: 'Calculating depreciation...' },
            { icon: '3', label: 'Estimating repair costs...' },
            { icon: '4', label: 'Offer ready!' }
        ];

        const animDiv = document.createElement('div');
        animDiv.id = 'calc-animation';
        animDiv.className = 'calculation-animation fade-in';

        steps.forEach((step, idx) => {
            animDiv.innerHTML += `
                <div class="calc-step ${idx === 0 ? 'active' : 'inactive'}" id="calc-step-${idx}">
                    <div class="calc-icon">${idx === 0 ? '&#10003;' : step.icon}</div>
                    <div class="calc-label">${step.label}</div>
                </div>
            `;
        });

        container.appendChild(animDiv);
        this.scrollToBottom();

        // Animate steps
        let currentStep = 0;
        const interval = setInterval(() => {
            currentStep++;
            if (currentStep < steps.length) {
                const stepEl = document.getElementById(`calc-step-${currentStep}`);
                if (stepEl) {
                    stepEl.classList.remove('inactive');
                    stepEl.classList.add('active');
                    stepEl.querySelector('.calc-icon').innerHTML = '&#10003;';
                }
            }
            if (currentStep >= steps.length - 1) {
                clearInterval(interval);
                // Trigger offer calculation after animation
                setTimeout(() => this.calculateOffer(), 500);
            }
        }, 1200);
    }

    // ============================================
    // OFFER CALCULATION
    // ============================================

    async calculateOffer() {
        try {
            const response = await fetch('/api/calculate-offer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const data = await response.json();

            // Remove animation
            const animDiv = document.getElementById('calc-animation');
            if (animDiv) animDiv.remove();

            if (data.success) {
                this.currentOffer = data.offer;
                this.displayOffer(data.offer);
            } else {
                this.showError(data.error || 'Failed to calculate offer');
            }
        } catch (error) {
            console.error('Offer calculation error:', error);
            this.showError('Error calculating offer. Please try again.');
        }
    }

    // ============================================
    // OFFER DISPLAY (Screen 3)
    // ============================================

    buildChoicesSummary() {
        const fields = this.productInfo.collected_fields || {};
        const metadata = new Set(['name', 'brand', 'category', 'model']);
        const items = [];

        // Friendly labels for field names
        const labels = {
            condition: 'Condition',
            damage: 'Damage',
            damage_details: 'Damage',
            condition_details: 'Condition',
            storage: 'Storage',
            color: 'Colour',
            colour: 'Colour',
            unlock_status: 'Network',
            network: 'Network',
            accessories: 'Accessories',
            battery_health: 'Battery health',
            year: 'Year',
            mileage: 'Mileage',
            size: 'Size',
            ram: 'RAM'
        };

        for (const [key, value] of Object.entries(fields)) {
            if (metadata.has(key) || !value) continue;
            const label = labels[key] || key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
            let display = Array.isArray(value) ? value.join(', ') : String(value);
            // Clean up internal values
            if (display === 'no_damage') display = 'No damage';
            if (display === 'unknown') display = 'Unknown';
            items.push({ label, display, isDamage: display.toLowerCase().includes('damage') || display.toLowerCase().includes('crack') || display.toLowerCase().includes('water') || display.toLowerCase().includes('broken') });
        }

        if (items.length === 0) return '';

        const rows = items.map(item =>
            `<div class="summary-row">
                <span class="summary-label">${this.escapeHtml(item.label)}</span>
                <span class="summary-value ${item.isDamage ? 'damage' : ''}">${this.escapeHtml(item.display)}</span>
            </div>`
        ).join('');

        return `
            <div class="choices-summary">
                <p class="summary-heading">YOUR DETAILS</p>
                ${rows}
            </div>
        `;
    }

    displayOffer(offer) {
        this.showScreen('offer-screen');
        const container = document.getElementById('offer-container');

        // Store for later
        this.productInfo = offer.product_info || {};

        const productName = `${this.productInfo.brand || ''} ${this.productInfo.model || ''}`.trim() || 'Your Item';

        // Handle user estimate request
        if (offer.recommendation === 'user_estimate') {
            container.innerHTML = `
                <div class="offer-header">
                    <p class="offer-label">PRICING</p>
                    <h2 class="offer-title">We need your help</h2>
                </div>
                <div class="pricing-breakdown">
                    <p style="color: var(--text-secondary); margin-bottom: 16px;">
                        We couldn't find enough pricing data for your item in the market.
                        Could you tell us what you think it's worth second-hand?
                    </p>
                    <input type="number" id="user-estimate" class="input-field" placeholder="e.g., 5000" min="0" step="50" style="width:100%; margin-bottom:12px;">
                    <button class="accept-button" id="submit-estimate-btn">Calculate My Offer</button>
                    <p style="color: var(--text-muted); font-size: 12px; margin-top: 12px;">
                        We'll make you an offer at 70% of your estimate and contact you for manual assessment.
                    </p>
                </div>
            `;
            document.getElementById('submit-estimate-btn').addEventListener('click', () => this.submitUserEstimate());
            return;
        }

        // Handle manual review with user estimate
        if (offer.recommendation === 'manual_review' && offer.based_on_user_estimate) {
            container.innerHTML = `
                <div class="offer-header">
                    <p class="offer-label">PRELIMINARY OFFER</p>
                    <h2 class="offer-title">${this.escapeHtml(productName)}</h2>
                </div>
                <div class="pricing-breakdown">
                    <div class="breakdown-row">
                        <span class="breakdown-label">Your Estimate</span>
                        <span class="breakdown-value">R${this.fmt(offer.market_value)}</span>
                    </div>
                    ${offer.repair_costs > 0 ? `
                    <div class="breakdown-row">
                        <span class="breakdown-label">Repair Costs</span>
                        <span class="breakdown-value negative">-R${this.fmt(offer.repair_costs)}</span>
                    </div>` : ''}
                    <div class="breakdown-row breakdown-divider">
                        <span class="breakdown-total-label">Our Offer (70%)</span>
                        <span class="breakdown-total-value">R${this.fmt(offer.offer_amount)}</span>
                    </div>
                    <p class="breakdown-source">This offer is based on your estimate and requires manual assessment. Our team will contact you within 2 working days.</p>
                </div>
            `;
            document.getElementById('customer-form').classList.remove('hidden');
            return;
        }

        if (offer.recommendation === 'instant_offer') {
            const sellNow = offer.sell_now_offer || 0;
            const consignment = offer.consignment_payout || 0;
            const extra = consignment - sellNow;
            const summaryHtml = this.buildChoicesSummary();

            container.innerHTML = `
                <div class="offer-header">
                    <p class="offer-label">YOUR OFFER</p>
                    <h2 class="offer-title">${this.escapeHtml(productName)}</h2>
                </div>

                ${summaryHtml}

                <div class="pricing-breakdown">
                    <div class="breakdown-row">
                        <span class="breakdown-label">Market value (used, working)</span>
                        <span class="breakdown-value">R${this.fmt(offer.market_value)}</span>
                    </div>
                    ${offer.repair_costs > 0 ? `
                    <div class="breakdown-row">
                        <span class="breakdown-label">Less: Repair costs</span>
                        <span class="breakdown-value negative">-R${this.fmt(offer.repair_costs)}</span>
                    </div>
                    <div class="breakdown-row breakdown-divider">
                        <span class="breakdown-total-label">Value to us</span>
                        <span class="breakdown-total-value">R${this.fmt(offer.adjusted_value)}</span>
                    </div>` : ''}
                    <p class="breakdown-source">Market value based on current used listings from PriceCheck, Bob Shop, and Gumtree (Feb 2026). Repair estimates from iStore, iFix, and local SA repair shops.</p>
                </div>

                <button class="offer-card" id="card-sell-now" onclick="app.selectOfferCard('sell_now')">
                    <div class="offer-card-content">
                        <div>
                            <p class="offer-card-title">Sell Now</p>
                            <p class="offer-card-subtitle">Paid within 3 working days. We collect via courier.</p>
                        </div>
                        <div class="offer-card-price-section">
                            <div class="offer-card-price">R${this.fmt(sellNow)}</div>
                        </div>
                    </div>
                </button>

                <button class="offer-card" id="card-consignment" onclick="app.selectOfferCard('consignment')">
                    <div class="offer-card-badge">RECOMMENDED</div>
                    <div class="offer-card-content">
                        <div>
                            <p class="offer-card-title">Consignment</p>
                            <p class="offer-card-subtitle">We sell for you. Paid 2 days after buyer receives.</p>
                        </div>
                        <div class="offer-card-price-section">
                            <div class="offer-card-price">R${this.fmt(consignment)}</div>
                            <p class="offer-card-savings">Get R${this.fmt(extra)} more</p>
                        </div>
                    </div>
                </button>

                ${this.isImeiDevice ? `
                <div class="imei-offer-warning">
                    <div class="imei-offer-warning-text">
                        <strong>🔒 Account Lock Policy</strong><br>
                        This device must arrive without an iCloud, Google, or Samsung account lock.
                        If locked on arrival: <strong>R550 remote unlock fee</strong> (with your assistance) or <strong>R550 return shipping</strong>.
                    </div>
                    <label class="imei-acknowledge-label" id="imei-ack-label">
                        <input type="checkbox" id="imei-acknowledge" onchange="app.onImeiAcknowledge()">
                        <span>I acknowledge the account lock policy</span>
                    </label>
                </div>
                ` : ''}

                <button class="accept-button" id="accept-offer-btn" style="display:none;" onclick="app.acceptOffer()">Accept Offer &rarr;</button>

                <button class="secondary-button" id="too-low-btn" onclick="app.showPriceDispute()">Offer too low? Tell us why</button>

                <p style="color: var(--text-muted); font-size: 12px; text-align: center; margin-top: 16px;">
                    All offers require manual verification. We'll confirm within 2 working days.
                </p>
            `;
        } else {
            // Manual review / other
            container.innerHTML = `
                <div class="offer-header">
                    <p class="offer-label">REVIEW NEEDED</p>
                    <h2 class="offer-title">${this.escapeHtml(productName)}</h2>
                </div>
                <div class="pricing-breakdown">
                    <p style="color: var(--text-secondary); margin-bottom: 12px;">${offer.reason || 'We would like to review your item personally.'}</p>
                    <div class="breakdown-row">
                        <span class="breakdown-label">Estimated Value Range</span>
                        <span class="breakdown-value">R${this.fmt(offer.market_value * 0.6)} - R${this.fmt(offer.market_value * 0.8)}</span>
                    </div>
                    <p class="breakdown-source">Our team will contact you within 2 working days with a personalized offer.</p>
                </div>
            `;
            document.getElementById('customer-form').classList.remove('hidden');
        }
    }

    selectOfferCard(type) {
        // Reset both
        document.getElementById('card-sell-now').classList.remove('selected');
        document.getElementById('card-consignment').classList.remove('selected');

        // Select chosen
        if (type === 'sell_now') {
            document.getElementById('card-sell-now').classList.add('selected');
        } else {
            document.getElementById('card-consignment').classList.add('selected');
        }

        this.selectedOfferType = type;

        // Show accept button only if IMEI acknowledged (or not an IMEI device)
        this.updateAcceptButton();
    }

    onImeiAcknowledge() {
        // Called when the IMEI acknowledgment checkbox changes
        this.updateAcceptButton();
    }

    updateAcceptButton() {
        const acceptBtn = document.getElementById('accept-offer-btn');
        if (!acceptBtn) return;

        const hasSelectedCard = this.selectedOfferType;
        const imeiCheckbox = document.getElementById('imei-acknowledge');
        const imeiAcknowledged = !this.isImeiDevice || (imeiCheckbox && imeiCheckbox.checked);

        if (hasSelectedCard && imeiAcknowledged) {
            acceptBtn.style.display = 'block';
        } else if (hasSelectedCard && !imeiAcknowledged) {
            // Card selected but IMEI not acknowledged — hide accept, highlight checkbox
            acceptBtn.style.display = 'none';
            const label = document.getElementById('imei-ack-label');
            if (label) {
                label.classList.add('highlight');
                setTimeout(() => label.classList.remove('highlight'), 1500);
            }
        } else {
            acceptBtn.style.display = 'none';
        }
    }

    acceptOffer() {
        // Show customer form
        document.getElementById('customer-form').classList.remove('hidden');
        document.getElementById('customer-form').scrollIntoView({ behavior: 'smooth' });
    }

    // ============================================
    // USER ESTIMATE
    // ============================================

    async submitUserEstimate() {
        const input = document.getElementById('user-estimate');
        const estimate = parseFloat(input.value);

        if (!estimate || estimate <= 0) {
            this.showError('Please enter a valid estimate amount');
            return;
        }

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
        }
    }

    // ============================================
    // PRICE DISPUTE
    // ============================================

    showPriceDispute() {
        const container = document.getElementById('offer-container');
        const ourEstimate = this.currentOffer?.adjusted_value || this.currentOffer?.market_value || 0;

        container.innerHTML = `
            <div class="offer-header">
                <p class="offer-label">FEEDBACK</p>
                <h2 class="offer-title">Help Us Get It Right</h2>
            </div>
            <div class="pricing-breakdown">
                <div class="breakdown-row">
                    <span class="breakdown-label">Our Estimate</span>
                    <span class="breakdown-value">R${this.fmt(ourEstimate)}</span>
                </div>
            </div>
            <div style="margin-top: 16px;">
                <label style="color: var(--text-secondary); font-size: 13px; display:block; margin-bottom:6px;">Your Estimate (ZAR)</label>
                <input type="number" id="dispute-estimate" class="input-field" placeholder="e.g., 8000" min="0" step="100" style="width:100%; margin-bottom:12px;">
                <label style="color: var(--text-secondary); font-size: 13px; display:block; margin-bottom:6px;">Why do you think it's worth more/less?</label>
                <textarea id="dispute-reason" class="input-field" rows="4" placeholder="Please explain..." style="width:100%; margin-bottom:12px; resize:vertical;"></textarea>
                <label style="color: var(--text-secondary); font-size: 13px; display:block; margin-bottom:6px;">Links to similar items (optional)</label>
                <input type="url" id="dispute-link1" class="input-field" placeholder="https://..." style="width:100%; margin-bottom:6px;">
                <input type="url" id="dispute-link2" class="input-field" placeholder="https://..." style="width:100%; margin-bottom:6px;">
                <input type="url" id="dispute-link3" class="input-field" placeholder="https://..." style="width:100%; margin-bottom:16px;">
                <button class="accept-button" onclick="app.submitPriceDispute()">Submit Feedback</button>
                <button class="secondary-button" onclick="app.displayOffer(app.currentOffer)" style="margin-top:8px;">Cancel</button>
            </div>
        `;
    }

    async submitPriceDispute() {
        const estimate = parseFloat(document.getElementById('dispute-estimate').value);
        const reason = document.getElementById('dispute-reason').value.trim();
        const link1 = document.getElementById('dispute-link1').value.trim();
        const link2 = document.getElementById('dispute-link2').value.trim();
        const link3 = document.getElementById('dispute-link3').value.trim();

        if (!estimate || estimate <= 0) {
            this.showError('Please enter your estimated value');
            return;
        }
        if (!reason) {
            this.showError('Please explain your reasoning');
            return;
        }

        const links = [link1, link2, link3].filter(l => l.length > 0);

        try {
            const response = await fetch('/api/dispute-price', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_estimate: estimate,
                    justification: reason,
                    links
                })
            });
            const data = await response.json();

            if (data.success) {
                const container = document.getElementById('offer-container');
                container.innerHTML = `
                    <div class="offer-header">
                        <p class="offer-label">SUBMITTED</p>
                        <h2 class="offer-title">Thank You!</h2>
                    </div>
                    <div class="pricing-breakdown">
                        <p style="color: var(--text-secondary);">${data.message || "We've received your feedback and will review it carefully."}</p>
                        <p style="color: var(--text-muted); font-size: 13px; margin-top: 12px;">You'll hear from us within 2 working days.</p>
                    </div>
                `;
            } else {
                this.showError(data.error || 'Failed to submit feedback');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showError('Connection error. Please try again.');
        }
    }

    // ============================================
    // CUSTOMER INFO SUBMISSION
    // ============================================

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

        try {
            const response = await fetch('/api/submit-customer-info', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name, email, phone, address,
                    collection_date: collectionDate,
                    terms_agreed: termsAgreed
                })
            });
            const data = await response.json();

            if (data.success) {
                document.getElementById('customer-form').classList.add('hidden');
                const container = document.getElementById('offer-container');

                if (data.type === 'instant_offer') {
                    container.innerHTML = `
                        <div class="offer-header">
                            <p class="offer-label">CONFIRMED</p>
                            <h2 class="offer-title">Offer Confirmed!</h2>
                        </div>
                        <div class="pricing-breakdown" style="text-align:center;">
                            <div style="font-size:36px; font-weight:800; color:var(--accent); margin:16px 0;">R${this.fmt(data.offer_amount)}</div>
                            <p style="color: var(--text-secondary);">${data.message}</p>
                            <p style="color: var(--text-muted); font-size: 13px; margin-top: 12px;">We'll be in touch soon to arrange collection.</p>
                        </div>
                        <button class="secondary-button" onclick="location.reload()" style="margin-top:16px;">Sell Another Item</button>
                    `;
                } else {
                    container.innerHTML = `
                        <div class="offer-header">
                            <p class="offer-label">SUBMITTED</p>
                            <h2 class="offer-title">Request Submitted!</h2>
                        </div>
                        <div class="pricing-breakdown">
                            <p style="color: var(--text-secondary);">${data.message}</p>
                        </div>
                        <button class="secondary-button" onclick="location.reload()" style="margin-top:16px;">Sell Another Item</button>
                    `;
                }
            } else {
                this.showError(data.error || 'Failed to submit. Please try again.');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showError('Connection error. Please try again.');
        }
    }

    // ============================================
    // UTILITIES
    // ============================================

    showError(message) {
        // Show error toast at top of screen
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed; top: 16px; left: 50%; transform: translateX(-50%);
            background: var(--danger); color: white; padding: 12px 24px;
            border-radius: 10px; font-size: 14px; font-weight: 600;
            z-index: 1000; animation: fadeIn 0.3s ease;
        `;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }

    fmt(num) {
        if (num === null || num === undefined || isNaN(num)) return '0';
        return Number(num).toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new EpicDealsApp();
});
