# 🚀 ROADMAP - Quant Invest Algo

**Data:** 22 Fevereiro, 2026  
**Status:** Projeto em Desenvolvimento  
**Prioridade:** CRÍTICO → IMPORTANTE → NECESSÁRIO

---

## 📊 RESUMO EXECUTIVO

Este é um roadmap consolidado que integra:
- ✅ Estrutura já criada no GitHub (5 modelos base)
- ✅ Planejamento detalhado no Notion (3 camadas de decisão)
- ❌ Implementações faltando (funções determinísticas codadas)

**Objetivo Principal:** Sistema de gestão automatizada de aportes com 3 perfis de risco (Conservador, Intermediário, Agressivo) que coleta indicadores macro, classifica regime econômico e distribui cada aporte com justificativa completa.

---

## 🔴 FASE 1: CRÍTICO (Sprint 1-2)

### 1.1 `algorithms/regime_detection.py` - VAZIO ❌
**O que falta:** Implementação completa do detector de regimes macro

**Responsabilidade:**
- Analisar indicadores macroeconômicos (SELIC, PIB, Inflação, Câmbio)
- Classificar regime atual: BULL, BEAR, SIDEWAYS, TRANSITION
- Retornar força do regime (0-1) para ajustar pesos

**Indicadores a usar:**
- BCB: SELIC, IPCA, PIB
- Yahoo Finance: USD/BRL, VIX
- FRED: Fed Funds Rate, CPI

**Método esperado:**
```python
def detect_regime(indicators: Dict) -> Tuple[str, float]:
    # regime: 'bull' | 'bear' | 'sideways' | 'transition'
    # strength: 0.0 - 1.0
    pass
```

---

### 1.2 `data/` Clients - VAZIOS ❌

#### 1.2.1 `yfinance_client.py`
**Responsabilidade:** Baixar dados de mercado (preços, FIIs, ações)

**Métodos:**
- `get_stock_prices(ticker, days=252)` → DataFrame
- `get_fii_data(fii_ticker)` → Dict com P/VP, DY, volume
- `get_us_stocks(ticker)` → Dados US
- `get_vix()` → Volatilidade global

#### 1.2.2 `bcb_client.py`
**Responsabilidade:** API do Banco Central do Brasil

**Series IDs:**
- 432: SELIC meta
- 433: IPCA
- 189: IGP-M
- 1: USD/BRL

**Métodos:**
- `get_selic()` → float (taxa atual)
- `get_ipca()` → float (inflação)
- `get_series(series_id, days=252)` → Series temporal

#### 1.3 `data/fred_client.py` - NÃO EXISTE ❌
**Novo arquivo necessário:** Cliente para FRED API (Federal Reserve Economic Data)

**Series IDs:**
- FEDFUNDS: Fed Funds Rate
- CPIAUCSL: CPI US
- A191RL1Q225SBEA: GDP Growth
- T10Y2Y: Yield Curve

---

### 1.3 `risk/rl_agent.py` - VAZIO ❌
**Responsabilidade:** Agente de Reinforcement Learning (DQN-based)

**O que implementar:**
- Rede neural (PyTorch ou TensorFlow)
- Replay Buffer
- Target Network
- Loss Function (MSE)
- Methods: `train()`, `predict(state)`, `save()`, `load()`

**Dependências a adicionar:**
```
torch==2.0.0
tensorflow==2.13.0
stable-baselines3==2.0.0
```

---

## 🟡 FASE 2: IMPORTANTE (Sprint 3-4)

### 2.1 `environment/backtest_env.py` - ESQUELETO ❌
**Responsabilidade:** Ambiente tipo Gym para backtesting

**Métodos obrigatórios:**
- `__init__(initial_capital, start_date, end_date)`
- `reset()` → state
- `step(action)` → (state, reward, done, info)
- `render()` → visualização

**State Space:**
```python
state = {
    'portfolio_value': float,
    'positions': Dict[str, float],  # ticker -> quantidade
    'regime': str,  # bull/bear/sideways
    'price_history': np.array,  # últimos 30 dias
    'macro_indicators': Dict,  # SELIC, PIB, VIX, etc
}
```

---

### 2.2 `risk/portfolio_risk.py` - VAZIO ❌
**Responsabilidade:** Cálculos de risco do portfólio

