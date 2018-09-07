#! /bin/bash

trap ctrl_c INT

function ctrl_c() {
        echo "** Trapped CTRL-C"
}

################### END VAR DECL ##############
day=$1
path=data/$day
time=$(date +"%H%M")
text_file="/WiFi-$time.txt"
path_full="$path$text_file"

timeout=60

###### WIFI DUMP ######

tshark -S -l -i mon0 -Y 'wlan.fc.type_subtype eq 4' \
-T fields -e frame.time -e wlan.ta_resolved -e wlan.sa -e wlan_radio.signal_dbm -e wlan.ssid \
-E separator=";" -a duration:$timeout > $path_full 

echo $path_full
