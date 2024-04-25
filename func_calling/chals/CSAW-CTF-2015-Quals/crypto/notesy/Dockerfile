FROM php:alpine
MAINTAINER Steven
LABEL Description="CSAW 2015-Q: Notesy" VERSION='1.0'
# Files
RUN mkdir -p /root/notesy
ADD challenge /root/notesy
WORKDIR /root/notesy
# Execute
ENTRYPOINT ["php", "-S", "0.0.0.0:8000"]
EXPOSE 8000