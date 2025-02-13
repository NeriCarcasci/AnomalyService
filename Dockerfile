
FROM python:3.10

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir fastapi uvicorn numpy scipy pydantic pandas minio

EXPOSE 8080

# Command to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]