FROM python:3.10-slim

WORKDIR /app

# Copy all required files
COPY gam_model.pkl /app
COPY features.json /app
COPY model_inference.py /app
COPY server.py /app
COPY iot_consumer.py /app
COPY logging_utils.py /app
COPY start.py /app
COPY requirements.txt /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Start *both* API and IoT consumer
CMD ["python", "start.py"]

