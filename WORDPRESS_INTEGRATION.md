# WordPress Integration Guide

This guide explains how to embed the EpicDeals AI Price Research Tool into your WordPress website.

## Prerequisites

1. The Flask application must be running on a server (not localhost for production)
2. WordPress admin access
3. Basic knowledge of WordPress page editing

## Method 1: iFrame Embedding (Easiest)

This is the simplest method and works with any WordPress theme.

### Step 1: Deploy the Application

First, deploy your Flask app to a server and note the URL (e.g., `https://tools.epicdeals.co.za`)

### Step 2: Create a WordPress Page

1. Go to **Pages → Add New** in WordPress admin
2. Give it a title like "Sell Your Item" or "Get an Instant Quote"
3. Switch to the **HTML/Code editor** (not Visual)

### Step 3: Add iFrame Code

```html
<div style="width: 100%; max-width: 600px; margin: 0 auto;">
    <iframe
        src="https://YOUR_SERVER_URL:5000/"
        width="100%"
        height="800px"
        frameborder="0"
        style="border: none; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    </iframe>
</div>
```

Replace `YOUR_SERVER_URL` with your actual server URL.

### Step 4: Publish

Click **Publish** and view your page!

---

## Method 2: WordPress Shortcode (More Flexible)

This method creates a shortcode you can use anywhere in WordPress.

### Step 1: Add to functions.php

1. Go to **Appearance → Theme Editor**
2. Open `functions.php`
3. Add this code at the bottom:

```php
<?php
// EpicDeals Price Tool Shortcode
function epicdeals_price_tool_shortcode($atts) {
    $atts = shortcode_atts(array(
        'width' => '100%',
        'height' => '800px',
    ), $atts);

    $output = '<div class="epicdeals-tool-container" style="width: 100%; max-width: 600px; margin: 0 auto;">';
    $output .= '<iframe ';
    $output .= 'src="https://YOUR_SERVER_URL:5000/" ';
    $output .= 'width="' . esc_attr($atts['width']) . '" ';
    $output .= 'height="' . esc_attr($atts['height']) . '" ';
    $output .= 'frameborder="0" ';
    $output .= 'style="border: none; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">';
    $output .= '</iframe>';
    $output .= '</div>';

    return $output;
}
add_shortcode('epicdeals_tool', 'epicdeals_price_tool_shortcode');
?>
```

**Important:** Replace `YOUR_SERVER_URL` with your actual server URL!

### Step 2: Use the Shortcode

Now you can use this shortcode anywhere:

```
[epicdeals_tool]
```

Or with custom dimensions:

```
[epicdeals_tool width="100%" height="900px"]
```

---

## Method 3: WooCommerce Integration

Add a "Sell Your Items" page alongside your shop.

### Step 1: Create a WooCommerce Page

1. Go to **WooCommerce → Settings**
2. Create a new page called "Sell to Us"
3. Use either the iFrame or shortcode method above

### Step 2: Add to Menu

1. Go to **Appearance → Menus**
2. Add your new page to the main navigation
3. Save the menu

---

## Method 4: Full Page Template (Advanced)

Create a custom page template for a seamless experience.

### Step 1: Create Template File

1. Access your theme files via FTP or cPanel File Manager
2. Navigate to `/wp-content/themes/YOUR_THEME/`
3. Create a new file: `template-epicdeals-tool.php`

```php
<?php
/*
Template Name: EpicDeals Price Tool
*/
?>
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php wp_title('|', true, 'right'); ?></title>
    <style>
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
        }
        #epicdeals-frame {
            width: 100vw;
            height: 100vh;
            border: none;
        }
    </style>
</head>
<body>
    <iframe
        id="epicdeals-frame"
        src="https://YOUR_SERVER_URL:5000/"
        frameborder="0">
    </iframe>
</body>
</html>
```

### Step 2: Use Template

1. Create a new page in WordPress
2. In **Page Attributes**, select **Template: EpicDeals Price Tool**
3. Publish

---

## Production Deployment Options

### Option 1: Dedicated Subdomain

Deploy on a subdomain like `tools.epicdeals.co.za`

**Advantages:**
- Clean URL
- Separate from main site
- Easy SSL setup

