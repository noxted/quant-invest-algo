import requests
import pandas as pd
from typing import Optional

class BCBClient:
    """Cliente para buscar dados macroeconômicos do Banco Central do Brasil."""
    
    # Códigos das séries temporais no SGS
    SERIES = {
        'SELIC': 432,       # Taxa de juros - Meta Copom
        'IPCA': 433,        # Inflação mensal
        'IBC_BR': 24363     # Índice de Atividade Econômica (Proxy do PIB mensal)
    }

    def __init__(self):
        self.base_url = "http://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados?formato=json"

    def fetch_serie(self, name: str, start_date: str = '2010-01-01') -> pd.DataFrame:
        """Busca uma série temporal específica do BCB."""
        if name not in self.SERIES:
            raise ValueError(f"Série {name} não mapeada. Escolha entre: {list(self.SERIES.keys())}")
            
        codigo = self.SERIES[name]
        url = self.base_url.format(codigo)
        
        response = requests.get(url)
        response.raise_for_status()
        
        # Converte JSON para DataFrame
        df = pd.DataFrame(response.json())
        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
        df['valor'] = df['valor'].astype(float)
        
        # Filtra a partir da data de início e seta o index
        df = df[df['data'] >= pd.to_datetime(start_date)]
        df.set_index('data', inplace=True)
        df.rename(columns={'valor': name}, inplace=True)
        
        return df[[name]]

    def fetch_multiple(self, series_names: list, start_date: str = '2010-01-01') -> pd.DataFrame:
        """Busca múltiplas séries e as une."""
        dfs = []
        for name in series_names:
            dfs.append(self.fetch_serie(name, start_date))
        
        result = pd.concat(dfs, axis=1)
        return result.dropna()

if __name__ == "__main__":
    # Teste rápido
    bcb = BCBClient()
    df_selic = bcb.fetch_serie('SELIC')
    print("Últimos dados da SELIC:")
    print(df_selic.tail())
