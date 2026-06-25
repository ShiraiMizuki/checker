import cloudscraper
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
from datetime import datetime

# ====================== CONFIGURATION ======================
PRODUCTS = {
    "Estradiol Enanthate (MCT)": "https://astrovials.com/product/estradiol-enanthate/",
    "Estradiol Valerate (MCT)": "https://astrovials.com/product/estradiol-valerate/",
    "Estradiol Undecylate (MCT)": "https://astrovials.com/product/estradiol-undecylate/",
    "Estradiol Enanthate (Castor)": "https://astrovials.com/product/estradiol-enanthate-castor/",
    "Erasadiol Enanthate (serapharma)": "https://serapharma.net/product/estradiol-enanthate/",
    "Erasadiol Enanthate (proletahrt)": "https://www.proletahrt.com/Shop/Product?slug=estradiol-enanthate-40mgml-mct",
    
}

# FIX: Strings are placed directly here. 
# REMINDER: Replace 'YOUR_16_DIGIT_APP_PASSWORD' with your actual spaces-free Google App Password.
EMAIL_FROM = "filipm.zst@gmail.com"
EMAIL_TO = "filipm.zst@gmail.com"
EMAIL_PASSWORD = "vmfojqjtmpsbebmx " 
# ========================================================

scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'mobile': False
    }
)

def check_product(name, url):
    try:
        r = scraper.get(url, timeout=40)
        print(f"   {name} → Status: {r.status_code}")  # Debug info
        
        if r.status_code != 200:
            return f"❌ Blocked ({r.status_code})"
        
        soup = BeautifulSoup(r.text, 'html.parser')
        text = soup.get_text().lower()

        if "out of stock" in text or "currently unavailable" in text:
            return "❌ Out of stock"
        elif "add to cart" in text or "in stock" in text:
            return "✅ IN STOCK!"
        else:
            return "⚠️ Unknown status"
    except Exception as e:
        return f"❌ Error: {str(e)[:70]}"

def send_email(subject, body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO

        print(f"Attempting to send email from {EMAIL_FROM} to {EMAIL_TO}...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Email failed: {e}")

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting AstroVials check...")
    message = f"AstroVials Stock Update - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    message += "--------------------------------------------------------\n\n"
    has_stock = False

    for name, url in PRODUCTS.items():
        status = check_product(name, url)
        print(f"   {name}: {status}")

        if "IN STOCK" in status:
            has_stock = True
            message += f"🚨 RESTOCK ALERT: {name} is now IN STOCK!\n👉 {url}\n\n"
        else:
            message += f"{name}: {status}\n"

    # CHANGED: The script now sends an email in BOTH cases.
    if has_stock:
        subject = "🚨 AstroVials RESTOCK ALERT!"
    else:
        subject = "📋 AstroVials Stock Update (All Out of Stock)"
        message += "\nNo items are currently available."

    send_email(subject, message)

if __name__ == "__main__":
    main()
