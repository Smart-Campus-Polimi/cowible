#! /bin/bash

iw_dev=$(iw dev | awk 'FNR==2 {print $2}')
echo The device is $iw_dev

iw phy phy0 interface add mon0 type monitor
iw dev $iw_dev del
ifconfig mon0 up

iw_dev=$(iw dev | awk 'FNR==2 {print $2}')
echo The device now is $iw_dev

data_day=$(date +"%y%m%d")
path="data/$data_day/"
timeout=60
#mkdir -p $path