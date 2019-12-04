#!/bin/bash

CONFIG_PATH=/data/options.json
LOG_PATH=/data/log.txt

TOKEN=$(jq --raw-output ".oauth_access_token" $CONFIG_PATH)
OUTPUT_DIR=$(jq --raw-output ".output // empty" $CONFIG_PATH)
RETRIES=$(jq --raw-output ".retries // empty" $CONFIG_PATH)
KEEP_LAST=$(jq --raw-output ".keep_last // empty" $CONFIG_PATH)
DEBUG=$(jq --raw-output ".debug // empty" $CONFIG_PATH)

if [[ -z "$OUTPUT_DIR" ]]; then
    OUTPUT_DIR="/"
fi

if [[ -z "$RETRIES" ]]; then
    RETRIES=1
fi

if [[ -z "$DEBUG" ]]; then
    DEBUG=""
else
    echo "$DEBUG"
    if [[ $DEBUG = true ]]; then
        DEBUG="--debug"
    else
        DEBUG=""
    fi
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
        echo "[Info] Uploading all .tar files in /backup (skipping those already in Dropbox)" | tee $LOG_PATH
        shopt -s nullglob | tee $LOG_PATH -a
        file_list=`ls -tc -r /backup/*.tar`

        echo python3 ./dropbox_uploader.py ${file_list[*]} ${TOKEN} ${OUTPUT_DIR} --retries ${RETRIES} ${DEBUG} | tee $LOG_PATH -a
        python3 ./dropbox_uploader.py ${file_list[*]} ${TOKEN} ${OUTPUT_DIR} --retries ${RETRIES} ${DEBUG} | tee $LOG_PATH -a
        echo "[Info] Uploading complete!" | tee $LOG_PATH -a
        
        if [[ "$KEEP_LAST" ]]; then
            echo "[Info] keep_last option is set, cleaning up files..." | tee $LOG_PATH -a
            python3 /backup_cleanup.py "$KEEP_LAST" | tee $LOG_PATH -a
        fi
    elif [[ $cmd = "log" ]]; then
        echo "[Info] Printing latest log file" 
        cat $LOG_PATH
    else
        # received undefined command
        echo "[Error] Command not found: ${cmd}"
    fi
done
