import os
import requests

# -------------------------------
# CONFIG
# -------------------------------
BLS_URL = "https://turkey.blsspainglobal.com/Global/Appointment/GetAvailableDates"

# Telegram
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# Cookie (login sonrası aldığın .AspNetCore.Cookies)
BLS_COOKIE = os.environ["BLS_COOKIE"]

# Headers (tarayıcı taklidi)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/121.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://turkey.blsspainglobal.com/"
}

# -------------------------------
# FUNCTIONS
# -------------------------------

def send_telegram(message):
    """Telegram mesaj gönderir."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })


def load_state():
    """State dosyasını oku"""
    if not os.path.exists("state_bls.txt"):
        return "unknown"
    return open("state_bls.txt").read().strip()


def save_state(state):
    """State dosyasına yaz"""
    open("state_bls.txt", "w").write(state)


def is_bls_open():
    """BLS endpoint kontrolü"""
    try:
        r = requests.get(BLS_URL, cookies={".AspNetCore.Cookies": BLS_COOKIE}, headers=HEADERS, timeout=20)
        print(f"Checking BLS -> Status: {r.status_code}")
        print("Response preview:", r.text[:300])
        if r.status_code != 200:
            return False
        data = r.json()
        return len(data) > 0
    except Exception as e:
        print("Error checking BLS:", e)
        return False


# -------------------------------
# MAIN
# -------------------------------

def main():
    last_state = load_state()
    current_state = "open" if is_bls_open() else "closed"

    if last_state != current_state:
        send_telegram(f"BLS Ankara durumu değişti: {current_state.upper()}")
        save_state(current_state)


if __name__ == "__main__":
    main()

