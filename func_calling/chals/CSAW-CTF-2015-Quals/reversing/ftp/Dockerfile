FROM ubuntu:latest
MAINTAINER Steven
LABEL Description="CSAW 2015-Q: FTP" VERSION='1.0'
# Update
RUN apt-get update && apt-get -y upgrade
# Files
RUN mkdir -p /root/ftp
ADD ftp /root/ftp
WORKDIR /root/ftp
RUN chmod 750 ./ftp
# Execute
ENTRYPOINT ["./ftp"]
EXPOSE 12012