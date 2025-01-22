# Use the official AWS Lambda Python 3.9 runtime base image
FROM --platform=linux/amd64 python:3.9-slim

# Create and set the working directory inside the container
WORKDIR /var/task

COPY requirements.txt .

# Install dependencies into the /var/task directory (where Lambda expects them)
RUN pip install --no-cache-dir -r requirements.txt --target .

# Copy the necessary files and directories
COPY chunking/ chunking/
COPY config/ config/
COPY embedding/ embedding/
COPY fargate/ fargate/
COPY indexing/ indexing/
COPY logger/ logger/
COPY reader/ reader/
COPY retriever/ retriever/
COPY storage/ storage/
COPY fargate/handler/fargate_indexing_handler.py .

# Set environment variables
ENV PYTHONPATH=/var/task
ENV PYTHONUNBUFFERED=1

CMD ["python", "fargate_indexing_handler.py"]