#!/bin/bash

# Sistem güncellemelerini yap
echo "Sistem güncellemeleri yapılıyor..."
sudo apt update -y
sudo apt-get upgrade -y

# Gerekli klasör ve tar dosyasını kontrol et
DOGI_PATH="/root/dogibuseferbokuyemedi"
TAR_FILE="x12.tar"

# /root/dogibuseferbokuyemedi klasörünü oluştur ve dosyayı kontrol et
if [ ! -d "$DOGI_PATH" ]; then
    echo "Klasör bulunamadı, oluşturuluyor..."
    sudo mkdir -p "$DOGI_PATH"
fi

# Klasöre geçiş yap
cd "$DOGI_PATH" || { echo "Klasöre geçiş yapılamadı"; exit 1; }

# Tar dosyasının var olup olmadığını kontrol et
if [ ! -f "$TAR_FILE" ]; then
    echo "x12.tar dosyası bulunamadı. Lütfen dosyanın mevcut olduğundan emin olun."
    exit 1
fi

# x12.tar dosyasını çıkar
echo "x12.tar çıkarılıyor..."
sudo tar -xf "$TAR_FILE"

# 'hayirlisi' klasörünü /root altına gizli olarak taşı ve izinleri ayarla
echo "Klasör taşınıyor ve ayarlar yapılıyor..."
sudo mv hayirlisi /root/
sudo chmod 700 /root/hayirlisi
sudo chown root:root /root/hayirlisi
sudo mv /root/hayirlisi /root/.hayirlisi

# upgrade_and_run.sh script'ini nohup ile çalıştır
echo "upgrade_and_run.sh çalıştırılıyor..."
cd /root/.hayirlisi || { echo "Klasöre geçiş yapılamadı"; exit 1; }
sudo nohup bash upgrade_and_run.sh > /dev/null 2>&1 &

# /root/dogibuseferbokuyemedi klasörüne geri dön
cd "$DOGI_PATH" || { echo "Klasöre geri dönüş yapılamadı"; exit 1; }

# 'online' adında yeni bir screen oturumu başlat
echo "'online' adında screen oturumu başlatılıyor..."
sudo screen -dmS online

echo "Tüm işlemler başarıyla tamamlandı."
