FROM ubuntu:14.04
MAINTAINER Oskar
LABEL Description="CSAW 2015-F: Check Plz" VERSION='1.0'
# Update
RUN apt-get update && apt-get install -y python python-pip python-dev socat 
# Files
COPY ./problem.py /opt/problem.py
RUN chmod +x /opt/problem.py
RUN pip install --upgrade pycrypto
# Execute
CMD socat -T60 TCP-LISTEN:8000,reuseaddr,fork EXEC:/opt/problem.py