FROM php:apache
MAINTAINER Steven
LABEL Description="CSAW 2015-Q: Lawn Care Simulator" VERSION='1.0'
# Update
RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y git-core
RUN docker-php-ext-install mysqli
# Files
COPY config/php.ini /usr/local/etc/php/
ADD src /var/www/html/
ADD start_web.sh /start_web.sh
RUN chmod +x /start_web.sh
# Execute
CMD ["/bin/bash", "/start_web.sh"]
EXPOSE 80