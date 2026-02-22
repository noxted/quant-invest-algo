"""
Portfolio Orchestrator
Coordinates all components: data collection, regime detection, sector allocation,
backtesting, and RL optimization for portfolio management
"""

import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from config.profiles import PortfolioProfile, get_profile
from algorithms.regime_detection import RegimeDetector
from algorithms.sector_allocation import SectorAllocator
from environment.backtest_env import PortfolioEnvironment
from risk.portfolio_risk import RiskManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AllocationDecision:
    """Encapsulates an allocation decision with full justification"""
    def __init__(self, date: datetime, profile_name: str, aporte_amount: float):
        self.date = date
        self.profile_name = profile_name
        self.aporte_amount = aporte_amount
        self.profile: Optional[PortfolioProfile] = None
        self.regime: Optional[Dict] = None
        self.sector_scores: Optional[Dict] = None
        self.allocation: Dict[str, float] = {}
        self.justification: str = ""
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert decision to dictionary for logging/storage"""
        return {
            "date": self.date.isoformat(),
            "profile": self.profile_name,
            "aporte_amount": self.aporte_amount,
            "regime": self.regime,
            "allocation": self.allocation,
            "justification": self.justification,
            "timestamp": self.timestamp.isoformat(),
        }


class PortfolioOrchestrator:
    """
    Main orchestrator that coordinates all portfolio management components
    
    Workflow:
    1. Collect market data (macro indicators, sector data)
    2. Detect market regime
    3. Allocate sectors based on regime and profile
    4. Execute trades with justification
    5. Track portfolio performance
    """
    
    def __init__(self, profile_name: str = "intermediate"):
        self.profile = get_profile(profile_name)
        self.regime_detector = RegimeDetector()
        self.sector_allocator = SectorAllocator()
        self.risk_manager = RiskManager()
        self.environment: Optional[PortfolioEnvironment] = None
        self.decision_log: List[AllocationDecision] = []
        logger.info(f"Orchestrator initialized with {self.profile.name} profile")
    
    def initialize_backtest(
        self,
        start_date: str,
        end_date: str,
        initial_capital: float,
        rebalance_freq: str = "monthly"
    ) -> None:
        """
        Initialize the backtesting environment
        
        Args:
            start_date: YYYY-MM-DD format
            end_date: YYYY-MM-DD format
            initial_capital: Starting portfolio value
            rebalance_freq: 'monthly', 'quarterly', 'yearly'
        """
        self.environment = PortfolioEnvironment(
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            transaction_cost=0.001,  # 0.1% transaction cost
        )
        logger.info(f"Backtest environment initialized: {start_date} to {end_date}")
    
    def process_monthly_aporte(
        self,
        date: datetime,
        aporte_amount: float,
        market_data: pd.DataFrame
    ) -> AllocationDecision:
        """
        Process monthly investment (aporte) with full allocation logic
        
        Args:
            date: Date of aporte
            aporte_amount: Amount to invest
            market_data: DataFrame with current market indicators
            
        Returns:
            AllocationDecision with full justification
        """
        decision = AllocationDecision(date, self.profile.name, aporte_amount)
        decision.profile = self.profile
        
        # Step 1: Detect market regime
        regime_data = self.regime_detector.detect(
            market_data,
            indicators=["price", "rsi", "moving_avg", "volatility"]
        )
        decision.regime = regime_data
        logger.info(f"Market regime detected: {regime_data['regime']} (confidence: {regime_data['confidence']:.2%})")
        
        # Step 2: Adjust profile weights based on regime
        adjusted_weights = self._adjust_weights_for_regime(
            self.profile,
            regime_data
        )
        
        # Step 3: Allocate across MEGA layer (asset classes)
        mega_allocation = self._allocate_mega_layer(
            aporte_amount,
            adjusted_weights,
            regime_data
        )
        
        # Step 4: Allocate across MESO layer (sectors)
        sector_scores = self.sector_allocator.score_sectors(
            market_data,
            self.profile
        )
        decision.sector_scores = sector_scores
        
        meso_allocation = self._allocate_meso_layer(
            mega_allocation,
            sector_scores,
            self.profile
        )
        
        # Step 5: Apply risk management constraints
        final_allocation = self.risk_manager.apply_constraints(
            meso_allocation,
            self.profile,
            existing_portfolio={},  # TODO: Get from environment
            market_data=market_data
        )
        
        decision.allocation = final_allocation
        
        # Step 6: Generate justification
        decision.justification = self._generate_justification(
            decision,
            mega_allocation,
            sector_scores,
            regime_data
        )
        
        self.decision_log.append(decision)
        logger.info(f"Allocation decision logged: {decision.justification[:100]}...")
        
        return decision
    
    def _adjust_weights_for_regime(
        self,
        profile: PortfolioProfile,
        regime: Dict
    ) -> Dict[str, float]:
        """
        Dynamically adjust profile weights based on detected market regime
        """
        regime_type = regime["regime"]
        adjustments = {
            "bull": {"us_stocks": 1.2, "br_stocks": 1.1, "fixed_income": 0.8},
            "bear": {"us_stocks": 0.6, "br_stocks": 0.7, "fixed_income": 1.3},
            "sideways": {"us_stocks": 1.0, "br_stocks": 1.0, "fixed_income": 1.0},
            "transition": {"us_stocks": 0.9, "br_stocks": 0.9, "fixed_income": 1.1},
        }
        
        return adjustments.get(regime_type, adjustments["sideways"])
    
    def _allocate_mega_layer(
        self,
        aporte_amount: float,
        adjustments: Dict[str, float],
        regime: Dict
    ) -> Dict[str, float]:
        """
        Allocate across asset classes (MEGA layer)
        Returns: {"fixed_income": X, "fiis": Y, "br_stocks": Z, "us_stocks": W}
        """
        # Apply regime adjustments to profile weights
        fi_pct = self.profile.fixed_income_pct * adjustments.get("fixed_income", 1.0)
        fiis_pct = self.profile.fiis_pct
        br_stocks_pct = self.profile.br_stocks_pct * adjustments.get("br_stocks", 1.0)
        us_stocks_pct = self.profile.us_stocks_pct * adjustments.get("us_stocks", 1.0)
        
        # Normalize to 100%
        total = fi_pct + fiis_pct + br_stocks_pct + us_stocks_pct
        
        return {
            "fixed_income": (fi_pct / total) * aporte_amount,
            "fiis": (fiis_pct / total) * aporte_amount,
            "br_stocks": (br_stocks_pct / total) * aporte_amount,
            "us_stocks": (us_stocks_pct / total) * aporte_amount,
        }
    
    def _allocate_meso_layer(
        self,
        mega_allocation: Dict[str, float],
        sector_scores: Dict[str, float],
        profile: PortfolioProfile
    ) -> Dict[str, float]:
        """
        Allocate across sectors (MESO layer)
        Returns nested allocation: {"br_stocks": {"energy": X, "tech": Y, ...}}
        """
        br_stocks_amount = mega_allocation.get("br_stocks", 0)
        
        # Apply sector weights
        sector_allocation = {}
        for sector, weight in profile.sector_weights.items():
            sector_allocation[sector] = br_stocks_amount * weight
        
        return {"br_stocks": sector_allocation}
    
    def _generate_justification(
        self,
        decision: AllocationDecision,
        mega_allocation: Dict[str, float],
        sector_scores: Dict[str, float],
        regime: Dict
    ) -> str:
        """
        Generate human-readable justification for the allocation decision
        """
        justification = f"""
        === PORTFOLIO ALLOCATION DECISION ===
        Date: {decision.date.strftime('%Y-%m-%d')}
        Profile: {decision.profile_name.upper()}
        Aporte Amount: R$ {decision.aporte_amount:,.2f}
        
        === MARKET REGIME ===
        Type: {regime['regime'].upper()}
        Confidence: {regime['confidence']:.1%}
        Volatility: {regime.get('volatility', 'N/A')}
        
        === MEGA LAYER ALLOCATION (Asset Classes) ===
        Fixed Income: R$ {mega_allocation.get('fixed_income', 0):,.2f}
        FIIs: R$ {mega_allocation.get('fiis', 0):,.2f}
        BR Stocks: R$ {mega_allocation.get('br_stocks', 0):,.2f}
        US Stocks: R$ {mega_allocation.get('us_stocks', 0):,.2f}
        
        === SECTOR PERFORMANCE SCORES ===
        """
        
        for sector, score in sorted(sector_scores.items(), key=lambda x: x[1], reverse=True)[:5]:
            justification += f"\n        {sector}: {score:.2f}"
        
        justification += f"""
        
        === DECISION RATIONALE ===
        Given the {regime['regime'].upper()} market regime with {regime['confidence']:.0%} confidence,
        the {decision.profile_name} profile reduces risk exposure by increasing defensive positions.
        Top-performing sectors ({list(sector_scores.keys())[:2]}) receive higher allocation weight.
        
        Risk Management Constraints Applied: Drawdown tolerance {self.profile.max_drawdown_tolerance:.0%},
        Maximum single position {self.profile.max_single_position:.0%},
        Rebalance threshold {self.profile.rebalance_threshold:.0%}
        """
        
        return justification.strip()
    
    def get_decision_history(self, days: int = 30) -> List[AllocationDecision]:
        """Get recent allocation decisions"""
        if not self.decision_log:
            return []
        
        cutoff_date = datetime.now() - pd.Timedelta(days=days)
        return [d for d in self.decision_log if d.timestamp >= cutoff_date]
    
    def export_decisions_to_csv(self, filename: str) -> None:
        """Export all decisions to CSV for analysis"""
        if not self.decision_log:
            logger.warning("No decisions to export")
            return
        
        df = pd.DataFrame([d.to_dict() for d in self.decision_log])
        df.to_csv(filename, index=False)
        logger.info(f"Decisions exported to {filename}")


if __name__ == "__main__":
    # Example usage
    orchestrator = PortfolioOrchestrator(profile_name="intermediate")
    print(f"Orchestrator initialized with {orchestrator.profile.name} profile")
    print(f"Risk tolerance: {orchestrator.profile.max_drawdown_tolerance:.0%}")
    print(f"Reward metric: {orchestrator.profile.reward_metric}")
