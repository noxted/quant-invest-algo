# Quant Invest Algo

Algoritmo quantitativo de investimento automatizado com agente autônomo, detecção de regime de mercado e interface web.

## Como funciona

O sistema opera em 3 camadas:

1. **MEGA**: Aloca entre Renda Fixa, FIIs e Ações (BR + EUA)
2. **MESO**: Distribui entre setores (Energia, Tecnologia, IA, Imóveis, Agro)
3. **MICRO**: Sugestão de ativos individuais por setor

O regime de mercado (bull/bear/sideways/transition) é detectado automaticamente usando dados reais do Ibovespa (Yahoo Finance), SELIC/IPCA (BCB) e Fed Funds Rate (FRED).

---

## Instalação

### Windows (recomendado)

```batch
# 1. Clone o repositório
git clone https://github.com/noxted/quant-invest-algo.git
cd quant-invest-algo

# 2. Execute o instalador automático
instalar.bat
```

O `instalar.bat` faz tudo: cria ambiente virtual, instala dependências e configura o `.env`.

> **IMPORTANTE**: Execute o `instalar.bat` de **dentro da pasta `quant-invest-algo`** (após o `cd quant-invest-algo`). Não rode de outro diretório.

### Linux / macOS

```bash
git clone https://github.com/noxted/quant-invest-algo.git
cd quant-invest-algo
bash instalar.sh
```

### Manual (qualquer OS)

```bash
git clone https://github.com/noxted/quant-invest-algo.git
cd quant-invest-algo

python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate.bat     # Windows

pip install -r requirements.txt

cp .env.example .env
# Edite o .env e adicione sua FRED_API_KEY
```

---

## Configuração

Edite o arquivo `.env` (criado a partir de `.env.example`):

```env
# API Key da FRED (Federal Reserve) - gratuita
# Obtenha em: https://fred.stlouisfed.org/docs/api/api_key.html
FRED_API_KEY=sua_chave_aqui
```

> **Nota**: Sem a `FRED_API_KEY`, o sistema usa o modo `demo` da FRED com dados limitados. O restante (BCB e Yahoo Finance) não requer chave.

---

## Uso

### Agente Autônomo (loop 24h sem intervenção)

```bash
python main.py --profile intermediate --auto --aporte 5000
```

Parâmetros:
- `--profile`: `conservative`, `intermediate` (padrão) ou `aggressive`
- `--aporte`: valor em reais a alocar (padrão: 5000.0)
- `--auto`: ativa o loop 24h sem parar

As decisões são salvas em `decisions.csv` e logs em `logs/portfolio.log`.

### Avaliação Única

```bash
python main.py --profile conservative --aporte 3000
```

### Dashboard Web

```bash
# Inicia o backend (FastAPI) e abre o dashboard no navegador
python app.py
```

Acesse: `http://localhost:8000`

Ou inicie apenas o backend:

```bash
python dashboard/backend_api.py
```

---

## Estrutura do Projeto

```
quant-invest-algo/
├── main.py              # CLI - ponto de entrada principal
├── app.py               # Launcher unificado (backend + browser)
├── orchestrator.py      # Núcleo: integra dados, detecta regime, aloca
├── requirements.txt     # Dependências Python
├── .env.example         # Modelo de configuração
├── instalar.bat         # Instalador Windows
├── instalar.sh          # Instalador Linux/macOS
├── build_exe.spec       # Configuração PyInstaller (.exe)
├── algorithms/
│   ├── regime_detection.py  # Detecção de regime (MA, RSI, volatilidade)
│   └── sector_allocation.py # Alocação por setor (3 camadas)
├── config/
│   └── profiles.py          # Perfis: conservador, intermediário, agressivo
├── data/
│   ├── bcb_client.py        # Banco Central do Brasil (SELIC, IPCA)
│   ├── fred_client.py       # FRED - Federal Reserve (Fed Funds, CPI)
│   └── yfinance_client.py   # Yahoo Finance (preços, índices)
└── dashboard/
    ├── backend_api.py       # API FastAPI com WebSocket
    └── index.html           # Interface web (HTML/JS vanilla)
```

---

## Dependências

Instale com `pip install -r requirements.txt`:

| Pacote | Versão | Uso |
|--------|--------|-----|
| pandas | 2.2.0 | Manipulação de dados |
| numpy | 1.26.4 | Cálculos numéricos |
| requests | 2.31.0 | APIs BCB e FRED |
| yfinance | 0.2.36 | Preços de mercado |
| python-dotenv | 1.0.0 | Variáveis de ambiente |
| scikit-learn | 1.3.0 | Algoritmos ML |
| scipy | 1.12.0 | Cálculos estatísticos |
| fastapi | 0.111.0 | Backend da API |
| uvicorn | 0.29.0 | Servidor ASGI |
| websockets | 12.0 | Comunicação em tempo real |
| httpx | 0.27.0 | Cliente HTTP assíncrono |
| pyinstaller | 6.6.0 | Gerar executável .exe |

---

## Gerar Executável (.exe)

```bash
pip install pyinstaller
pyinstaller build_exe.spec
```

O executável será gerado em `dist/QuantInvestAlgo.exe`.

---

## Perfis de Investimento

| Perfil | Renda Fixa | FIIs | Ações BR | Ações EUA |
|--------|-----------|------|----------|----------|
| `conservative` | 50% | 20% | 20% | 10% |
| `intermediate` | 35% | 20% | 30% | 15% |
| `aggressive` | 15% | 15% | 40% | 30% |

Os pesos são ajustados dinamicamente pelo regime de mercado detectado.

---

## Regimes de Mercado

| Regime | Descrição | Ação |
|--------|-----------|------|
| `bull` | Alta com volatilidade controlada | Aumenta exposição a ações |
| `bear` | Queda com risco elevado | Postura defensiva (RF + FIIs) |
| `sideways` | Lateral sem tendência clara | Mantém equilíbrio |
| `transition` | Transição entre regimes | Conservador |

---

*Agente autônomo - sem interferência humana necessária.*
