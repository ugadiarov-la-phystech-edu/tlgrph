FROM python:3.8-slim
WORKDIR /deploy

ENV FLASK_APP=/deploy/app/tlgrph.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_CONFIG=application.config

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE ${FLASK_RUN_PORT}
CMD ["flask", "run"]
