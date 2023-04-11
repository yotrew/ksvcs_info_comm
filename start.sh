#/bin/bash
date -R  >> ksvcs_ic.log.txt
#sudo nohup python3 ksvcssotre.py  >> ksvcssotre.log.txt 2>&1 &
nohup gunicorn -w 1 -b 127.0.0.1:5002 ksvcs_ic_main:app >> ksvcs_ic.log.txt 2>&1 &


