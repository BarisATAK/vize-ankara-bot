import requests
import os
import json

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

STATE_FILE = "state.json"

CLOSED_KEYWORDS = [
    "no appointment",
    "no available appointments",
    "all appointments are booked",
    "fully booked",
    "please check back later",
    "currently no slots",
    "appointments are not available"
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

# ------------- CHECK OPEN -------------

def is_open_by_keywords(page_text, extra_closed=None):
    text = page_text.lower()
    keywords = CLOSED_KEYWORDS.copy()

    if extra_closed:
        keywords.extend(extra_closed)

    #return True #For test. Delete Cache and run workflow.
    return not any(k in text for k in keywords)

# ---------------- BLS ----------------

BLS_URL = "https://www.blsspainvisa.com/turkey/ankara/"

def is_bls_open():
    try:
        r = requests.get(BLS_URL, timeout=20)
        return is_open_by_keywords(r.text)
    except Exception as e:
        print("BLS error:", e)
        return False

# ---------------- VFS CZECH ----------------

VFS_CZ_URL = "https://visa.vfsglobal.com/tur/en/cze/"

def is_vfs_czech_open():
    try:
        r = requests.get(VFS_CZ_URL, timeout=20)
        return is_open_by_keywords(r.text)
    except Exception as e:
        print("VFS error:", e)
        return False

# ---------------- MAIN ----------------

def main():
    state = load_state()

    # BLS
    bls_open = is_bls_open()
    if bls_open and not state["bls_spain"]:
        send_telegram("🇪🇸 BLS İSPANYA/ANKARA RANDEVU AÇILDI!")
        state["bls_spain"] = True
    elif not bls_open:
        state["bls_spain"] = False

    # VFS
    vfs_open = is_vfs_czech_open()
    if vfs_open and not state["vfs_czech"]:
        send_telegram("🇨🇿 VFS ÇEK CUMHURİYETİ/ANKARA RANDEVU AÇILDI!")
        state["vfs_czech"] = True
    elif not vfs_open:
        state["vfs_czech"] = False

    save_state(state)

if __name__ == "__main__":
    main()
