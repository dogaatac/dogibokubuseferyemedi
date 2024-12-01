import requests
import time
import random
import string

A_SERVER_URL = "http://188.245.182.52:5003/heartbeat"  # Ana sunucunun IP adresini girin

# Rastgele server ID oluşturma
def generate_server_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

SERVER_ID = generate_server_id()

# Kullanıcıdan mail adresi isteme
email = input("Mail gir dayı : (boş bırakabilirsiniz): ").strip()

while True:
    try:
        data = {"server_id": SERVER_ID, "email": email}
        response = requests.post(A_SERVER_URL, json=data)
        if response.status_code == 200:
            print(f"Heartbeat gönderildi: {SERVER_ID} - {email if email else 'Mailsiz'}")
        else:
            print("Heartbeat gönderilirken hata oluştu.")
    except Exception as e:
        print(f"Hata: {e}")

    # 1 dakika bekle
    time.sleep(60)
