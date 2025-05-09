import pandas as pd
import ast
import numpy as np
from tabulate import tabulate
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from math import radians, cos, sin, asin, sqrt
import re

def safe_convert_to_lat_long(value):
    # Remover pontos
    value = str(value).replace('.', '')

    # Verificar se o valor não é vazio e se pode ser convertido
    if value and value.strip() != '':
        numeros_sem_ponto = value.replace('.', '')
          # Coloca o último ponto no lugar certo (antes dos 3 últimos dígitos)
        return float(re.sub(r'(\d+)(\d{3})$', r'\1.\2', numeros_sem_ponto))
    else:
        # Retornar um valor padrão, como 0, caso a célula esteja vazia ou inválida
        return '0.000000'
    
def prediction(entrada_modelo):
    # Carregar a planilha
    df = pd.read_csv('DADOS.csv')

    df = df[df['Estimatives'].notnull()].copy()


    # Verificar se 'Estimatives' está em string ou dict
    if isinstance(df['Estimatives'].iloc[0], str):
        df['Estimatives'] = df['Estimatives'].apply(ast.literal_eval)

    df['valor_uber'] = df['Estimatives'].apply(lambda x: x.get('UberX') if isinstance(x, dict) else np.nan)
    df['valor_pop99'] = df['Estimatives'].apply(lambda x: x.get('pop99') if isinstance(x, dict) else np.nan)
    df['valor_poupa99'] = df['Estimatives'].apply(lambda x: x.get('poupa99') if isinstance(x, dict) else np.nan)
    df['valor_Comfort'] = df['Estimatives'].apply(lambda x: x.get('Comfort') if isinstance(x, dict) else np.nan)


    # Remover linhas sem valor_uber
    df = df.dropna(subset=['valor_uber'])
    df = df.dropna(subset=['valor_pop99'])
    df = df.dropna(subset=['valor_poupa99'])
    df = df.dropna(subset=['valor_Comfort'])


    # Mapear os dias da semana
    dias_semana = {
        'Monday': 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4,
        'Saturday': 5,
        'Sunday': 6
    }
    df['dia_semana'] = df['Dia'].map(dias_semana)

    # Converter horário e extrair hora
    df['Horario'] = pd.to_datetime(df['Horario'], format='%H:%M:%S', errors='coerce')
    df['hora'] = df['Horario'].dt.hour

    df.loc[:, 'LatOrigem'] = df['LatOrigem'].apply(safe_convert_to_lat_long)
    df.loc[:, 'LongOrigem'] = df['LongOrigem'].apply(safe_convert_to_lat_long)
    df.loc[:, 'LatDestino'] = df['LatDestino'].apply(safe_convert_to_lat_long)
    df.loc[:, 'LongDestino'] = df['LongDestino'].apply(safe_convert_to_lat_long)

    # Selecionar colunas de entrada (X) e saída (y)
    X = df[['Distancia_KM', 'hora', 'dia_semana', 'LatOrigem', 'LongOrigem', 'LatDestino', 'LongDestino', 'valor_Comfort', 'valor_poupa99', 'valor_pop99']]
    y = df['valor_uber']

    # Dividir os dados
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Treinar o modelo
    modelo = RandomForestRegressor()
    modelo.fit(X_train, y_train)

    # Fazer previsões
    return modelo.predict(entrada_modelo)

    # # Calcular métricas
    # mae = mean_absolute_error(y_test, y_pred)
    # rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    # r2 = r2_score(y_test, y_pred)

    # # Exibir resultados
    # print(f"MAE (Erro Absoluto Médio): {mae:.2f}")
    # print(f"RMSE (Raiz do Erro Quadrático Médio): {rmse:.2f}")
    # print(f"R² (Coeficiente de Determinação): {r2:.4f}")

