FROM python:3.10-slim

WORKDIR /app

COPY gam_model.pkl /app
COPY features.json /app
COPY model_inference.py /app
COPY server.py /app
COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
