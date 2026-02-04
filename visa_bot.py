import requests
import os

BLS_URL = "https://www.blsspainvisa.com/turkey/ankara/"
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
STATE_FILE = "state.txt"


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })


def is_appointment_open():
    r = requests.get(BLS_URL, timeout=20)
    page = r.text.lower()

    # BLS genelde kapalıyken bu ifadeler olur
    closed_keywords = [
        "no appointment",
        "currently no slots",
        "appointment slots are not available"
    ]

    return not any(k in page for k in closed_keywords)


def load_previous_state():
    if not os.path.exists(STATE_FILE):
        return None  # ilk çalıştırma
    with open(STATE_FILE, "r") as f:
        return f.read().strip()


def save_state(state):
    with open(STATE_FILE, "w") as f:
        f.write(state)


def main():
    current_open = is_appointment_open()
    previous_state = load_previous_state()

    # previous_state: None | "open" | "closed"

    if previous_state is None:
        # Bot ilk kez çalışıyor
        if current_open:
            send_telegram("🚨 BLS Ankara RANDEVU AÇIK! (bot ilk çalıştırma)")
            save_state("open")
        else:
            save_state("closed")

    elif previous_state == "closed" and current_open:
        # Kapalı → Açık
        send_telegram("🚨 BLS Ankara RANDEVU AÇILDI!")
        save_state("open")

    elif previous_state == "open" and not current_open:
        # Açık → Kapalı
        save_state("closed")

    # Diğer durumlar: hiçbir şey yapma


if __name__ == "__main__":
    main()
