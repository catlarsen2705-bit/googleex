"""
Email notification system for sales alerts.
Sends SMTP emails when sales are found on tracked stores.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List

from dotenv import load_dotenv

from backend.models import Product

load_dotenv()

# Email configuration
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", MAIL_USERNAME)


def send_sale_notification(store: str, products: List[Product]) -> bool:
    """
    Send an email notification about sales.

    Args:
        store: Store name (e.g., 'JYSK', 'IKEA')
        products: List of products on sale

    Returns:
        True if email was sent, False otherwise
    """
    if not MAIL_USERNAME or not MAIL_PASSWORD:
        print("Warning: Email credentials not configured in .env")
        return False

    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🛒 Udsalg på {store}!"
        msg["From"] = MAIL_USERNAME
        msg["To"] = RECIPIENT_EMAIL

        # Create plain text version
        text = f"Udsalg på {store}!\n\n"
        text += f"Fandt {len(products)} produkter:\n\n"
        for product in products[:10]:  # Max 10 products in email
            text += f"- {product.name}\n"
            text += f"  Pris: {product.price.amount} {product.price.currency}\n"
            if product.url:
                text += f"  Link: {product.url}\n"
            text += "\n"

        # Create HTML version
        html = f"""
        <html>
            <body>
                <h2>🛒 Udsalg på {store}!</h2>
                <p>Fandt {len(products)} produkter på udsalg:</p>
                <ul>
        """
        for product in products[:10]:  # Max 10 products in email
            html += f"""
                    <li>
                        <strong>{product.name}</strong><br>
                        Pris: {product.price.amount} {product.price.currency}
            """
            if product.url:
                html += f'<br><a href="{product.url}">Se produktet →</a>'
            html += "</li>"

        html += """
                </ul>
                <p><em>Udsalgstracker</em></p>
            </body>
        </html>
        """

        # Attach both versions
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        msg.attach(part1)
        msg.attach(part2)

        # Send email
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            if MAIL_USE_TLS:
                server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)

        print(f"✓ Email sent for {store} with {len(products)} products")
        return True

    except Exception as e:
        print(f"✗ Error sending email notification: {e}")
        return False


def send_browser_notification(title: str, message: str) -> None:
    """
    This would trigger browser notifications via the extension.
    For now, it's a placeholder for future integration.
    """
    print(f"Browser notification: {title} - {message}")
