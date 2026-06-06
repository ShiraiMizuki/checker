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
}

EMAIL_FROM = os.getenv("shirai110409@gmail.com")
EMAIL_TO = os.getenv("filipm.zst@gmail.com")
EMAIL_PASSWORD = os.getenv("1507 5713")
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

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Email failed: {e}")

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting AstroVials check...")
    message = f"AstroVials Stock Update - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    has_stock = False

    for name, url in PRODUCTS.items():
        status = check_product(name, url)
        print(f"   {name}: {status}")

        if "IN STOCK" in status:
            has_stock = True
            message += f"🚨 RESTOCK ALERT: {name} is now IN STOCK!\n{url}\n\n"

        message += f"{name}: {status}\n"

    if has_stock:
        send_email("🚨 AstroVials RESTOCK ALERT!", message)
    else:
        print("   No items in stock.")

if __name__ == "__main__":
    main()
