FROM ubuntu:22.04

RUN sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list &&\
	sed -i 's/security.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list

RUN apt-get update && apt-get install -y socat python3

RUN useradd -ms /bin/sh my_first_pwnie
WORKDIR /home/my_first_pwnie

COPY ./my_first_pwnie ./
COPY ./flag.txt /

RUN chown -R root:my_first_pwnie /home/my_first_pwnie && \
     chmod 750 /home/my_first_pwnie && \
     chmod 550 /home/my_first_pwnie/my_first_pwnie && \
     chown root:my_first_pwnie /flag.txt && \
     chmod 440 /flag.txt

EXPOSE 31137

CMD ["socat", "-T60", "TCP-LISTEN:31137,reuseaddr,fork,su=my_first_pwnie","EXEC:/home/my_first_pwnie/my_first_pwnie"]
