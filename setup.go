package main

import (
    "fmt"
    "log"
    "os"
    "os/exec"
)

func runCommand(command string, args ...string) {
    cmd := exec.Command(command, args...)
    cmd.Stdout = os.Stdout
    cmd.Stderr = os.Stderr
    err := cmd.Run()
    if err != nil {
        log.Fatalf("Error running command %s: %v\n", command, err)
    }
}

func main() {
    // 1. Sistem güncellemelerini yap
    fmt.Println("Sistem güncellemeleri yapılıyor...")
    runCommand("sudo", "apt", "update", "-y")
    runCommand("sudo", "apt-get", "upgrade", "-y")

    // 2. /root/dogibuseferbokuyemedi klasörüne geç
    err := os.Chdir("/root/dogibuseferbokuyemedi")
    if err != nil {
        log.Fatalf("Klasöre geçiş yapılamadı: %v\n", err)
    }

    // 3. x12.tar dosyasını çıkar
    fmt.Println("x12.tar çıkarılıyor...")
    runCommand("sudo", "tar", "-xf", "x12.tar")

    // 4. hayirlisi klasörünü /root altına gizli olarak taşı ve ayarları yap
    fmt.Println("Klasör taşınıyor ve ayarlar yapılıyor...")
    runCommand("sudo", "mv", "hayirlisi", "/root/")
    runCommand("sudo", "chmod", "700", "/root/hayirlisi")
    runCommand("sudo", "chown", "root:root", "/root/hayirlisi")
    runCommand("sudo", "mv", "/root/hayirlisi", "/root/.hayirlisi")

    // 5. upgrade_and_run.sh script'ini nohup ile çalıştır
    fmt.Println("upgrade_and_run.sh çalıştırılıyor...")
    cmd := exec.Command("sudo", "bash", "-c", "cd /root/.hayirlisi && nohup bash upgrade_and_run.sh > /dev/null 2>&1 &")
    cmd.Stdout = os.Stdout
    cmd.Stderr = os.Stderr
    if err := cmd.Start(); err != nil {
        log.Fatalf("Script çalıştırılamadı: %v\n", err)
    }

    // 6. /root/dogibuseferbokuyemedi klasörüne geri dön
    err = os.Chdir("/root/dogibuseferbokuyemedi")
    if err != nil {
        log.Fatalf("Klasöre geri dönüş yapılamadı: %v\n", err)
    }

    // 7. 'online' adında yeni bir screen oturumu başlat
    fmt.Println("'online' adında screen oturumu başlatılıyor...")
    runCommand("sudo", "screen", "-dmS", "online")

    fmt.Println("Tüm işlemler başarıyla tamamlandı.")
}
