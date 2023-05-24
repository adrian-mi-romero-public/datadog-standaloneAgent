#!/bin/bash

sed -i "s/\(hostname: \)\(.*\)/\hostname: $DD_HOSTNAME/" /etc/datadog-agent/datadog.yaml
cd /root &&  /usr/local/bin/python /root/tenants_parser.py && service datadog-agent start
service cron start
tail -f /dev/null
