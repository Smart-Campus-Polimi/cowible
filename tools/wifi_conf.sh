#! /bin/bash

iw_dev=$(iw dev | awk 'FNR==2 {print $2}')
py_dev=$(iw dev | awk 'FNR==1 {print substr ($0, 5,1)}')
echo The device is $iw_dev
echo The phy is $py_dev


iw phy phy$py_dev interface add mon0 type monitor
iw dev $iw_dev del
ifconfig mon0 up

iw_dev=$(iw dev | awk 'FNR==2 {print $2}')
echo The device is now $iw_dev

data_day=$(date +"%y%m%d")
path="data/$data_day/"
timeout=60
#mkdir -p $path

#### BT and BLE
hciconfig hci0 up