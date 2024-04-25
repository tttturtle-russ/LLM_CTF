FROM linode/lamp:latest
MAINTAINER Steven
LABEL Description="CSAW 2015-Q: Lawn Care Simulator/Web Problem" VERSION='1.0'
# Update
RUN apt-get update && apt-get install -y php5-mysql git-core
# Files
COPY db/create_tables.sql /tmp
RUN rm -rf /var/www/example.com/public_html/
COPY web/config/php.ini /usr/local/etc/php
COPY web/src /var/www/example.com/public_html/
COPY run.sh /opt
RUN chmod +x /opt/run.sh
# Execute
EXPOSE 80
CMD /opt/run.sh