import os
import json
from typing import Dict, Any
from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np

from model_inference import predict as model_predict
from influxdb_client import InfluxDBClient, Point, WriteOptions

# -------------------------
# ENV VARS
# -------------------------
INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")

influx_enabled = all([INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET])

if influx_enabled:
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    query_api = client.query_api()
    write_api = client.write_api(write_options=WriteOptions(batch_size=1))

# -------------------------
# FASTAPI SETUP
# -------------------------
app = FastAPI()

class InputSample(BaseModel):
    features: Dict[str, Any]


@app.get("/")
def root():
    return {
        "status": "alive",
        "model": "GAM",
        "influx_enabled": influx_enabled
    }


@app.post("/predict")
def predict_endpoint(payload: InputSample):
    yhat = model_predict(payload.features)
    return {"prediction": yhat}


@app.get("/predict-latest")
def predict_latest():
    if not influx_enabled:
        return {"error": "InfluxDB not configured"}

    query = f'''
        from(bucket: "{INFLUX_BUCKET}")
            |> range(start: -5m)
            |> filter(fn: (r) => r._measurement == "gc")
    '''
    tables = query_api.query(query)

    values = {}
    for table in tables:
        for record in table.records:
            values[record["_field"]] = record["_value"]

    if not values:
        return {"error": "No recent data"}

    yhat = model_predict(values)

    point = Point("predictions").field("scalarized_utility", yhat)
    write_api.write(INFLUX_BUCKET, INFLUX_ORG, point)

    return {"prediction": yhat, "features_used": values}
