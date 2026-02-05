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
    "no slots",
    "appointments are not available"
]

# ---------------- STATE ----------------

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {
        "bls_spain": False,
        "vfs_czech": False,
        "vfs_france": False
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

# ---------------- BLS/SPAIN----------------

#BLS_URL = "https://www.blsspainvisa.com/turkey/ankara/"
BLS_URL = "https://turkey.blsspainglobal.com/Global/Appointment/NewAppointment"
def is_bls_es_open():
    try:
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive"
    }

        r = requests.get(BLS_URL, headers=headers, timeout=20)
        print(r.text)#debug.
        return is_open_by_keywords(r.text)
    except Exception as e:
        print("BLS/ES error:", e)
        return False

# ---------------- VFS/CZECH ----------------

VFS_CZ_URL = "https://visa.vfsglobal.com/tur/en/cze/"

def is_vfs_czech_open():
    try:
        r = requests.get(VFS_CZ_URL, timeout=20)
        return is_open_by_keywords(r.text)
    except Exception as e:
        print("VFS/CZ error:", e)
        return False

# ---------------- VFS/FRANCE ----------------

VFS_FR_URL = "https://visa.vfsglobal.com/tur/en/fra/"

def is_vfs_fr_open():
    try:
        r = requests.get(VFS_FR_URL, timeout=20)
        return is_open_by_keywords(r.text)
    except Exception as e:
        print("VFS/FR error:", e)
        return False
        
# ---------------- MAIN ----------------

def main():
    state = load_state()

    # BLS/ES
    es_bls_open = is_bls_es_open()
    if es_bls_open and not state["bls_spain"]:
        send_telegram("🇪🇸 BLS İSPANYA/ANKARA RANDEVU AÇILDI!")
        state["bls_spain"] = True
    elif not es_bls_open:
        state["bls_spain"] = False

    # VFS/CZ  
    #cz_vfs_open = is_vfs_czech_open()
 #   if cz_vfs_open and not state["vfs_czech"]:
  #      send_telegram("🇨🇿 VFS ÇEK CUMHURİYETİ/ANKARA RANDEVU AÇILDI!")
   #     state["vfs_czech"] = True
 #   elif not cz_vfs_open:
#        state["vfs_czech"] = False

    # VFS/FR
 #   fr_vfs_open = is_vfs_fr_open()
 #   if fr_vfs_open and not state["vfs_france"]:
#        send_telegram("🇫🇷 VFS FRANSA/ANKARA RANDEVU AÇILDI!")
     #   state["vfs_france"] = True
    #elif not fr_vfs_open:
    #    state["vfs_france"] = False
        
    save_state(state)

if __name__ == "__main__":
    main()
