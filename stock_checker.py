import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
import time
from datetime import datetime

# ====================== CONFIGURATION ======================
PRODUCTS = {
    "Estradiol Enanthate (MCT)": "https://astrovials.com/product/estradiol-enanthate/",
    "Estradiol Valerate (MCT)": "https://astrovials.com/product/estradiol-valerate/",
    "Estradiol Undecylate (MCT)": "https://astrovials.com/product/estradiol-undecylate/",
    "Estradiol Enanthate (Castor)": "https://astrovials.com/product/estradiol-enanthate-castor/",
}

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
# ========================================================

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://astrovials.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

def check_product(name, url):
    for attempt in range(3):  # Try 3 times
        try:
            r = requests.get(url, headers=get_headers(), timeout=25)
            if r.status_code == 403:
                time.sleep(5)  # Wait before retry
                continue
                
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')
            text = soup.get_text().lower()

            if "out of stock" in text or "availability: out of stock" in text:
                return "❌ Out of stock"
            elif "add to cart" in text or "in stock" in text:
                return "✅ IN STOCK!"
            else:
                return "⚠️ Unknown status"
        except Exception as e:
            if attempt == 2:
                return f"❌ Error: {str(e)[:80]}"
            time.sleep(3)
    return "❌ Blocked (403)"

def send_email(subject, body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        print(f"✅ Email sent!")
    except Exception as e:
        print(f"❌ Email failed: {e}")

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking AstroVials stock...")
    message = f"AstroVials Stock Update - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    stock_changed = False

    for name, url in PRODUCTS.items():
        status = check_product(name, url)
        print(f"   {name}: {status}")

        if "IN STOCK" in status:
            stock_changed = True
            message += f"🚨 RESTOCK ALERT: {name} is now IN STOCK!\n{url}\n\n"

        message += f"{name}: {status}\n"

    if stock_changed:
        send_email("🚨 AstroVials Stock Alert!", message)
    else:
        print("   No in-stock items detected.")

if __name__ == "__main__":
    main()