**Métricas a implementar:**
- Value at Risk (VaR 95%)
- Conditional VaR (CVaR)
- Sharpe Ratio
- Sortino Ratio
- Calmar Ratio
- Máximo Drawdown
- Beta

**Métodos:**
```python
def calculate_var(returns, confidence=0.95) -> float
def calculate_sharpe(returns, risk_free_rate=0.05) -> float
def calculate_max_drawdown(prices) -> float
```

---

### 2.3 `orchestrator.py` - COMPLETAR JUSTIFICATIVAS ❌
**Responsabilidade:** Sistema de decisão + Justificativas

**O que tem:**
- Pipeline de decisão ✅
- Integração com 3 camadas ✅

**O que falta:**
- Log estruturado de decisões
- Geração de justificativas em texto
- Rastreamento de performance vs prognóstico

---

## 🟢 FASE 3: NECESSÁRIO (Sprint 5+)

### 3.1 Tests (`tests/`)
- Unit tests para cada módulo
- Integration tests (pipeline completo)
- Backtesting tests (histórico)
- Edge cases (mercado anormal, gaps)

### 3.2 Documentação
- API Reference completa
- Guias de uso (CLI, API)
- Exemplos práticos
- Troubleshooting

### 3.3 CI/CD
- GitHub Actions workflows
- Docker container
- Automated tests on commit

### 3.4 Performance & Monitoring
- Logging estruturado
- Métricas de performance
- Alertas configuráveis

---

## 📋 DEPENDENCY UPDATES NECESSÁRIOS

**Adicionar a `requirements.txt`:**
```
torch==2.0.0                    # RL Networks
tensorflow==2.13.0              # Alternative RL
stable-baselines3==2.0.0        # RL Framework
gym==0.26.2                     # RL Environment
pandas==2.2.0                   # ✅ Já existe
numpy==1.26.4                   # ✅ Já existe
requests==2.31.0                # ✅ Já existe
yfinance==0.2.36                # ✅ Já existe
matplotlib==3.8.2               # ✅ Já existe
scipy==1.12.0                   # ✅ Já existe
scikit-learn==1.3.0             # Para métricas
python-dotenv==1.0.0            # Config/Secrets
```

---

## 🎯 FASES DE IMPLEMENTAÇÃO

### Sprint 1 (Semana 1): REGIME + BCB
- [ ] `regime_detection.py` completo
- [ ] `bcb_client.py` com todas as séries
- [ ] Testes básicos

### Sprint 2 (Semana 2): DATA CLIENTS
- [ ] `yfinance_client.py` funcional
- [ ] `fred_client.py` novo
- [ ] Integração com environment

### Sprint 3 (Semana 3): RL + BACKTEST
- [ ] `rl_agent.py` DQN completo
- [ ] `backtest_env.py` completo
- [ ] Primeiro backtest

### Sprint 4 (Semana 4): RISCO + JUSTIFICATIVAS
- [ ] `portfolio_risk.py` com todas métricas
- [ ] `orchestrator.py` justificativas
- [ ] Log de decisões

### Sprint 5+ (Ongoing): TESTES + DOCS
- [ ] Suite completa de testes
- [ ] Documentação API
- [ ] CI/CD setup

---

## 📎 REFERÊNCIAS

**Notion:** [Algoritmo de Investimento — Planejamento Geral](https://www.notion.so/Algoritmo-de-Investimento-Planejamento-Geral)

**Arquitetura:** [Técnica: Backtest & IA (RL)](https://www.notion.so/Arquitetura-T-cnica-Backtest-IA-RL)

**Databases:**
- 📊 Indicadores Macro
- 🏛️ Setores & Subsegmentos
- 📝 Log de Decisões por Aporte
- 🚀 Roadmap de Módulos Avançados

---

## ✅ CHECKLIST DE PRIORIDADES

**CRÍTICO (Must Have):**
- [ ] Regime Detection
- [ ] Data Clients (BCB + YFinance + FRED)
- [ ] RL Agent

**IMPORTANTE (Should Have):**
- [ ] Backtest Environment
- [ ] Risk Module
- [ ] Decision Justification System

**NECESSÁRIO (Nice to Have):**
- [ ] Tests
- [ ] Documentation
- [ ] CI/CD
- [ ] Monitoring

---

**Última atualização:** 22 Fevereiro, 2026 12:00 -03  
**Próxima revisão:** 29 Fevereiro, 2026
