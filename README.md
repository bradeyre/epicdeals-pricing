# EpicDeals AI Price Research Tool

An intelligent price research and offer generation system for EpicDeals.co.za that automatically evaluates second-hand items and makes instant purchase offers.

## Features

- **Adaptive Questionnaire**: AI-driven conversation that asks relevant questions based on item type
- **Multi-Source Price Research**:
  - EpicDeals.co.za website
  - Competitor sites (wefix.co.za, swopp.co.za, istorepreowned.co.za)
  - Facebook Marketplace
  - eBay (with USD/ZAR conversion)
- **Repair Cost Estimation**: AI researches repair costs for damaged items
- **Smart Offer Calculation**: 70% of market value minus repair costs
- **Confidence-Based Decisions**: Instant offers when confident, email fallback when uncertain
- **WordPress Integration**: Easy embedding via iframe or shortcode

## Technology Stack

- **Backend**: Python 3.9+, Flask
- **AI**: Anthropic Claude API (for intelligent conversations and research)
- **Web Scraping**: BeautifulSoup4, Selenium (for dynamic content)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Email**: SMTP for notifications

## Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Anthropic API key (get from https://console.anthropic.com/)
- Chrome/Chromium browser (for Selenium scraping)

### Installation

1. Clone or download this repository

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install ChromeDriver (for web scraping):
```bash
# macOS
brew install chromedriver

# Linux
sudo apt-get install chromium-chromedriver

# Windows - download from https://chromedriver.chromium.org/
```

4. Create `.env` file with your configuration:
```bash
cp .env.example .env
```

5. Edit `.env` with your actual values:
```
ANTHROPIC_API_KEY=your_api_key_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
NOTIFICATION_EMAIL=brad@epicdeals.co.za
```

### Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser to `http://localhost:5000`

### WordPress Integration

See `WORDPRESS_INTEGRATION.md` for detailed embedding instructions.

## Project Structure

```
.
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .env                           # Your actual configuration (git-ignored)
├── config.py                      # Configuration management
├── services/
│   ├── ai_service.py              # Claude AI integration
│   ├── price_research_service.py  # Multi-source price research
│   ├── repair_cost_service.py     # Repair cost estimation
│   ├── offer_service.py           # Offer calculation logic
│   └── email_service.py           # Email notifications
├── scrapers/
│   ├── epicdeals_scraper.py       # EpicDeals.co.za scraper
│   ├── competitor_scraper.py      # Competitor sites scraper
│   ├── facebook_scraper.py        # Facebook Marketplace scraper
│   └── ebay_scraper.py            # eBay scraper
├── static/
│   ├── css/
│   │   └── style.css              # Frontend styles
│   └── js/
│       └── app.js                 # Frontend JavaScript
├── templates/
│   └── index.html                 # Main web interface
└── utils/
    ├── currency_converter.py      # USD/ZAR conversion
    └── validators.py              # Input validation
```

## How It Works

1. **Customer initiates**: Visits the tool on your website
2. **AI conversation**: System asks adaptive questions about the item
3. **Price research**: Checks multiple sources for market value
4. **Repair assessment**: If damaged, estimates repair costs
5. **Offer calculation**: Applies formula: (Market Value - Repair Costs) × 70%
6. **Instant offer or email**: High confidence = instant offer; Low confidence = email to Brad

## Configuration

### Price Research Settings

Edit `config.py` to adjust:
- Offer percentage (default: 70%)
- Minimum/maximum item value (R5,000 - R25,000)
- Confidence threshold for instant offers
- Timeout values for scraping
- Price source priorities

### Email Templates

Email templates are in `services/email_service.py` and can be customized.

## Security & Privacy

- Never commit `.env` file
- Use app passwords for email (not your main password)
- FB Marketplace scraping may be against TOS - use at your own risk
- Implement rate limiting in production
- Use HTTPS in production

## Support

For issues or questions, contact the development team.

## License

Proprietary - EpicDeals.co.za
