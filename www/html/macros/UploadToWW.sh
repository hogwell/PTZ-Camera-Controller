#!/bin/bash

# Upload the file to WW using curl
echo "Uploading $1 ..."
curl --disable-eprt --keepalive-time 60 --connect-timeout 60 -m 1800 -P - -u pi1:CCRider -T $1 ftp://192.168.0.106
rval=$?
echo "return code=" $rval
if [ $rval -eq 0 ]
then
	echo "Transferred $1"
#	echo "rm $1"
#	rm $1
fi
exit $rval

