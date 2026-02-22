# 🚀 Quant Invest Algo - App Único

Algoritmo Quantitativo de Investimento Automatizado com interface visual e agente autônomo.

## 🤖 Modo Agente Automático (Sem Intervenção)
O algoritmo monitora o mercado e gera recomendações automaticamente a cada 24h.
```bash
python main.py --profile intermediate --auto --aporte 5000
```

## 🚀 Launcher Unificado (Dashboard)
Inicia o backend e abre o dashboard no navegador automaticamente.
```bash
python app.py
```

## 📦 Instalação Rápida
1. Clone o repositório.
2. Dê duplo-clique em `instalar.bat` (Windows).
3. Configure sua `FRED_API_KEY` no arquivo `.env`.

## 🛠️ Estrutura Otimizada
- `algorithms/`: Lógica de detecção de regime e alocação.
- `app.py`: Ponto de entrada para uso com interface gráfica.
- `main.py`: CLI para o agente automático e backtest.
- `orchestrator.py`: Núcleo de integração em tempo real.
- `dashboard/`: Interface web (FastAPI + HTML/JS).

---
*Foco em simplicidade e automação total.*
