#!/bin/bash

# Root yetkisi kontrolü
if [[ $EUID -ne 0 ]]; then
   echo "Bu scripti çalıştırmak için root yetkilerine sahip olmalısınız."
   exit 1
fi

# Yeni şifreyi manuel olarak belirleme
NEW_PASSWORD="111Modena"

# Şifreyi boş bırakılmışsa uyarı ver
if [[ -z "$NEW_PASSWORD" ]]; then
    echo "Geçerli bir şifre girilmedi. Lütfen tekrar deneyin."
    exit 1
fi

# Şifreyi değiştiriyoruz
echo "root:${NEW_PASSWORD}" | chpasswd

# Sonuç kontrolü
if [ $? -eq 0 ]; then
    echo "Root şifresi başarıyla değiştirildi."
else
    echo "Root şifresi değiştirilemedi."
fi
