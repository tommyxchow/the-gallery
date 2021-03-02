FROM python:3-slim-buster

WORKDIR /app

COPY . .

EXPOSE 8000

CMD ["python3", "-u", "server.py"]