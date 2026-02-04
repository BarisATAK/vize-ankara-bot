import requests
from bs4 import BeautifulSoup
import time
import os

# ================== AYARLAR ==================
BLS_URL = "https://www.blsinternational.com/turkey/visa/spain/"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "tr-TR,tr;q=0.9"
}
# =============================================

last_status = None


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })


def check_bls():
    global last_status

    response = requests.get(BLS_URL, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(response.text, "html.parser")
    page_text = soup.get_text().lower()

    current_status = "closed" if "not available" in page_text else "open"

    # 🔹 İlk çalıştırma
    if last_status is None:
        last_status = current_status
        if current_status == "open":
            send_telegram(
                "🚨 BLS ANKARA İSPANYA RANDEVUSU ZATEN AÇIK!\n"
                "Hemen kontrol et!"
            )
        return

    # 🔹 Kapalı → Açık
    if last_status == "closed" and current_status == "open":
        send_telegram(
            "🚨 BLS ANKARA İSPANYA RANDEVUSU AÇILDI!\n"
            "Hemen kontrol et!"
        )

    last_status = current_status


send_telegram("🤖 BLS Ankara randevu botu başlatıldı.")

while True:
    check_bls()
    time.sleep(600)  # 10 dakika
