FROM python:3-alpine

RUN apk update && apk upgrade

WORKDIR /app
COPY . /app

RUN pip3 install -U pip && pip3 install -r requirements.txt

ENTRYPOINT [ "/bin/sh" ]
CMD ["./start.sh"]
