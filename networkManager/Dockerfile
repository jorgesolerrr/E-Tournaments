FROM python:3.10-slim-buster
FROM alpine:latest

RUN pip install python-nmap

RUN pip install scapy

RUN apk update && apk add nmap



WORKDIR /app


COPY . .

CMD [ "python", "netManager.py" ]
