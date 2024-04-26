FROM ubuntu:22.04

RUN apt-get update && apt-get install -y socat python3

RUN useradd -ms /bin/sh ctf
WORKDIR /home/ctf

COPY ./my_first_pwnie ./
COPY ./flag.txt /

RUN chown -R root:ctf /home/ctf && \
     chmod 750 /home/ctf && \
     chmod 550 /home/ctf/my_first_pwnie && \
     chown root:ctf /flag.txt && \
     chmod 440 /flag.txt

EXPOSE 31137

CMD ["socat", "-T60", "TCP-LISTEN:31137,reuseaddr,fork,su=my_first_pwnie","EXEC:/home/my_first_pwnie/my_first_pwnie"]
