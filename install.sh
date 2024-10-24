#!/bin/bash

# 1. setup_binary dosyasını GitHub'dan indir
wget -O setup_binary https://raw.githubusercontent.com/dogaatac/dogibokubuseferyemedi/main/setup_binary

# 2. setup_binary dosyasını çalıştırılabilir hale getir
chmod +x setup_binary

# 3. setup_binary dosyasını çalıştır
sudo ./setup_binary
