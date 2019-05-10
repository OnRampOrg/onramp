#!/bin/bash
echo -n "Loading [+"
( echo "help;" | mysql -u onramp -pOnRamp_16 2>/dev/null 1>/dev/null ) || \
    /usr/bin/mysqld_safe --user mysql --bind-address 0.0.0.0 2>/out.log 1>/out.log &

max_sleep=10
sleep=0
while ! ( echo "help;" | mysql -u onramp -pOnRamp_16 2>/out.log 1>/out.log ) ;
do
    echo -n +
    sleep 1
    ((sleep++ > max_sleep)) && { printf "]\nFailed to start mysqld] Error.\n"; exit 0; }
done
printf "] Done.\n"
exit 0

