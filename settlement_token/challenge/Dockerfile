FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir flask

COPY server.py /app/server.py

EXPOSE 5001

CMD ["python", "server.py"]
