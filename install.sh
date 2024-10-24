#!/bin/bash

# 1. setup.sh dosyasını GitHub'dan indir
wget -O setup.sh https://raw.githubusercontent.com/dogaatac/dogibokubuseferyemedi/main/setup.sh

# 2. setup.sh dosyasını çalıştırılabilir hale getir
chmod +x setup.sh

# 3. setup.sh dosyasını çalıştır
sudo bash setup.sh
