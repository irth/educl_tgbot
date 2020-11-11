FROM python:3-slim-buster
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV REDIS_HOST redis
ENV REDIS_PORT 6379
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt && pip install gunicorn
COPY . /app/ 
WORKDIR /app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]