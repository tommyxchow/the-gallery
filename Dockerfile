FROM python:3.9.1-slim-buster

WORKDIR /app

COPY . .

EXPOSE 8000

CMD ["python3", "-u", "server.py"]