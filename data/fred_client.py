import requests
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Union
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')


class FREDClient:
    """Cliente para buscar dados macroeconômicos da API FRED (Federal Reserve Economic Data).
    
    Principais séries econômicas dos EUA:
    - FEDFUNDS: Taxa de juros do Fed (Fed Funds Rate)
    - CPIAUCSL: CPI (Consumer Price Index) - Inflação
    - A191RL1Q225SBEA: PIB Real (crescimento trimestral)
    - T10Y2Y: Yield Curve (10Y - 2Y Treasury)
    - UNRATE: Taxa de desemprego
    - DGS10: Taxa de 10-Year Treasury
    
    Requer API Key da FRED (grátis): https://fred.stlouisfed.org/docs/api/api_key.html
    """
    
    # Séries principais
    SERIES = {
        'FEDFUNDS': 'FEDFUNDS',           # Fed Funds Rate (%)
        'CPI': 'CPIAUCSL',                # Consumer Price Index
        'GDP': 'A191RL1Q225SBEA',         # GDP Growth Rate (quarterly)
        'YIELD_CURVE': 'T10Y2Y',          # 10Y-2Y Treasury Spread
        'UNEMPLOYMENT': 'UNRATE',         # Unemployment Rate (%)
        'TREASURY_10Y': 'DGS10',          # 10-Year Treasury Rate (%)
        'TREASURY_2Y': 'DGS2',            # 2-Year Treasury Rate (%)
        'SP500': 'SP500',                 # S&P 500 Index
        'NASDAQ': 'NASDAQCOM',            # NASDAQ Composite
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """Inicializa o cliente FRED.
        
        Args:
            api_key: API key da FRED (opcional para testes limitados)
                    Obtenha em: https://fred.stlouisfed.org/docs/api/api_key.html
        """
        self.api_key = api_key or "demo"  # API key demo (limitada)
        self.base_url = "https://api.stlouisfed.org/fred/series/observations"
        self.cache = {}
        
    def fetch_series(self, 
                    series_id: Union[str, List[str]], 
                    start_date: str = '2010-01-01',
                    end_date: Optional[str] = None,
                    frequency: str = 'monthly') -> pd.DataFrame:
        """Busca uma ou múltiplas séries temporais da FRED.
        
        Args:
            series_id: ID da série ou lista de IDs (ex: 'FEDFUNDS', ['FEDFUNDS', 'CPI'])
            start_date: Data inicial (YYYY-MM-DD)
            end_date: Data final (YYYY-MM-DD), None para hoje
            frequency: 'daily', 'weekly', 'monthly', 'quarterly', 'annual'
            
        Returns:
            DataFrame com as séries temporais
        """
        # Normalizar input
        if isinstance(series_id, str):
            series_id = [series_id]
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Mapear nomes amigáveis para IDs
        series_ids = [self.SERIES.get(s, s) for s in series_id]
        
        dfs = []
        for sid in series_ids:
            df = self._fetch_single_series(sid, start_date, end_date, frequency)
            if not df.empty:
                dfs.append(df)
        
        if not dfs:
            return pd.DataFrame()
        
        # Consolidar todas as séries
        result = pd.concat(dfs, axis=1)
        return result.dropna(how='all')
    
    def _fetch_single_series(self, 
                            series_id: str,
                            start_date: str,
                            end_date: str,
                            frequency: str) -> pd.DataFrame:
        """Busca uma única série da FRED."""
        # Mapear frequência para formato da API
        freq_map = {
            'daily': 'd',
            'weekly': 'w',
            'monthly': 'm',
            'quarterly': 'q',
            'annual': 'a'
        }
        
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json',
            'observation_start': start_date,
            'observation_end': end_date,
            'frequency': freq_map.get(frequency, 'm'),
        }
        
        cache_key = f"{series_id}_{start_date}_{end_date}_{frequency}"
        if cache_key in self.cache:
            print(f"[FRED] Usando cache para {series_id}")
            return self.cache[cache_key]
        
        print(f"[FRED] Buscando série {series_id}...")
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'observations' not in data:
                print(f"[FRED] Nenhum dado encontrado para {series_id}")
                return pd.DataFrame()
            
            # Processar dados
            observations = data['observations']
            df = pd.DataFrame(observations)
            
            # Converter data e valor
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            
            # Remover valores ausentes ('.')
            df = df[df['value'].notna()]
            
            # Configurar índice e renomear coluna
            df.set_index('date', inplace=True)
            df = df[['value']]
            df.columns = [series_id]
            
            # Cache
            self.cache[cache_key] = df
            
            print(f"[FRED] {len(df)} observações recuperadas para {series_id}")
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"[FRED] Erro na requisição para {series_id}: {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"[FRED] Erro ao processar {series_id}: {e}")
            return pd.DataFrame()
    
    def get_fed_rate(self, months: int = 12) -> pd.DataFrame:
        """Retorna histórico da taxa de juros do Fed.
        
        Args:
            months: Número de meses de histórico
            
        Returns:
            DataFrame com Fed Funds Rate
        """
        start_date = (datetime.now() - timedelta(days=months*30)).strftime('%Y-%m-%d')
        return self.fetch_series('FEDFUNDS', start_date=start_date, frequency='monthly')
    
    def get_inflation_data(self, years: int = 5) -> pd.DataFrame:
        """Retorna dados de inflação (CPI).
        
        Args:
            years: Número de anos de histórico
            
        Returns:
            DataFrame com CPI
        """
        start_date = (datetime.now() - timedelta(days=years*365)).strftime('%Y-%m-%d')
        cpi = self.fetch_series('CPI', start_date=start_date, frequency='monthly')
        
        # Calcular inflação anual (% change)
        if not cpi.empty:
            cpi['inflation_yoy'] = cpi['CPIAUCSL'].pct_change(12) * 100
        
        return cpi
    
    def get_yield_curve(self, days: int = 365) -> pd.DataFrame:
        """Retorna o spread da curva de juros (10Y - 2Y).
        
        Args:
            days: Número de dias de histórico
            
        Returns:
            DataFrame com yield curve spread
        """
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        yield_curve = self.fetch_series('YIELD_CURVE', start_date=start_date, frequency='daily')
        
        # Curva invertida indica recessão quando negativa
        if not yield_curve.empty:
            yield_curve['inverted'] = yield_curve['T10Y2Y'] < 0
        
        return yield_curve
    
    def get_macro_indicators(self, start_date: str = '2020-01-01') -> pd.DataFrame:
        """Busca principais indicadores macroeconômicos dos EUA.
        
        Returns:
            DataFrame consolidado com múltiplos indicadores
        """
        indicators = ['FEDFUNDS', 'CPI', 'UNEMPLOYMENT', 'TREASURY_10Y', 'YIELD_CURVE']
        
        df = self.fetch_series(indicators, start_date=start_date, frequency='monthly')
        
        # Adicionar coluna de tendência da yield curve
        if 'T10Y2Y' in df.columns:
            df['recession_signal'] = df['T10Y2Y'] < 0
        
        return df
    
    def is_recession_likely(self) -> Dict[str, any]:
        """Analisa indicadores para prever recessão.
        
        Returns:
            Dict com análise de probabilidade de recessão
        """
        # Buscar yield curve dos últimos 6 meses
        yield_curve = self.get_yield_curve(days=180)
        
        # Buscar desemprego
        unemployment = self.fetch_series('UNEMPLOYMENT', 
                                        start_date=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
                                        frequency='monthly')
        
        analysis = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'yield_curve_inverted': False,
            'unemployment_rising': False,
            'recession_probability': 'Low'
        }
        
        # Verificar curva invertida
        if not yield_curve.empty:
            recent_inversion = yield_curve['T10Y2Y'].tail(30).mean()
            if recent_inversion < 0:
                analysis['yield_curve_inverted'] = True
        
        # Verificar desemprego crescente
        if not unemployment.empty and len(unemployment) > 6:
            recent_trend = unemployment['UNRATE'].tail(6).diff().mean()
            if recent_trend > 0.1:
                analysis['unemployment_rising'] = True
        
        # Avaliar probabilidade
        if analysis['yield_curve_inverted'] and analysis['unemployment_rising']:
            analysis['recession_probability'] = 'High'
        elif analysis['yield_curve_inverted'] or analysis['unemployment_rising']:
            analysis['recession_probability'] = 'Medium'
        
        return analysis
    
    def clear_cache(self):
        """Limpa o cache de dados."""
        self.cache = {}
        print("[FRED] Cache limpo")


