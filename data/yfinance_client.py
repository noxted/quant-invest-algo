import yfinance as yf
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Union
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore', category=FutureWarning)


class MarketDataClient:
    """Cliente para buscar dados de mercado via Yahoo Finance.
    
    Funcionalidades:
    - Preços históricos (Adj Close para reinvestimento de dividendos)
    - Dados de FIIs brasileiros
    - Índices de mercado (^BVSP, ^GSPC, etc)
    - VIX (volatilidade global)
    - Dividendos e splits
    - Dados fundamentalistas básicos
    """
    
    # Índices importantes
    INDICES = {
        'IBOVESPA': '^BVSP',
        'SP500': '^GSPC',
        'NASDAQ': '^IXIC',
        'VIX': '^VIX',
        'USD_BRL': 'BRL=X',
    }
    
    def __init__(self):
        """Inicializa o cliente de dados de mercado."""
        self.cache = {}  # Cache simples para evitar requisições duplicadas
    
    def fetch_daily_data(self, 
                        tickers: Union[str, List[str]], 
                        start_date: str = '2015-01-01',
                        end_date: Optional[str] = None) -> pd.DataFrame:
        """Busca preços de fechamento ajustados para lista de tickers.
        
        Args:
            tickers: Ticker único ou lista de tickers
            start_date: Data inicial (YYYY-MM-DD)
            end_date: Data final (YYYY-MM-DD), None para hoje
            
        Returns:
            DataFrame com preços ajustados (colunas = tickers, índice = datas)
            
        Example:
            >>> client = MarketDataClient()
            >>> df = client.fetch_daily_data(['WEGE3.SA', 'PETR4.SA'])
            >>> print(df.tail())
        """
        # Normalizar entrada
        if isinstance(tickers, str):
            tickers = [tickers]
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"[YFinance] Baixando {len(tickers)} ticker(s): {', '.join(tickers[:3])}{'...' if len(tickers) > 3 else ''}")
        
        # Cache key
        cache_key = f"{','.join(sorted(tickers))}_{start_date}_{end_date}"
        if cache_key in self.cache:
            print(f"[YFinance] Usando dados em cache")
            return self.cache[cache_key]
        
        try:
            # YFinance aceita string com espaços
            tickers_str = " ".join(tickers)
            data = yf.download(
                tickers_str, 
                start=start_date, 
                end=end_date,
                progress=False,
                threads=True
            )
            
            # Tratamento para caso único vs múltiplos tickers
            if len(tickers) == 1:
                if 'Adj Close' in data.columns:
                    df = data[['Adj Close']].copy()
                    df.columns = tickers
                else:
                    df = data[['Close']].copy()
                    df.columns = tickers
            else:
                if 'Adj Close' in data.columns:
                    df = data['Adj Close'].copy()
                else:
                    df = data['Close'].copy()
            
            # Remover NaN no início (IPOs recentes)
            df = df.dropna(how='all')
            
            # Cache result
            self.cache[cache_key] = df
            
            print(f"[YFinance] Baixados {len(df)} dias de dados")
            return df
            
        except Exception as e:
            print(f"[YFinance] ERRO ao baixar dados: {e}")
            return pd.DataFrame()
    
    def fetch_fii_data(self, 
                      fii_ticker: str, 
                      start_date: str = '2020-01-01') -> Dict:
        """Busca dados específicos de FIIs (Fundos Imobiliários).
        
        Args:
            fii_ticker: Ticker do FII (ex: 'KNIP11.SA')
            start_date: Data inicial
            
        Returns:
            Dict com preços, dividendos, P/VP, dividend yield
        """
        print(f"[YFinance] Buscando dados do FII {fii_ticker}")
        
        ticker = yf.Ticker(fii_ticker)
        
        # Preços históricos
        prices = ticker.history(start=start_date)
        
        # Dividendos
        dividends = ticker.dividends
        dividends_filtered = dividends[dividends.index >= start_date]
        
        # Info básica
        info = ticker.info
        
        return {
            'ticker': fii_ticker,
            'prices': prices[['Close']],
            'dividends': dividends_filtered,
            'total_dividends': dividends_filtered.sum() if len(dividends_filtered) > 0 else 0,
            'current_price': prices['Close'].iloc[-1] if len(prices) > 0 else None,
            'price_range_52w': (
                prices['Close'].iloc[-252:].min() if len(prices) >= 252 else None,
                prices['Close'].iloc[-252:].max() if len(prices) >= 252 else None
            ),
            'market_cap': info.get('marketCap'),
            'sector': info.get('sector', 'FII'),
        }
    
    def fetch_index(self, 
                   index_name: str, 
                   start_date: str = '2020-01-01',
                   end_date: Optional[str] = None) -> pd.DataFrame:
        """Busca dados de um índice de mercado.
        
        Args:
            index_name: Nome do índice ('IBOVESPA', 'SP500', 'VIX', etc)
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            DataFrame com dados do índice
        """
        ticker = self.INDICES.get(index_name, index_name)
        return self.fetch_daily_data(ticker, start_date, end_date)
    
    def get_vix(self, days: int = 30) -> pd.DataFrame:
        """Retorna índice VIX (volatilidade global) dos últimos N dias.
        
        Args:
            days: Número de dias
            
        Returns:
            DataFrame com VIX diário
        """
        start_date = (datetime.now() - timedelta(days=days+10)).strftime('%Y-%m-%d')
        vix = self.fetch_index('VIX', start_date=start_date)
        return vix.tail(days)
    
    def fetch_with_volume(self, 
                         ticker: str,
                         start_date: str = '2020-01-01') -> pd.DataFrame:
        """Busca preços e volume para análise técnica.
        
        Args:
            ticker: Ticker do ativo
            start_date: Data inicial
            
        Returns:
            DataFrame com OHLCV (Open, High, Low, Close, Volume)
        """
        print(f"[YFinance] Buscando OHLCV para {ticker}")
        
        t = yf.Ticker(ticker)
        data = t.history(start=start_date)
        
        return data[['Open', 'High', 'Low', 'Close', 'Volume']]
    
    def calculate_returns(self, 
                         prices: pd.DataFrame,
                         period: str = 'daily') -> pd.DataFrame:
        """Calcula retornos a partir de preços.
        
        Args:
            prices: DataFrame com preços
            period: 'daily', 'monthly', 'yearly'
            
        Returns:
            DataFrame com retornos
        """
        if period == 'daily':
            returns = prices.pct_change()
        elif period == 'monthly':
            # Resample para fim de mês e calcular retorno
            monthly_prices = prices.resample('M').last()
            returns = monthly_prices.pct_change()
        elif period == 'yearly':
            yearly_prices = prices.resample('Y').last()
            returns = yearly_prices.pct_change()
        else:
            raise ValueError(f"Period {period} não suportado")
        
        return returns.dropna()
    
    def get_stock_info(self, ticker: str) -> Dict:
        """Obtém informações fundamentalistas de uma ação.
        
        Args:
            ticker: Ticker da ação
            
        Returns:
            Dict com informações da empresa
        """
        t = yf.Ticker(ticker)
        info = t.info
        
        return {
            'ticker': ticker,
            'name': info.get('longName', info.get('shortName')),
            'sector': info.get('sector'),
            'industry': info.get('industry'),
            'market_cap': info.get('marketCap'),
            'pe_ratio': info.get('trailingPE'),
            'dividend_yield': info.get('dividendYield'),
            'beta': info.get('beta'),
            '52w_high': info.get('fiftyTwoWeekHigh'),
            '52w_low': info.get('fiftyTwoWeekLow'),
            'avg_volume': info.get('averageVolume'),
        }
    
    def fetch_multiple_with_fallback(self,
                                    tickers: List[str],
                                    start_date: str = '2020-01-01') -> pd.DataFrame:
        """Busca múltiplos tickers com fallback individual em caso de erro.
        
        Útil quando alguns tickers podem estar incorretos ou indisponíveis.
        
        Args:
            tickers: Lista de tickers
            start_date: Data inicial
            
        Returns:
            DataFrame com dados disponíveis
        """
        successful_data = {}
        
        for ticker in tickers:
            try:
                data = self.fetch_daily_data(ticker, start_date)
                if len(data) > 0:
                    successful_data[ticker] = data[ticker]
            except Exception as e:
                print(f"[YFinance] Falha ao buscar {ticker}: {e}")
                continue
        
        if successful_data:
            return pd.DataFrame(successful_data)
        return pd.DataFrame()
    
    def clear_cache(self):
        """Limpa o cache de dados."""
        self.cache = {}
        print("[YFinance] Cache limpo")


