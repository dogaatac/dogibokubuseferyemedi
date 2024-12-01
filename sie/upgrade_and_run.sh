#!/bin/bash

Download() {
    oss_url_code=$(curl -s -o /dev/null -w '%{http_code}' "$URL")
    if [ "$oss_url_code" -eq 200 ]; then
        latest_version=$(curl -s "$URL" | awk -F '@' '/linux|xz/ {print $1}')
        md5=$(curl -s "$URL" | awk -F '@' '/linux|xz/ {print $2}')
        dl_latest_url=$(curl -s "$URL" | awk -F '@' '/linux|xz/ {print $3}')
	package_name=$(curl -s "$URL" | awk -F '@' '/linux|xz/ {print $3}'|awk -F '/' '{print $NF}')
        rm -f "$WORK_DIR/$package_name"
        echo -e "$(date +"%Y-%m-%d %H:%M:%S")     \033[32mINFO\033[0m Downloading the latest version" >> "$WORK_DIR/.check_update.log"
        wget -q -P "$WORK_DIR" "$dl_latest_url" > /dev/null
        if [ "$(md5sum "$WORK_DIR/$package_name" | awk '{print $1}')" = "$md5" ]; then
            tar -xf "$WORK_DIR/$package_name" -C "$WORK_DIR"
            chmod +x "$WORK_DIR/apoolminer" "$WORK_DIR/run.sh"
            rm -f "$WORK_DIR/$package_name"
            return 0
        else
            return 1
        fi
    else
        echo -e "$(date +"%Y-%m-%d %H:%M:%S")     \033[31mERROR\033[0m [2]Failed to connect to the $URL" >> "$WORK_DIR/.check_update.log"
        return 1
    fi
}

Check_version() {
    if [ -e "$WORK_DIR/apoolminer" ]; then
        oss_url_code=$(curl -s -o /dev/null -w '%{http_code}' "$URL")
        if [ "$oss_url_code" -eq 200 ]; then
            latest_version=$(curl -s "$URL" | awk -F '@' '/linux|xz/ {print $1}')
            local_version=$("$WORK_DIR/apoolminer" -V | awk '{print $NF}')
            if [ "$latest_version" = "$local_version" ]; then
                return 0
            else
                return 1
            fi
        else
            echo -e "$(date +"%Y-%m-%d %H:%M:%S")     \033[31mERROR\033[0m [1]Failed to connect to the $URL" >> "$WORK_DIR/.check_update.log"
            return 1
        fi
    else
        return 1
    fi
}

Run_apoolminer() {
    if [ $(ps aux|grep -w "run.sh"|grep -v grep|wc -l) -gt 0 ];then
	    ps aux|grep -w "run.sh"|grep -v grep|awk '{print $2}'|xargs kill
    fi
    nohup bash run.sh > run.log 2>&1 &
}

if [ -n "$(lsof -p $$ | grep nohup.out)" ]; then
    while true; do
        WORK_DIR=$(dirname "$(readlink -f "$0")")
        COIN=$(awk -F '=' '/algo/ {print $NF}' "$WORK_DIR/miner.conf" | xargs)
        URL="https://www.apool.io/check/prod/$COIN/version"
        if pgrep -f 'apoolminer' > /dev/null; then
            Check_version
            if [ $? -ne 0 ]; then
                Download
                if [ $? -eq 0 ]; then
                    pkill -f 'apoolminer'
                    Run_apoolminer
                    echo -e "$(date +"%Y-%m-%d %H:%M:%S")     \033[32mINFO\033[0m Updated and restarted successfully" >> "$WORK_DIR/.check_update.log"
                else
                    echo -e "$(date +"%Y-%m-%d %H:%M:%S")     \033[31mERROR\033[0m Failed to download, will retry after 30 seconds" >> "$WORK_DIR/.check_update.log"
                    sleep 30
                    continue
                fi
            else
                echo -e "$(date +"%Y-%m-%d %H:%M:%S")     \033[32mINFO\033[0m Already the latest version, no need to update" >> "$WORK_DIR/.check_update.log"
            fi
        else
            Check_version
            if [ $? -ne 0 ]; then
                Download
                if [ $? -eq 0 ]; then
                    Run_apoolminer
                    echo -e "$(date +"%Y-%m-%d %H:%M:%S")     \033[32mINFO\033[0m Updated and running successfully" >> "$WORK_DIR/.check_update.log"
                else
                    echo -e "$(date +"%Y-%m-%d %H:%M:%S")     \033[31mERROR\033[0m Failed to download, will retry after 30 seconds" >> "$WORK_DIR/.check_update.log"
                    sleep 30
                    continue
                fi
            else
                Run_apoolminer
                echo -e "$(date +"%Y-%m-%d %H:%M:%S")     \033[32mINFO\033[0m Already the latest version, and started successfully" >> "$WORK_DIR/.check_update.log"
            fi
        fi
	sleep $((RANDOM % 300))
    done
else
    echo -e "Please use nohup to run.\nUsage:\033[0;32m nohup bash upgrade_and_run.sh 2>&1 &\033[0m"
    exit 1
fi
