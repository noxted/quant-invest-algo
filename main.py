#!/usr/bin/env python3
\"\"\"
Main Entry Point for Quantitative Investment Algorithm

Usage:
    python main.py --profile intermediate --auto --aporte 5000
    python main.py --profile conservative --backtest --start-date 2020-01-01
\"\"\"
import sys
import logging
import argparse
import time
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

def parse_args():
    parser = argparse.ArgumentParser(description=\"Quant Invest Algo CLI\")
    parser.add_argument(\"--profile\", type=str, default=\"intermediate\", choices=[\"conservative\", \"intermediate\", \"aggressive\"])
    parser.add_argument(\"--auto\", action=\"store_true\", help=\"Run as an autonomous agent\")
    parser.add_argument(\"--aporte\", type=float, default=5000.0, help=\"Monthly aporte amount for auto mode\")
    parser.add_argument(\"--backtest\", action=\"store_true\", help=\"Run backtest\")
    parser.add_argument(\"--start-date\", type=str, default=\"2020-01-01\")
    parser.add_argument(\"--end-date\", type=str, default=datetime.now().strftime('%Y-%m-%d'))
    parser.add_argument(\"--initial-capital\", type=float, default=100000.0)
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Initialize orchestrator
    orch = PortfolioOrchestrator(profile_name=args.profile)
    
    if args.auto:
        # Modo Agente Automatico (sem interferencia humana)
        logger.info(f\"Starting in AUTONOMOUS MODE with profile: {args.profile}\")
        orch.run_autonomous_agent(aporte_mensal=args.aporte)
    elif args.backtest:
        # Modo Backtest
        logger.info(f\"Starting BACKTEST from {args.start_date} to {args.end_date}...\")
        orch.initialize_backtest(
            start_date=args.start_date,
            end_date=args.end_date,
            initial_capital=args.initial_capital
        )
        logger.info(\"Backtest completed. Check reports/ folder.\")
    else:
        # Modo Avaliacao Unica (CLI)
        logger.info(\"Running single evaluation...\")
        decision = orch.process_monthly_aporte(datetime.now(), args.aporte)
        print(\"\
\" + \"=\"*40)
        print(decision.justification)
        print(\"=\"*40 + \"\
\")

if __name__ == \"__main__\":
    main()
