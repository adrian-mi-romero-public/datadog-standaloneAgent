import requests
from urllib.parse import urlparse
import os
import filecmp
import re

url = 'http://172.77.20.249:8000/master/vanity'

response = requests.get(url).json()

def get_vanity_url():
  vanity_list = []
  for vanity_url in response:
        if vanity_url['vanity'] == '':
            continue
        else:
            vanity_list.append(vanity_url['vanity']+'.tidemark.net') 
            os.system('cp http-check.conf.yaml.template http_check_conf.yaml')
            os.system('cp tls.conf.yaml.template tls_check_conf.yaml')
  for item in vanity_list:
      if re.search('preview|sandbox|academy', item):
            continue
      else:
            tenant_name = item.split('.tidemark.net')[0]
            cmd_httpcheck = "yq e -i ' .instances += {\"name\": \"%s\", \"url\": \"https://%s\", \"method\": \"get\", \"tls_ignore_warning\": \"true\", \"collect_response_time\": \"true\"}' %s" % (tenant_name, item, 'http_check_conf.yaml')
            os.system(cmd_httpcheck)
            cmd_tlscheck = "yq e -i ' .instances += {\"server\": \"https://%s\", \"name\": \"%s\", \"days_critical\": 30.0, \"days_warning\": 60.0, \"tls_verify\": false}' %s" % (item, tenant_name, 'tls_check_conf.yaml')         
            os.system(cmd_tlscheck)
  
  if filecmp.cmp('http_check_conf.yaml', '/etc/datadog-agent/conf.d/http_check.d/conf.yaml') and filecmp.cmp('tls_check_conf.yaml', '/etc/datadog-agent/conf.d/tls.d/conf.yaml'):
      print('No Changes detected')
      exit
  else:
      print('Changes detected')
      if os.system("kubectl get configmap dd-agent-cm -n $NAMESPACE") == 0:
              os.system("kubectl delete configmap dd-agent-cm -n $NAMESPACE")              
              os.system('kubectl create configmap dd-agent-cm --from-file=httpcheck-conf-yaml=http_check_conf.yaml --from-file=tlscheck-conf-yaml=tls_check_conf.yaml -n $NAMESPACE')
              #print("configmap found, deleted and recreated")
              os.system('kubectl delete pod -l app.kubernetes.io/name=dd-agent-standalone --grace-period=0 -n $NAMESPACE')
      else:
              os.system('kubectl create configmap dd-agent-cm --from-file=httpcheck-conf-yaml=http_check_conf.yaml --from-file=tlscheck-conf-yaml=tls_check_conf.yaml -n $NAMESPACE')
              #print("configmap not found, created")      
              os.system('kubectl delete pod -l app.kubernetes.io/name=dd-agent-standalone --grace-period=0 -n $NAMESPACE')

if __name__ == '__main__':
      get_vanity_url()