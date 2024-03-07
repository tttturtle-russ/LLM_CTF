FROM ubuntu:22.04

RUN sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list &&\
	sed -i 's/security.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list

RUN apt-get update && apt-get install -y socat

RUN useradd -ms /bin/sh puffin
WORKDIR /home/puffin

COPY ./puffin ./
COPY ./flag.txt /

RUN chown -R root:puffin /home/puffin && \
     chmod 750 /home/puffin && \
     chmod 550 /home/puffin/puffin && \
     chown root:puffin /flag.txt && \
     chmod 444 /flag.txt

EXPOSE 31140

CMD ["socat", "-T60", "TCP-LISTEN:31140,reuseaddr,fork,su=puffin","EXEC:/home/puffin/puffin"]
