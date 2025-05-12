from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import pandas as pd
import pickle
import os

app = FastAPI()

# Load model
try:
    current_dir = os.path.dirname(__file__)  # /home/prabhav/SPE_Project/backend/src
    model_path = os.path.join(current_dir, "../models/logistic_model.pkl")  # resolves correctly
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