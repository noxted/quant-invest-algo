"""
Portfolio Orchestrator - Core
Coordinates real-time data collection, regime detection, and sector allocation.
"""
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
from data.yfinance_client import MarketDataClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


class PortfolioOrchestrator:
    def __init__(self, profile_name: str = "intermediate"):
        self.profile = get_profile(profile_name)
        self.regime_detector = RegimeDetection()
        self.sector_allocator = SectorAllocation(profile=profile_name)
        self.bcb = BCBClient()
        self.fred = FREDClient()
        self.market = MarketDataClient()
        self.decision_log: List[Dict] = []
        logger.info(f"Orchestrator initialized: {profile_name}")

    def fetch_macro_data(self) -> Dict:
        """Fetch latest macro indicators from BCB and FRED."""
        logger.info("Fetching macro indicators...")
        selic = self.bcb.get_latest_selic()
        inflation = self.bcb.get_latest_inflation()
        fed_rate_df = self.fred.get_fed_rate(months=1)
        fed_funds = float(fed_rate_df['FEDFUNDS'].iloc[-1]) if not fed_rate_df.empty else 0.0
        return {
            'selic': selic,
            'ipca': inflation.get('IPCA', 0.0),
            'fed_funds': fed_funds,
        }

    def fetch_price_history(self, ticker: str = '^BVSP', period_days: int = 250) -> pd.DataFrame:
        """Fetch historical price data for regime detection."""
        from datetime import timedelta
        start = (datetime.now() - timedelta(days=period_days)).strftime('%Y-%m-%d')
        df = self.market.fetch_daily_data(ticker, start_date=start)
        if df.empty:
            return pd.DataFrame()
        # Rename column to 'close' for RegimeDetection compatibility
        df.columns = ['close']
        return df

    def process_aporte(self, amount: float) -> Dict:
        """Single entry point for generating allocation decisions."""
        # Fetch price history for regime detection
        price_data = self.fetch_price_history('^BVSP')
        macro = self.fetch_macro_data()

        # Detect market regime
        if price_data.empty or len(price_data) < 50:
            logger.warning("Insufficient price data - defaulting to TRANSITION regime")
            regime_result = {'regime': 'transition', 'strength': 0.5}
        else:
            macro_df = pd.DataFrame([macro])
            regime_result = self.regime_detector.detect_regime(price_data, macro_data=macro_df)

        regime = regime_result['regime']
        strength = regime_result.get('strength', 0.5)

        # Mega layer allocation (RF, FIIs, Stocks)
        mega = self.sector_allocator.allocate_mega_layer(regime, strength)

        # Meso layer allocation (sectors)
        meso = self.sector_allocator.allocate_meso_layer(regime, strength)

        # Build value allocation
        allocation = {
            'fixed_income': mega['fixed_income'] * amount,
            'fiis': mega['fiis'] * amount,
            'stocks_br': mega['stocks'] * self.profile.br_stocks_pct / (
                self.profile.br_stocks_pct + self.profile.us_stocks_pct + 0.001) * amount,
            'stocks_us': mega['stocks'] * self.profile.us_stocks_pct / (
                self.profile.br_stocks_pct + self.profile.us_stocks_pct + 0.001) * amount,
        }

        decision = {
            'date': datetime.now().isoformat(),
            'regime': regime,
            'strength': round(strength, 3),
            'macro': macro,
            'mega_allocation': mega,
            'sector_weights': meso,
            'allocation': allocation,
            'justification': (
                f"Regime {regime} (forca {strength:.2f}) detectado. "
                f"SELIC={macro['selic']:.1f}%, IPCA={macro['ipca']:.2f}%, "
                f"Fed={macro['fed_funds']:.2f}%."
            ),
        }
        self.decision_log.append(decision)
        return decision

    def run_agent(self, amount: float = 5000.0):
        """Autonomous execution loop - runs every 24h without human intervention."""
        logger.info("AGENT STARTING - FULL AUTONOMY")
        while True:
            try:
                res = self.process_aporte(amount)
                logger.info(f"DECISION: {res['justification']}")
                pd.DataFrame(self.decision_log).to_csv("decisions.csv", index=False)
            except Exception as e:
                logger.error(f"Agent Error: {e}")
            time.sleep(86400)  # 24h interval


# Alias for backward compatibility
Orchestrator = PortfolioOrchestrator
