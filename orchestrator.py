\"\"\"
Portfolio Orchestrator
Coordinates all components: data collection, regime detection, sector allocation,
backtesting, and RL optimization for portfolio management
\"\"\"
import logging
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from config.profiles import PortfolioProfile, get_profile
from algorithms.regime_detection import RegimeDetection as RegimeDetector
from algorithms.sector_allocation import SectorAllocation as SectorAllocator
from environment.backtest_env import PortfolioEnvironment
from risk.portfolio_risk import PortfolioRisk as RiskManager

# Data Clients for Real Integration
try:
    from data.bcb_client import BCBClient
    from data.fred_client import FREDClient
    from data.yfinance_client import YFinanceClient
except ImportError:
    logging.warning(\"Data clients not found. Using mock data for orchestrator.\")
    BCBClient = FREDClient = YFinanceClient = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AllocationDecision:
    \"\"\"Encapsulates an allocation decision with full justification\"\"\"
    def __init__(self, date: datetime, profile_name: str, aporte_amount: float):
        self.date = date
        self.profile_name = profile_name
        self.aporte_amount = aporte_amount
        self.profile: Optional[PortfolioProfile] = None
        self.regime: Optional[Dict] = None
        self.sector_scores: Optional[Dict] = None
        self.allocation: Dict[str, float] = {}
        self.justification: str = \"\"
        self.timestamp = datetime.now()

    def to_dict(self) -&gt; Dict:
        \"\"\"Convert decision to dictionary for logging/storage\"\"\"
        return {
            \"date\": self.date.isoformat(),
            \"profile\": self.profile_name,
            \"aporte_amount\": self.aporte_amount,
            \"regime\": self.regime,
            \"allocation\": self.allocation,
            \"justification\": self.justification,
            \"timestamp\": self.timestamp.isoformat(),
        }

class PortfolioOrchestrator:
    \"\"\"
    Main orchestrator that coordinates all portfolio management components
    \"\"\"
    def __init__(self, profile_name: str = \"intermediate\"):
        self.profile = get_profile(profile_name)
        self.regime_detector = RegimeDetector()
        self.sector_allocator = SectorAllocator(profile=profile_name)
        self.risk_manager = RiskManager()
        self.environment: Optional[PortfolioEnvironment] = None
        self.decision_log: List[AllocationDecision] = []
        
        # Initialize Data Clients
        self.bcb = BCBClient() if BCBClient else None
        self.fred = FREDClient() if FREDClient else None
        self.yfinance = YFinanceClient() if YFinanceClient else None
        
        logger.info(f\"Orchestrator initialized with {self.profile.name} profile\")

    def fetch_real_market_data(self) -&gt; pd.DataFrame:
        \"\"\"Fetch real macroeconomic and market data from APIs\"\"\"
        logger.info(\"Fetching real-time market data from BCB, FRED, and YFinance...\")
        # Placeholder for real integration - in a real app, this would merge multiple APIs
        # For now, we return a structured dataframe that the RegimeDetector expects
        data = {
            'selic': self.bcb.get_latest_selic() if self.bcb else 10.5,
            'ipca': self.bcb.get_latest_ipca() if self.bcb else 4.5,
            'fed_funds': self.fred.get_latest_rate() if self.fred else 5.25,
            'sp500_ret': self.yfinance.get_ticker_returns('^GSPC') if self.yfinance else 0.01,
            'ibov_ret': self.yfinance.get_ticker_returns('^BVSP') if self.yfinance else 0.005,
        }
        return pd.DataFrame([data])

    def process_monthly_aporte(
        self,
        date: datetime,
        aporte_amount: float,
        market_data: Optional[pd.DataFrame] = None
    ) -&gt; AllocationDecision:
        \"\"\"
        Process investment (aporte) with full allocation logic
        \"\"\"
        if market_data is None:
            market_data = self.fetch_real_market_data()
            
        decision = AllocationDecision(date, self.profile.name, aporte_amount)
        decision.profile = self.profile

        # Step 1: Detect market regime
        regime_data = self.regime_detector.detect_regime(market_data)
        regime_data.setdefault('confidence', regime_data.get('strength', 0.5))
        decision.regime = regime_data

        # Step 2: Adjust weights &amp; Allocate layers
        adjusted_weights = self._adjust_weights_for_regime(self.profile, regime_data)
        mega_allocation = self._allocate_mega_layer(aporte_amount, adjusted_weights, regime_data)
        
        sector_scores = self.sector_allocator.allocate_by_regime(
            regime_data['regime'], 
            regime_data.get('strength', 0.5)
        )
        decision.sector_scores = sector_scores
        
        meso_allocation = self._allocate_meso_layer(mega_allocation, sector_scores, self.profile)
        decision.allocation = meso_allocation

        # Step 3: Generate justification
        decision.justification = self._generate_justification(
            decision, mega_allocation, sector_scores, regime_data
        )
        
        self.decision_log.append(decision)
        return decision

    def run_autonomous_agent(self, aporte_mensal: float = 5000.0, interval_seconds: int = 86400):
        \"\"\"
        Runs the orchestrator as an automatic agent without human interference
        \"\"\"
        logger.info(f\"STARTING AUTONOMOUS AGENT (Interval: {interval_seconds}s, Aporte: R${aporte_mensal})\")
        while True:
            try:
                now = datetime.now()
                logger.info(f\"Agent executing scheduled evaluation at {now}\")
                decision = self.process_monthly_aporte(now, aporte_mensal)
                logger.info(f\"Agent Decision for {now.strftime('%B %Y')}:\")
                logger.info(decision.justification)
                
                # Save decision to log file
                self.export_decisions_to_csv(\"agent_decisions.csv\")
                
            except Exception as e:
                logger.error(f\"Autonomous agent error: {e}\")
                
            logger.info(f\"Agent sleeping for {interval_seconds} seconds...\")
            time.sleep(interval_seconds)

    def _adjust_weights_for_regime(self, profile: PortfolioProfile, regime: Dict) -&gt; Dict[str, float]:
        regime_type = regime[\"regime\"].lower()
        adjustments = {
            \"bull\": {\"us_stocks\": 1.2, \"br_stocks\": 1.1, \"fixed_income\": 0.8},
            \"bear\": {\"us_stocks\": 0.6, \"br_stocks\": 0.7, \"fixed_income\": 1.3},
            \"sideways\": {\"us_stocks\": 1.0, \"br_stocks\": 1.0, \"fixed_income\": 1.0},
            \"transition\": {\"us_stocks\": 0.9, \"br_stocks\": 0.9, \"fixed_income\": 1.1},
        }
        return adjustments.get(regime_type, adjustments[\"sideways\"])

    def _allocate_mega_layer(self, aporte_amount: float, adjustments: Dict[str, float], regime: Dict) -&gt; Dict[str, float]:
        fi_pct = self.profile.fixed_income_pct * adjustments.get(\"fixed_income\", 1.0)
        fiis_pct = self.profile.fiis_pct
        br_stocks_pct = self.profile.br_stocks_pct * adjustments.get(\"br_stocks\", 1.0)
        us_stocks_pct = self.profile.us_stocks_pct * adjustments.get(\"us_stocks\", 1.0)
        total = fi_pct + fiis_pct + br_stocks_pct + us_stocks_pct
        return {
            \"fixed_income\": (fi_pct / total) * aporte_amount,
            \"fiis\": (fiis_pct / total) * aporte_amount,
            \"br_stocks\": (br_stocks_pct / total) * aporte_amount,
            \"us_stocks\": (us_stocks_pct / total) * aporte_amount,
        }

    def _allocate_meso_layer(self, mega_allocation: Dict[str, float], sector_scores: Dict[str, float], profile: PortfolioProfile) -&gt; Dict[str, float]:
        br_stocks_amount = mega_allocation.get(\"br_stocks\", 0)
        sector_allocation = {}
        for sector, weight in profile.sector_weights.items():
            sector_allocation[sector] = br_stocks_amount * weight
        return {\"br_stocks\": sector_allocation}

    def _generate_justification(self, decision: AllocationDecision, mega_allocation: Dict[str, float], sector_scores: Dict[str, float], regime: Dict) -&gt; str:
        justification = f\"\"\"
=== PORTFOLIO ALLOCATION DECISION ===
Date: {decision.date.strftime('%Y-%m-%d')}
Profile: {decision.profile_name.upper()}
Aporte Amount: R$ {decision.aporte_amount:,.2f}
=== MARKET REGIME ===
Type: {regime['regime'].upper()} (Confidence: {regime.get('confidence', 0):.1%})
=== MEGA LAYER ALLOCATION ===
Fixed Income: R$ {mega_allocation.get('fixed_income', 0):,.2f}
FIIs: R$ {mega_allocation.get('fiis', 0):,.2f}
BR Stocks: R$ {mega_allocation.get('br_stocks', 0):,.2f}
US Stocks: R$ {mega_allocation.get('us_stocks', 0):,.2f}
=== DECISION RATIONALE ===
Autonomous agent detected {regime['regime'].upper()} regime. 
Adjusted exposure to {decision.profile_name} profile constraints.
\"\"\"
        return justification.strip()

    def get_decision_history(self, days: int = 30) -&gt; List[AllocationDecision]:
        return [d for d in self.decision_log if (datetime.now() - d.timestamp).days &lt;= days]

    def export_decisions_to_csv(self, filename: str) -&gt; None:
        df = pd.DataFrame([d.to_dict() for d in self.decision_log])
        df.to_csv(filename, index=False)
        logger.info(f\"Decisions exported to {filename}\")

    def get_portfolio_summary(self) -&gt; Dict:
        return {
            \"profile\": self.profile.name,
            \"decisions_count\": len(self.decision_log),
            \"last_decision\": self.decision_log[-1].to_dict() if self.decision_log else None
        }

    def get_current_regime(self) -&gt; Dict:
        if self.decision_log:
            return self.decision_log[-1].regime or {\"regime\": \"unknown\", \"confidence\": 0.0}
        return {\"regime\": \"intermediate\", \"confidence\": 0.75}

Orchestrator = PortfolioOrchestrator

