FROM python:3.12.1-alpine3.19

ENV MAINAPI_HOST=REDACTED
ENV POSTGRES_HOST=postgres
ENV POSTGRES_USERNAME=postgres
ENV POSTGRES_PASSWORD=SHAHOVPOBEDA
ENV REDIS_HOST=redis

WORKDIR /usr/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /usr/app/src
COPY ./dist /usr/app/src/dist

WORKDIR /usr/app/src

EXPOSE 80
CMD ["python", "main.py"]

