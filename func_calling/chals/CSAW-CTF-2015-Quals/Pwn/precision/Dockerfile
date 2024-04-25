FROM ubuntu:latest
MAINTAINER Steven
LABEL Description="CSAW 2015-Q: Precision" VERSION='1.0'
# Update
RUN apt-get update && apt-get -y upgrade
# Files
RUN mkdir -p /root/precision
ADD precision /root/precision
WORKDIR /root/precision
RUN chmod 750 precision
# Execute
ENTRYPOINT ["./precision"]
EXPOSE 1259