# www-data does not have sufficient permissions for GPIO access
#python /var/www/html/pantilt_wakeup.py
#echo "AWAKE" >/dev/shm/mjpeg/user_annotate.txt

echo -n "servowake 0 0" >/var/www/html/FIFO_pipan
