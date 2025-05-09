import pandas as pd
import ast
import numpy as np
from tabulate import tabulate
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from math import radians, cos, sin, asin, sqrt
import re
import datetime
from geopy.geocoders import Nominatim
import geopy.distance
from prediction import prediction

def estimativa(origem, destino):
    # Carregar a planilha
    df = pd.read_csv('DADOS.csv')
    df = df[df['Estimatives'].notnull()].copy()

    # Verificar e converter 'Estimatives' de string para dict
    if isinstance(df['Estimatives'].iloc[0], str):
        df['Estimatives'] = df['Estimatives'].apply(ast.literal_eval)

    # Extrair valores dos dicionários
    df['valor_uber'] = df['Estimatives'].apply(lambda x: x.get('UberX') if isinstance(x, dict) else np.nan)
    df['valor_pop99'] = df['Estimatives'].apply(lambda x: x.get('pop99') if isinstance(x, dict) else np.nan)
    df['valor_poupa99'] = df['Estimatives'].apply(lambda x: x.get('poupa99') if isinstance(x, dict) else np.nan)
    df['valor_Comfort'] = df['Estimatives'].apply(lambda x: x.get('Comfort') if isinstance(x, dict) else np.nan)

    # Remover linhas sem estimativas
    df = df.dropna(subset=['valor_uber', 'valor_pop99', 'valor_poupa99', 'valor_Comfort'])

    # Mapear os dias da semana
    dias_semana = {
        'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
        'Friday': 4, 'Saturday': 5, 'Sunday': 6
    }

    df['dia_semana'] = df['Dia'].map(dias_semana)

    # Converter 'Horario' para datetime e extrair hora
    df['Horario'] = pd.to_datetime(df['Horario'], format='%H:%M:%S', errors='coerce')
    df['hora'] = df['Horario'].dt.hour

    loc = Nominatim(user_agent="Geopy Library")
    origem = loc.geocode(origem)
    destino = loc.geocode(destino)

    coords_1 = (origem.latitude, origem.longitude)
    coords_2 = (destino.latitude, destino.longitude)

    dist = geopy.distance.distance(coords_1, coords_2).km
    
    print(f"Coordenadas de origem: {coords_1}")
    print(f"Coordenadas de destino: {coords_2}")
    print(f"Distancia do trajeto: {dist} ")

    x = datetime.datetime.now()
    # Entrada do usuário
    input_usuario = {
        'Distancia_KM': dist,
        'hora': int(x.strftime("%H")) - 3,
        'dia_semana': dias_semana[x.strftime("%A")],
        'LatOrigem': origem.latitude,
        'LongOrigem': origem.longitude,
        'LatDestino': destino.latitude,
        'LongDestino': destino.longitude,
    }

    X = df[['Distancia_KM', 'hora', 'dia_semana', 'LatOrigem', 'LongOrigem', 'LatDestino', 'LongDestino', 'valor_Comfort', 'valor_poupa99', 'valor_pop99']]


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

    # Aplicar a função de conversão para todas as colunas de latitude e longitude
    df.loc[:, 'LatOrigem'] = df['LatOrigem'].apply(safe_convert_to_lat_long)
    df.loc[:, 'LongOrigem'] = df['LongOrigem'].apply(safe_convert_to_lat_long)
    df.loc[:, 'LatDestino'] = df['LatDestino'].apply(safe_convert_to_lat_long)
    df.loc[:, 'LongDestino'] = df['LongDestino'].apply(safe_convert_to_lat_long)

    # Função Haversine
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # Raio da Terra em km
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return R * c

    # Filtrar pelo mesmo dia e hora
    filtro = df[
        (df['dia_semana'] == input_usuario['dia_semana']) &
        (df['hora'] == input_usuario['hora'])
    ].copy()
    valores = 0
    
    # Se houver dados no filtro, calcular distância e buscar corrida mais próxima
    if not filtro.empty:
        filtro['distancia_total'] = filtro.apply(lambda row: (
            haversine(input_usuario['LatOrigem'], input_usuario['LongOrigem'], row['LatOrigem'], row['LongOrigem']) +
            haversine(input_usuario['LatDestino'], input_usuario['LongDestino'], row['LatDestino'], row['LongDestino'])
        ), axis=1)

        if not filtro['distancia_total'].isna().all():
            linha_mais_proxima = filtro.loc[filtro['distancia_total'].idxmin()]
            distancia_corrida = linha_mais_proxima['Distancia_KM']
            valores = linha_mais_proxima.filter(like='valor_').drop(labels='valor_uber', errors='ignore')

            valores_por_km = valores / distancia_corrida
            diferenca_km=0
            if input_usuario['Distancia_KM'] > distancia_corrida:
                diferenca_km = input_usuario['Distancia_KM'] - distancia_corrida
                valores_ajustados = valores + (valores_por_km * diferenca_km)
                input_usuario.update(valores_ajustados.to_dict())
            else:
                diferenca_km = distancia_corrida - input_usuario['Distancia_KM']
                valores_ajustados = valores - (valores_por_km * diferenca_km)
                input_usuario.update(valores_ajustados.to_dict())
                # print("Valores encontrados:")
                # print(valores_ajustados)
                # print(linha_mais_proxima)
        else:
            print("Nenhuma linha com coordenadas válidas para calcular distância.")
    else:
        print("Nenhuma corrida encontrada com o mesmo dia e hora.")
    
    # print(input_usuario)
    colunas_modelo = ['Distancia_KM', 'hora', 'dia_semana',
                    'LatOrigem', 'LongOrigem', 'LatDestino', 'LongDestino',
                    'valor_Comfort', 'valor_poupa99', 'valor_pop99']

    entrada_modelo = pd.DataFrame([[input_usuario[col] for col in colunas_modelo]], columns=colunas_modelo)

    # Agora você pode passar para o modelo
    print(f"Valor estimado {prediction(entrada_modelo)}")
    return prediction(entrada_modelo)
    #