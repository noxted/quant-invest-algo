"""Pytest configuration and shared fixtures."""
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta


@pytest.fixture
def mock_market_data():
    """Cria dados de mercado sintéticos para testes."""
    dates = pd.date_range('2023-01-01', '2024-01-01', freq='D')
    return pd.DataFrame({
        'PETR4.SA': np.random.uniform(25, 35, len(dates)),
        'VALE3.SA': np.random.uniform(60, 80, len(dates)),
        'ITUB4.SA': np.random.uniform(25, 30, len(dates)),
        'BBAS3.SA': np.random.uniform(40, 50, len(dates)),
    }, index=dates)


@pytest.fixture
def mock_macro_data():
    """Cria dados macroeconômicos sintéticos."""
    dates = pd.date_range('2023-01-01', '2024-01-01', freq='D')
    return pd.DataFrame({
        'SELIC': np.random.uniform(10, 12, len(dates)),
        'IPCA': np.random.uniform(4, 5, len(dates)),
        'PIB': np.random.uniform(-2, 3, len(dates)),
        'CAMBIO': np.random.uniform(4.8, 5.2, len(dates)),
    }, index=dates)


@pytest.fixture
def sample_returns():
    """Retornos diários sintéticos para testes de risco."""
    np.random.seed(42)
    return np.random.normal(0.001, 0.02, 252)  # 1 ano de retornos


@pytest.fixture
def sample_portfolio():
    """Portfolio sintético para testes."""
    return {
        'PETR4.SA': 0.25,
        'VALE3.SA': 0.25,
        'ITUB4.SA': 0.25,
        'BBAS3.SA': 0.25,
    
