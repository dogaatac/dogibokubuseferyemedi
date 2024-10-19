import requests
import time
import random
import string

A_SERVER_URL = "http://213.199.52.11:5002/heartbeat"  # Ana sunucunun IP adresini girin

# Rastgele server ID oluşturma
def generate_server_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

SERVER_ID = generate_server_id()

while True:
    try:
        response = requests.post(A_SERVER_URL, json={"server_id": SERVER_ID})
        if response.status_code == 200:
            print(f"Heartbeat gönderildi: {SERVER_ID}")
        else:
            print("Heartbeat gönderilirken hata oluştu.")
    except Exception as e:
        print(f"Hata: {e}")

    # 1 dakika bekle
    time.sleep(60)
