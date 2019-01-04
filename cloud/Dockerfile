FROM python:3.6-alpine

RUN adduser -D cloud

WORKDIR /home/cloud

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip3 install -r requirements.txt

COPY app app
COPY cloud.py config.py boot.sh ./
RUN chmod +x boot.shw

ENV FLASK_APP cloud.py

RUN chown -R cloud:cloud ./
USER cloud

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
