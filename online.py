import requests
import time
import socket
import os
from subprocess import check_output

A_SERVER_URL = "http://54.91.133.48:5000/ping"  # A'nın IP'si yazılacak
INTERVAL = 180  # 3 dakika (saniye cinsinden)

def get_ip():
    # Lokal IP'yi otomatik bulma (alternatif metodlar da kullanılabilir)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = "IP_BULUNAMADI"
    finally:
        s.close()
    return ip

def get_cpu_cores():
    try:
        return int(check_output(["nproc"]).decode().strip())
    except:
        return os.cpu_count()  # Fallback

while True:
    ip = get_ip()
    cpu_cores = get_cpu_cores()
    
    try:
        response = requests.post(
            A_SERVER_URL,
            json={"ip": ip, "cpu": cpu_cores}
        )
        print(f"A'ya ping gönderildi: {response.status_code}")
    except Exception as e:
        print(f"Hata: {e}")
    
    time.sleep(INTERVAL)