# www-data does not have sufficient permissions for GPIO access
#python /var/www/html/pantilt_sleep.py
#echo "ASLEEP" >/dev/shm/mjpeg/user_annotate.txt

# Send pantilt command through the pipe
echo -n "servosleep 0 0" >/var/www/html/FIFO_pipan
