\"\"\"
Portfolio Orchestrator - Optimized Core
Coordinates real-time data collection, regime detection, and sector allocation.
\"\"\"
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from config.profiles import get_profile
from algorithms.regime_detection import RegimeDetection
from algorithms.sector_allocation import SectorAllocation
from data.bcb_client import BCBClient
from data.fred_client import FREDClient
from data.yfinance_client import YFinanceClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class PortfolioOrchestrator:
    def __init__(self, profile_name: str = \"intermediate\"):
        self.profile = get_profile(profile_name)
        self.regime_detector = RegimeDetection()
        self.sector_allocator = SectorAllocation(profile=profile_name)
        self.bcb = BCBClient()
        self.fred = FREDClient()
        self.yfinance = YFinanceClient()
        self.decision_log: List[Dict] = []
        logger.info(f\"Orchestrator initialized: {profile_name}\")

    def fetch_market_data(self) -&gt; pd.DataFrame:
        \"\"\"Consolidated data fetching from all APIs\"\"\"
        logger.info(\"Fetching market indicators...\")
        return pd.DataFrame([{
            'selic': self.bcb.get_latest_selic(),
            'ipca': self.bcb.get_latest_ipca(),
            'fed_funds': self.fred.get_latest_rate(),
            'sp500_ret': self.yfinance.get_ticker_returns('^GSPC'),
            'ibov_ret': self.yfinance.get_ticker_returns('^BVSP')
        }])

    def process_aporte(self, amount: float) -&gt; Dict:
        \"\"\"Single entry point for generating allocation decisions\"\"\"
        data = self.fetch_market_data()
        regime = self.regime_detector.detect_regime(data)
        
        # Adjust weights based on regime
        adj = {\"bull\": 1.1, \"bear\": 0.7, \"sideways\": 1.0}.get(regime['regime'].lower(), 1.0)
        
        # Allocation layers
        allocation = {
            \"fixed_income\": self.profile.fixed_income_pct * (2.0 - adj) * amount,
            \"stocks\": self.profile.br_stocks_pct * adj * amount,
            \"us_stocks\": self.profile.us_stocks_pct * adj * amount
        }
        
        decision = {
            \"date\": datetime.now().isoformat(),
            \"regime\": regime['regime'],
            \"allocation\": allocation,
            \"justification\": f\"Regime {regime['regime']} detected. Exposure adjusted by factor {adj:.2f}.\"
        }
        self.decision_log.append(decision)
        return decision

    def run_agent(self, amount: float = 5000.0):
        \"\"\"Autonomous execution loop\"\"\"
        logger.info(\"AGENT STARTING - FULL AUTONOMY\")
        while True:
            try:
                res = self.process_aporte(amount)
                logger.info(f\"DECISION: {res['justification']}\")
                pd.DataFrame(self.decision_log).to_csv(\"decisions.csv\", index=False)
            except Exception as e:
                logger.error(f\"Agent Error: {e}\")
            time.sleep(86400) # 24h interval

Orchestrator = PortfolioOrchestrator
