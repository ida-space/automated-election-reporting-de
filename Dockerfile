# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster

WORKDIR /src

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN python -m nltk.downloader punkt

COPY . .

CMD ["script.py"]
ENTRYPOINT ["python3"]
