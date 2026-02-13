import numpy as np

def predict_score(processed_df):
    """
    Aqui seria o model.predict_proba().
    Vamos simular um cálculo baseado no tamanho da empresa.
    """
    tamanho = processed_df['tamanho_empresa'].iloc[0]
    has_missing = processed_df['is_missing_tamanho'].iloc[0]
    
    # Simulação: empresas maiores tendem a ter score maior
    # Se faltou dado (flag), penalizamos um pouco o score
    base_score = min(tamanho / 500, 0.95) 
    if has_missing:
        base_score -= 0.15
        
    return max(float(base_score), 0.05)