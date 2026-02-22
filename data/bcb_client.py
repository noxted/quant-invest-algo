import requests
import pandas as pd
import numpy as np
from typing import Optional, List, Dict
from datetime import datetime

class BCBClient:
    """Cliente para buscar dados macroeconômicos do Banco Central do Brasil (SGS).
    
    Principais séries:
    - SELIC (432): Taxa de juros - Meta Copom
    - IPCA (433): Inflação mensal
    - IGP-M (189): Índice Geral de Preços do Mercado
    - IBC-BR (24363): Índice de Atividade Econômica
    - USD/BRL (1): Taxa de câmbio
    """
    
    # Códigos das séries temporais no SGS
    SERIES = {
        'SELIC': 432,      # % a.a.
        'IPCA': 433,       # % variação mensal
        'IGPM': 189,       # % variação mensal
        'IBC_BR': 24363,   # Índice
        'PIB_MENSAL': 4380, # R$ milhões
        'CAMBIO': 1,       # USD/BRL
    }
    
    def __init__(self):
        """Inicializa o cliente com a URL base do SGS."""
        self.base_url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados?formato=json"
        self.cache = {}

    def fetch_serie(self, name: str, start_date: str = '2010-01-01') -> pd.DataFrame:
        """Busca uma série temporal específica do BCB.
        
        Args:
            name: Nome amigável da série (SELIC, IPCA, etc)
            start_date: Data inicial (YYYY-MM-DD)
            
        Returns:
            pd.DataFrame com data como índice e valor da série
        """
        if name not in self.SERIES:
            available = list(self.SERIES.keys())
            raise ValueError(f"Série '{name}' não mapeada. Disponíveis: {available}")
            
        codigo = self.SERIES[name]
        url = self.base_url.format(codigo)
        
        print(f"[BCB] Buscando série {name} (código {codigo})...")
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            df = pd.DataFrame(data)
            
            # Formatação
            df['data'] = pd.to_datetime(df['data'], dayfirst=True)
            df['valor'] = df['valor'].astype(float)
            
            # Filtro de data e indexação
            df = df[df['data'] >= pd.to_datetime(start_date)]
            df.set_index('data', inplace=True)
            df.sort_index(inplace=True)
            
            # Renomear coluna para o nome da série
            df.rename(columns={'valor': name}, inplace=True)
            
            return df
            
        except Exception as e:
            print(f"[BCB] Erro ao buscar série {name}: {e}")
            return pd.DataFrame()

    def fetch_indicators(self, names: List[str], start_date: str = '2020-01-01') -> pd.DataFrame:
        """Busca múltiplos indicadores e os consolida em um único DataFrame.
        
        Args:
            names: Lista de nomes das séries
            start_date: Data inicial
            
        Returns:
            pd.DataFrame consolidado
        """
        dfs = []
        for name in names:
            df = self.fetch_serie(name, start_date)
            if not df.empty:
                dfs.append(df)
        
        if not dfs:
            return pd.DataFrame()
            
        # Join de todas as séries pelo índice (data)
        result = pd.concat(dfs, axis=1)
        
        # Preenchimento de NaNs (forward fill para séries com frequências diferentes)
        result.ffill(inplace=True)
        
        return result.dropna()

    def get_latest_selic(self) -> float:
        """Retorna a taxa SELIC mais recente."""
        df = self.fetch_serie('SELIC')
        if not df.empty:
            return float(df['SELIC'].iloc[-1])
        return 0.0

    def get_latest_inflation(self) -> Dict[str, float]:
        """Retorna os dados mais recentes de IPCA e IGPM."""
        ipca = self.fetch_serie('IPCA').tail(1)
        igpm = self.fetch_serie('IGPM').tail(1)
        
        return {
            'IPCA': float(ipca['IPCA'].iloc[0]) if not ipca.empty else 0.0,
            'IGPM': float(igpm['IGPM'].iloc[0]) if not igpm.empty else 0.0,
            'date_ipca': ipca.index[0].strftime('%Y-%m-%d') if not ipca.empty else None,
            'date_igpm': igpm.index[0].strftime('%Y-%m-%d') if not igpm.empty else None
        }

if __name__ == "__main__":
    # Teste rápido
    bcb = BCBClient()
    
    print("
=== TESTE: Indicadores Macro BR ===")
    indicadores = bcb.fetch_indicators(['SELIC', 'IPCA', 'IBC_BR'], start_date='2023-01-01')
    print(indicadores.tail())
    
    print(f"
SELIC Atual: {bcb.get_latest_selic()}%")
    
    inflacao = bcb.get_latest_inflation()
    print(f"IPCA (último mês): {inflacao['IPCA']}% ({inflacao['date_ipca']})")
    print(f"IGP-M (último mês): {inflacao['IGPM']}% ({inflacao['date_igpm']})")
    
    print("
✅ Cliente BCB testado com sucesso!")
