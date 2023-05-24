FROM python:3.10.1-slim-buster

MAINTAINER "Tidemark Cloud Devops Team"

ENV DD_HOME=/opt/datadog-agent \
    # prevent the agent from being started after install
    DD_START_AGENT=0 \
    PYCURL_SSL_LIBRARY=openssl \
    DD_CONF_LOG_TO_SYSLOG=no \
    NON_LOCAL_TRAFFIC=yes \
    DD_API_KEY=XXXXXXXXX \
    DD_AGENT_MAJOR_VERSION=7 \
    DD_HOSTNAME=stand-alone-agent \
    DD_TAGS=usage:httpcheck \
    DD_SITE="datadoghq.com"

# Install minimal dependencies
RUN pip install kubernetes wrapt_timeout_decorator tenacity
RUN apt-get update && apt-get install -y coreutils curl tar sysstat procps cron vim libpq-dev gcc && pip install psycopg2
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && install -o root -g 0 -m 0755 kubectl /usr/local/bin/kubectl; rm -f ./kubectl
RUN curl -LO https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 && mv yq_linux_amd64 yq && chmod +x yq && mv yq /usr/bin/yq
RUN crontab -l | { cat; echo "0 7 * * * /usr/local/bin/python /root/tenants_parser.py > /dev/null 2>&1"; } | crontab -

# Install the Datadog Agent
RUN bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script.sh)"

# Copy the config files
COPY service.sh $DD_HOME
COPY http-check.conf.yaml.template /root/http-check.conf.yaml.template
COPY tls.conf.yaml.template /root/tls.conf.yaml.template
COPY tenants_parser.py /root/tenants_parser.py
RUN chmod +x $DD_HOME/service.sh

# Expose DogStatsD port
EXPOSE 8125/udp

ENTRYPOINT ["/bin/bash"]

WORKDIR $DD_HOME
CMD ["service.sh"]
