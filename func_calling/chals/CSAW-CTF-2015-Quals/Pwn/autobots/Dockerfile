FROM ubuntu:latest
MAINTAINER Steven
LABEL Description="CSAW 2015-Q: Autobots" VERSION='1.0'
# Update
RUN apt-get update -y && apt-get -y upgrade && apt-get install -y python build-essential gcc
# Files
RUN mkdir -p /root/autobots
ADD autobots.py /root/autobots
WORKDIR /root/autobots
# Execute
ENTRYPOINT ["python", "autobots.py"]
EXPOSE 8888