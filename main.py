#!/usr/bin/env python3
"""
Main Entry Point - Quant Invest Algo

Usage:
    python main.py --profile intermediate --auto --aporte 5000
    python main.py --profile conservative --aporte 3000
    python main.py  # avaliacao unica com perfil padrao
"""
import sys
import os
import logging
import argparse
from pathlib import Path
from datetime import datetime
from orchestrator import PortfolioOrchestrator

# Garante que a pasta logs/ existe
Path('logs').mkdir(exist_ok=True)

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
    parser = argparse.ArgumentParser(description="Quant Invest Algo CLI")
    parser.add_argument("--profile", type=str, default="intermediate",
                        choices=["conservative", "intermediate", "aggressive"])
    parser.add_argument("--auto", action="store_true",
                        help="Executa como agente autonomo (loop 24h sem intervencao humana)")
    parser.add_argument("--aporte", type=float, default=5000.0,
                        help="Valor mensal do aporte em reais")
    return parser.parse_args()


def main():
    args = parse_args()

    # Inicializa orquestrador
    orch = PortfolioOrchestrator(profile_name=args.profile)

    if args.auto:
        # Modo Agente Automatico - sem interferencia humana
        logger.info(f"Iniciando MODO AUTONOMO com perfil: {args.profile}")
        orch.run_agent(amount=args.aporte)
    else:
        # Avaliacao unica
        logger.info("Executando avaliacao unica...")
        decision = orch.process_aporte(amount=args.aporte)
        print("\n" + "=" * 50)
        print(f"Data: {decision['date']}")
        print(f"Regime: {decision['regime']}")
        print(f"Justificativa: {decision['justification']}")
        print("\nAlocacao recomendada:")
        for asset, value in decision['allocation'].items():
            print(f"  {asset}: R$ {value:,.2f}")
        print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
