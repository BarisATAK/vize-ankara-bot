import requests
import os
import json

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

STATE_FILE = "state.json"

closed_keywords = [
    "no appointment",
    "no available appointments",
    "all appointments are booked",
    "please check back later"
]
# ---------------- STATE ----------------

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {
        "bls_spain": False,
        "vfs_czech": False
    }

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

# ---------------- TELEGRAM ----------------

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })

# ---------------- BLS ----------------

BLS_URL = "https://ankara.blsspainvisa.com/appointment.php"

def is_bls_open():
    r = requests.get(BLS_URL, timeout=20)
    page = r.text.lower()
    
    return not any(k in page for k in closed_keywords)

# ---------------- VFS CZECH ----------------

VFS_CZ_URL = "https://visa.vfsglobal.com/tur/en/cze/"

def is_vfs_czech_open():
    r = requests.get(VFS_CZ_URL, timeout=20)
    page = r.text.lower()
    
    return not any(k in page for k in closed_keywords)

# ---------------- MAIN ----------------

def main():
    state = load_state()

    # BLS
    bls_open = is_bls_open()
    if bls_open and not state["bls_spain"]:
        send_telegram("🇪🇸 BLS İSPANYA (ANKARA) RANDEVU AÇILDI!")
        state["bls_spain"] = True
    elif not bls_open:
        state["bls_spain"] = False

    # VFS
    vfs_open = is_vfs_czech_open()
    if vfs_open and not state["vfs_czech"]:
        send_telegram("🇨🇿 VFS ÇEK CUMHURİYETİ RANDEVU AÇILDI!")
        state["vfs_czech"] = True
    elif not vfs_open:
        state["vfs_czech"] = False

    save_state(state)

if __name__ == "__main__":
    main()
