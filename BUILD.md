# Como gerar o .exe do Quant Invest Algo

Este guia explica como empacotar o projeto num unico executavel **`QuantInvestAlgo.exe`** (Windows) ou binario (Linux/Mac) usando o PyInstaller. Depois disso, qualquer pessoa pode usar o app com um duplo-clique, sem instalar Python, sem abrir terminal.

---

## Pre-requisitos (so voce, o desenvolvedor, precisa fazer isso)

- Python 3.10 ou superior instalado
- Git instalado
- Todas as dependencias do projeto instaladas

---

## Passo a passo

### 1. Clone e configure o projeto

```bash
git clone https://github.com/noxted/quant-invest-algo.git
cd quant-invest-algo
```

### 2. Instale as dependencias

```bash
pip install -r requirements.txt
```

### 3. Configure o .env (necessario para o build incluir suas chaves)

```bash
# Windows
copy .env.example .env
# Linux/Mac
cp .env.example .env
```

Abra o arquivo `.env` e preencha:
```
FRED_API_KEY=sua_chave_fred_aqui
```

### 4. Instale o PyInstaller

```bash
pip install pyinstaller
```

### 5. Gere o executavel

```bash
pyinstaller build_exe.spec
```

Aguarde alguns minutos. O PyInstaller vai empacotar Python + todas as dependencias + o dashboard.

### 6. Executavel gerado

O arquivo final estara em:
```
dist/
  QuantInvestAlgo.exe    <- Windows
  QuantInvestAlgo        <- Linux/Mac
```

---

## Como o .exe funciona (para o usuario final)

1. **Copie o .exe** para qualquer pasta do seu computador
2. **Crie um arquivo `.env`** na mesma pasta com sua chave FRED:
   ```
   FRED_API_KEY=sua_chave_aqui
   ```
3. **Duplo-clique no `QuantInvestAlgo.exe`**
4. Uma janela de terminal abre mostrando o progresso
5. Em alguns segundos, o **browser abre automaticamente** com o dashboard em `http://localhost:8000`
6. Para encerrar: feche a janela do terminal ou pressione `Ctrl+C`

> O usuario **nao precisa** ter Python instalado. O .exe carrega tudo sozinho.

---

## Tamanho estimado do .exe

| Bibliotecas incluidas | Tamanho aproximado |
|---|---|
| Sem PyTorch (so FastAPI + pandas) | ~150-250 MB |
| Com PyTorch (agente RL) | ~500-800 MB |

> Dica: Para reduzir o tamanho, use um ambiente virtual limpo com so as dependencias necessarias antes de rodar o PyInstaller.

---

## Arquivos gerados pelo PyInstaller (pode ignorar/gitignore)

```
build/          <- arquivos temporarios do build
dist/           <- executavel final fica aqui
*.spec.bak      <- backup automatico
__pycache__/
```

Esses diretorios ja estao no `.gitignore`.

---

## Solucao de problemas

### Erro: `ModuleNotFoundError` ao rodar o .exe
Significa que alguma dependencia nao foi incluida. Adicione o modulo na lista `hiddenimports` do `build_exe.spec` e regenere.

### Erro: `backend_api.py not found`
Verifique se o build foi feito a partir da raiz do projeto (onde o `build_exe.spec` esta).

### Dashboard nao abre no browser
Acesse manualmente: `http://localhost:8000`

### Antivirus bloqueia o .exe
Isso e normal com executaveis gerados pelo PyInstaller. Adicione uma excecao no antivirus ou assine o executavel digitalmente.

---

## Estrutura que o .exe carrega internamente

```
QuantInvestAlgo.exe
  -> app.py               (launcher principal)
  -> dashboard/
       index.html         (interface visual)
       backend_api.py     (servidor FastAPI)
  -> algorithms/          (regime detection, sector allocation)
  -> config/              (perfis conservative/intermediate/aggressive)
  -> data/                (BCB, FRED, YFinance clients)
  -> environment/         (backtesting engine)
  -> risk/                (RL agent, portfolio risk)
  -> orchestrator.py      (coordenador central)
  -> .env                 (suas chaves de API)
```

---

**Desenvolvido para o mercado BR + US | MIT License**
