FROM python:3.11.1-alpine
RUN mkdir /app
WORKDIR /app

ADD . /app/

RUN pip install -r requirements.txt
RUN pip install gunicorn

CMD ["gunicorn", "application:app", "--bind=0.0.0.0:8000", "--workers=4"]