if __name__ == "__main__":
    # Testes de exemplo
    client = MarketDataClient()
    
    print("\n=== TESTE 1: Ações Brasileiras ===")
    br_stocks = client.fetch_daily_data(
        ['WEGE3.SA', 'PETR4.SA', 'VALE3.SA'],
        start_date='2024-01-01'
    )
    print(br_stocks.tail())
    print(f"Shape: {br_stocks.shape}")
    
    print("\n=== TESTE 2: Índices ===")
    ibov = client.fetch_index('IBOVESPA', start_date='2024-01-01')
    print(ibov.tail())
    
    print("\n=== TESTE 3: VIX (Volatilidade) ===")
    vix = client.get_vix(days=10)
    print(vix)
    print(f"VIX Médio (10 dias): {vix['^VIX'].mean():.2f}")
    
    print("\n=== TESTE 4: FII ===")
    fii_data = client.fetch_fii_data('KNIP11.SA', start_date='2024-01-01')
    print(f"Ticker: {fii_data['ticker']}")
    print(f"Preço Atual: R$ {fii_data['current_price']:.2f}")
    print(f"Dividendos Totais: R$ {fii_data['total_dividends']:.2f}")
    
    print("\n=== TESTE 5: Info de Ação ===")
    info = client.get_stock_info('WEGE3.SA')
    print(f"Nome: {info['name']}")
    print(f"Setor: {info['sector']}")
    print(f"P/L: {info['pe_ratio']}")
    print(f"Beta: {info['beta']}")
    
    print("\n✅ Todos os testes concluídos com sucesso!")
