import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class SectorWeights:
    """Pesos de alocação para cada setor."""
    energy: float  # Energia
    real_estate: float  # Imóveis (FIIs)
    technology: float  # Tecnologia
    ia: float  # IA/Innovation
    agriculture: float  # Agricultura/Logística
    
    def normalize(self):
        """Normaliza pesos para somar 1.0."""
        total = self.energy + self.real_estate + self.technology + self.ia + self.agriculture
        if total > 0:
            self.energy /= total
            self.real_estate /= total
            self.technology /= total
            self.ia /= total
            self.agriculture /= total
    
    def to_dict(self) -> Dict[str, float]:
        """Converte para dicionário."""
        return {
            'energy': self.energy,
            'real_estate': self.real_estate,
            'technology': self.technology,
            'ia': self.ia,
            'agriculture': self.agriculture,
        }


class SectorAllocation:
    """Aloca recursos entre setores baseado em regime de mercado.
    
    Camadas de alocação:
    1. MEGA: RF, FIIs, Ações
    2. MESO: Setores econômicos
    3. MICRO: Stock picking individual
    """
    
    # Setores
    ENERGY = 'energy'
    REAL_ESTATE = 'real_estate'
    TECHNOLOGY = 'technology'
    IA = 'ia'
    AGRICULTURE = 'agriculture'
    
    # Perfis de investidor
    CONSERVATIVE = 'conservative'
    INTERMEDIATE = 'intermediate'
    AGGRESSIVE = 'aggressive'
    
    def __init__(self, profile: str = INTERMEDIATE):
        """Inicializa alocador de setores.
        
        Args:
            profile: Perfil do investidor (conservative, intermediate, aggressive)
        """
        self.profile = profile
        self.sector_weights = None
        self._initialize_base_weights()
    
    def _initialize_base_weights(self):
        """Inicializa pesos base por perfil."""
        if self.profile == self.CONSERVATIVE:
            # Conservador: energia estavel e imoveisl defensivos
            self.sector_weights = SectorWeights(
                energy=0.30,
                real_estate=0.35,
                technology=0.15,
                ia=0.10,
                agriculture=0.10,
            )
        elif self.profile == self.INTERMEDIATE:
            # Intermediário: equilíbrio entre risco e retorno
            self.sector_weights = SectorWeights(
                energy=0.25,
                real_estate=0.25,
                technology=0.25,
                ia=0.15,
                agriculture=0.10,
            )
        else:  # AGGRESSIVE
            # Agressivo: foco em crescimento (tech e IA)
            self.sector_weights = SectorWeights(
                energy=0.15,
                real_estate=0.15,
                technology=0.35,
                ia=0.25,
                agriculture=0.10,
            )
        
        self.sector_weights.normalize()
    
    def allocate_by_regime(self, regime: str, regime_strength: float) -> Dict[str, float]:
        """Aloca setores conforme regime de mercado.
        
        Args:
            regime: Regime detectado (bull, bear, sideways, transition)
            regime_strength: Força do regime (0-1)
            
        Returns:
            Dict com pesos atualizados para cada setor
        """
        weights = SectorWeights(
            energy=self.sector_weights.energy,
            real_estate=self.sector_weights.real_estate,
            technology=self.sector_weights.technology,
            ia=self.sector_weights.ia,
            agriculture=self.sector_weights.agriculture,
        )
        
        if regime == 'bull':
            # Regime altista: aumentar tech e IA
            weights.technology *= (1 + 0.3 * regime_strength)
            weights.ia *= (1 + 0.4 * regime_strength)
            weights.energy *= (1 - 0.1 * regime_strength)
            weights.real_estate *= (1 - 0.1 * regime_strength)
        
        elif regime == 'bear':
            # Regime baixista: defensivo - energia e imóveis
            weights.energy *= (1 + 0.2 * regime_strength)
            weights.real_estate *= (1 + 0.2 * regime_strength)
            weights.agriculture *= (1 + 0.1 * regime_strength)
            weights.technology *= (1 - 0.2 * regime_strength)
            weights.ia *= (1 - 0.3 * regime_strength)
        
        elif regime == 'sideways':
            # Mercado lateral: manter equilíbrio
            pass  # Manter pesos base
        
        else:  # transition
            # Transição: reduzir risco geral
            weights.energy *= 1.1
            weights.real_estate *= 1.1
            weights.technology *= 0.9
            weights.ia *= 0.85
        
        weights.normalize()
        return weights.to_dict()
    
    def allocate_mega_layer(self, regime: str, regime_strength: float) -> Dict[str, float]:
        """Aloca camada MEGA: RF, FIIs, Ações.
        
        Returns:
            Pesos para fixed_income, fiis, stocks
        """
        if regime == 'bull':
            return {
                'fixed_income': 0.15,
                'fiis': 0.20,
                'stocks': 0.65,
            }
        elif regime == 'bear':
            return {
                'fixed_income': 0.50,
                'fiis': 0.25,
                'stocks': 0.25,
            }
        elif regime == 'sideways':
            return {
                'fixed_income': 0.30,
                'fiis': 0.30,
                'stocks': 0.40,
            }
        else:  # transition
            return {
                'fixed_income': 0.40,
                'fiis': 0.25,
                'stocks': 0.35,
            }
    
    def allocate_meso_layer(self, regime: str, regime_strength: float) -> Dict[str, float]:
        """Aloca camada MESO: setores econômicos.
        
        Returns:
            Pesos para cada setor
        """
        return self.allocate_by_regime(regime, regime_strength)
    
    def allocate_micro_layer(self, regime: str, 
                            meso_weights: Dict[str, float],
                            price_data: Optional[pd.DataFrame] = None) -> Dict[str, float]:
        """Aloca camada MICRO: stock picking individual.
        
        Args:
            regime: Regime atual
            meso_weights: Pesos da camada meso
            price_data: Dados de preço para análise técnica
            
        Returns:
            Pesos para ações/ativos individuais
        """
        # Exemplo de alocação por setor
        micro_allocation = {}
        
        # Energia
        if meso_weights.get('energy', 0) > 0:
            micro_allocation['energy_stocks'] = {
                'petr3': 0.5,  # Petrobrás
                'ggbr4': 0.3,  # Gerdau
                'engi11': 0.2,  # Engenharia
            }
        
        # Imóveis (FIIs)
        if meso_weights.get('real_estate', 0) > 0:
            micro_allocation['real_estate_fiis'] = {
                'knri11': 0.25,  # Kinea
                'rbrr11': 0.25,  # RB Institucional
                'mxrf11': 0.25,  # Multisector
                'vghf11': 0.25,  # VGF FII
            }
        
        # Tecnologia
        if meso_weights.get('technology', 0) > 0:
            micro_allocation['technology_stocks'] = {
                'wege3': 0.4,  # WEG
                'alpa4': 0.3,  # Alpargatas
                'flry3': 0.3,  # Fleury
            }
        
        # IA/Innovation
        if meso_weights.get('ia', 0) > 0:
            micro_allocation['ia_stocks'] = {
                'ttmkx': 0.5,  # Tech stocks
                'irbr3': 0.5,  # IRB Brasil
            }
        
        # Agricultura/Logística
        if meso_weights.get('agriculture', 0) > 0:
            micro_allocation['agriculture_stocks'] = {
                'agro3': 0.4,  # Agíola
                'rail3': 0.3,  # RUMO Logística
                'ccim3': 0.3,  # CCR
            }
        
        return micro_allocation
    
    def get_sector_momentum(self, price_data: pd.DataFrame) -> Dict[str, float]:
        """Calcula momentum de cada setor usando preços históricos.
        
        Args:
            price_data: DataFrame com preços dos ativos
            
        Returns:
            Dict com momentum de cada setor
        """
        momentum = {}
        
        for sector in [self.ENERGY, self.REAL_ESTATE, self.TECHNOLOGY, self.IA, self.AGRICULTURE]:
            if sector in price_data.columns:
                prices = price_data[sector].values
                if len(prices) > 10:
                    momentum[sector] = (prices[-1] - prices[-10]) / prices[-10]
                else:
                    momentum[sector] = 0.0
            else:
                momentum[sector] = 0.0
        
        return momentum
    
    def apply_momentum_adjustment(self, base_weights: Dict[str, float],
                                 momentum: Dict[str, float]) -> Dict[str, float]:
        """Ajusta pesos baseado em momentum dos setores.
        
        Args:
            base_weights: Pesos base
            momentum: Momentum de cada setor
            
        Returns:
            Pesos ajustados
        """
        adjusted_weights = base_weights.copy()
        
        # Aumentar setores com momentum positivo
        for sector, mom in momentum.items():
            if sector in adjusted_weights:
                if mom > 0.02:  # Momentum positivo
                    adjusted_weights[sector] *= 1.1
                elif mom < -0.02:  # Momentum negativo
                    adjusted_weights[sector] *= 0.9
        
        # Normalizar
        total = sum(adjusted_weights.values())
        adjusted_weights = {k: v/total for k, v in adjusted_weights.items()}
        
        return adjusted_weights


if __name__ == "__main__":
    # Teste rápido
    allocator = SectorAllocation(profile=SectorAllocation.INTERMEDIATE)
    print(f"SectorAllocation criado com sucesso!")
    print(f"Pesos base: {allocator.sector_weights.to_dict()}")
    
    # Teste de alocação em regime bull
    bull_weights = allocator.allocate_by_regime('bull', 0.8)
    print(f"Pesos em regime BULL: {bull_weights}")
    
    # Teste de camada mega
    mega_allocation = allocator.allocate_mega_layer('bull', 0.8)
    print(f"Camada MEGA (BULL): {mega_allocation}")
