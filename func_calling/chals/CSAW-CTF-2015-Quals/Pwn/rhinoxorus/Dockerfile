FROM ubuntu:latest
MAINTAINER Steven
LABEL Description="CSAW 2015-Q: Rhinoxorus" VERSION='1.0'
# Update
RUN apt-get update && apt-get -y upgrade \
	apt-get -y install build-essential
# Files
RUN mkdir -p /root/rhino
WORKDIR /root/rhino
COPY password.txt .
COPY rhinoxorus .
RUN chmod +x rhinoxorus
# Execute
EXPOSE 24242
CMD ["./rhinoxorus"]