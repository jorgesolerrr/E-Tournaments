FROM python:3.10-slim-buster

RUN pip install numpy

RUN pip install fastapi

RUN pip install uvicorn

WORKDIR /server

COPY . .

CMD ["python", "match_server.py"]