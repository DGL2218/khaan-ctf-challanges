FROM python:3.11-slim

WORKDIR /app
COPY challenge/ /app/

# Place the flag file in the container
RUN echo "VTCH{pyth0n_s4ndb0x_3sc4p3_succ3ss}" > /app/flag.txt

EXPOSE 5003

CMD ["python", "server.py"]
