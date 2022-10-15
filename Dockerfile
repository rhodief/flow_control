FROM python:3.7-alpine3.15

WORKDIR /usr/src/app

COPY . .
RUN pip install -r dev.requirements.txt

ENTRYPOINT [ "python" ]