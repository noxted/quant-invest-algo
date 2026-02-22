#!/usr/bin/env python3
"""
Main Entry Point for Quantitative Investment Algorithm

Usage:
    python main.py --profile conservative --start-date 2020-01-01 --end-date 2026-12-31 --initial-capital 100000
    python main.py --profile intermediate --backtest
    python main.py --profile aggressive --train-rl
"""

import sys
import logging
import argparse
from datetime import datetime, timedelta
import pandas as pd
from typing import Optional

from orchestrator import PortfolioOrchestrator
from config.profiles import PROFILES, get_profile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/portfolio.log'),
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


class PortfolioAlgorithmApp:
    """
    Main application for running the quantitative portfolio algorithm
    """
    
    def __init__(self, profile_name: str):
        self.profile_name = profile_name.lower()
        self.profile = get_profile(self.profile_name)
        self.orchestrator = PortfolioOrchestrator(profile_name=self.profile_name)
        logger.info(f"Portfolio Algorithm initialized with {self.profile.name} profile")
    
    def run_backtest(
        self,
        start_date: str,
        end_date: str,
        initial_capital: float,
        monthly_aporte: Optional[float] = 1500,
    ) -> None:
        """
        Run a complete backtest from start_date to end_date
        
        Args:
            start_date: YYYY-MM-DD format
            end_date: YYYY-MM-DD format
            initial_capital: Starting portfolio value
            monthly_aporte: Monthly investment amount (default: 1500 BRL)
        """
        logger.info(f"Starting backtest: {start_date} to {end_date}")
        logger.info(f"Initial capital: R$ {initial_capital:,.2f}")
        logger.info(f"Monthly aporte: R$ {monthly_aporte:,.2f}")
        
        # Initialize backtesting environment
        self.orchestrator.initialize_backtest(
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
        )
        
        # TODO: Load market data from data module
        # TODO: Simulate monthly aporte processing
        # TODO: Track portfolio performance
        # TODO: Calculate metrics (Sharpe, Sortino, Calmar, max drawdown)
        # TODO: Generate performance report
        
        logger.info("Backtest completed successfully")
    
    def run_training(
        self,
        start_date: str,
        end_date: str,
        episodes: int = 100,
        learning_rate: float = 0.001,
    ) -> None:
        """
        Train the RL agent on historical data
        
        Args:
            start_date: Training period start
            end_date: Training period end
            episodes: Number of training episodes
            learning_rate: RL learning rate
        """
        logger.info(f"Starting RL training: {start_date} to {end_date}")
        logger.info(f"Episodes: {episodes}, Learning rate: {learning_rate}")
        
        # TODO: Initialize RL agent from risk/agents/rl_agent.py
        # TODO: Load training data
        # TODO: Run training loop
        # TODO: Track training metrics
        # TODO: Save trained model
        
        logger.info("RL training completed successfully")
    
    def run_live(
        self,
        days: int = 30,
    ) -> None:
        """
        Run live allocation decisions (paper trading)
        
        Args:
            days: Number of days to simulate
        """
        logger.info(f"Starting live simulation: {days} days")
        
        # TODO: Fetch current market data
        # TODO: Process daily decisions
        # TODO: Log allocations
        # TODO: Display performance summary
        
        logger.info("Live simulation completed")
    
    def generate_report(self, output_file: str = None) -> None:
        """
        Generate a comprehensive performance report
        
        Args:
            output_file: Path to save report (CSV, HTML, etc.)
        """
        logger.info("Generating performance report")
        
        if not output_file:
            output_file = f"reports/portfolio_{self.profile_name}_{datetime.now().strftime('%Y%m%d')}.csv"
        
        self.orchestrator.export_decisions_to_csv(output_file)
        logger.info(f"Report saved to {output_file}")
    
    def show_profile_summary(self) -> None:
        """
        Display profile configuration summary
        """
        profile = self.profile
        print(f"\n{'='*60}")
        print(f"PORTFOLIO PROFILE: {profile.name.upper()}")
        print(f"{'='*60}")
        print(f"\nRisk Level: {profile.risk_level}/3")
        print(f"Max Drawdown Tolerance: {profile.max_drawdown_tolerance:.0%}")
        print(f"Reward Metric: {profile.reward_metric}")
        print(f"Risk Penalty Factor: {profile.risk_penalty_factor}")
        
        print(f"\nMEGA LAYER (Asset Classes):")
        print(f"  Fixed Income: {profile.fixed_income_pct:.0%} ({profile.fixed_income_min:.0%}-{profile.fixed_income_max:.0%})")
        print(f"  FIIs: {profile.fiis_pct:.0%} ({profile.fiis_min:.0%}-{profile.fiis_max:.0%})")
        print(f"  BR Stocks: {profile.br_stocks_pct:.0%} ({profile.br_stocks_min:.0%}-{profile.br_stocks_max:.0%})")
        print(f"  US Stocks: {profile.us_stocks_pct:.0%} ({profile.us_stocks_min:.0%}-{profile.us_stocks_max:.0%})")
        
        print(f"\nMESO LAYER (Sectors):")
        for sector, weight in sorted(profile.sector_weights.items(), key=lambda x: x[1], reverse=True):
            min_w = profile.sector_min.get(sector, 0)
            max_w = profile.sector_max.get(sector, 1)
            print(f"  {sector.capitalize()}: {weight:.0%} ({min_w:.0%}-{max_w:.0%})")
        
        print(f"\nRisk Management:")
        print(f"  Max Single Position: {profile.max_single_position:.0%}")
        print(f"  Rebalance Threshold: {profile.rebalance_threshold:.0%}")
        print(f"{'='*60}\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Quantitative Portfolio Investment Algorithm",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --profile conservative --show-profile
  python main.py --profile intermediate --backtest --start-date 2020-01-01 --end-date 2026-12-31
  python main.py --profile aggressive --train-rl --episodes 100
  python main.py --profile intermediate --live --days 30
        """
    )
    
    parser.add_argument(
        '--profile',
        choices=list(PROFILES.keys()),
        default='intermediate',
        help='Investment profile (default: intermediate)'
    )
    parser.add_argument(
        '--show-profile',
        action='store_true',
        help='Display profile configuration and exit'
    )
    parser.add_argument(
        '--backtest',
        action='store_true',
        help='Run backtest'
    )
    parser.add_argument(
        '--train-rl',
        action='store_true',
        help='Train RL agent'
    )
    parser.add_argument(
        '--live',
        action='store_true',
        help='Run live simulation'
    )
    parser.add_argument(
        '--start-date',
        type=str,
        default='2020-01-01',
        help='Start date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--end-date',
        type=str,
        default=datetime.now().strftime('%Y-%m-%d'),
        help='End date (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--initial-capital',
        type=float,
        default=100000,
        help='Initial portfolio capital (default: 100000)'
    )
    parser.add_argument(
        '--monthly-aporte',
        type=float,
        default=1500,
        help='Monthly investment amount (default: 1500)'
    )
    parser.add_argument(
        '--episodes',
        type=int,
        default=100,
        help='RL training episodes (default: 100)'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate performance report'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file for report'
    )
    
    args = parser.parse_args()
    
    # Initialize app
    app = PortfolioAlgorithmApp(profile_name=args.profile)
    
    # Show profile if requested
    if args.show_profile:
        app.show_profile_summary()
        return
    
    # Run selected mode
    if args.backtest:
        app.run_backtest(
            start_date=args.start_date,
            end_date=args.end_date,
            initial_capital=args.initial_capital,
            monthly_aporte=args.monthly_aporte,
        )
    elif args.train_rl:
        app.run_training(
            start_date=args.start_date,
            end_date=args.end_date,
            episodes=args.episodes,
        )
    elif args.live:
        app.run_live(days=30)
    else:
        # Default: show help
        parser.print_help()
        app.show_profile_summary()
    
    # Generate report if requested
    if args.report:
        app.generate_report(output_file=args.output)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
