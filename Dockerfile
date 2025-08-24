FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11
RUN apt-get update && apt-get install -y git
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install --no-cache-dir . || \
    pip install --no-cache-dir . --use-deprecated=legacy-resolver
RUN fc-cache -f -v
RUN chmod a+x bin/*.sh
RUN mkdir -p logs
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
EXPOSE 8500
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000"]
