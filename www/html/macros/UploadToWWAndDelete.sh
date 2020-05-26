#!/bin/bash

# Upload the file to WW using an Active ftp connection with curl

maxtime=1800 # 30 minutes
dest="ftp://192.168.0.106"

echo "Uploading $1 ..."
curl --disable-eprt --keepalive-time 60 --connect-timeout 60 -m $maxtime -P - -u pi1:CCRider -T $1 $dest
rval=$?
echo "return code=" $rval

if [ $rval -eq 0 ]
then
	echo "Deleting $1"
	rm $1
	list=( $1*.th.jpg )
	thumb="${list[-1]}"
	echo "Deleting thumbnail $thumb"
	rm $thumb
fi
exit $rval

