import numpy as np
import pandas as pd
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta


class RegimeDetection:
    """Detecta regimes de mercado usando indicadores técnicos e macro.
    
    Identifica 4 regimes:
    - BULL: Mercado em alta com alta volatilidade controlada
    - BEAR: Mercado em queda com risco elevado
    - SIDEWAYS: Mercado lateralizado sem tendência clara
    - TRANSITION: Período de transição entre regimes
    """
    
    # Regimes
    BULL = 'bull'
    BEAR = 'bear'
    SIDEWAYS = 'sideways'
    TRANSITION = 'transition'
    
    def __init__(self, 
                 window_short: int = 20,
                 window_medium: int = 50,
                 window_long: int = 200,
                 volatility_window: int = 30,
                 rsi_oversold: float = 30.0,
                 rsi_overbought: float = 70.0):
        """Inicializa detector de regimes.
        
        Args:
            window_short: Janela curta para MAs
            window_medium: Janela média para MAs
            window_long: Janela longa para MAs
            volatility_window: Janela para cálculo de volatilidade
            rsi_oversold: Nível de RSI sobrevenda
            rsi_overbought: Nível de RSI sobrecompra
        """
        self.window_short = window_short
        self.window_medium = window_medium
        self.window_long = window_long
        self.volatility_window = volatility_window
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.current_regime = None
        self.regime_strength = 0.0
    
    def detect_regime(self, price_data: pd.DataFrame, 
                     macro_data: Optional[pd.DataFrame] = None) -> Dict:
        """Detecta o regime atual de mercado.
        
        Args:
            price_data: DataFrame com histórico de preços (close)
            macro_data: DataFrame com indicadores macro (SELIC, IPCA, PIB)
            
        Returns:
            Dict com regime, força e indicadores
        """
        if len(price_data) < self.window_long:
            return {'regime': self.TRANSITION, 'strength': 0.0}
        
        close = price_data['close'].values if isinstance(price_data, pd.DataFrame) else price_data.values
        
        # Calcular indicadores
        mas = self._calculate_mas(close)
        rsi = self._calculate_rsi(close)
        volatility = self._calculate_volatility(close)
        trend = self._calculate_trend(close, mas)
        momentum = self._calculate_momentum(close)
        
        # Detectar regime
        regime, strength = self._identify_regime(
            trend=trend,
            rsi=rsi,
            volatility=volatility,
            momentum=momentum,
            macro_data=macro_data
        )
        
        self.current_regime = regime
        self.regime_strength = strength
        
        return {
            'regime': regime,
            'strength': strength,
            'trend': trend,
            'rsi': rsi[-1],
            'volatility': volatility[-1],
            'momentum': momentum[-1],
            'mas': {
                'short': mas['short'][-1],
                'medium': mas['medium'][-1],
                'long': mas['long'][-1],
            }
        }
    
    def _calculate_mas(self, close: np.ndarray) -> Dict:
        """Calcula médias móveis."""
        ma_short = pd.Series(close).rolling(window=self.window_short).mean().values
        ma_medium = pd.Series(close).rolling(window=self.window_medium).mean().values
        ma_long = pd.Series(close).rolling(window=self.window_long).mean().values
        
        return {
            'short': ma_short,
            'medium': ma_medium,
            'long': ma_long,
        }
    
    def _calculate_rsi(self, close: np.ndarray, window: int = 14) -> np.ndarray:
        """Calcula RSI (Relative Strength Index)."""
        delta = np.diff(close)
        seed = delta[:window+1]
        up = seed[seed >= 0].sum() / window
        down = -seed[seed < 0].sum() / window
        rs = up / down if down != 0 else 0
        rsi = np.zeros_like(close)
        rsi[:window] = 100. - 100. / (1. + rs)
        
        for i in range(window, len(close)):
            delta_val = delta[i-1]
            if delta_val >= 0:
                up = (up * (window - 1) + delta_val) / window
                down = (down * (window - 1)) / window
            else:
                up = (up * (window - 1)) / window
                down = (down * (window - 1) - delta_val) / window
            
            rs = up / down if down != 0 else 0
            rsi[i] = 100. - 100. / (1. + rs)
        
        return rsi
    
    def _calculate_volatility(self, close: np.ndarray) -> np.ndarray:
        """Calcula volatilidade (desvio padrão dos retornos)."""
        returns = np.diff(np.log(close))
        volatility = pd.Series(returns).rolling(window=self.volatility_window).std().values
        volatility = np.insert(volatility, 0, [0] * (len(close) - len(volatility)))
        return volatility * 100  # Percentual
    
    def _calculate_trend(self, close: np.ndarray, mas: Dict) -> float:
        """Calcula força da tendência usando MAs.
        
        Retorna valor entre -1 (tendência baixista) e 1 (tendência altista)
        """
        ma_short = mas['short'][-1]
        ma_medium = mas['medium'][-1]
        ma_long = mas['long'][-1]
        current_price = close[-1]
        
        # Scores
        trend_score = 0.0
        
        # Price vs MAs
        if current_price > ma_short > ma_medium > ma_long:
            trend_score += 1.0  # Forte tendência de alta
        elif current_price > ma_medium > ma_long:
            trend_score += 0.5
        elif current_price < ma_short < ma_medium < ma_long:
            trend_score -= 1.0  # Forte tendência de baixa
        elif current_price < ma_medium < ma_long:
            trend_score -= 0.5
        
        # MA alignment
        if ma_short > ma_medium and ma_medium > ma_long:
            trend_score += 0.3
        elif ma_short < ma_medium and ma_medium < ma_long:
            trend_score -= 0.3
        
        return np.clip(trend_score, -1, 1)
    
    def _calculate_momentum(self, close: np.ndarray, window: int = 10) -> float:
        """Calcula momentum (taxa de mudança)."""
        if len(close) < window:
            return 0.0
        return (close[-1] - close[-window-1]) / close[-window-1]
    
    def _identify_regime(self, trend: float, rsi: np.ndarray, 
                        volatility: np.ndarray, momentum: float,
                        macro_data: Optional[pd.DataFrame] = None) -> Tuple[str, float]:
        """Identifica regime baseado em indicadores."""
        
        rsi_current = rsi[-1]
        vol_current = volatility[-1]
        vol_avg = np.nanmean(volatility[-20:]) if len(volatility) >= 20 else vol_current
        
        # Scores para cada regime
        bull_score = 0.0
        bear_score = 0.0
        sideways_score = 0.0
        
        # Análise de trend
        if trend > 0.5:
            bull_score += 0.4
        elif trend < -0.5:
            bear_score += 0.4
        elif -0.2 <= trend <= 0.2:
            sideways_score += 0.3
        
        # Análise de RSI
        if rsi_current > self.rsi_overbought:
            bull_score += 0.2
            bear_score += 0.1  # Pode ser reversão
        elif rsi_current < self.rsi_oversold:
            bear_score += 0.2
            bull_score += 0.1  # Pode ser reversão
        elif 40 <= rsi_current <= 60:
            sideways_score += 0.2
        
        # Análise de volatilidade
        if vol_current > vol_avg * 1.5:
            # Alta volatilidade - pode ser oportunidade ou risco
            if trend > 0:
                bull_score += 0.1
            else:
                bear_score += 0.1
        elif vol_current < vol_avg * 0.7:
            # Baixa volatilidade
            sideways_score += 0.2
        
        # Análise de momentum
        if momentum > 0.02:
            bull_score += 0.3
        elif momentum < -0.02:
            bear_score += 0.3
        elif -0.01 <= momentum <= 0.01:
            sideways_score += 0.2
        
        # Detectar transição
        max_score = max(bull_score, bear_score, sideways_score)
        if max_score < 0.4:  # Scores baixos indicam transição
            return self.TRANSITION, max_score
        
        # Identificar regime
        if bull_score >= bear_score and bull_score >= sideways_score:
            return self.BULL, min(bull_score, 1.0)
        elif bear_score >= bull_score and bear_score >= sideways_score:
            return self.BEAR, min(bear_score, 1.0)
        else:
            return self.SIDEWAYS, min(sideways_score, 1.0)
    
    def get_allocation_adjustments(self) -> Dict[str, float]:
        """Retorna ajustes de alocação baseado no regime atual.
        
        Para cada regime, recomenda pesos para:
        - Ações (stocks)
        - Renda Fixa (bonds)
        - Caixa (cash)
        """
        if self.current_regime is None:
            return {'stocks': 0.6, 'bonds': 0.3, 'cash': 0.1}
        
        if self.current_regime == self.BULL:
            # Regime altista: aumentar exposição a ações
            adjustment = {
                'stocks': 0.75,
                'bonds': 0.15,
                'cash': 0.10,
            }
        elif self.current_regime == self.BEAR:
            # Regime baixista: reduzir risco
            adjustment = {
                'stocks': 0.30,
                'bonds': 0.50,
                'cash': 0.20,
            }
        elif self.current_regime == self.SIDEWAYS:
            # Mercado lateral: manter equilíbrio
            adjustment = {
                'stocks': 0.50,
                'bonds': 0.35,
                'cash': 0.15,
            }
        else:  # TRANSITION
            # Período de transição: ser conservador
            adjustment = {
                'stocks': 0.40,
                'bonds': 0.45,
                'cash': 0.15,
            }
        
        # Aplicar força do regime como multiplicador
        base_stocks = adjustment['stocks']
        base_bonds = adjustment['bonds']
        base_cash = adjustment['cash']
        
        # Aumentar/diminuir exposição baseado na força
        strength_factor = self.regime_strength
        
        final_stocks = base_stocks + (base_cash * strength_factor * 0.5)
        final_bonds = base_bonds
        final_cash = base_cash * (1 - strength_factor * 0.5)
        
        # Normalizar
        total = final_stocks + final_bonds + final_cash
        
        return {
            'stocks': final_stocks / total,
            'bonds': final_bonds / total,
            'cash': final_cash / total,
        }


if __name__ == "__main__":
    # Teste rápido
    detector = RegimeDetection()
    print(f"RegimeDetection criado com sucesso!")
    print(f"Regimes disponíveis: {detector.BULL}, {detector.BEAR}, {detector.SIDEWAYS}, {detector.TRANSITION}")
