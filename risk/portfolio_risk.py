import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from scipy.stats import norm
import warnings


@dataclass
class RiskMetrics:
    """Métricas de risco do portfolio."""
    var_95: float  # Value at Risk (95%)
    cvar_95: float  # Conditional Value at Risk (95%)
    expected_shortfall: float  # Expected Shortfall
    volatility: float  # Volatilidade anualizada
    sharpe_ratio: float  # Sharpe Ratio
    sortino_ratio: float  # Sortino Ratio
    max_drawdown: float  # Máximo drawdown
    beta: float  # Beta (sensibilidade ao mercado)
    correlation_matrix: Optional[np.ndarray] = None


class PortfolioRisk:
    """Gerenciador de risco do portfolio.
    
    Calcula métricas de risco, aplica constraints e otimiza
    alocação para perfis de risco diferentes.
    """
    
    # Perfis de risco
    LOW_RISK = 0.1
    MODERATE_RISK = 0.5
    HIGH_RISK = 0.9
    
    def __init__(self, risk_free_rate: float = 0.05, 
                 lookback_period: int = 252,
                 confidence_level: float = 0.95):
        """Inicializa gerenciador de risco.
        
        Args:
            risk_free_rate: Taxa livre de risco (anual)
            lookback_period: Período para cálculo de métricas (dias)
            confidence_level: Nível de confiança para VaR/CVaR
        """
        self.risk_free_rate = risk_free_rate
        self.lookback_period = lookback_period
        self.confidence_level = confidence_level
        self.risk_profile = None
        self.max_volatility = None
        self.max_var = None
    
    def set_risk_profile(self, profile: str) -> None:
        """Define perfil de risco.
        
        Args:
            profile: 'conservative', 'moderate', 'aggressive'
        """
        if profile == 'conservative':
            self.max_volatility = 0.10  # 10% vol anu
            self.max_var = -0.05  # Máx -5% VaR
            self.risk_profile = self.LOW_RISK
        elif profile == 'moderate':
            self.max_volatility = 0.18  # 18% vol anu
            self.max_var = -0.15  # Máx -15% VaR
            self.risk_profile = self.MODERATE_RISK
        else:  # aggressive
            self.max_volatility = 0.30  # 30% vol anu
            self.max_var = -0.30  # Máx -30% VaR
            self.risk_profile = self.HIGH_RISK
    
    def calculate_metrics(self, returns: np.ndarray) -> RiskMetrics:
        """Calcula métricas de risco.
        
        Args:
            returns: Array de retornos diários
            
        Returns:
            RiskMetrics com todas as métricas
        """
        if len(returns) < 2:
            return RiskMetrics(
                var_95=0.0, cvar_95=0.0, expected_shortfall=0.0,
                volatility=0.0, sharpe_ratio=0.0, sortino_ratio=0.0,
                max_drawdown=0.0, beta=0.0
            )
        
        # Volatilidade
        volatility = np.std(returns) * np.sqrt(252)
        
        # VaR (95%)
        var_95 = np.percentile(returns, (1 - self.confidence_level) * 100)
        
        # CVaR (Expected Shortfall)
        cvar_95 = returns[returns <= var_95].mean() if len(returns[returns <= var_95]) > 0 else var_95
        
        # Sharpe Ratio
        mean_return = np.mean(returns) * 252
        sharpe_ratio = (mean_return - self.risk_free_rate) / volatility if volatility > 0 else 0.0
        
        # Sortino Ratio (downside deviation)
        negative_returns = returns[returns < 0]
        downside_vol = np.std(negative_returns) * np.sqrt(252) if len(negative_returns) > 0 else 0.0
        sortino_ratio = (mean_return - self.risk_free_rate) / downside_vol if downside_vol > 0 else 0.0
        
        # Máximo Drawdown
        cumulative_returns = (1 + returns).cumprod()
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = np.min(drawdown) if len(drawdown) > 0 else 0.0
        
        # Beta (simplificado - usar benchmark em produção)
        beta = 1.0  # Placeholder
        
        return RiskMetrics(
            var_95=var_95,
            cvar_95=cvar_95,
            expected_shortfall=cvar_95,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            beta=beta
        )
    
    def calculate_portfolio_var(self, weights: np.ndarray, 
                               asset_returns: np.ndarray,
                               method: str = 'historical') -> float:
        """Calcula VaR do portfolio.
        
        Args:
            weights: Pesos do portfolio
            asset_returns: Matriz de retornos (dias x ativos)
            method: 'historical' ou 'parametric'
            
        Returns:
            VaR do portfolio
        """
        if method == 'historical':
            portfolio_returns = asset_returns @ weights
            var = np.percentile(portfolio_returns, (1 - self.confidence_level) * 100)
            return var
        else:  # parametric
            portfolio_returns = asset_returns @ weights
            mean_return = np.mean(portfolio_returns)
            std_return = np.std(portfolio_returns)
            z_score = norm.ppf(1 - self.confidence_level)
            var = mean_return + z_score * std_return
            return var
    
    def calculate_portfolio_correlation(self, asset_returns: np.ndarray) -> np.ndarray:
        """Calcula matriz de correlação entre ativos.
        
        Args:
            asset_returns: Matriz de retornos (dias x ativos)
            
        Returns:
            Matriz de correlação
        """
        return np.corrcoef(asset_returns.T)
    
    def optimize_weights_for_risk(self, expected_returns: np.ndarray,
                                  cov_matrix: np.ndarray,
                                  target_volatility: float) -> np.ndarray:
        """Otimiza pesos do portfolio para volatilidade alvo.
        
        Args:
            expected_returns: Retorno esperado de cada ativo
            cov_matrix: Matriz de covariância
            target_volatility: Volatilidade alvo
            
        Returns:
            Pesos otimizados
        """
        n_assets = len(expected_returns)
        
        # Começar com pesos iguais
        weights = np.ones(n_assets) / n_assets
        
        # Iterar para encontrar pesos que alcancem volatilidade alvo
        for _ in range(100):  # Máximo 100 iterações
            portfolio_vol = np.sqrt(weights @ cov_matrix @ weights)
            
            if abs(portfolio_vol - target_volatility) < 0.001:
                break
            
            # Ajustar pesos proporcionalmente
            scale = target_volatility / portfolio_vol if portfolio_vol > 0 else 1.0
            weights = weights * scale
            weights = weights / weights.sum()  # Normalizar
        
        return weights
    
    def apply_risk_constraints(self, weights: np.ndarray,
                               var_values: np.ndarray,
                               volatilities: np.ndarray) -> np.ndarray:
        """Aplica constraints de risco aos pesos.
        
        Args:
            weights: Pesos originais
            var_values: VaR de cada ativo
            volatilities: Volatilidade de cada ativo
            
        Returns:
            Pesos ajustados com constraints
        """
        adjusted_weights = weights.copy()
        
        if self.max_var is not None:
            # Reduzir peso de ativos com VaR muito alto
            for i, var in enumerate(var_values):
                if var < self.max_var:
                    adjusted_weights[i] *= 0.8  # Reduzir 20%
        
        if self.max_volatility is not None:
            # Reduzir peso de ativos muito voláteis
            for i, vol in enumerate(volatilities):
                if vol > self.max_volatility:
                    adjusted_weights[i] *= 0.7  # Reduzir 30%
        
        # Normalizar
        adjusted_weights = adjusted_weights / adjusted_weights.sum()
        
        return adjusted_weights
    
    def calculate_diversification_ratio(self, weights: np.ndarray,
                                       volatilities: np.ndarray,
                                       cov_matrix: np.ndarray) -> float:
        """Calcula rácio de diversificação.
        
        Args:
            weights: Pesos do portfolio
            volatilities: Volatilidade de cada ativo
            cov_matrix: Matriz de covariância
            
        Returns:
            Rácio de diversificação (0-1, maior é melhor)
        """
        # Volatilidade média ponderada
        weighted_vol = np.sum(weights * volatilities)
        
        # Volatilidade do portfolio
        portfolio_vol = np.sqrt(weights @ cov_matrix @ weights)
        
        if portfolio_vol > 0:
            return weighted_vol / portfolio_vol
        return 0.0
    
    def stress_test(self, weights: np.ndarray,
                   asset_returns: np.ndarray,
                   shock_magnitude: float = 0.1) -> Dict[str, float]:
        """Realiza teste de stress no portfolio.
        
        Args:
            weights: Pesos do portfolio
            asset_returns: Histórico de retornos
            shock_magnitude: Magnitude do choque (ex: 0.1 = -10%)
            
        Returns:
            Dict com impacto do stress test
        """
        portfolio_returns = asset_returns @ weights
        
        # Retorno normal
        normal_return = np.mean(portfolio_returns)
        normal_vol = np.std(portfolio_returns)
        
        # Retorno sob stress
        stressed_returns = portfolio_returns - shock_magnitude
        stressed_return = np.mean(stressed_returns)
        stressed_vol = np.std(stressed_returns)
        
        return {
            'normal_return': normal_return,
            'normal_volatility': normal_vol,
            'stressed_return': stressed_return,
            'stressed_volatility': stressed_vol,
            'impact': stressed_return - normal_return,
            'volatility_increase': stressed_vol - normal_vol,
        }


if __name__ == "__main__":
    # Teste rápido
    risk_manager = PortfolioRisk(risk_free_rate=0.05)
    risk_manager.set_risk_profile('moderate')
    print(f"PortfolioRisk criado com sucesso!")
    print(f"Perfil: {risk_manager.risk_profile}")
    print(f"Vol máx: {risk_manager.max_volatility}")
