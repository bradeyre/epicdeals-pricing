import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config
from datetime import datetime


class EmailService:
    """Handles email notifications"""

    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.username = Config.SMTP_USERNAME
        self.password = Config.SMTP_PASSWORD
        self.notification_email = Config.NOTIFICATION_EMAIL

    def send_manual_review_request(self, product_info, damage_info, offer_data, customer_info):
        """
        Send email to Brad for manual review

        Args:
            product_info: Product details
            damage_info: Damage information
            offer_data: Offer calculation data
            customer_info: Customer contact details
        """

        subject = f"Manual Review Required: {product_info.get('brand', '')} {product_info.get('model', '')}"

        body = self._format_review_email(product_info, damage_info, offer_data, customer_info)

        return self._send_email(
            to_email=self.notification_email,
            subject=subject,
            body=body
        )

    def send_offer_to_customer(self, customer_email, offer_data, product_info):
        """
        Send offer confirmation email to customer

        Args:
            customer_email: Customer's email address
            offer_data: Offer details
            product_info: Product information
        """

        subject = f"Your EpicDeals Offer: R{offer_data['offer_amount']:,.2f}"

        body = self._format_customer_offer_email(offer_data, product_info)

        return self._send_email(
            to_email=customer_email,
            subject=subject,
            body=body
        )

    def send_price_dispute_request(self, product_info, our_estimate, user_estimate, justification, links, customer_info):
        """
        Send email to Brad when user disputes pricing

        Args:
            product_info: Product details
            our_estimate: Our automated price estimate
            user_estimate: User's estimated value
            justification: User's reasoning
            links: List of URLs user provided as evidence
            customer_info: Customer contact details
        """

        subject = f"PRICE DISPUTE: {product_info.get('brand', '')} {product_info.get('model', '')} - User thinks R{user_estimate:,.0f} vs Our R{our_estimate:,.0f}"

        body = f"""
PRICE DISPUTE REQUEST
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRICING DISCREPANCY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Our Automated Estimate: R{our_estimate:,.2f}
User's Estimate: R{user_estimate:,.2f}
Difference: R{abs(user_estimate - our_estimate):,.2f} ({((user_estimate - our_estimate) / our_estimate * 100):.1f}%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CUSTOMER INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Name: {customer_info.get('name', 'Not provided')}
Email: {customer_info.get('email', 'Not provided')}
Phone: {customer_info.get('phone', 'Not provided')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRODUCT INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Category: {product_info.get('category', 'Unknown')}
Brand: {product_info.get('brand', 'Unknown')}
Model: {product_info.get('model', 'Unknown')}
Specifications: {product_info.get('specifications', {})}
Condition: {product_info.get('condition', 'Unknown')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USER'S JUSTIFICATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{justification if justification else 'No justification provided'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USER-PROVIDED LINKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""

        if links and len(links) > 0:
            for i, link in enumerate(links, 1):
                body += f"{i}. {link}\n"
        else:
            body += "No links provided\n"

        body += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ACTION REQUIRED:
1. Review the user's estimate and evidence
2. Check the provided links
3. Verify our automated pricing
4. Contact the user with revised offer or explanation

"""

        return self._send_email(
            to_email=self.notification_email,
            subject=subject,
            body=body
        )

    def _format_review_email(self, product_info, damage_info, offer_data, customer_info):
        """Format email for Brad's manual review"""

        email_body = f"""
MANUAL REVIEW REQUIRED
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CUSTOMER INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Name: {customer_info.get('name', 'Not provided')}
Email: {customer_info.get('email', 'Not provided')}
Phone: {customer_info.get('phone', 'Not provided')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRODUCT INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Category: {product_info.get('category', 'Unknown')}
Brand: {product_info.get('brand', 'Unknown')}
Model: {product_info.get('model', 'Unknown')}
Specifications: {product_info.get('specifications', {})}

Condition: {product_info.get('condition', 'Unknown')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DAMAGE DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{self._format_damage_info(damage_info)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AUTOMATED ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Reason for Review: {offer_data.get('reason', 'Unknown')}
Confidence Score: {offer_data.get('confidence', 0):.0%}

Market Value (Estimated): R{offer_data.get('market_value', 0):,.2f}
Repair Costs (Estimated): R{offer_data.get('repair_costs', 0):,.2f}
Suggested Offer: R{offer_data.get('offer_amount', 0):,.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRICE RESEARCH RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Sources Checked: {', '.join(offer_data.get('price_research', {}).get('sources_checked', []))}
Total Listings Found: {offer_data.get('price_research', {}).get('total_listings', 0)}

{self._format_price_breakdown(offer_data.get('price_research', {}).get('price_breakdown', {}))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please review and contact the customer with your offer.

"""

        return email_body

    def _format_customer_offer_email(self, offer_data, product_info):
        """Format offer confirmation email for customer"""

        email_body = f"""
Hi there!

Thank you for using the EpicDeals instant valuation tool.

Based on our market research, here's what we found:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR ITEM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{product_info.get('brand', '')} {product_info.get('model', '')}
Condition: {product_info.get('condition', '')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUR OFFER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Market Value: R{offer_data['market_value']:,.2f}
"""

        if offer_data['repair_costs'] > 0:
            email_body += f"Repair Costs: -R{offer_data['repair_costs']:,.2f}\n"

        email_body += f"""
YOUR OFFER: R{offer_data['offer_amount']:,.2f}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This offer is valid for 48 hours.

To accept this offer or ask any questions, please reply to this email or contact us at:
Phone: [Your phone number]
Email: {Config.NOTIFICATION_EMAIL}

Visit us: www.epicdeals.co.za

Thank you!
EpicDeals Team
"""

        return email_body

    def _format_damage_info(self, damage_info):
        """Format damage information for email"""
        if not damage_info:
            return "No damage reported"

        lines = []
        for key, value in damage_info.items():
            if value and value not in ['none', 'good', 'fully_working']:
                lines.append(f"{key.title()}: {value}")

        return '\n'.join(lines) if lines else "No significant damage"

    def _format_price_breakdown(self, price_breakdown):
        """Format price research breakdown"""
        lines = []

        for source, results in price_breakdown.items():
            if results:
                lines.append(f"\n{source.upper()}:")
                for result in results[:3]:  # Top 3 per source
                    price = result.get('price', result.get('price_usd', 0))
                    lines.append(f"  - {result.get('title', 'Unknown')}: R{price:,.2f}")

        return '\n'.join(lines) if lines else "No prices found"

    def _send_email(self, to_email, subject, body):
        """Send email via SMTP"""

        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject

            # Plain text version
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)

            # Send via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            print(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            print(f"Error sending email: {e}")
            return False
