import requests
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
    # Add more products here as needed
}

# Email settings
EMAIL_FROM = os.getenv("shirai110409@gmail.com")
EMAIL_TO = os.getenv("filipm.zst@gmail.com")
EMAIL_PASSWORD = os.getenv("1507 5713")
# ========================================================

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; AstroVialsStockChecker/1.0)"
}

def send_email(subject, body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        print(f"✅ Email sent: {subject}")
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

def check_product(name, url):
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        text = soup.get_text().lower()

        if "availability: out of stock" in text or "out of stock" in text:
            return "❌ Out of stock"
        elif "add to cart" in text or "in stock" in text:
            return "✅ IN STOCK!"
        else:
            return "⚠️ Unknown status"
    except Exception as e:
        return f"❌ Error: {str(e)[:60]}"

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking AstroVials stock...")

    message = f"AstroVials Stock Update - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    stock_changed = False

    for name, url in PRODUCTS.items():
        status = check_product(name, url)
        print(f"   {name}: {status}")

        # For GitHub Actions we always send if something is in stock
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
