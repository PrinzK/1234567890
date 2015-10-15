gunzip $1.img.gz
sudo dd if=/media/daten/pi2goimage/$1.img of=/dev/mmcblk0 bs=4M
sudo sync
