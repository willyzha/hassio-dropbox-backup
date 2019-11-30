#!/bin/bash

CONFIG_PATH=/data/options.json

TOKEN=$(jq --raw-output ".oauth_access_token" $CONFIG_PATH)
OUTPUT_DIR=$(jq --raw-output ".output // empty" $CONFIG_PATH)
RETRIES=$(jq --raw-output ".retries // empty" $CONFIG_PATH)
KEEP_LAST=$(jq --raw-output ".keep_last // empty" $CONFIG_PATH)

if [[ -z "$OUTPUT_DIR" ]]; then
    OUTPUT_DIR="/"
fi

if [[ -z "$RETRIES" ]]; then
    RETRIES=1
fi

echo "[Info] Files will be uploaded to: ${OUTPUT_DIR}"

#echo "[Info] Saving OAUTH_ACCESS_TOKEN to /etc/uploader.conf"
#echo "OAUTH_ACCESS_TOKEN=${TOKEN}" >> /etc/uploader.conf

echo "[Info] Listening for messages via stdin service call..."

# listen for input
while read -r msg; do
    # parse JSON
    echo "$msg"
    cmd="$(echo "$msg" | jq --raw-output '.command')"
    echo "[Info] Received message with command ${cmd}"
    if [[ $cmd = "upload" ]]; then
        echo "[Info] Uploading all .tar files in /backup (skipping those already in Dropbox)"
        shopt -s nullglob
        file_list=""
        for f in `ls -tc -r /backup/*.tar`
        do
            #echo "Uploading ${f}..."
            file_list="${file_list} ${f}"
            #echo "Done!"
            if [[ "$FILETYPES" ]]; then
                echo "[Info] filetypes option is set, scanning share directory for files with extensions ${FILETYPES}"
                find /share -regextype posix-extended -regex "^.*\.(${FILETYPES})" -exec ./dropbox_uploader.sh -s -f /etc/uploader.conf upload {} "$OUTPUT_DIR" \;
            fi
        done
        python3 ./dropbox_uploader.py "$file_list" "$TOKEN" "$OUTPUT_DIR" --retries "$RETRIES"        
        echo "[Info] Uploading complete!"
        
        if [[ "$KEEP_LAST" ]]; then
            echo "[Info] keep_last option is set, cleaning up files..."
            python3 /backup_cleanup.py "$KEEP_LAST"
        fi
    else
        # received undefined command
        echo "[Error] Command not found: ${cmd}"
    fi
done
