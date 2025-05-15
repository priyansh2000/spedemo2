from fastapi import FastAPI, HTTPException, Request, Response
from prometheus_client import generate_latest
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import numpy as np
import pandas as pd
import pickle
import os
import time

from prometheus_client import start_http_server, Counter, Histogram, generate_latest

app = FastAPI()

# Start Prometheus metrics server on a separate port (e.g., 8001)
start_http_server(8001)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'app_request_count',
    'Application Request Count',
    ['method', 'endpoint', 'http_status']
)

REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds',
    'Application Request Latency',
    ['method', 'endpoint']
)

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    method = request.method
    endpoint = request.url.path

    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        status_code = 500
        raise e
    finally:
        latency = time.time() - start_time
        REQUEST_LATENCY.labels(method, endpoint).observe(latency)
        REQUEST_COUNT.labels(method, endpoint, status_code).inc()

    return response

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")

# Load model
try:
    current_dir = os.path.dirname(__file__)
    model_path = os.path.join(current_dir, "../models/logistic_model.pkl")
    with open(model_path, "rb") as f:
        model = pickle.load(f)
except Exception as e:
    raise RuntimeError(f"Failed to load model: {str(e)}")

class PatientData(BaseModel):
    age: float
    gender: int
    total_bilirubin: float
    direct_bilirubin: float
    alkaline_phosphotase: float
    alanine_aminotransferase: float
    aspartate_aminotransferase: float
    total_proteins: float
    albumin: float
    albumin_globulin_ratio: float

@app.post("/predict")
async def predict(data: PatientData):
    try:
        input_values = [
            data.age,
            data.gender,
            data.total_bilirubin,
            data.direct_bilirubin,
            data.alkaline_phosphotase,
            data.alanine_aminotransferase,
            data.aspartate_aminotransferase,
            data.total_proteins,
            data.albumin,
            data.albumin_globulin_ratio
        ]

        input_array = np.array(input_values).reshape(1, -1)
        scaled_data = (input_array - model['mean']) / model['std']
        pca_data = np.dot(scaled_data, model['eigenvectors'])
        pca_with_bias = np.c_[np.ones((pca_data.shape[0], 1)), pca_data]
        probability = 1 / (1 + np.exp(-np.dot(pca_with_bias, model['weights'])))

        return {
            "probability": float(probability[0][0]),
            "prediction": int(probability[0][0] >= 0.5)
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
