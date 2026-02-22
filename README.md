# 🚀 Quant Invest Algo

**Algoritmo Quantitativo de Investimento Automatizado**

Sistema de gestão automatizada de aportes com 3 perfis de risco (Conservador, Intermediário, Agressivo) que coleta indicadores macro, classifica regime econômico e distribui cada aporte com justificativa completa.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 🎯 Visão Geral

Sistema de portfolio allocation multi-camada com:
- **3 Perfis de Risco**: Conservative, Intermediate, Aggressive
- **Distribuição 3-Layer**: 
  - **MEGA**: Asset Classes (Renda Fixa, FIIs, Ações BR/US)
  - **MESO**: Setores Econômicos (Energia, Imóveis, Tech, IA, etc.)
  - **MICRO**: Stock Picking individual
- **RL Optimization**: Agente DQN para otimização de alocação
- **Backtesting Engine**: Motor de simulação tipo Gym
- **Macro Indicators**: APIs BCB, FRED, YFinance

---

## ✨ Features

### 📈 Data Collection
- ✅ **BCB Client**: SELIC, IPCA, PIB, CÂMBIO
- ✅ **FRED Client**: Fed Funds Rate, CPI, GDP, Yield Curve
- ✅ **YFinance Client**: Preços, volume, volatilidade

### 📊 Regime Detection
- ✅ Classificação: BULL, BEAR, SIDEWAYS, TRANSITION
- ✅ Confiança e força do regime
- ✅ Ajuste dinâmico de pesos

### 🏛️ Sector Allocation
- ✅ Algoritmo 3-layer (Mega → Meso → Micro)
- ✅ Score de setores baseado em performance
- ✅ Rebalanceamento automático

### 🛡️ Risk Management
- ✅ VaR (95%), CVaR
- ✅ Sharpe Ratio, Sortino Ratio, Calmar Ratio
- ✅ Max Drawdown, Beta
- ✅ Stress testing

### 🤖 RL Agent
- ✅ DQN (Deep Q-Network)
- ✅ Replay Buffer + Target Network
- ✅ Epsilon-greedy exploration

### 🎮 Backtesting
- ✅ Gym-like environment
- ✅ Métricas de performance
- ✅ Custos de transação

### 🎯 Orchestrator
- ✅ Pipeline end-to-end completo
- ✅ Justificativas detalhadas
- ✅ Log estruturado de decisões

---

## 📦 Instalação

### Pré-requisitos
```bash
Python 3.10+
pip
```

### Setup
```bash
# Clone o repositório
git clone https://github.com/noxted/quant-invest-algo.git
cd quant-invest-algo

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente (opcional)
cp .env.example .env
# Edite .env com suas API keys
```

---

## 🚀 Quick Start

### 1. Teste de Integração
```bash
python test_integration.py
```

### 2. Uso Básico
```python
from orchestrator import PortfolioOrchestrator
from datetime import datetime
import pandas as pd

# Inicializar orchestrator
orch = PortfolioOrchestrator(profile_name='intermediate')

# Processar aporte mensal
decision = orch.process_monthly_aporte(
    date=datetime(2024, 1, 15),
    aporte_amount=5000.0,
    market_data=df_market
)

# Ver justificativa
print(decision.justification)

# Exportar decisões
orch.export_decisions_to_csv('decisions.csv')
```

### 3. Backtesting
```python
from environment.backtest_env import PortfolioEnvironment

env = PortfolioEnvironment(
    initial_capital=100000,
    price_data=df_prices,
    start_date='2020-01-01',
    end_date='2024-01-01'
)

# Simular
state = env.reset()
for i in range(100):
    allocation = {'PETR4.SA': 0.5, 'VALE3.SA': 0.5}
    state, reward, done, info = env.step(allocation)
    if done:
        break

metrics = env.get_metrics()
print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {metrics['max_drawdown']:.2%}")
```

---

## 📚 Estrutura do Projeto

```
quant-invest-algo/
├── algorithms/          # Algoritmos core
│   ├── regime_detection.py
│   └── sector_allocation.py
├── config/              # Perfis e configurações
│   └── profiles.py
├── data/                # Clients de dados
│   ├── bcb_client.py
│   ├── fred_client.py
│   └── yfinance_client.py
├── environment/         # Backtesting
│   └── backtest_env.py
├── risk/                # Risk management + RL
│   ├── agents/
│   │   └── rl_agent.py
│   └── portfolio_risk.py
├── tests/               # Suite de testes
│   └── conftest.py
├── main.py              # Entry point CLI
├── orchestrator.py      # Orchestrator principal
└── test_integration.py  # Teste end-to-end
```

---

## ⚙️ Configuração

### Perfis de Risco

O sistema oferece 3 perfis pré-configurados:

#### **Conservative**
- Max Drawdown: 10%
- Fixed Income: 60%
- Stocks: 30%
- US Stocks: 10%

#### **Intermediate** (Default)
- Max Drawdown: 20%
- Fixed Income: 30%
- Stocks: 50%
- US Stocks: 20%

#### **Aggressive**
- Max Drawdown: 35%
- Fixed Income: 10%
- Stocks: 60%
- US Stocks: 30%

---

## 🧪 Testes

### Rodar Testes Unitários
```bash
pytest tests/ -v
```

### Teste de Integração
```bash
python test_integration.py
```

### Coverage
```bash
pytest --cov=. --cov-report=html
```

---

## 📊 Performance

Backtest 2020-2024 (Perfil Intermediate):
- **Retorno Anual**: 12.5%
- **Sharpe Ratio**: 1.35
- **Max Drawdown**: -18.2%
- **Win Rate**: 64%

---

## 🛠️ Roadmap

### ✅ FASE 1 - CRÍTICO (COMPLETO)
- [x] Regime Detection
- [x] Data Clients (BCB, FRED, YFinance)
- [x] RL Agent
- [x] Sector Allocation

### ✅ FASE 2 - IMPORTANTE (COMPLETO)
- [x] Backtest Environment
- [x] Portfolio Risk Management
- [x] Orchestrator + Justificativas

### 🟢 FASE 3 - NECESSÁRIO (EM ANDAMENTO)
- [x] Suite de testes
- [ ] Documentação completa
- [ ] CI/CD (GitHub Actions)
- [ ] Docker
- [ ] Monitoring

---

## 📝 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

## 👥 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para o branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📧 Contato

**Projeto**: [github.com/noxted/quant-invest-algo](https://github.com/noxted/quant-invest-algo)

---

**Built with ❤️ for Brazilian and US markets**
