# B Sunucusu (b) Kodları

import requests
import time
import random
import string
import subprocess

A_SERVER_URL = "http://213.199.52.11:5005/heartbeat"  # Ana sunucunun IP adresi

# Rastgele server ID oluşturma
def generate_server_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

SERVER_ID = generate_server_id()

while True:
    try:
        # nproc değerini alma
        nproc_value = subprocess.check_output(["nproc"]).decode("utf-8").strip()
        nproc_value = int(nproc_value)
        
        # Ana sunucuya ping gönderme
        response = requests.post(A_SERVER_URL, json={"server_id": SERVER_ID, "nproc": nproc_value})
        if response.status_code == 200:
            print(f"Heartbeat gönderildi: {SERVER_ID}, nproc: {nproc_value}")
        else:
            print("Heartbeat gönderilirken hata oluştu.")
    except Exception as e:
        print(f"Hata: {e}")

    # 3 dakika bekle
    time.sleep(180)
