# datadog-standaloneAgent
datadog-standaloneAgent

Data dog agent to run in a conatainer in k8s using http_check and tls_check modules, urls to monitor are automatically updated with an internal python script that pulls the URL from an json API, if it finds a difference between the URLs in the DD agent and the JSON api it updates and restart the DD Agent. 
