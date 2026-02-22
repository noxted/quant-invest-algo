import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, List


class PortfolioEnvironment:
    """Motor de backtesting para o algoritmo de investimento.
    Simula retornos diarios e processa decisoes de alocacao.
    """

    def __init__(self, initial_capital: float = 1000000.0,
                 price_data: pd.DataFrame = None,
                 macro_data: pd.DataFrame = None,
                 start_date: str = '2020-01-01',
                 end_date: str = '2026-02-22'):
        """
        Args:
            initial_capital: Capital inicial em reais
            price_data: DataFrame com precos de ativos (fechamento ajustado)
            macro_data: DataFrame com dados macro (SELIC, IPCA, PIB)
            start_date: Data inicial do backtest
            end_date: Data final do backtest
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.price_data = price_data
        self.macro_data = macro_data
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        
        # Estado do portfolio
        self.positions = {}  # ticker -> quantidade de ativos
        self.allocation = {}  # ticker -> % do portfolio
        self.portfolio_value = initial_capital
        self.returns_history = []
        self.nav_history = [initial_capital]
        self.current_date_idx = 0
        self.dates = pd.date_range(start=self.start_date, end=self.end_date, freq='D')
        
        # Metricas
        self.total_trades = 0
        self.transaction_costs = 0.0
        self.max_drawdown = 0.0
        self.sharpe_ratio = 0.0
        self.cumulative_return = 0.0

    def reset(self) -> np.ndarray:
        """Reseta o ambiente para o inicio do backtest."""
        self.current_capital = self.initial_capital
        self.positions = {}
        self.allocation = {}
        self.portfolio_value = self.initial_capital
        self.returns_history = []
        self.nav_history = [self.initial_capital]
        self.current_date_idx = 0
        self.total_trades = 0
        self.transaction_costs = 0.0
        return self._get_state()

    def _get_state(self) -> np.ndarray:
        """Retorna o estado atual do portfolio como vetor."""
        if self.current_date_idx >= len(self.dates):
            return np.array([])
        
        # Estado incluindo: capital, valor portfolio, alocacao atual
        state = np.array([
            self.current_capital / self.initial_capital,  # capital normalizado
            self.portfolio_value / self.initial_capital,   # valor normalizado
            len(self.positions),                            # numero de posicoes
        ])
        
        # Adicionar macro data se disponivel
        if self.macro_data is not None and self.current_date_idx < len(self.macro_data):
            macro_row = self.macro_data.iloc[self.current_date_idx]
            state = np.concatenate([
                state,
                np.array([macro_row['SELIC'] / 100, macro_row['IPCA'] / 100])
            ])
        
        return state

    def step(self, allocation: Dict[str, float]) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        Avanca um dia no tempo e processa a alocacao.
        
        Args:
            allocation: Dicionario {ticker: peso (0-1)} para o portfolio
            
        Returns:
            state, reward, done, info
        """
        if self.current_date_idx >= len(self.dates) - 1:
            return self._get_state(), 0.0, True, {'error': 'Backtest finished'}
        
        current_date = self.dates[self.current_date_idx]
        next_date = self.dates[self.current_date_idx + 1]
        
        # Valida alocacao
        total_allocation = sum(allocation.values())
        if abs(total_allocation - 1.0) > 0.01:
            allocation = {k: v / total_allocation for k, v in allocation.items()}
        
        # Calcula valor atual do portfolio antes de reaalocar
        portfolio_value_before = self._calculate_portfolio_value(current_date)
        
        # Rebalanceia portfolio
        self._rebalance_portfolio(allocation, portfolio_value_before)
        
        # Avanca para proximo dia
        self.current_date_idx += 1
        portfolio_value_after = self._calculate_portfolio_value(next_date)
        
        # Calcula retorno
        daily_return = (portfolio_value_after - portfolio_value_before) / portfolio_value_before if portfolio_value_before > 0 else 0
        self.returns_history.append(daily_return)
        self.portfolio_value = portfolio_value_after
        self.nav_history.append(portfolio_value_after)
        
        # Calcula reward (Sharpe ratio normalizado)
        reward = self._calculate_reward(daily_return)
        
        # Check done
        done = self.current_date_idx >= len(self.dates) - 1
        
        # Info
        info = {
            'date': next_date,
            'portfolio_value': portfolio_value_after,
            'daily_return': daily_return,
            'cumulative_return': (portfolio_value_after / self.initial_capital) - 1,
        }
        
        return self._get_state(), reward, done, info

    def _calculate_portfolio_value(self, date: pd.Timestamp) -> float:
        """Calcula valor total do portfolio em uma data."""
        if not self.positions:
            return self.current_capital
        
        total_value = self.current_capital
        for ticker, qty in self.positions.items():
            if ticker in self.price_data.columns:
                try:
                    price = self.price_data.loc[date, ticker]
                    total_value += qty * price
                except (KeyError, TypeError):
                    pass
        
        return total_value

    def _rebalance_portfolio(self, allocation: Dict[str, float], portfolio_value: float) -> None:
        """Rebalanceia o portfolio para a alocacao desejada."""
        # Liquida posicoes atuais
        liquidated_value = 0
        for ticker in list(self.positions.keys()):
            if ticker in self.price_data.columns:
                try:
                    current_date = self.dates[self.current_date_idx]
                    price = self.price_data.loc[current_date, ticker]
                    liquidated_value += self.positions[ticker] * price
                except (KeyError, TypeError):
                    pass
        
        # Total de caixa disponivel
        cash_available = self.current_capital + liquidated_value
        
        # Abre novas posicoes conforme alocacao
        self.positions = {}
        for ticker, weight in allocation.items():
            if weight > 0 and ticker in self.price_data.columns:
                try:
                    current_date = self.dates[self.current_date_idx]
                    price = self.price_data.loc[current_date, ticker]
                    amount = cash_available * weight
                    qty = amount / price
                    self.positions[ticker] = qty
                    
                    # Aplica custo de transacao (0.1%)
                    transaction_cost = amount * 0.001
                    cash_available -= transaction_cost
                    self.transaction_costs += transaction_cost
                    self.total_trades += 1
                except (KeyError, TypeError):
                    pass
        
        self.current_capital = cash_available
        self.allocation = allocation

    def _calculate_reward(self, daily_return: float) -> float:
        """Calcula reward usando Sharpe Ratio."""
        if len(self.returns_history) < 2:
            return daily_return
        
        # Sharpe ratio diario (assumindo 252 dias de trading por ano)
        returns_array = np.array(self.returns_history)
        avg_return = np.mean(returns_array)
        std_return = np.std(returns_array)
        risk_free_rate = 0.0001  # 0.01% ao dia
        
        if std_return == 0:
            return daily_return
        
        sharpe = (avg_return - risk_free_rate) / std_return
        return sharpe

    def get_metrics(self) -> Dict:
        """Retorna metricas do backtest."""
        returns_array = np.array(self.returns_history)
        nav_array = np.array(self.nav_history)
        
        if len(returns_array) == 0:
            return {}
        
        # Calculo de metricas
        cumulative_return = (self.portfolio_value / self.initial_capital) - 1
        annual_return = ((self.portfolio_value / self.initial_capital) ** (252 / max(len(returns_array), 1)) - 1)
        
        # Volatilidade anualizada
        daily_vol = np.std(returns_array)
        annual_vol = daily_vol * np.sqrt(252)
        
        # Sharpe Ratio
        risk_free_rate = 0.05 / 252  # 5% aa
        sharpe = (annual_return - risk_free_rate) / annual_vol if annual_vol > 0 else 0
        
        # Drawdown
        cumulative_returns = (1 + returns_array).cumprod()
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - running_max) / running_max
        max_dd = np.min(drawdown) if len(drawdown) > 0 else 0
        
        return {
            'cumulative_return': cumulative_return,
            'annual_return': annual_return,
            'annual_volatility': annual_vol,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_dd,
            'total_trades': self.total_trades,
            'transaction_costs': self.transaction_costs,
            'final_portfolio_value': self.portfolio_value,
        }


if __name__ == "__main__":
    # Teste rapido
    env = PortfolioEnvironment(initial_capital=100000)
    state = env.reset()
    print(f"Estado inicial: {state}")
    print(f"Portfolio value: {env.portfolio_value}")
    print("Backtesting environment criado com sucesso!")
