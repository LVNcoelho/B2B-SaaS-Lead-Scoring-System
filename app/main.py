from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import time
from .utils import preprocess_lead
from .model import predict_score

app = FastAPI(title="B2B SaaS Lead Scoring")

class LeadInput(BaseModel):
    nome_empresa: str
    setor: str
    tamanho_empresa: Optional[int] = None
    origem_lead: str

@app.post("/predict")
async def predict(lead: LeadInput):
    start_time = time.time()
    
    # 1. Preprocessamento (Mediana + Flag)
    input_data = lead.model_dump()
    df_processed = preprocess_lead(input_data)
    
    # 2. Predição
    score = predict_score(df_processed)
    
    # 3. Regra de Negócio (High vs Low Touch)
    segment = "High Touch" if score > 0.7 else "Low Touch"
    
    latency = (time.time() - start_time) * 1000 # em ms

    return {
        "lead_id": hash(lead.nome_empresa),
        "score": round(score, 2),
        "segment": segment,
        "treatment_applied": "Median + Flag" if df_processed['is_missing_tamanho'].iloc[0] else "None",
        "latency_ms": f"{latency:.2f}ms"
    }

@app.get("/")
def health_check():
    return {"status": "online"}