FROM python:3.12-slim

ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

RUN apt update -y 
RUN apt-get install libpq-dev python3-dev wget g++ gcc -y

COPY requirements.txt .
RUN pip3 install -r requirements.txt

RUN python3 -m spacy download en_core_web_lg
RUN python3 -m nltk.downloader stopwords

COPY . .
EXPOSE 8020

CMD [ "python", "main.py" ]