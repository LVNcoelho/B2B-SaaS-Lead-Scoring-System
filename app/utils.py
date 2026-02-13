import pandas as pd
import numpy as np

# Simulando uma mediana de mercado (ex: 50 funcionários)
MEDIANA_TAMANHO_EMPRESA = 50

def preprocess_lead(data: dict):
    # Transforma o dicionário em DataFrame
    df = pd.DataFrame([data])
    
    # Lógica: Mediana + Flag
    df['is_missing_tamanho'] = df['tamanho_empresa'].isnull().astype(int)
    df['tamanho_empresa'] = df['tamanho_empresa'].fillna(MEDIANA_TAMANHO_EMPRESA)
    
    return df