if __name__ == "__main__":
    # Testes
    fred = FREDClient()  # Usar API key demo
    
    print("\n=== TESTE 1: Taxa de Juros do Fed ===")
    fed_rate = fred.get_fed_rate(months=24)
    if not fed_rate.empty:
        print(fed_rate.tail())
        print(f"\nTaxa atual (aproximada): {fed_rate['FEDFUNDS'].iloc[-1]:.2f}%")
    
    print("\n=== TESTE 2: Inflação (CPI) ===")
    inflation = fred.get_inflation_data(years=3)
    if not inflation.empty:
        print(inflation[['CPIAUCSL', 'inflation_yoy']].tail())
    
    print("\n=== TESTE 3: Yield Curve ===")
    yield_curve = fred.get_yield_curve(days=180)
    if not yield_curve.empty:
        print(yield_curve.tail())
        inverted_days = yield_curve['inverted'].sum()
        print(f"\nDias com curva invertida (últimos 180): {inverted_days}")
    
    print("\n=== TESTE 4: Análise de Recessão ===")
    recession_analysis = fred.is_recession_likely()
    print(f"Curva invertida: {recession_analysis['yield_curve_inverted']}")
    print(f"Desemprego crescente: {recession_analysis['unemployment_rising']}")
    print(f"Probabilidade de recessão: {recession_analysis['recession_probability']}")
    
    print("\n=== TESTE 5: Múltiplos Indicadores ===")
    macro = fred.get_macro_indicators(start_date='2023-01-01')
    if not macro.empty:
        print(macro.tail())
        print(f"\nShape: {macro.shape}")
    
    print("\n✅ Todos os testes do cliente FRED concluídos!")
