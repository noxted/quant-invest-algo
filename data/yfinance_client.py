import yfinance as yf
import pandas as pd
from typing import List, Optional

class MarketDataClient:
    """Cliente para buscar histórico de preços e dividendos de ativos financeiros."""

    def __init__(self):
        pass

    def fetch_daily_data(self, tickers: List[str], start_date: str = '2015-01-01') -> pd.DataFrame:
        """
        Busca preços de fechamento ajustados (Adj Close) para uma lista de tickers.
        Adj Close é crucial pois já contabiliza o reinvestimento de dividendos.
        """
        print(f"Baixando dados para: {tickers}...")
        
        # O yfinance aceita uma string com tickers separados por espaço
        tickers_str = " ".join(tickers)
        
        data = yf.download(tickers_str, start=start_date, progress=False)
        
        # Se for só um ticker, o yfinance retorna uma Series no Adj Close, precisamos tratar
        if len(tickers) == 1:
            df = data[['Adj Close']].copy()
            df.columns = tickers
            return df
            
        return data['Adj Close']

    def fetch_with_dividends(self, ticker: str, start_date: str = '2015-01-01') -> pd.DataFrame:
        """
        Busca preços e dividendos para um ativo específico.
        """
        prices = yf.download(ticker, start=start_date, progress=False)[['Adj Close']]
        prices.columns = [ticker]
        
        # Buscar histórico de dividendos
        t = yf.Ticker(ticker)
        dividends = t.dividends
        
        if len(dividends) > 0:
            # Juntar com os preços
            result = pd.DataFrame({ticker: prices[ticker], f'{ticker}_div': 0.0})
            result.loc[dividends.index, f'{ticker}_div'] = dividends
            return result
        
        return prices

if __name__ == "__main__":
    # Teste rápido
    market = MarketDataClient()
    tickers = ['^BVSP', '^GSPC', 'KNIP11.SA', 'WEGE3.SA']
    df_market = market.fetch_daily_data(tickers, start_date='2020-01-01')
    print("\nÚltimos preços ajustados de mercado:")
    print(df_market.tail())