**Steps:**
1. Create A record pointing to your server IP
2. Configure your server to serve the app on this subdomain
3. Install SSL certificate (Let's Encrypt is free)

### Option 2: Same Server as WordPress

Run Flask app on the same server as WordPress.

**Using Apache:**

1. Install mod_wsgi: `sudo apt-get install libapache2-mod-wsgi-py3`

2. Create WSGI file: `/var/www/epicdeals-tool/app.wsgi`

```python
import sys
sys.path.insert(0, '/var/www/epicdeals-tool')

from app import app as application
```

3. Configure Apache virtual host:

```apache
<VirtualHost *:80>
    ServerName tools.epicdeals.co.za

    WSGIDaemonProcess epicdeals user=www-data group=www-data threads=5
    WSGIScriptAlias / /var/www/epicdeals-tool/app.wsgi

    <Directory /var/www/epicdeals-tool>
        WSGIProcessGroup epicdeals
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>
</VirtualHost>
```

### Option 3: Cloud Hosting

Deploy to cloud platforms:

**Heroku:**
1. Create `Procfile`:
```
web: python app.py
```

2. Deploy:
```bash
heroku create epicdeals-tool
git push heroku main
```

**DigitalOcean App Platform:**
1. Connect GitHub repo
2. Configure build command: `pip install -r requirements.txt`
3. Configure run command: `python app.py`

**AWS EC2:**
1. Launch Ubuntu EC2 instance
2. Install dependencies
3. Use gunicorn to run: `gunicorn -w 4 -b 0.0.0.0:5000 app:app`
4. Set up nginx as reverse proxy

---

## Security Considerations

### 1. HTTPS (SSL)

Always use HTTPS in production. Get free certificates from Let's Encrypt:

```bash
sudo apt-get install certbot python3-certbot-apache
sudo certbot --apache -d tools.epicdeals.co.za
```

### 2. CORS Configuration

In `app.py`, restrict CORS to your domain:

```python
CORS(app, resources={r"/api/*": {"origins": "https://epicdeals.co.za"}})
```

### 3. Rate Limiting

Add rate limiting to prevent abuse:

```bash
pip install Flask-Limiter
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)
```

### 4. Environment Variables

Never commit `.env` file. Use server environment variables or secure vaults.

---

## Styling Tips

### Match WordPress Theme Colors

Add custom CSS in WordPress:

1. Go to **Appearance → Customize → Additional CSS**
2. Add:

```css
.epicdeals-tool-container {
    /* Match your theme's container */
    padding: 20px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .epicdeals-tool-container iframe {
        height: 100vh !important;
    }
}
```

### Remove WordPress Header/Footer

If using iFrame, the app already has its own header. To remove WP header/footer for full-page embedding:

```php
<?php
/*
Template Name: EpicDeals Full Width
*/

// Remove WordPress header
remove_action('wp_head', 'wp_print_styles', 8);
remove_action('wp_head', 'wp_print_head_scripts', 9);

get_header(); ?>

<div style="padding: 0; margin: 0;">
    <?php echo do_shortcode('[epicdeals_tool]'); ?>
</div>

<?php get_footer(); ?>
```

---

## Troubleshooting

### iFrame Not Loading

**Problem:** White screen or "Connection refused"

**Solutions:**
- Check Flask app is running: `curl http://YOUR_SERVER:5000/api/health`
- Check firewall allows port 5000
- Verify CORS settings in `app.py`

### Mixed Content Errors

**Problem:** Browser blocks HTTP content on HTTPS site

**Solution:** Ensure Flask app uses HTTPS too, or use relative URLs

### Session Issues

**Problem:** Conversation resets or loses state

**Solution:** Configure Flask session to use database instead of cookies:

```python
from flask_session import Session
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
```

### Styling Conflicts

**Problem:** WordPress CSS affects the iframe content

**Solution:** iFrame content is isolated, but if using full template, add:

```php
wp_deregister_style('style');
```

---

## Support

For issues:
1. Check Flask logs: `tail -f /var/log/flask/app.log`
2. Check WordPress debug: Enable `WP_DEBUG` in `wp-config.php`
3. Test API directly: `https://YOUR_SERVER:5000/api/health`

Need help? Contact your development team.
