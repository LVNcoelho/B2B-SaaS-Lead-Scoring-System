import time
import hashlib
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

# Ajuste das importações para rodar perfeitamente no servidor e no terminal
try:
    from app.utils import preprocess_lead
    from app.model import predict_score
except ImportError:
    from utils import preprocess_lead
    from model import predict_score

app = FastAPI(title="B2B SaaS Lead Scoring")

# Definindo a versão atual do seu motor de regras/scoring
MODEL_VERSION = "1.0.0"

class LeadInput(BaseModel):
    nome_empresa: str = Field(..., min_length=1, description="Nome da empresa do lead")
    setor: str = Field(..., min_length=1, description="Setor de atuação do lead")
    tamanho_empresa: Optional[int] = Field(None, ge=0, description="Número de funcionários")
    origem_lead: str = Field(..., description="Canal de origem de onde o lead foi coletado")

@app.post("/predict", status_code=status.HTTP_200_OK)
async def predict(lead: LeadInput):
    # 1. Gera o MD5 completo e trunca nos primeiros 8 caracteres para um ID curto e elegante
    md5_completo = hashlib.md5(lead.nome_empresa.encode()).hexdigest()
    id_curto = md5_completo[:8]
    
    start_time = time.time()
    
    try:
        # 2. Preprocessamento (Mediana + Flag)
        input_data = lead.model_dump()
        df_processed = preprocess_lead(input_data)
        
        # 3. Predição / Cálculo do Score
        score = predict_score(df_processed)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao processar dados do lead ou calcular score: {str(e)}"
        )
        
    # 4. Regra de Negócio (High vs Low Touch)
    segment = "High Touch" if score > 0.7 else "Low Touch"
    
    # 5. Cálculo exato de latência da predição
    latency = (time.time() - start_time) * 1000  # em ms
    
    treatment = "median_imputation" if df_processed['is_missing_tamanho'].iloc[0] else "none"

    # 6. Retorna o JSON estruturado no padrão profissional sugerido pelo Claude
    return {
        "lead_id": id_curto,
        "input": {
            "nome_empresa": lead.nome_empresa,
            "setor": lead.setor,
            "tamanho_empresa": lead.tamanho_empresa,
            "origem_lead": lead.origem_lead
        },
        "output": {
            "score": round(score, 2),
            "segment": segment,
            "treatment_applied": treatment,
            "latency_ms": round(latency, 2)
        },
        "model_version": MODEL_VERSION,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }

@app.get("/", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "online"}